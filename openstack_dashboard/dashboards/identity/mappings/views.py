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

from openstack_dashboard.dashboards.identity.mappings \
    import forms as project_forms
from openstack_dashboard.dashboards.identity.mappings \
    import tables as project_tables


class MappingEntry(object):

    def __init__(self, id, rules):
        self.id = id
        self.rules = rules

class RuleEntry(object):

    def __init__(self, rule):
        self.remote = rule.get('remote')
        self.local = rule.get('local')

class IndexView(tables.DataTableView):
    table_class = project_tables.MappingsTable
    template_name = 'identity/mappings/index.html'

    def get_data(self):
        mappings = []
        try:
            client = api.keystone.keystoneclient(self.request)
            mappings = client.federation.mappings.list()
        except Exception:
            exceptions.handle(self.request,
                              _('Unable to retrieve mapping list.'))
        return [MappingEntry(mapping.id, mapping.rules) for mapping in mappings]

class UpdateView(forms.ModalFormView):
    form_class = project_forms.UpdateMappingForm
    template_name = 'identity/mappings/update.html'
    success_url = reverse_lazy('horizon:identity:mappings:index')

    @method_decorator(sensitive_post_parameters('password',
                                                'confirm_password'))
    def dispatch(self, *args, **kwargs):
        return super(UpdateView, self).dispatch(*args, **kwargs)

    @memoized.memoized_method
    def get_object(self):
        try:
            client = api.keystone.keystoneclient(self.request)
            return client.federation.mappings.get(self.kwargs['mapping_id'])
        except Exception:
            redirect = reverse("horizon:identity:mappings:index")
            exceptions.handle(self.request,
                              _('Unable to update user.'),
                              redirect=redirect)

    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        context['user'] = self.get_object()
        return context

    def get_initial(self):
        user = self.get_object()
        return {'id': user.id,
                'rules': user.rules}


class CreateView(forms.ModalFormView):
    form_class = project_forms.CreateMappingForm
    template_name = 'identity/mappings/create.html'
    success_url = reverse_lazy('horizon:identity:mappings:index')

    @method_decorator(sensitive_post_parameters('password',
                                                'confirm_password'))
    def dispatch(self, *args, **kwargs):
        return super(CreateView, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(CreateView, self).get_form_kwargs()
        return kwargs

    def get_initial(self):
        return {"id": "",
                "rules": [{"remote":[], "local":[]}]}
