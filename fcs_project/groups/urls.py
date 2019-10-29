from groups import views as group_views
from django.urls import path,include
urlpatterns = [ path('create_group',group_views.create_group,name='create_group'),
path('groups_by_you',group_views.groups_u_created,name='group_created'),
path('group_wall/<int:pk>',group_views.group_wall,name='group_wall'),
path('group_settings/<int:pk>',group_views.group_settings,name='group_settings'),
path('accept_group_request/<int:pk>',group_views.accept_group_request,name='accept_group_request'),
path('reject_group_request/<int:pk>',group_views.reject_group_request,name='reject_group_request'),
path('groups_you_are_member_of',group_views.groups_you_are_member_of,name='groups_you_are_member_of'),
# path('confirm_accept_group_request/<int:pk>',group_views.confirm_accept_group_request,name='confirm_accept_group_request'),
# path('confirm_reject_group_request/<int:pk>',group_views.confirm_reject_group_request,name='confirm_reject_group_request'),
]
