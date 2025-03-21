from django_tables2 import SingleTableView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django_tables2.config import RequestConfig
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.conf import settings
from mailer import send_html_mail
import datetime
from django.contrib.contenttypes.models import ContentType

from base.models import Notification



def format_phone(phone_number):
    if not phone_number:
        return ""
    stripped_phone = phone_number.strip().replace(" ","").replace(".","").replace("-","")
    if len(stripped_phone)==10 and stripped_phone.isdigit():
        return "%s%s %s%s %s%s %s%s %s%s" % tuple(stripped_phone)
    elif len(stripped_phone)==13 and stripped_phone.startswith("+212"):
        return "+212 %s %s%s %s%s %s%s %s%s" % tuple(stripped_phone[4:])
    elif len(stripped_phone)==14 and stripped_phone.startswith("00212"):
        return "00212 %s %s%s %s%s %s%s %s%s" % tuple(stripped_phone[5:])
    else:
        return phone_number.strip()


def parse_ids(ids: str):
    result = []
    for id in ids.split(','):
        try:
            result.append(int(id))
        except ValueError:
            pass
    return result

class PagedFilteredTableView(PermissionRequiredMixin,SingleTableView):
    filter_class = None
    formhelper_class = None
    permission_required = None
    context_filter_name = 'filter'
    active_item = None
    active_menu = None
    per_page = 100

    def get_filter_kwargs(self):
        return {self.request}

    def get_queryset(self, **kwargs):
        qs = super(PagedFilteredTableView, self).get_queryset()
        
        # Le cas où on transmet une list d'IDs 
        delivery_ids_str = self.kwargs.get('ids',"")
        delivery_ids = parse_ids(delivery_ids_str)
        if delivery_ids : 
            qs = qs.filter(pk__in = delivery_ids)
            
        if self.filter_class:
            self.filter = self.filter_class(self.request.GET, queryset=qs)
            self.filter.form.helper = self.formhelper_class()
            return self.filter.qs
        else:
            self.filter = None
            return qs
        

    def get_context_data(self, **kwargs):
        context = super(PagedFilteredTableView, self).get_context_data()
        context[self.context_filter_name] = self.filter
        context["per_page"] = self.request.GET.get('per_page', self.per_page )
        if self.active_item:
            context["active_item"] = self.active_item
        if self.active_menu:
            context["active_menu"] = self.active_menu
        return context

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(PagedFilteredTableView, self).dispatch(request, *args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        if request.htmx:
            self.template_name = "base/includes/list_table.html"
        return super().get(request, *args, **kwargs)



def mention_notification(users, object, mentionned_by):
    site_url = settings.SITE_URL
    app_name = settings.APPLICATION_NAME
    model_name = object._meta.verbose_name

    for user in users:
        if not user or not user.email:
            return
        
        Notification.objects.create(
            user=user,
            created_at=datetime.datetime.now(),
            title="Nouvelle mention : {0}".format(object),
            message="Vous avez été mentionné sur une fiche {0} par {1}".format(model_name, mentionned_by),
            content_type = ContentType.objects.get_for_model(object),
            object_id = object.pk,
        )
        

        # corps = notification_mail_corps_html.format(
        #                     user.first_name,
        #                     modele,
        #                     url, 
        #                     app_name
        #                 )
        # corpstext = notification_mail_corps_text.format(
        #                     user.first_name,
        #                     modele,
        #                     url,
        #                     app_name
        #                 )
        # corps = "Test"
        # corpstext = "Test"
        
        # sujet = "[{0}] Votre nom a été mentionné sur une fiche {1}".format(app_name, modele)

        # send_html_mail(sujet, corpstext, corps, settings.DEFAULT_FROM_EMAIL, (user.email,))

