from django.urls import path

from . import views


app_name = 'friendships'
urlpatterns = [
    path(
        'friends/', 
        views.FriendListView.as_view(),
        name='list'
    ),
    path(
        'friends/add/',
        views.FriendshipRequestCreateView.as_view(),
        name='create_friendship_request'
    ),
    path(
        'friends/remove/<slug:username>/',
        views.FriendDeleteView.as_view(),
        name='delete'
    ),
    path(
        'friends/requests/',
        views.FriendshipRequestListView.as_view(),
        name='friendship_request_list'
    ),
    path(
        'friends/requests/sent/',
        views.SentFriendshipRequestListView.as_view(),
        name='sent_friendship_request_list'
    ),
    path(
        'friends/requests/<int:pk>/',
        views.FriendshipRequestDetailView.as_view(),
        name='friendship_request_detail'
    ),
    path(
        'friends/requests/<int:pk>/accept/',
        views.FriendshipRequestAcceptView.as_view(),
        name='accept_friendship_request'
    ),
    path(
        'friends/requests/<int:pk>/reject/',
        views.FriendshipRequestRejectView.as_view(),
        name='reject_friendship_request'
    ),
]