from django import forms
from django.utils import timezone


class UploadFileForm(forms.Form):
    #title = forms.CharField(max_length=50)
    file = forms.FileField(label='Select a file', help_text='max. 42 megabytes')

class UploadDateForm(forms.Form):
    date = forms.DateField(widget=forms.TextInput(attrs={'type':'date', 'placeholder':'xxx'}))


class FormDateAndUpload(forms.Form):
    #date = forms.DateField(widget=forms.TextInput(attrs={'type': 'month'}), help_text="vyberte měsíc a rok")
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'month'}), help_text="vyberte měsíc a rok")
    date1 = forms.CharField(max_length=50)
    start_date = forms.DateField(label=("Start date"),
                                        initial=timezone.now().date(),
                                        input_formats=['%Y/%m/%d'],
                                        widget=forms.DateInput(format='%Y/%m/%d'))

    #file = forms.FileField(label='Select a file', help_text='zde nahrejte korespondující AIS')


    def clean(self):
        cleaned_data = super().clean()
        print("cleaned_data-%s" %cleaned_data)
        #date = cleaned_data.get('date')
        date1 = cleaned_data.get('date1')
        start_date = cleaned_data.get('start_date')
        print( date1, start_date)
        #file = cleaned_data.get('file')
        if not date1:
            raise forms.ValidationError('You have to write something!')
        return cleaned_data


    def clean_date(self):
        data = self.cleaned_data['date']
        print("printing-%s" %date)

        return data

