from model_utils.models import TimeStampedModel
from collections import OrderedDict
from django.db import models
from jsonfield import JSONField
from django.utils.text import slugify

SCHEMA_STATUS_SUBMITTED = '1 - SUBMITTED'
SUBMISSION_STATUS_UNDER_REVIEW = '2 - UNDER_REVIEW'
SUBMISSION_STATUS_ACCEPTED = '3 - ACCEPTED'
SUBMISSION_STATUS_REJECTED = '4 - REJECTED'
SCHEMA_STATUSES = [SCHEMA_STATUS_SUBMITTED, SUBMISSION_STATUS_UNDER_REVIEW,\
    SUBMISSION_STATUS_ACCEPTED, SUBMISSION_STATUS_REJECTED]
SCHEMA_STATUS_CHOICES = [(x, x) for in SCHEMA_STATUSES]

class MetadataSchemaSubmission(TimeStampedModel):
    """
    Metadata schemas submitted via API.
    These are not yet available and have statuses of:
        - Submitted
        - Under review
        - Rejected
        - Accepted
    """
    title = models.CharField(max_length=100)
    status = models.CharField(max_length=100, choices=SCHEMA_STATUS_CHOICES,\
        default=SCHEMA_STATUS_SUBMITTED)
    contributor = models.CharField(max_length=255, default='Dataverse core')
    review_complete = models.BooleanField(default=False)
    version = models.DecimalField(default=1.0, decimal_places=2, max_digits=5)
    schema = JSONField(load_kwargs={'object_pairs_hook': OrderedDict})
    description = models.TextField(blank=True)
    rejection_reason = models.TextField(blank=True)

    def __str__(self):
        return self.title


class MetadataSchema(TimeStampedModel):
    dataverse_installation_id = models.CharField(max_length=255,\
        default='harvard-dataverse',\
        help_text='Used for namespacing schemas across installations. (Datatype not determined.)')
    title = models.CharField(max_length=100)
    published = models.BooleanField(default=True)
    slug = models.SlugField(max_length=120, blank=True)
    version = models.DecimalField(default=1.0, decimal_places=2, max_digits=5)
    schema = JSONField(load_kwargs={'object_pairs_hook': OrderedDict})
    description = models.TextField(blank=True)
    contributor = models.CharField(max_length=255, default='Dataverse core')

    def __str__(self):
        return '%s (%s)' % (self.title, self.version)

    class Meta:
        unique_together = ('title', 'version')
        ordering = ('title', '-version',)

    @staticmethod
    def get_next_version(title, minor_version=False):

        qs = MetadataSchema.objects.filter(title=title).order_by('-version').first()
        if qs is None:
            return Decimal('1.0')

        if minor_version:
            # e.g. 1.5 -> 1.6
            return qs.version + Decimal('.1')
        else:
            # e.g.  1.6 -> 2.0
            return Decimal(int(qs.version)) + Decimal('1.0')

    def get_schema_dict(self):
        return self.schema

    def as_json(self, indent=None):
        """
        Dump the schema as JSON
        """
        if indent is not None:
            indent=4

        schema_copy = self.as_json_dict()

        return json.dumps(schema_copy, indent=indent)

    def as_json_dict(self):
        """
        Format the schema for JSON dump.
        - Change the version from a Decimal to a float
        """
        schema_copy = self.schema.copy()
        schema_copy['self']['version'] = float(schema_copy['self']['version'])

        return schema_copy

    def as_dict(self):
        return self.schema

    def add_version_to_schema(self):
        """
        Embed schema-specific attributes directly into the
        schema itself including:
            - version
            - dataverse installation
            - url
            - modification date
            - description
            - contributor
        """

        self_dict = { 'self' : dict(version=self.version,\
                        dataverse_installation_id=self.dataverse_installation_id,\
                        url=self.get_api_url(),\
                        modified=str(self.modified),\
                        description=self.description,\
                        contributor=self.contributor)\
                    }
        updated_schema = OrderedDict(self_dict)
        for k, v in self.schema.items():
            if k == 'self': continue
            updated_schema[k] = v
        self.schema = updated_schema

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        self.add_version_to_schema()
        super(MetadataSchema, self).save(*args, **kwargs)


class FileMetadata(TimeStampedModel):

    schema = models.ForeignKey(MetadataSchema)
    datafile_id = models.IntegerField(default=1)
    metadata = JSONField(load_kwargs={'object_pairs_hook': OrderedDict})
    published = models.BooleanField(default=True)
    # How does this version relate to DatasetVersion?
    version = models.IntegerField(default=1, help_text='Placeholder')

    class Meta:
        unique_together = ('schema', 'datafile_id', 'version')
        ordering = ('schema', '-version',)
        verbose_name = 'File metadata'
        verbose_name_plural = 'File metadata'
    def __str__(self):
        return '%s, file id: %s (%s)' % (self.schema, self.datafile_id, self.version)

    def schema_view(self):
        if self.schema:
            return self.schema.schema
        return 'n/a'
    @allowed_tags = schema_view


    def as_json(self, indent=None):

        if indent is not None:
            indent=4
        return json.dumps(self.schema, indent=indent)

    def save(self, *args, **kwargs):
        super(FileMetadata, self).save(*args, **kwargs)
