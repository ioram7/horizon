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

from django.conf.urls import patterns  # noqa
from django.conf.urls import url  # noqa

from openstack_dashboard.dashboards.identity.identity_providers import views

urlpatterns = patterns('openstack_dashboard.dashboards.identity.identity_providers.views',
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^(?P<identity_provider_id>[^/]+)/update/$',
        views.UpdateView.as_view(), name='update'),
    url(r'^create/$', views.CreateView.as_view(), name='create'),
    url(r'^(?P<identity_provider_id>[^/]+)/manage_protocol/$',
        views.ProtocolView.as_view(), name='manage_protocols'),
    url(r'^(?P<identity_provider_id>[^/]+)/add_protocol/$',
        views.AddProtocolView.as_view(), name='add_protocol'),
    url(r'^(?P<identity_provider_id>[^/]+)/update_protocol/(?P<protocol>[^/]+)$',
        views.UpdateProtocolView.as_view(), name='update_protocol'),
    url(r'^(?P<identity_provider_id>[^/]+)/update_protocol/$',
        views.UpdateProtocolView.as_view(), name='update_protocol'))
