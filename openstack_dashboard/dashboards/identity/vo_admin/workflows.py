from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import workflows

from openstack_dashboard import api
from openstack_dashboard.api import keystone


class CreateRoleInfoAction(workflows.Action):
    name = forms.RegexField(label=_("VO Name"),
                            max_length=255,
                            regex=r'^[\w\.\- ]+$',
                            error_messages={'invalid': _('VO Name may only '
                                'contain letters, numbers, underscores, '
                                'periods and hyphens.')},
                            help_text=_("Name of the VO Role"))
    vo_role = forms.RegexField(label=_("VO Role"),
                             regex=r'^[\w\.\- ]+$',
                             required=True,
                             initial='')
    description = forms.CharField(label=_("Description"),
				widget=forms.Textarea)
    enabled = forms.BooleanField(label=_("Enabled"),
                                 required=False)
    pin = forms.CharField(label=_("PIN"),
                          widget=forms.PasswordInput,
                          help_text=_("Password used to send a join request"))
    auto_join = forms.BooleanField(label=_("Automatic Joining"),
                                   help_text=_("Users won't need administrator "
                                               "validation to join the VO role"),
				                   required=False)
    class Meta:
        name = _("VO Role Info")
        help_text = _("From here you can create a new "
                      "VO role.<br>"
                      "Automatic Joining means users won't need an administrator "
                      "validation to join the VO role")

    def clean(self):
        return self.cleaned_data

class CreateRoleInfo(workflows.Step):
    action_class = CreateRoleInfoAction
    contributes = ("role_id",
                   "name",
                   "vo_role",
                   "description",
                   "enabled",
                   "pin",
                   "auto_join")

class CreateRole(workflows.Workflow):
    slug = "create_role"
    name = _("Create VO Role")
    finalize_button_name = _("Create VO Role")
    success_message = _('Created new VO role "%s".')
    failure_message = _('Unable to create VO role "%s".')
    success_url = "horizon:identity:vo_admin:index"
    default_steps = (CreateRoleInfo,
                     )

    def format_status_message(self, message):
        return message % self.context['name']

    def handle(self, request, data):
        try:
            self.object = api.keystone.vo_role_create(request,
                                              vo_name=data["name"],
                                              vo_role_name=data["vo_role"],
                                              pin=data["pin"],
                                              auto_join=data["auto_join"],
                                              description=data["description"], 
                                              enabled=data["enabled"])
        except Exception:
            exceptions.handle(request, _('Unable to create VO role.'))
            return False
        return True



class UpdateRoleInfoAction(CreateRoleInfoAction):
    role_id = forms.CharField(widget=forms.widgets.HiddenInput)

    class Meta:
        name = _("VO Role Info")
        slug = 'update_info'
        help_text = _("From here you can edit the VO role details.")
        

    def clean(self):
        return self.cleaned_data


class UpdateRoleInfo(workflows.Step):
    action_class = UpdateRoleInfoAction
    depends_on = ("role_id",)
    contributes = ("name",
                   "vo_role",
                   "description",
                   "enabled",
                   "pin",
                   "auto_join")

class UpdateRole(workflows.Workflow):
    slug = "update_role"
    name = _("Edit VO Role")
    finalize_button_name = _("Save")
    success_message = _('Modified VO role "%s".')
    failure_message = _('Unable to modify VO role "%s".')
    success_url = "horizon:identity:vo_admin:index"
    default_steps = (UpdateRoleInfo,
                     )

    def format_status_message(self, message):
        return message % self.context['name']

    def handle(self, request, data):
        try:
            self.object = api.keystone.vo_role_update(request, 
                                                vo_role_id=data["role_id"],
                                                vo_name=data["name"],
                                                vo_role_name=data["vo_role"],
                                                pin=data["pin"],
                                                auto_join=data["auto_join"],
                                                description=data["description"], 
                                                enabled=data["enabled"],
                                                vo_is_domain=False)
        except Exception:
            exceptions.handle(request, _('Unable to update VO role.'))
            return False
        return True


"""
Adding users to a role Logic
"""

class Userr:
    def __init__(self, r_id, user_id, idp, role="aa", vo="my vo"):
        self.id = r_id
        self.user_id = user_id
        self.idp = idp
        self.role = role
        self.vo = vo

