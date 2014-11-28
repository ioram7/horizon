from django.conf.urls import include  # noqa
from django.conf.urls import patterns  # noqa
from django.conf.urls import url  # noqa

from openstack_dashboard.dashboards.identity.vo_admin import views

urlpatterns = patterns('openstack_dashboard.dashboards.identity.flavors.views',
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^create/$', views.CreateView.as_view(), name='create'),
    url(r'^(?P<id>[^/]+)/update/$', views.UpdateView.as_view(), name='update'),
    url(r'^(?P<id>[^/]+)/manage/$', views.ManageView.as_view(), name='manage'),

    url(r'^(?P<id>[^/]+)/blacklist/$', views.BlacklistView.as_view(), name='blacklist'),
    url(r'^(?P<id>[^/]+)/requests/$', views.ViewRequestsView.as_view(), name='view_requests'),
    url(r'^(?P<id>[^/]+)/change_role/$', views.ChangeRoleView.as_view(), name='change_role'),

    url(r'^(?P<id>[^/]+)/add_user/$', views.AddUserView.as_view(), name='add_user'),
)
