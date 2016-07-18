from django.contrib import admin
from apps.filemetadata.models import MetadataSchema, FileMetadata
from apps.filemetadata.admin_forms import FileMetadataForm

class MetadataSchemaAdmin(admin.ModelAdmin):
    """
    For the JSON schema, only checks if JSON
    can be turned into a valid python dict
    """
    save_on_top = True
    list_display = ['title', 'slug', 'version', 'published', 'contributor',\
        'description','modified', 'created']
    search_fields = ['title',]
    list_filter = ['published', 'contributor', 'version', 'title']
    readonly_fields = ['modified', 'created']
admin.site.register(MetadataSchema, MetadataSchemaAdmin)


class FileMetadataAdmin(admin.ModelAdmin):
    """
    Includes validation of the metadata against the selected schema
    """
    form = FileMetadataForm
    save_on_top = True
    readonly_fields = ['modified', 'created',  'schema_link', 'view_schema']
    list_display = ['schema', 'datafile_id', 'version', 'published', 'schema_link', 'modified', 'created']
    search_fields = ['schema__title',]
    list_filter = ['published', 'schema',]
admin.site.register(FileMetadata, FileMetadataAdmin)
