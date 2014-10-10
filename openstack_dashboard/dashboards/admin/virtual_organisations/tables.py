from horizon import tables
from django.utils.translation import ugettext_lazy as _
from django.template import defaultfilters as filters
from django.core.urlresolvers import reverse
from openstack_dashboard import api


class DeleteRole(tables.DeleteAction):
    data_type_singular = _("Role")
    data_type_plural = _("Roles")

    def delete(self, request, obj_id):
        #TODO: call api to delete entry
        try:
            api.keystone.vo_role_delete(request, obj_id)
        except Exception:
            return False
        return True
        
class CreateRole(tables.LinkAction):
    name = "create"
    verbose_name = _("Create Role")
    url = "horizon:admin:virtual_organisations:create"
    classes = ("ajax-modal", "btn-create")
    policy = ("identity" , "identity:create_role")

class UpdateRole(tables.LinkAction):
    name = "update"
    verbose_name = _("Edit Role Information")
    url = "horizon:admin:virtual_organisations:update"
    classes = ("ajax-modal", "btn-edit")

    """def allowed(self, request, role):
        if(role.id == 1):
            return True
        else:
            return False"""

class ManageRole(tables.LinkAction):
    name = "manage"
    verbose_name = _("Manage Role Membership")
    url = "horizon:admin:virtual_organisations:manage"


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
    actions = tables.Column('actions', 
                        verbose_name=_('Actions'))
    class Meta:
        name = "roles"
        verbose_name = _("Roles")
        table_actions = (CreateRole, DeleteRole)
        row_actions = (UpdateRole,
                       ManageRole,
                       DeleteRole)

class ChangeUserRole(tables.LinkAction):
    name = "change_role"
    verbose_name = _("Manage User's VO Role Memberships")
    url = "horizon:admin:virtual_organisations:change_role"
    classes = ("ajax-modal",)



class ViewRequests(tables.LinkAction):
    name = "view_requests"
    verbose_name = _("VO Role Join Requests")
    url = "horizon:admin:virtual_organisations:view_requests"
    classes = ("btn-list")

    def get_link_url(self, datum=None):
        return reverse(self.url, args=[self.table.kwargs.get('id')])
    

class ViewBlacklist(tables.LinkAction):
    name = "blacklist"
    verbose_name = _("Blacklisted Users")
    classes = ("btn-list")
    url = "horizon:admin:virtual_organisations:blacklist"
    def get_link_url(self, datum=None):
        return reverse(self.url, args=[self.table.kwargs.get('id')])
    
class AddUser(tables.LinkAction):
    name = "add_user"
    verbose_name = _("Add User")
    classes = ("ajax-modal", "btn-create")
    url = "horizon:admin:virtual_organisations:add_user"
    def get_link_url(self, datum=None):
        return reverse(self.url, args=[self.table.kwargs.get('id')])


class RemoveUserRole(tables.DeleteAction):
    data_type_singular = _("User")
    data_type_plural = _("Users")
    action_present = _("Remove")

    def delete(self, request, obj_id):
        print obj_id
        data = obj_id.split('@')
        print request
        try:
            api.keystone.vo_membership_delete(request, self.table.kwargs.get('id'), data[0], data[1])
        except Exception as e:
            print e
            return False
        return True

class ManageTable(tables.DataTable):
    name = tables.Column('id', 
                        verbose_name=_('User'))
    '''idp = tables.Column('idp', 
                        verbose_name=_('IDP'))                        
    actions = tables.Column('actions', 
                        verbose_name=_('Actions'))'''
    class Meta:
        name = "manage"
        verbose_name = _("VO Role Membership")
        table_actions = (ViewBlacklist,ViewRequests, RemoveUserRole)
        '''row_actions = RemoveUserRole'''

class ApproveUser(tables.BatchAction):
    name = "approve_user"
    action_present = _("Approve")
    action_past = _("Approved")
    data_type_singular = _("User")
    data_type_plural = _("Users")
    classes = ("btn-enable",)
    def action(self, request, datum_id):
        try:
            api.keystone.vo_role_approve_request(request, self.table.kwargs.get('id'), datum_id)
        except Exception as e:
            print e
            return False
        return True

class DeclineUser(tables.BatchAction):
    name = "decline_user"
    action_present = _("Decline")
    action_past = _("Declined")
    data_type_singular = _("User")
    data_type_plural = _("Users")
    classes = ("btn-disable",)
    def action(self, request, datum_id):
        try:
            api.keystone.vo_role_delete_request(request, self.table.kwargs.get('id'), datum_id)
        except Exception as e:
            print e
            return False
        return True


class RequestTable(tables.DataTable):
    vo = tables.Column('vo',
                        verbose_name=_('Virtual Organization'))   
    role = tables.Column('role', 
                        verbose_name=_('Role'))
    user_id = tables.Column('user_id', 
                        verbose_name=_('User ID'))
    idp = tables.Column('idp', 
                        verbose_name=_('Identity Provider'))                        
    actions = tables.Column('actions', 
                        verbose_name=_('Actions'))
    class Meta:
        name = "requests"
        verbose_name = _("VO Role Join Requests")
        table_actions = (ApproveUser, DeclineUser)
        row_actions = (ApproveUser, DeclineUser)

class RemoveBlacklist(tables.BatchAction):
    name = "remove_blacklist_user"
    action_present = _("Remove %(data_type)s from Blacklist ")
    action_past = _("Removed %(data_type)s from Blacklist")
    data_type_singular = _("User")
    data_type_plural = _("Users")
    classes = ("btn-disable", )
    def action(self, request, datum_id):
        #TODO: Remove User from blacklist
        print datum_id        
        try:
            api.keystone.vo_blacklist_delete_entry(request, self.table.kwargs.get('id'), datum_id)
        except Exception as e:
	    print e
            return False
        return True

class BlacklistTable(RequestTable):
    
    class Meta:
        name = "blacklist"
        verbose_name = _("Blacklisted Users")
        table_actions = (RemoveBlacklist,)
        row_actions = (RemoveBlacklist,)

