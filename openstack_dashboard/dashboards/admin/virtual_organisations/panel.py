from django.utils.translation import ugettext_lazy as _

import horizon

from openstack_dashboard.dashboards.admin import dashboard


class VirtualOrganisations(horizon.Panel):
    name = _("Virtual Organizations")
    slug = "virtual_organisations"


dashboard.Admin.register(VirtualOrganisations)
