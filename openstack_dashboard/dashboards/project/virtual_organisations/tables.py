from horizon import tables
from django.utils.translation import ugettext_lazy as _
from django.template import defaultfilters as filters
from django.core.urlresolvers import reverse
from openstack_dashboard import api

from keystoneclient import exceptions


class JoinRole(tables.LinkAction):
    name = "join_request"
    verbose_name = _("Join Request")
    url = "horizon:project:virtual_organisations:join"
    classes = ("ajax-modal", "btn-edit")

    def allowed(self, request, role):
        return True



class RoleTable(tables.DataTable):
    name = tables.Column('vo_name', verbose_name=_('Virtual Organization'))
    roles = tables.Column('vo_role', 
                        verbose_name=_('Role'))                        
    status = tables.Column('enabled', 
                        verbose_name=_('Status'))
    joining = tables.Column('automatic_join', 
                        verbose_name=_('Automatic Joining'),
                        empty_value=False,
                        filters=(filters.yesno, filters.capfirst))
    desc = tables.Column('description', 
                        verbose_name=_('Description'),
                        )
    class Meta:
        name = "roles"
        verbose_name = _("Roles")
        table_actions = (JoinRole,)
        

