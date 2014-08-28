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


class BaseMappingForm(forms.SelfHandlingForm):
    def __init__(self, request, *args, **kwargs):
        super(BaseMappingForm, self).__init__(request, *args, **kwargs)

        mapping_id = kwargs['initial'].get('id', None)
        rules = kwargs['initial'].get('rules', None)

    def clean(self):
        '''Check to make sure password fields match.'''
        data = super(forms.Form, self).clean()
        if 'password' in data:
            if data['password'] != data.get('confirm_password', None):
                raise ValidationError(_('Passwords do not match.'))
        return data




class CreateMappingForm(BaseMappingForm):
    id = forms.CharField(label=_("ID"),
                                required=True)
    rules = forms.CharField(label=_("Rules"), required=True)

    def __init__(self, *args, **kwargs):
        super(CreateMappingForm, self).__init__(*args, **kwargs)


    # We have to protect the entire "data" dict because it contains the
    # password and confirm_password strings.
    @sensitive_variables('data')
    def handle(self, request, data):
        try:
            LOG.info('Creating mapping with ID "%s"' % data['id'])
            id = data["id"]
            rules = json.loads(data['rules'])
            mapping_ref = {"rules":rules}
            client = api.keystone.keystoneclient(request)
            new_mapping = client.federation.mappings.create(mapping_id=id, rules=rules)
            messages.success(request,
                             _('Mapping "%s" was successfully created.')
                             % data['id'])
            return new_mapping
        except Exception:
            exceptions.handle(request, _('Unable to create mapping.'))


class UpdateMappingForm(BaseMappingForm):
    id = forms.CharField(label=_("ID"), widget=forms.HiddenInput)
    rules = forms.CharField(label=_("Rules"),
                                required=True)

    def __init__(self, request, *args, **kwargs):
        super(UpdateMappingForm, self).__init__(request, *args, **kwargs)

        if api.keystone.keystone_can_edit_user() is False:
            for field in ('id', 'rules'):
                self.fields.pop(field)

    # We have to protect the entire "data" dict because it contains the
    # password and confirm_password strings.
    @sensitive_variables('data', 'password')
    def handle(self, request, data):
        user = data.pop('id')

        try:
            if "rules" in data:
                data['rules'] = json.loads(data['rules'])
            client = api.keystone.keystoneclient(request)
            response = client.federation.mappings.update(user, **data)
            messages.success(request,
                             _('Mapping has been updated successfully.'))
        except Exception:
            response = exceptions.handle(request, ignore=True)
            messages.error(request, _('Unable to update the user.'))

        if isinstance(response, http.HttpResponse):
            return response
        else:
            return True
