from horizon import tables
from django.utils.translation import ugettext_lazy as _
from horizon import exceptions
from horizon import workflows

from openstack_dashboard import api

from openstack_dashboard.dashboards.project.virtual_organisations \
    import tables as vo_tables
from openstack_dashboard.dashboards.project.virtual_organisations \
    import workflows as vo_workflows
    
INDEX_URL = "horizon:project:virtual_organisations:index"

class IndexView(tables.DataTableView):
    table_class = vo_tables.RoleTable
    template_name = 'project/virtual_organisations/index.html'

    def get_data(self):
        data = []
        try:
            data = api.keystone.vo_roles_list(self.request)
        except Exception:
            exceptions.handle(self.request,
                              _('Unable to retrieve virtual organisation list.'))
        data.sort(key=lambda vo: vo.vo_name.lower())
        return data
        
class JoinRequestView(workflows.WorkflowView):
    workflow_class = vo_workflows.JoinRole
    template_name = 'project/virtual_organisations/join_role.html'

    def get_initial(self):
        try:
            return { 
                }
        except Exception:
            exceptions.handle(self.request,
                              _('Unable to retrieve role details.'),
                              redirect=reverse_lazy(INDEX_URL))
