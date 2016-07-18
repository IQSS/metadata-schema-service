from django.test import TestCase
from apps.filemetadata.models import MetadataSchema, FileMetadata
from apps.filemetadata.utils import validate_schema, validate_schema_string,\
    ERR_MSG_SCHEMA_NONE, ERR_MSG_DATA_NONE, ERR_MSG_EMPTY_DICT,\
    ERR_MSG_JSON_CONVERSION_FAILED, ERR_NO_SCHEMA_SPECIFIED

class SchemaTestCase(TestCase):

    fixtures = ['test_schemas.json']

    def setUp(self):
        pass
        #print ('count: ', MetadataSchema.objects.all().count())
        #Animal.objects.create(name="lion", sound="roar")
        #Animal.objects.create(name="cat", sound="meow")

    def test_01_schema_validation(self):
        """Test valid schemas loaded in fixtures"""

        for mschema in MetadataSchema.objects.all():
            # validate schema as dict
            valid, msg = validate_schema(mschema.schema)
            self.assertEqual(valid, True)

            # validate schema as JSON string
            valid2, msg2 = validate_schema_string(mschema.as_json())
            self.assertEqual(valid2, True)


    def test_02_schema_empty(self):
        """Test schemas: Empty schema"""
        bad_schema = {}
        valid, msg = validate_schema(bad_schema)
        self.assertEqual(valid, False)
        self.assertEqual(msg, [ERR_MSG_EMPTY_DICT])


    def test_03_schema_invalid_json(self):
        """Test schema: Invalid JSON"""
        bad_schema = "howdy"    #{ 1 : "no json here "}
        valid, msg = validate_schema_string(bad_schema)
        self.assertEqual(valid, False)
        self.assertEqual(msg, [ERR_MSG_JSON_CONVERSION_FAILED])


    def test_04_bad_schema(self):
        """Test invalid schema: No "$schema" element"""
        bad_schema = { 1 : "no json here "}
        valid, msg = validate_schema(bad_schema)
        self.assertEqual(valid, False)
        self.assertTrue(len(msg) > 0)
        if len(msg) > 0:
            self.assertTrue(msg[0].startswith(ERR_NO_SCHEMA_SPECIFIED[:25]))
        print (msg, msg)
