from horizon import tables
from .tables import RoleTable
from .tables import RequestTable
from .tables import ManageTable
from .tables import BlacklistTable


from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from horizon import workflows
from horizon import exceptions

from openstack_dashboard import api
from openstack_dashboard.api import keystone

from openstack_dashboard.dashboards.admin.virtual_organisations \
    import workflows as role_workflows

INDEX_URL = "horizon:admin:virtual_organisations:index"

class IndexView(tables.DataTableView):
    # A very simple class-based view...
    table_class = RoleTable
    template_name = 'admin/virtual_organisations/index.html'

    def get_data(self):
        data = []
        try:
            data = api.keystone.vo_roles_list(self.request)
   #        print "Ioram H" 
        except Exception:
            exceptions.handle(self.request,
                              _('Unable to retrieve virtual organisation list.'))
        data.sort(key=lambda vo: vo.vo_name.lower())
        return data

class CreateView(workflows.WorkflowView):
    workflow_class = role_workflows.CreateRole
    template_name = 'admin/virtual_organisations/create.html'

class UpdateView(workflows.WorkflowView):
    workflow_class = role_workflows.UpdateRole
    template_name = 'admin/virtual_organisations/create.html'

    def get_initial(self):
        role_id = self.kwargs['id']
        try:
            data = api.keystone.vo_role_get(self.request, role_id)            

            return { "role_id" : data.id,
                'name': data.vo_name,
                'vo_role' : data.vo_role,
                'enabled' : data.enabled,
                'auto_join' : data.automatic_join,
                'description' : data.description,
                'pin' : "",}
        except Exception:
            exceptions.handle(self.request,
                              _('Unable to retrieve VO role details.'),
                              redirect=reverse_lazy(INDEX_URL))

class ManageView(tables.DataTableView):
    table_class = ManageTable
    template_name = 'admin/virtual_organisations/manage.html'
    def get_data(self):
        role_id = self.kwargs['id']
        # Add data to the context here...
        try:
            data = api.keystone.vo_membership_list(self.request, role_id)
            print data
            for datum in data:
                uid = datum.id
                idp = datum.idp
                datum.id = "%(uid)s@%(idp)s" % {"uid":uid, "idp":idp}
            return data
        except Exception as e: 
            exceptions.handle(self.request,
                              _('Unable to retrieve VO role membership.'),
                              redirect=reverse_lazy(INDEX_URL))
    def get_context_data(self, **kwargs):
        context = super(ManageView, self).get_context_data(**kwargs)
        role_id = self.kwargs['id']
        try:
            context["role"] = api.keystone.vo_role_get(self.request, role_id)
            print context["role"].id
        except Exception:
            exceptions.handle(self.request,
                _('Unable to retrieve VO role information.'))

        return context

class ViewRequestsView(tables.DataTableView):
    # A very simple class-based view...
    table_class = RequestTable
    template_name = 'admin/virtual_organisations/manage.html'

    def get_data(self):
        # Add data to the context here...
        vo_role_id = self.kwargs['id']
        data = []
        try:
            data = api.keystone.vo_requests_list(self.request, vo_role_id)
        except Exception:
            exceptions.handle(self.request,
                              _('Unable to retrieve VO role join requests.'))
        #data.sort(key=lambda vo: vo.vo_name.lower())
        return data

    def get_context_data(self, **kwargs):
        vo_role_id = self.kwargs['id']
        context = super(ViewRequestsView, self).get_context_data(**kwargs)
        try:
            context["role"] = api.keystone.vo_role_get(self.request, vo_role_id)
        except Exception:
            exceptions.handle(self.request,
                _('Unable to retrieve VO role information.'))
        return context

class BlacklistView(tables.DataTableView):
    table_class = BlacklistTable
    template_name = 'admin/virtual_organisations/manage/blacklist.html'
    
    def get_data(self):
        # Add data to the context here...
        vo_role_id = self.kwargs['id']
        data = []
        try:            
            data = api.keystone.vo_blacklist_list(self.request, vo_role_id)
        except Exception:
            exceptions.handle(self.request,
                _('Unable to retrieve VO role blacklist.'))
        return data
        
    def get_context_data(self, **kwargs):
        vo_role_id = self.kwargs['id']
        context = super(BlacklistView, self).get_context_data(**kwargs)
        try:
            context["role"] = api.keystone.vo_role_get(self.request, vo_role_id)
        except Exception:
            exceptions.handle(self.request,
                _('Unable to retrieve VO role information.'))
        return context

class ChangeRoleView(workflows.WorkflowView):
    workflow_class = role_workflows.MoveUser
    template_name = 'admin/virtual_organisations/user_membership.html'

    def get_initial(self):
        role_id = self.kwargs['id']
        return {'user_id': role_id,
                'name': 'Robert',}

    def get_context_data(self, **kwargs):
        context = super(ChangeRoleView, self).get_context_data(**kwargs)
        try:
            a = 1 #context["user"] = Userr(2, 115, 'tote')
        except Exception:
            exceptions.handle(self.request,
                _('Unable to retrieve VO role information.'))
        return context

class AddUserView(workflows.WorkflowView):
    workflow_class = role_workflows.AddUser
    template_name = 'admin/virtual_organisations/user_workflow.html'

    def get_initial(self):
        role_id = self.kwargs['id']
        try:
            role = api.keystone.vo_role_get(self.request, role_id)
        except Exception:
            exceptions.handle(self.request,
                _('Unable to retrieve VO role information.'))

        return {'role_id': role_id,
                'name': role.vo_name,}

    def get_context_data(self, **kwargs):
        context = super(AddUserView, self).get_context_data(**kwargs)
        role_id = self.kwargs['id']
        try:
            context["role"] = api.keystone.vo_role_get(self.request, role_id)            
        except Exception:
            exceptions.handle(self.request,
                _('Unable to retrieve VO role information.'))
        return context
