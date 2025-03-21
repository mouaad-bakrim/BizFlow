from django.contrib import admin
from django.forms import models

from admin_interface.models import Theme

from tree_queries.forms import TreeNodeChoiceField

from .managers import BaseModelAdmin
from .models import Site,  Company, SiteSequences



@admin.register(Company)
class CompanyAdmin(BaseModelAdmin):
    fieldsets = [
        ('Général', {'fields': [('name', 'company_form'), 'logo', ('address1', 'address2'), ('city', 'phone')]}),
        ('Infos administratives', {'fields': [('licence', 'registration_id'), ('social_id', 'tax_id'), 'company_id']}),
    ]
    list_display = ('name', 'city')
    search_fields = ['name', 'city']
    ordering = ['name']


class SiteSequencesInlineFormset(models.BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super(SiteSequencesInlineFormset, self).__init__(*args, **kwargs)
        self.can_delete = False


class SiteSequencesInline(admin.StackedInline):
    model = SiteSequences
    formset = SiteSequencesInlineFormset


@admin.register(Site)
class SiteAdmin(BaseModelAdmin):
    fieldsets = [
        ('Général', {'fields': ['reference', 'name', 'company']}),
        ('Coordonnées', {'fields': ['address1', 'address2', 'city', 'phone']}),
        ('Emplacement', {'fields': ['latitude', 'longitude', "region"]}),
    ]
    list_display = ('__str__', 'reference', 'city')
    search_fields = ['name', 'city', 'reference']
    ordering = ['reference', 'name']
    inlines = [SiteSequencesInline]





