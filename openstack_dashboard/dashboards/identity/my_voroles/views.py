import json

from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy

from horizon import tables
from django.utils.translation import ugettext_lazy as _
from horizon import exceptions
from horizon import workflows

from openstack_dashboard import api

from openstack_dashboard.dashboards.identity.my_voroles \
    import tables as vo_tables
from openstack_dashboard.dashboards.identity.my_voroles \
    import workflows as vo_workflows
    
INDEX_URL = "horizon:identity:my_voroles:index"

class IndexView(tables.DataTableView):
    table_class = vo_tables.RoleTable
    template_name = 'identity/my_voroles/index.html'

    def get_data(self):
        data = []
	#print "=-=-=-=-=-=-="
	#print self.request.user.id
	#print self.request.user.idp_id
	#print "=-=-=-=-=-=-="
        try:
            data = api.keystone.vo_roles_list_user_vo_roles(self.request)
        except Exception:
            exceptions.handle(self.request,
                              _('Unable to retrieve virtual organisation list.'))
	#print "dddddddddddddddddddddddddddd"
	#print data
	#print "dddddddddddddddddddddddddddd"
        data.sort(key=lambda vo: vo.vo_name.lower())
        return data
        
class JoinRequestView(workflows.WorkflowView):
    workflow_class = vo_workflows.JoinRole
    template_name = 'identity/my_voroles/join_role.html'

    def get_initial(self):
        try:
            return { 
                }
        except Exception:
            exceptions.handle(self.request,
                              _('Unable to retrieve role details.'),
                              redirect=reverse_lazy(INDEX_URL))
