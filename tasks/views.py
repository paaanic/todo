from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, TemplateView, View
from django.views.generic.detail import (
    SingleObjectMixin,
    SingleObjectTemplateResponseMixin
)
from django.views.generic.edit import (
    CreateView,
    DeleteView,
    FormMixin,
    ModelFormMixin,
    ProcessFormView,
    UpdateView
)

from tasks.forms import TaskShareForm

from .mixins import (
    UserIsTaskAuthorTestMixin,
    UserIsTaskShareToUserTestMixin
)
from .models import Task, TaskShare


user_model = get_user_model()


class TaskIndexView(LoginRequiredMixin, TemplateView):
    template_name = 'tasks/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_tasks = (
            Task.objects.filter(author=self.request.user)
            .order_by('-create_date')
        )
        context['active_tasks'] = [t for t in all_tasks if t.active]
        context['done_tasks'] = (
            Task.objects.filter(author=self.request.user, done=True)
            .order_by('-done_date')
        )
        context['failed_tasks'] = [t for t in all_tasks if t.failed]
        shared_tasks = (
            TaskShare.objects.filter(to_user=self.request.user)
            .order_by('-task__create_date')
        )
        context['active_shared_tasks'] = [
            tsh for tsh in shared_tasks if tsh.active
        ]
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
        task = self.get_object()
        task.done = True
        task.done_date = now
        task.save()
        return HttpResponseRedirect(reverse('tasks:index'))


class TaskDeleteView(
    LoginRequiredMixin, UserIsTaskAuthorTestMixin, DeleteView
):
    model = Task
    template_name = 'tasks/delete.html'
    success_url = reverse_lazy('tasks:index')


class TaskRepeatView(
    LoginRequiredMixin,
    UserIsTaskAuthorTestMixin,
    SingleObjectTemplateResponseMixin,
    ModelFormMixin,
    ProcessFormView
):
    model = Task
    template_name = 'tasks/repeat.html'
    fields = ['title', 'comment', 'expire_date']
    success_url = reverse_lazy('tasks:index')

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        if self.object.active:
            return HttpResponseForbidden()
            
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = None
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class TaskShareCreateView(
    LoginRequiredMixin,
    UserIsTaskAuthorTestMixin,
    SingleObjectTemplateResponseMixin,
    FormMixin,
    ProcessFormView
):
    model = TaskShare
    form_class = TaskShareForm
    template_name = 'tasks/task_share_create.html'
    success_url = reverse_lazy('tasks:index')

    def get(self, request, *args, **kwargs):
        get_object_or_404(Task, pk=self.kwargs.get('task_id'))
        self.object = None
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        task = Task.objects.get(pk=self.kwargs.get('task_id'))
        to_username = form.cleaned_data.get('to_username')
        comment = form.cleaned_data.get('comment')

        try:
            to_user = user_model.objects.get(username=to_username)
        except user_model.DoesNotExist:
            pass
        else:
            try:
                TaskShare.objects.create(
                    task=task,
                    from_user=self.request.user,
                    to_user=to_user,
                    comment=comment
                )
            except IntegrityError:
                form.add_error(None, "You've already shared this task with this user")
                return self.form_invalid(form)

        return HttpResponseRedirect(self.get_success_url())

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_object(self):
        return Task.objects.get(pk=self.kwargs.get('task_id'))


class TaskShareListView(ListView):
    model = TaskShare
    template_name = 'tasks/task_shares.html'
    context_object_name = 'task_shares'

    def get_queryset(self):
        return TaskShare.objects.filter(task__id=self.kwargs.get('task_id'))


class TaskShareDoneView(
    LoginRequiredMixin,
    UserIsTaskShareToUserTestMixin,
    SingleObjectMixin,
    View
):
    model = TaskShare
    success_url = reverse_lazy('tasks:index')

    def post(self, request, *args, **kwargs):
        task_share = self.get_object()
        task_share.done = True
        task_share.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return self.success_url
