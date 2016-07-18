"""
Convenience methods that wrap jsonschema libraries validation

See jsonschema docs for error breakdown:
https://python-jsonschema.readthedocs.org/en/latest/errors/#module-jsonschema
"""
import json
import jsonschema
from collections import OrderedDict
from jsonschema import Draft4Validator
from apps.proj_utils.msg_util import msg, msgt


# JSON Schema validator information
CHOSEN_VALIDATOR_CLASS = Draft4Validator
ERR_NOTE_VALIDATOR_TYPE = '(Note: JSON schema Draft 4 validation was used)'

# General error messages for Null (None) values
ERR_MSG_JSON_CONVERSION_FAILED = 'The schema could not be converted to JSON.'
ERR_MSG_SCHEMA_NONE = 'The schema was None (or null)'
ERR_MSG_DATA_NONE = 'The JSON metadata was None (or null)'
ERR_MSG_EMPTY_DICT = 'The JSON schema was empty.'

# Acceptable schema versions
ACCEPTABLE_SCHEMA_VERSIONS = ['http://json-schema.org/draft-04/schema#']
ERR_NO_SCHEMA_SPECIFIED = 'Please specify an acceptable schema. example {"$schema" : "%s"}'\
    % ACCEPTABLE_SCHEMA_VERSIONS[0]
ERR_NOT_ACCEPTABLE_SCHEMA = 'The "$schema" value is not recognized.  %s' % ERR_NO_SCHEMA_SPECIFIED


def format_error_message(jsonschema_err):
    """
    Given a jsonschema.exceptions.SchemaError,
    return a list of formatted error messages
    """
    assert isinstance(jsonschema_err, jsonschema.exceptions.SchemaError) or\
        isinstance(jsonschema_err, jsonschema.exceptions.ValidationError),\
        ("jsonschema_err must be an instance of: jsonschema.exceptions.SchemaError"
        " or jsonschema.exceptions.ValidationError ")

    err_msgs = []
    if jsonschema_err.path:
        path_as_strings = [str(x) for x in jsonschema_err.path]
        err_msg = 'Error Location: %s' % '->'.join(path_as_strings)
        err_msgs.append(err_msg)
    err_msgs.append('Error: %s' % jsonschema_err.message)
    err_msgs.append(ERR_NOTE_VALIDATOR_TYPE)

    return err_msgs

def validate_schema_string(schema_string):
    """
    Convert schema_string to a python OrderedDict
    and then validate it
    """
    if schema_string is None:
        return False, [ERR_MSG_SCHEMA_NONE]

    try:
        schema_dict = json.loads(schema_string, object_pairs_hook=OrderedDict)
    except ValueError as value_err:
        return False, [ERR_MSG_JSON_CONVERSION_FAILED]

    return validate_schema(schema_dict)


def validate_schema(schema_dict):
    """
    Validate a schema using the Draft4Validator
    "schema_dict" should be a python dict or OrderedDict
    """
    if schema_dict is None:
        return False, [ERR_MSG_SCHEMA_NONE]

    if len(schema_dict) == 0:
        return False, [ERR_MSG_EMPTY_DICT]

    schema_string = schema_dict.get('$schema', None)
    if schema_string is None:
        return False, [ERR_NO_SCHEMA_SPECIFIED]
    if not schema_string in ACCEPTABLE_SCHEMA_VERSIONS:
        return False, [ERR_NOT_ACCEPTABLE_SCHEMA]


    try:
        CHOSEN_VALIDATOR_CLASS.check_schema(schema_dict)
        #print ("looks ok:", schema_dict)
        return True, None
    except jsonschema.exceptions.SchemaError as schema_err:
        return False, format_error_message(schema_err)


def validate_filemetadata(schema_dict, data_dict):
    """
    (a) Validate a JSON schema and then
    (b) Validate data against that JSON schema
    """
    if schema_dict is None:
        return False, [ERR_MSG_SCHEMA_NONE]

    if data_dict is None:
        return False, [ERR_MSG_DATA_NONE]

    try:
        el_validator = CHOSEN_VALIDATOR_CLASS(schema_dict)
        el_validator.validate(data_dict)
        return True, None
    except jsonschema.exceptions.SchemaError as schema_err:
        #
        # The schema did not pass Validation
        return False, format_error_message(schema_err)

    except jsonschema.exceptions.ValidationError as validation_err:
        #
        # The data did not validate against the schema
        return False, format_error_message(validation_err)


"""
import json
import jsonschema
from jsonschema import Draft4Validator
import os

def validate_schemas():
    json_fnames = [x for x in os.listdir('.') if x.endswith('.json')]
    for fname in json_fnames:
        #if not fname == 'customGSD.json': continue
        print ('-' * 40)
        print ('checking: %s', fname)
        print ('-' * 40)
        content = open(fname, 'r').read()
        schema_dict = json.loads(content)
        try:
            Draft4Validator.check_schema(schema_dict)
            print ('yes')
        except jsonschema.exceptions.SchemaError as schema_err:
            print (schema_err)

"""
