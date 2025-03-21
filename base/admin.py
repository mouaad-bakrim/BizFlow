from typing import Iterable
from django.contrib import admin
from django.contrib.admin.options import InlineModelAdmin
from django.forms import models
from django.conf import settings
from admin_interface.models import Theme
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.http import HttpRequest
from tree_queries.forms import TreeNodeChoiceField

from client.models import ClientUser
from .models import Site, User, Company, SiteSequences, PerimeterCategory, Perimeter, UserPerimeterRel
from dataimport.admin import SitesExternalIdsInline
from .managers import BaseModelAdmin
from .forms import PerimeterAdminForm

APP_VERSION_NUMBER = settings.APP_VERSION_NUMBER or ""
APPLICATION_NAME = settings.APPLICATION_NAME or "Orderly"

# admin.site.site_header = 'Administration {1} {0}'.format(APP_VERSION_NUMBER, APPLICATION_NAME)
try:
    default_theme = Theme.objects.filter(active=True).first()
except:
    default_theme = None

if not default_theme or not default_theme.logo or not default_theme.logo.url or not default_theme.logo_visible:
    admin.site.site_header = 'Administration {1} {0}'.format(APP_VERSION_NUMBER, APPLICATION_NAME)
else:
    admin.site.site_header = 'V {0}'.format(APP_VERSION_NUMBER, APPLICATION_NAME)

admin.site.site_title = 'Administration {1} {0}'.format(APP_VERSION_NUMBER, APPLICATION_NAME)
admin.site.index_title = "Menu principal"


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User

    fieldsets = [
        ('Informations personnelles',
         {'fields': [('first_name', 'last_name'), ('password1', 'password2'), 'email', 'is_active']}),
    ]
    search_fields = ['email', 'first_name', 'last_name']


class User_activity_linkInline(admin.TabularInline):
    model = ClientUser
    extra = 0
    can_delete = True
    fields = ['user', 'client']
    # def get_formset(self, request, obj=None, **kwargs):
    #     formset = super(User_activity_linkInline, self).get_formset(request, obj, **kwargs)
    #     form = formset.form
    #    # widget = form.base_fields['activite'].widget
    #     #widget.can_add_related = False
    #     #widget.can_change_related = False
    #     return formset


class UserPerimeterRelInline(admin.TabularInline):
    model = UserPerimeterRel
    extra = 0
    can_delete = True
    fields = ['perimeter', "email_notify_new_order", "email_notify_new_ticket", "web_notifications", "assign_tickets"]

    def get_formset(self, request, obj, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        form = formset.form
        form.base_fields['perimeter'] = TreeNodeChoiceField(queryset=form.base_fields['perimeter'].queryset)
        return formset


@admin.register(User)
class CustomUserAdmin(UserAdmin, BaseModelAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    fieldsets = [
        ('Informations personnelles', {
            'fields': [('first_name', 'last_name'), 'email', "welcome_email_to_send", "welcome_email_sent",
                       'is_active']}),
        ('Coordonnées', {'fields': ['company', 'phone', ]}),
        ('Dates importantes', {'fields': ['date_joined', 'last_login']}),
        ('Permissions', {'fields': ["is_internal", 'is_staff', 'is_superuser', 'groups', 'user_permissions']}),
    ]
    add_fieldsets = [
        ('Informations personnelles',
         {'fields': [('first_name', 'last_name'), "email", "is_internal", "password1", "password2"]}),
    ]
    list_display = ('email', 'first_name', 'last_name', 'is_internal')
    search_fields = ['email', 'first_name', 'last_name']
    readonly_fields = ['last_login', 'date_joined', "welcome_email_sent"]

    def get_readonly_fields(self, request, obj):
        read_only_fields = super().get_readonly_fields(request, obj)
        if obj and read_only_fields:
            read_only_fields = read_only_fields + ['is_internal']
        elif obj:
            read_only_fields = ['is_internal']

        if obj and obj.welcome_email_sent:
            read_only_fields = read_only_fields + ['welcome_email_to_send']

        return read_only_fields

    def has_delete_permission(self, request, obj=None):
        return False

    def has_soft_delete_permission(self, request, obj=None):
        return False

    def get_inlines(self, request, obj):
        if not obj:
            return []
        inlines = super().get_inlines(request, obj)
        if not obj.is_internal:
            if User_activity_linkInline not in inlines:
                return list(inlines) + [User_activity_linkInline, ]
        else:
            if UserPerimeterRelInline not in inlines:
                return list(inlines) + [UserPerimeterRelInline, ]


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
    inlines = [SiteSequencesInline, SitesExternalIdsInline]


@admin.register(PerimeterCategory)
class PerimeterCategoryAdmin(BaseModelAdmin):
    model = PerimeterCategory
    fieldsets = [
        ('Général', {'fields': ['name', 'description', ]}),
    ]
    list_display = ('name', 'description')
    search_fields = ['name', 'description', ]
    ordering = ['name']


@admin.register(Perimeter)
class PerimeterAdmin(BaseModelAdmin):
    model = Perimeter
    form = PerimeterAdminForm
    fieldsets = [
        ('Général', {'fields': ["external_id", 'name', 'category', 'site', "parent", 'description', "display_order"]}),
    ]
    list_display = ('tree_label', "category", 'site')
    search_fields = ['name', 'external_id', 'site__name', 'site__reference', 'site__company__name', 'category__name']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.with_tree_fields()
        return qs
