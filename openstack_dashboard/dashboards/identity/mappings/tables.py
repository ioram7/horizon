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

from django.template import defaultfilters
from django.utils.translation import ugettext_lazy as _

from horizon import messages
from horizon import tables

from openstack_dashboard import api


ENABLE = 0
DISABLE = 1


class CreateMappingLink(tables.LinkAction):
    name = "create"
    verbose_name = _("Create Mapping")
    url = "horizon:identity:mappings:create"
    classes = ("ajax-modal",)
    icon = "plus"
    policy_rules = (('identity', 'identity:create_mapping'),)

    def allowed(self, request, user):
        return True


class EditMappingLink(tables.LinkAction):
    name = "edit"
    verbose_name = _("Edit")
    url = "horizon:identity:mappings:update"
    classes = ("ajax-modal",)
    icon = "pencil"
    policy_rules = (("identity", "identity:update_mapping"),)

    def get_policy_target(self, request, user):
        return {"user_id": user.id}

    def allowed(self, request, user):
        return True


class DeleteMappingsAction(tables.DeleteAction):
    data_type_singular = _("Mapping")
    data_type_plural = _("Mappings")
    policy_rules = (("identity", "identity:delete_mapping"),)

    def allowed(self, request, datum):
        return True

    def delete(self, request, obj_id):
        client = api.keystone.keystoneclient(request)
        client.federation.mappings.delete(obj_id)


class MappingFilterAction(tables.FilterAction):
    def filter(self, table, mappings, filter_string):
        """Naive case-insensitive search."""
        q = filter_string.lower()
        return [mapping for mapping in mappings
                if q in mapping.id.lower()
                or q in getattr(mapping, 'rules', '').lower()]


class MappingsTable(tables.DataTable):
    STATUS_CHOICES = (
        ("true", True),
        ("false", False)
    )
    id = tables.Column('id', verbose_name=_('Mapping ID'))
    rules = tables.Column('rules', verbose_name=_('Rules'),
                          filters=(lambda v: defaultfilters
                                   .default_if_none(v, ""),
                                   defaultfilters.escape,
                                   defaultfilters.urlize)
                          )
    class Meta:
        name = "mappings"
        verbose_name = _("Mappings")
        row_actions = (EditMappingLink,  DeleteMappingsAction)
        table_actions = (MappingFilterAction, CreateMappingLink, DeleteMappingsAction)
