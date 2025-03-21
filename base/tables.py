import django_tables2 as tables
from .models import  Notification



class NotificationListTable(tables.Table):
    created_at = tables.DateTimeColumn(format="d/m/Y H:i", order_by=("created_at"), verbose_name = "Date")
    # read_at = tables.BooleanColumn(order_by=("read_at"),null=True, verbose_name = "Lue?")
    cropped_message = tables.Column(orderable=False, verbose_name = "Message")
    title = tables.Column(attrs={"td":{"class":"text-nowrap"}})
    content_object = tables.Column(attrs={"td":{"class":"text-nowrap"}}, verbose_name = "Lien",
                                   linkify=lambda record: record.content_object.get_path if hasattr(record.content_object, 'get_path') else None)
    class Meta:
        model = Notification
        fields = ("created_at", "title","content_object","cropped_message")
        per_page = 100
        attrs = {
            "class": "table table-bordered table-striped table-hover text-gray-600 table-heading table-datatable  g-3 fs-6"
        }
    # tables.order_by= "name"

