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

import logging
import json

from django.forms import ValidationError  # noqa
from django import http
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.debug import sensitive_variables  # noqa

from horizon import exceptions
from horizon import forms
from horizon import messages
from horizon.utils import validators

from openstack_dashboard import api


LOG = logging.getLogger(__name__)
PROJECT_REQUIRED = api.keystone.VERSIONS.active < 3


class BaseIdentityProviderForm(forms.SelfHandlingForm):
    def __init__(self, request, *args, **kwargs):
        super(BaseIdentityProviderForm, self).__init__(request, *args, **kwargs)

        identity_provider_id = kwargs['initial'].get('id', None)
        description = kwargs['initial'].get('description')


class CreateIdentityProviderForm(BaseIdentityProviderForm):
    id = forms.CharField(label=_("ID"),
                                required=True)
    description = forms.CharField(label=_("Description"), required=False)

    def __init__(self, *args, **kwargs):
        super(CreateIdentityProviderForm, self).__init__(*args, **kwargs)


    def handle(self, request, data):
        try:
            LOG.info('Creating Identity Provider with ID "%s"' % data['id'])
            id = data["id"]
            description = data['description']
            idp_ref = {"id":id, "description":description}
            client = api.keystone.keystoneclient(request)
            new_idp = client.federation.identity_providers.create(**idp_ref)
            messages.success(request,
                             _('IdentityProvider "%s" was successfully created.')
                             % data['id'])
            return new_idp
        except Exception:
            exceptions.handle(request, _('Unable to create identity provider.'))


class UpdateIdentityProviderForm(BaseIdentityProviderForm):
    id = forms.CharField(label=_("ID"), widget=forms.HiddenInput)
    description = forms.CharField(label=_("Description"),
                                required=True)

    def __init__(self, request, *args, **kwargs):
        super(UpdateIdentityProviderForm, self).__init__(request, *args, **kwargs)

    def handle(self, request, data):
        idp = data.pop('id')

        try:
            client = api.keystone.keystoneclient(request)
            response = client.federation.identity_providers.update(idp, **data)
            messages.success(request,
                             _('Identity Provider has been updated successfully.'))
        except Exception:
            response = exceptions.handle(request, ignore=True)
            messages.error(request, _('Unable to update the identity provider.'))

        if isinstance(response, http.HttpResponse):
            return response
        else:
            return True


class AddProtocolsForm(forms.SelfHandlingForm):
    id = forms.CharField(label=_("ID"), widget=forms.HiddenInput)
    protocol = forms.CharField(label=_("Protocol"), required=True)
    mapping_id = forms.ChoiceField(label=_("Mapping ID"),
                                required=True)

    def __init__(self, request, *args, **kwargs):
        super(AddProtocolsForm, self).__init__(request, *args, **kwargs)
        client = api.keystone.keystoneclient(request)
        mappings = client.federation.mappings.list()
        self.fields['mapping_id'].choices = [(mapping.id, mapping.id) for mapping in mappings] 

    def handle(self, request, data):
        idp = data.pop('id')
        protocol = data.pop('protocol')
        mapping_id = data.pop('mapping_id')
        try:
            client = api.keystone.keystoneclient(request)
            response = client.federation.protocols.create(protocol, idp, mapping_id)
            messages.success(request,
                             _('Protocol has been registered successfully.'))
        except Exception:
            response = exceptions.handle(request, ignore=True)
            messages.error(request, _('Unable to register protocol.'))

        if isinstance(response, http.HttpResponse):
            return response
        else:
            return True


class UpdateProtocolsForm(AddProtocolsForm):
    protocol = forms.CharField(label=_("Protocol"), required=True)

    def __init__(self, request, *args, **kwargs):
        super(UpdateProtocolsForm, self).__init__(request, *args, **kwargs)
        self.fields["protocol"].widget.attrs["readonly"] = True

    def handle(self, request, data):
        idp = data.pop('id')
        protocol = data.pop('protocol')
        mapping_id = data.pop('mapping_id')
        try:
            client = api.keystone.keystoneclient(request)
            response = client.federation.protocols.update(idp, protocol, mapping_id)
            messages.success(request,
                             _('Protocol has been updated successfully.'))
        except Exception:
            response = exceptions.handle(request, ignore=True)
            messages.error(request, _('Unable to update protocol.'))

        if isinstance(response, http.HttpResponse):
            return response
        else:
            return True
