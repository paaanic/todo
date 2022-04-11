from django.urls import path

from . import views


app_name = 'tasks'
urlpatterns = [
    path('', views.TaskIndexView.as_view(), name='index'),
    path('new/', views.TaskCreateView.as_view(), name='create'),
    path('<int:pk>/edit/', views.TaskUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.TaskDeleteView.as_view(), name='delete'),
    path('<int:pk>/done/', views.TaskDoneView.as_view(), name='done'),
    path('<int:pk>/repeat/', views.TaskRepeatView.as_view(), name='repeat'),
    path(
        '<int:task_id>/shares/', 
        views.TaskShareListView.as_view(), 
        name='share_list'
    ),
    path(
        '<int:task_id>/shares/new/', 
        views.TaskShareCreateView.as_view(), 
        name='share_create'
    )
]