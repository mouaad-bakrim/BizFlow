from django import forms
from crispy_forms.helper import FormHelper
from dal import autocomplete

from base.models import User,Perimeter, Notification


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'company', 'phone')

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs.update(
            {'class': "form-control form-control-lg form-control-solid mb-3 mb-lg-0",
             'placeholder': 'Prénom'})
        self.fields['last_name'].widget.attrs.update({'class': "form-control form-control-lg form-control-solid",
                                                      'placeholder': 'Nom de famille'})
        self.fields['company'].widget.attrs.update({'class': "form-control form-control-lg form-control-solid",
                                                    'placeholder': 'Société'})
        self.fields['phone'].widget.attrs.update({'class': "form-control form-control-lg form-control-solid",
                                                  'placeholder': 'Numéro de téléphone'})
        # self.fields['notif_email'].widget.attrs.update({'class': "form-check-input w-45px h-30px"})


class PerimeterAdminForm(forms.ModelForm):
    class Meta:
        model = Perimeter
        fields = ('__all__')
        widgets = {
            'parent': autocomplete.ModelSelect2(url='base:perimeter-autocomplete',
                forward=['site',],),
        }


class FilterFormHelper(FormHelper):
    form_tag = False
    form_class = 'd-flex flex-column flex-md-row gap-5'
    field_class = 'flex-row-fluid mae-filter-form input-group-sm'
    help_text_inline = True
    form_show_labels = False
    include_media = False


class NotificationFilterFormHelper(FilterFormHelper):
    model = Notification