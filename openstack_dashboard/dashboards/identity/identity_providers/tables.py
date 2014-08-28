# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import logging

from django.template import defaultfilters
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from horizon import messages
from horizon import tables

from openstack_dashboard import api
from openstack_dashboard.dashboards.identity.identity_providers import constants


LOG = logging.getLogger(__name__)


class CreateIdentityProviderLink(tables.LinkAction):
    name = "create"
    verbose_name = _("Create Identity Provider")
    url = "horizon:identity:identity_providers:create"
    classes = ("ajax-modal",)
    icon = "plus"
    policy_rules = (('identity', 'identity:create_mapping'),)

    def allowed(self, request, idp):
        return True


class EditIdentityProviderLink(tables.LinkAction):
    name = "edit"
    verbose_name = _("Edit")
    url = "horizon:identity:identity_providers:update"
    classes = ("ajax-modal",)
    icon = "pencil"
    policy_rules = (("identity", "identity:update_mapping"),)

    def get_policy_target(self, request, idp):
        return {"identity_provider_id": idp.id}

    def allowed(self, request, user):
        return True


class EditProtocolLink(tables.LinkAction):
    name = "edit"
    verbose_name = _("Edit")
    url = "horizon:identity:identity_providers:update_protocol"
    classes = ("ajax-modal",)
    icon = "pencil"
    policy_rules = (("identity", "identity:update_mapping"),)

    def allowed(self, request, protocol):
        return True

    def get_link_url(self, datum=None):
        kwargs = dict.copy(self.table.kwargs)
        kwargs["protocol"] = datum.id
        return reverse(self.url, kwargs=kwargs)


class AddProtocolLink(tables.LinkAction):
    name = "add_protocol"
    verbose_name = _("Add Protocol")
    url = "horizon:identity:identity_providers:add_protocol"
    classes = ("ajax-modal",)
    icon = "plus"
    policy_rules = (("identity", "identity:add_protocol"),)

    def allowed(self, request, protocol):
        return True

    def get_link_url(self, datum=None):
        return reverse(self.url, kwargs=self.table.kwargs)


class ManageProtocolsLink(tables.LinkAction):
    name = "manage_protocols"
    verbose_name = _("Manage Protocols")
    url = constants.IDPS_MANAGE_URL
    icon = "pencil"
    policy_rules = ()

    def allowed(self, request, datum):
        return True


class DeleteIdentityProvidersAction(tables.DeleteAction):
    data_type_singular = _("Identity Provider")
    data_type_plural = _("Identity Providers")
    policy_rules = (("identity", "identity:delete_mapping"),)

    def allowed(self, request, datum):
        return True

    def delete(self, request, obj_id):
        client = api.keystone.keystoneclient(request)
        client.federation.identity_providers.delete(obj_id)


class DeleteProtocolAction(tables.DeleteAction):
    data_type_singular = _("Protocol")
    data_type_plural = _("Protocols")
    policy_rules = (("identity", "identity:delete_mapping"),)

    def allowed(self, request, datum):
        return True

    def action(self, request, obj_id):
        protocol_obj = self.table.get_object_by_id(obj_id)
        group_id = self.table.kwargs['identity_provider_id']
        LOG.info('Removing user %s from group %s.' % (protocol_obj.id,
                                                      group_id))

        client = api.keystone.keystoneclient(request)
        client.federation.protocols.delete(group_id, protocol_obj.id)


class IdentityProviderFilterAction(tables.FilterAction):
    def filter(self, table, identity_providers, filter_string):
        """Naive case-insensitive search."""
        q = filter_string.lower()
        return [idp for idp in identity_providers
                if q in idp.id.lower()
                or q in getattr(idp, 'description', '').lower()
                or q in getattr(idp, 'protocols', '').lower()]

class ProtocolFilterAction(tables.FilterAction):
    def filter(self, table, identity_providers, filter_string):
        """Naive case-insensitive search."""
        q = filter_string.lower()
        return [idp for idp in identity_providers
                if q in idp.id.lower()
                or q in getattr(idp, 'mapping_id', '').lower()]


class IdentityProvidersTable(tables.DataTable):
    id = tables.Column('id', verbose_name=_('Identity Provider ID'))
    description = tables.Column('description', verbose_name=_('Description'))
    protocols = tables.Column('protocols', verbose_name=_('Supported Protocols'))

    def get_object_display(self, datum):
        if hasattr(datum, 'id'):
            return datum.id
        return None

    class Meta:
        name = "identity_providers"
        verbose_name = _("Identity Providers")
        row_actions = (EditIdentityProviderLink,  ManageProtocolsLink, DeleteIdentityProvidersAction)
        table_actions = (IdentityProviderFilterAction, CreateIdentityProviderLink, DeleteIdentityProvidersAction)


class ProtocolsTable(tables.DataTable):
    id = tables.Column('id', verbose_name=_('Protocol ID'))
    mapping_id = tables.Column('mapping_id', verbose_name=_('Mapping ID'))

    def get_object_display(self, datum):
        if hasattr(datum, 'id'):
            return datum.id
        return None

    class Meta:
        name = "protocols"
        verbose_name = _("Protocols")
        row_actions = (EditProtocolLink, DeleteProtocolAction)
        table_actions = (ProtocolFilterAction, AddProtocolLink, DeleteProtocolAction)
