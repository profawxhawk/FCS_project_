from groups import views as group_views
from django.urls import path,include
urlpatterns = [ path('create_group',group_views.create_group,name='create_group'),
path('groups_by_you',group_views.groups_u_created,name='group_created'),
path('group_wall/(?P<pk>\d+)',group_views.group_wall,name='group_wall'),
]
