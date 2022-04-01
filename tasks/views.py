from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import TemplateView, View
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from .mixins import (
    UserIsTaskAuthorTestMixin, 
    UserIsTaskAuthorNotificationTestMixin
)
from .models import Task, TaskNotification


class TaskListView(
    LoginRequiredMixin, TemplateView
):
    template_name = 'tasks/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_tasks'] = [t for t in Task.objects.all() if t.active]
        context['done_tasks'] = Task.objects.filter(done=True)
        context['failed_tasks'] = [t for t in Task.objects.all() if t.failed]
        return context


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


class TaskDoneView(
    LoginRequiredMixin, UserIsTaskAuthorTestMixin, SingleObjectMixin, View
):
    model = Task

    def post(self, request, *args, **kwargs):
        now = timezone.now()
        task = get_object_or_404(Task, pk=self.kwargs['pk'])
        task.done = True
        task.done_time = now
        task.save()
        return HttpResponseRedirect(reverse('tasks:index'))


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
