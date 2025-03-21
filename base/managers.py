from django.db import models
from django.contrib.auth.models import UserManager
from django.db.models import query
import logging


from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import transaction
from django.contrib.auth import get_permission_codename
from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from django.db.models import JSONField


class SoftDeleteQuerySet(query.QuerySet):
    def delete(self, using='default', *args, **kwargs):
        return



class BaseModelManager(models.Manager):

    def _get_base_queryset(self):
        return super(BaseModelManager, self).get_queryset()
        
    def _get_self_queryset(self):
        qs = self.get_queryset()
        if not issubclass(qs.__class__, SoftDeleteQuerySet):
            qs.__class__ = SoftDeleteQuerySet
        return qs
        
    def get_queryset(self):
        qs = super(BaseModelManager, self).get_queryset().filter(deleted=False)
        if not issubclass(qs.__class__, SoftDeleteQuerySet):
            qs.__class__ = SoftDeleteQuerySet
        return qs

    def get(self, *args, **kwargs):
        # if 'pk' in kwargs:
        #     return self.all_with_deleted().get(*args, **kwargs)
        # else:
        return self._get_self_queryset().get(*args, **kwargs)

    def filter(self, *args, **kwargs):
        # if 'pk' in kwargs:
        #     qs = self.all_with_deleted().filter(*args, **kwargs)
        # else:
        qs = self._get_self_queryset().filter(*args, **kwargs)
        if not issubclass(qs.__class__, SoftDeleteQuerySet):
            qs.__class__ = SoftDeleteQuerySet
        return qs
    


class CustomUserManager(UserManager):
    def create_user(self, email, password=None, is_staff=False , is_superuser = False):
        if not email:
            raise ValueError("L'email est obligatoire.")
        user = self.model(email=self.normalize_email(email), is_superuser=is_superuser, is_staff=is_staff)

        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password):
        user = self.create_user(
            email=email,
            password=password,
            is_staff=True,
            is_superuser=True
        )



@admin.action(description="Supprimer les éléments sélectionnés", permissions=["soft_delete"])
def soft_delete(modeladmin, request, queryset):
    for obj in queryset:
        with transaction.atomic():
            try:
                obj.soft_delete()
            except ValidationError as e:
                message = "Impossible de supprimer l'élément '{0}' : {1}".format(obj, e.message)
                modeladmin.message_user(request, message, level=messages.WARNING)
                return
    

class BaseModelAdmin(SimpleHistoryAdmin):
    actions = [soft_delete]

    def get_queryset(self, request):
        qs = super(BaseModelAdmin, self).get_queryset(request)
        return qs.filter(deleted=False)
    
    def has_delete_permission(self, request, obj=None):
        return False
    def has_soft_delete_permission(self, request, obj=None):
        opts = self.opts
        codename = get_permission_codename("soft_delete", opts)
        # print("%s.%s" % (opts.app_label, codename))
        return request.user.has_perm("%s.%s" % (opts.app_label, codename))
    # def get_form(self, request, obj=None, **kwargs):
    #     form = super().get_form(request, obj, **kwargs)
        
    #     # disable deletion for related objects
    #     if obj:
    #         for field in obj._meta.get_fields():
    #             if field.is_relation and field.many_to_one:
    #                 field_name = field.name
    #                 form.base_fields[field_name].widget.can_delete_related = False
    #     return form
        