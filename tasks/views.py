from audioop import reverse
from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic import DetailView, TemplateView

from .forms import TaskForm
from .mixins import (
    UserIsTaskAuthorTestMixin, 
    UserIsTaskAuthorNotificationTestMixin
)
from .models import Task, TaskNotification


class IndexView(
    LoginRequiredMixin, TemplateView
):
    template_name = 'tasks/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_tasks'] = Task.objects.filter(done=False)
        context['done_tasks'] = Task.objects.filter(done=True)


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    template_name = 'tasks/create.html'
    fields = ['title', 'comment', 'expire_date']
    success_url = reverse_lazy('tasks:index')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class TaskUpdateView(
    LoginRequiredMixin, UserIsTaskAuthorTestMixin, UpdateView
):
    model = Task
    template_name = 'tasks/update.html'
    fields = ['title', 'comment', 'expire_date']
    success_url = reverse_lazy('tasks:index')


class TaskDeleteView(
    LoginRequiredMixin, UserIsTaskAuthorTestMixin, DeleteView
):
    model = Task
    template_name = 'tasks/delete.html'
    success_url = reverse_lazy('tasks:index')


class TaskNotificationCreateView(
    LoginRequiredMixin, UserIsTaskAuthorNotificationTestMixin, CreateView
):
    model = TaskNotification
    template_name = 'tasks/notif_create.html'

    def form_valid(self, form):
        form.instance.task = Task.objects.get(pk=self.kwargs['task_id'])
        return super().form_valid(form)


class TaskNotificationDeleteView(
    LoginRequiredMixin, UserIsTaskAuthorNotificationTestMixin, DeleteView
):
    model = TaskNotification
    template_name = 'tasks/notif_delete.html'
