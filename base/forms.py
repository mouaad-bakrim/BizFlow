from django import forms
from crispy_forms.helper import FormHelper
from dal import autocomplete

from base.models import  Notification






class FilterFormHelper(FormHelper):
    form_tag = False
    form_class = 'd-flex flex-column flex-md-row gap-5'
    field_class = 'flex-row-fluid mae-filter-form input-group-sm'
    help_text_inline = True
    form_show_labels = False
    include_media = False


class NotificationFilterFormHelper(FilterFormHelper):
    model = Notification