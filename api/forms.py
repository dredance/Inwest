from django import forms
from .models import KamienieMilowe, Projekt, SL, SM, UK, OB, MB
from django.forms.models import modelformset_factory


class DateInput(forms.DateInput):
    input_type = "date"

    def __init__(self, **kwargs):
        kwargs["format"] = "%Y-%m-%d"
        super().__init__(**kwargs)


class KamienieMiloweForm(forms.ModelForm):
    # id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    def __init__(self, *args, **kwargs):
        super(KamienieMiloweForm, self).__init__(*args, **kwargs)
        for _, field in self.fields.items():
            if type(field) is type(forms.DateField()):
                field.widget = DateInput()
        self.fields['okres'].widget.attrs.update({'class': 'disabled'})
        self.fields['projekt'].widget.attrs.update({'class': 'disabled'})

    class Meta:
        model = KamienieMilowe
        fields = '__all__'


class CustomTableForm(forms.ModelForm):
    id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    def __init__(self, prefix=None, *args, **kwargs):
        super(CustomTableForm, self).__init__(*args, **kwargs)
        for _, field in self.fields.items():
            if type(field) is type(forms.DateField()):
                field.widget = DateInput()
            if field.required == True:
                field.widget.attrs['required'] = ''
        self.fields['projekt'].widget = forms.HiddenInput()
        self.fields['okres'].widget = forms.HiddenInput()
        self.prefix = f'{prefix}'

    class Meta:
        fields = '__all__'
        widgets = {'sily_wlasne': forms.CheckboxInput()}


    # New + Update
SlFormSet = modelformset_factory(SL, form=CustomTableForm, extra=0)
SmFormSet = modelformset_factory(SM, form=CustomTableForm, extra=0)
UkFormSet = modelformset_factory(UK, form=CustomTableForm, extra=0)
OBFormSet = modelformset_factory(OB, form=CustomTableForm, extra=0)
MBFormSet = modelformset_factory(MB, form=CustomTableForm, extra=0)

# Only New
NewSlFormSet = modelformset_factory(SL, form=CustomTableForm, extra=1)
NewSmFormSet = modelformset_factory(SM, form=CustomTableForm, extra=1)
NewUkFormSet = modelformset_factory(UK, form=CustomTableForm, extra=1)
NewOBFormSet = modelformset_factory(OB, form=CustomTableForm, extra=1)
NewMBFormSet = modelformset_factory(MB, form=CustomTableForm, extra=1)


class NewDataForm(forms.Form):
    projekt = forms.ModelChoiceField(queryset=Projekt.objects.all())
    okres = forms.DateField(widget=DateInput(attrs={'class': 'disabled'}), required=False)
    download_data = forms.BooleanField(required=False, label="Ładuj dane z poprzedniego miesiąca")


class UpdateDataForm(forms.Form):
    projekt = forms.ModelChoiceField(queryset=Projekt.objects.all())
    okres = forms.DateField()


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={"id": "defaultLoginFormName",
                                                            "class": "form-control mb4 validate"}),
                               label='Login')
    password = forms.CharField(widget=forms.PasswordInput(attrs={"id": "defaultLoginFormPassword",
                                                            "class": "form-control mb-4 validate"}),
                               label='Hasło')