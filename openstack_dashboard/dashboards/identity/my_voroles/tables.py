from horizon import tables
from django.utils.translation import ugettext_lazy as _
from django.template import defaultfilters as filters
from django.core.urlresolvers import reverse
from openstack_dashboard import api

from keystoneclient import exceptions


class JoinRole(tables.LinkAction):
    name = "join_request"
    verbose_name = _("Join Request")
    url = "horizon:identity:my_voroles:join"
    classes = ("ajax-modal", "btn-edit")

    def allowed(self, request, role):
        return True

class ResignUserRole(tables.DeleteAction):
    data_type_singular = _("User")
    data_type_plural = _("Users")
    action_present = _("Resign")

    def delete(self, request, obj_id):
        #print obj_id
        #data = obj_id.split('@')
        #print request
        try:
            api.keystone.vo_membership_resign(request, obj_id, request.user)
        except Exception as e:
            print e
            return False
        return True

class RoleTable(tables.DataTable):
    name = tables.Column('vo_name', verbose_name=_('Virtual Organization'))
    roles = tables.Column('vo_role', 
                        verbose_name=_('VO Role'))
#    status = tables.Column('enabled', 
#                        verbose_name=_('Status'))
#    joining = tables.Column('automatic_join', 
#                        verbose_name=_('Automatic Joining'),
#                        empty_value=False,
#                        filters=(filters.yesno, filters.capfirst))
    desc = tables.Column('description', 
                        verbose_name=_('Description'),
                        )
    class Meta:
        name = "roles"
        verbose_name = _("My VO Roles")
        table_actions = (JoinRole,)
        row_actions = (ResignUserRole,)
        
