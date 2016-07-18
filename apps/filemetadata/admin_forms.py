from django import forms
from apps.filemetadata.models import FileMetadata
from apps.filemetadata.utils import validate_filemetadata

class FileMetadataForm(forms.ModelForm):

    class Meta:
        model = FileMetadata
        exclude = ('modified', 'created')

    def clean(self):
        schema = self.cleaned_data.get('schema')
        metadata = self.cleaned_data.get('metadata')

        success, err_msg = validate_filemetadata(schema.get_schema_dict(), metadata)
        if not success:
            if err_msg:
                user_msg = err_msg
            else:
                user_msg = 'The metadata does not comply with the schema.'
            self.add_error('metadata', user_msg)
            #raise forms.ValidationError('The metadata does no comply with the schema.')

        return self.cleaned_data

        #return self.cleaned_data
