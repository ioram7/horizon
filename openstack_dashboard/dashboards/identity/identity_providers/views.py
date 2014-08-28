# Copyright 2012 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
# Copyright 2012 Nebula, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import operator
import json

from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.utils.decorators import method_decorator  # noqa
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.debug import sensitive_post_parameters  # noqa

from horizon import exceptions
from horizon import forms
from horizon import tables
from horizon.utils import memoized

from openstack_dashboard import api

from openstack_dashboard.dashboards.identity.identity_providers \
    import forms as project_forms
from openstack_dashboard.dashboards.identity.identity_providers \
    import tables as project_tables


class IdentityProviderEntry(object):

    def __init__(self, id, desc, client):
        self.id = id
        self.description = desc
        protocol_list = client.federation.protocols.list(id)
        self.protocols = ""
        for p in protocol_list:
            self.protocols = self.protocols+p.id+" "


class IndexView(tables.DataTableView):
    table_class = project_tables.IdentityProvidersTable
    template_name = 'identity/identity_providers/index.html'

    def get_data(self):
        identity_providers = []
        try:
            client = api.keystone.keystoneclient(self.request)
            print self.request.session.get('_unscopedtoken')
            identity_providers = client.federation.identity_providers.list()
        except Exception:
            exceptions.handle(self.request,
                              _('Unable to retrieve identity provider list.'))
        return [IdentityProviderEntry(idp.id, idp.description, client) for idp in identity_providers]


class UpdateView(forms.ModalFormView):
    form_class = project_forms.UpdateIdentityProviderForm
    template_name = 'identity/identity_providers/update.html'
    success_url = reverse_lazy('horizon:identity:identity_providers:index')

    def dispatch(self, *args, **kwargs):
        return super(UpdateView, self).dispatch(*args, **kwargs)

    @memoized.memoized_method
    def get_object(self):
        try:
            client = api.keystone.keystoneclient(self.request)
            return client.federation.identity_providers.get(self.kwargs['identity_provider_id'])
        except Exception:
            redirect = reverse("horizon:identity:identity_providers:index")
            exceptions.handle(self.request,
                              _('Unable to update identity provider.'),
                              redirect=redirect)

    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        context['identity_provider'] = self.get_object()
        return context

    def get_initial(self):
        idp = self.get_object()
        return {'id': idp.id,
                'description': idp.description}


class ProtocolsManageMixin(object):
    @memoized.memoized_method
    def _get_identity_provider(self):
        idp_id = self.kwargs['identity_provider_id']
        client = api.keystone.keystoneclient(self.request)
        return client.federation.identity_providers.get(idp_id)

    @memoized.memoized_method
    def _get_protocols(self):
        client = api.keystone.keystoneclient(self.request)
        return client.federation.protocols.list(self.kwargs['identity_provider_id'])


class ProtocolView(ProtocolsManageMixin, tables.DataTableView):
    table_class = project_tables.ProtocolsTable
    template_name = 'identity/identity_providers/protocols.html'

    def get_context_data(self, **kwargs):
        context = super(ProtocolView, self).get_context_data(**kwargs)
        context['identity_provider'] = self._get_identity_provider()
        return context

    def get_data(self):
        protocols = []
        try:
            protocols = self._get_protocols()
        except Exception:
            exceptions.handle(self.request,
                              _('Unable to retrieve protocol list.'))
        return protocols


class AddProtocolView(forms.ModalFormView):
    form_class = project_forms.AddProtocolsForm
    template_name = 'identity/identity_providers/add_protocol.html'
    success_url = reverse_lazy('horizon:identity:identity_providers:manage_protocols')

    def dispatch(self, *args, **kwargs):
        self.success_url = reverse('horizon:identity:identity_providers:manage_protocols', kwargs=self.kwargs)
        return super(AddProtocolView, self).dispatch(*args, **kwargs)

    @memoized.memoized_method
    def get_object(self):
        try:
            client = api.keystone.keystoneclient(self.request)
            return client.federation.identity_providers.get(self.kwargs['identity_provider_id'])
        except Exception:
            redirect = reverse("horizon:identity:identity_providers:manage_protocols",
                               kwargs={"identity_provider_id": self.kwargs["identity_provider_id"]})
            exceptions.handle(self.request,
                              _('Unable to add protocol.'),
                              redirect=redirect)

    def get_context_data(self, **kwargs):
        context = super(AddProtocolView, self).get_context_data(**kwargs)
        context['identity_provider'] = self.get_object()
        return context

    def get_initial(self):
        idp = self.get_object()
        return {'id': idp.id,
                'protocol': "",
                'mapping_id': ""}


class UpdateProtocolView(AddProtocolView):
    form_class = project_forms.UpdateProtocolsForm
    template_name = 'identity/identity_providers/update_protocol.html'

    def dispatch(self, *args, **kwargs):
        self.success_url = reverse('horizon:identity:identity_providers:manage_protocols',
                                   kwargs={"identity_provider_id": self.kwargs["identity_provider_id"]})
        self.protocol = kwargs.get('protocol')
        return super(AddProtocolView, self).dispatch(*args, **kwargs)

    def get_initial(self):
        idp = self.get_object()
        mapping_id=""
        client = api.keystone.keystoneclient(self.request)
        if self.protocol:
            mapping_id = client.federation.protocols.get(idp.id, self.protocol).mapping_id
        return {'id': idp.id,
                'protocol': self.protocol,
                'mapping_id': mapping_id}


class CreateView(forms.ModalFormView):
    form_class = project_forms.CreateIdentityProviderForm
    template_name = 'identity/identity_providers/create.html'
    success_url = reverse_lazy('horizon:identity:identity_providers:index')

    def dispatch(self, *args, **kwargs):
        return super(CreateView, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(CreateView, self).get_form_kwargs()
        return kwargs

    def get_initial(self):
        return {"id": "",
                "description": ""}
