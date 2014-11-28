from django.utils.translation import ugettext_lazy as _

import horizon

from openstack_dashboard.dashboards.identity import dashboard


class VOAdmin(horizon.Panel):
    name = _("VO Admin")
    slug = "vo_admin"
    policy_rules = (("identity", "identity:vo_admin"),)

dashboard.Identity.register(VOAdmin)
