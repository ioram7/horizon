from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import workflows

from openstack_dashboard import api
from openstack_dashboard.api import keystone

class JoinRoleInfoAction(workflows.Action):    
    name = forms.RegexField(label=_("VO Name"),
                            max_length=255,
                            regex=r'^[\w\.\- ]+$',
                            error_messages={'invalid': _('VO Name may only '
                                'contain letters, numbers, underscores, '
                                'periods and hyphens.')})
    vo_role = forms.RegexField(label=_("VO Role"),
                             regex=r'^[\w\.\- ]+$',
                             required=True)
    pin = forms.CharField(label=_("PIN"),
                          widget=forms.PasswordInput,
                          help_text=_("Password of the role"),
                          )
    class Meta:
        name = _("Join Request")
        help_text = _("From here you can make a request to join a "
                      "role.<br>")

    def clean(self):
        return self.cleaned_data
        
class JoinRoleInfo(workflows.Step):
    action_class = JoinRoleInfoAction
    contributes = ("name",
                   "pin",
                   "vo_role")

class JoinRole(workflows.Workflow):
    slug = "join_role"
    name = _("Join VO Role")
    finalize_button_name = _("Send Request")
    success_message = _('Request sent to VO "%s".')
    failure_message = _('Unable to find role in VO "%s".')
    success_url = "horizon:identity:my_voroles:index"
    default_steps = (JoinRoleInfo,
                     )
                     
    def format_status_message(self, message):
        return message % self.context['name']

    def handle(self, request, data):
        try:
	    #Ioram 29/10/2014
   	    #print "===VO: "+data["name"]+" VO Role: "+data["vo_role"]+" PIN: "+data["pin"]
            self.object = api.keystone.vo_membership_join(request,
                                              vo_name=data["name"],
                                              vo_role=data["vo_role"],
                                              pin=data["pin"])
        except Exception:
            exceptions.handle(request, _('Join request failed.'))
            return False
        return True
