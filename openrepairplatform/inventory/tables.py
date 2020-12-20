import django_tables2 as tables
from openrepairplatform.user.models import (
    CustomUser, 
    Organization
)
from openrepairplatform.event.models import (
    Event
)
from openrepairplatform.inventory.models import (
    Stuff
) 
from django_tables2_column_shifter.tables import ColumnShiftTable
from django_tables2.export.export import TableExport

class StockTable(ColumnShiftTable):

    id = tables.Column(
        attrs={"td": {"class": "small-column"},"th": {"class": "small-column"}}
        )
    
    state = tables.TemplateColumn(
        template_name="extra_column_data.html",
         extra_context={"column": "stuff_state"},
        verbose_name="Etat",
        )

    action = tables.TemplateColumn(
        accessor='get_absolute_url', 
        template_name="extra_column_data.html",
         extra_context={"column": "details"},
        verbose_name="Action",
        linkify=True,
        )

    def get_column_default_show(self):
        self.column_default_show = ['id', 'device', 'state', 'action']
   
    class Meta:
        model = Stuff
        attrs = {"class": "table table-fixed table-hover"}
        sequence = (
         "id",
         "device",
         "place",
         "state",
         "is_visible",
         'action',
        )
        exclude = (
          "member_owner",
          "organization_owner",
          "subpart",
          "added_date",
          "information",
        )