class AddUserAction(workflows.MembershipAction):
    def __init__(self, request, *args, **kwargs):
        super(AddUserAction, self).__init__(request,
                                                        *args,
                                                        **kwargs)
        err_msg = _('Unable to get the user list')

        default_role_field_name = self.get_default_role_field_name()
        self.fields[default_role_field_name] = forms.CharField(required=False)
        self.fields[default_role_field_name].initial = 'member'

        field_name = self.get_member_field_name('member')
        self.fields[field_name] = forms.MultipleChoiceField(required=False)

        users = api.keystone.user_list(request)
        users2 = []
        print args
        print kwargs
        self.fields[field_name].choices = \
            [(user.id, user.name) for user in users]

        self.fields[field_name].initial = api.keystone.vo_membership_list(request, vo_role_id=args[0]["role_id"])

    class Meta:
        name = _("Add User")
        slug = "add_user"


class AddUserStep(workflows.UpdateMembersStep):
    action_class = AddUserAction
    depends_on = ("role_id",)
    help_text = _("You can control the membership of a VO role by moving "
                  "users from the left column to the right column. Only users "
                  "in the right column will be VO role members ")
    available_list_title = _("Non Members")
    members_list_title = _("VO Role Members")
    no_available_text = _("No users found.")
    no_members_text = _("No users selected. ")
    show_roles = False

    contribute = ("role_users",)

    def contribute(self, data, context):
        if data:
            member_field_name = self.get_member_field_name('member')
            context['role_users'] = data.get(member_field_name, [])
        return context

class AddUser(workflows.Workflow):
    slug = "add_user"
    name = _("Manage VO Role Membership")
    finalize_button_name = _("Add User")
    success_message = _('Added new user "%s".')
    failure_message = _('Unable to add user "%s".')
    default_steps = (AddUserStep,
                     )

    def format_status_message(self, message):
        return message % self.context['role_users']

    def handle(self, request, data):
        return True

class Data:
    def __init__(self, r_id, name, role, status, joining, desc, pin):
        self.id = r_id
        self.name = name
        self.roles = role
        self.status = status
        self.joining = joining
        self.desc = desc
        self.pin = pin

class MoveUserAction(workflows.MembershipAction):
    def __init__(self, request, *args, **kwargs):
        super(MoveUserAction, self).__init__(request,
                                                        *args,
                                                        **kwargs)
        err_msg = _('Unable to get the VO role list')

        default_role_field_name = self.get_default_role_field_name()
        self.fields[default_role_field_name] = forms.CharField(required=False)
        self.fields[default_role_field_name].initial = 'member'

        field_name = self.get_member_field_name('member')
        self.fields[field_name] = forms.MultipleChoiceField(required=False)

        roles = [Data(1,'member',3,4,True,6,7), Data(4,'admin',3,4,True,6,7),
                 Data(3,'editor',3,4,True,6,7), Data(2,'soldier',3,4,True,6,7)]

        self.fields[field_name].choices = \
            [(role.id, role.name) for role in roles]

        self.fields[field_name].initial = [3, 2]  

    class Meta:
        name = _("Move User")
        slug = "move_user"


class MoveUserStep(workflows.UpdateMembersStep):
    action_class = MoveUserAction
    depends_on = ("user_id",)
    help_text = _("You can control the membership of the user by moving "
                  "roles from the left column to the right column. User will "
                  "be a member of the VO roles in the right column")
    available_list_title = _("Not A Member Of These VO Roles")
    members_list_title = _("Member Of These VO Roles")
    no_available_text = _("No VO role found.")
    no_members_text = _("No VO roles selected. ")
    show_roles = False

    contribute = ("role_users",)

    def contribute(self, data, context):
        if data:
            member_field_name = self.get_member_field_name('member')
            context['role_users'] = data.get(member_field_name, [])
        return context

class MoveUser(workflows.Workflow):
    slug = "move_user"
    name = _("Manage User's VO Role Memberships")
    finalize_button_name = _("Move User")
    success_message = _('Moved user "%s".')
    failure_message = _('Unable to move user "%s".')
    default_steps = (MoveUserStep,
                     )

    def format_status_message(self, message):
        return message % self.context['role_users']

    def handle(self, request, data):
        return True

