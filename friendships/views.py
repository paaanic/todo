from audioop import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, TemplateView
from django.views.generic.detail import BaseDetailView, DetailView, SingleObjectTemplateResponseMixin
from django.views.generic.edit import CreateView, DeleteView, FormMixin

from . import manager as friendships_manager
from .models import Friend, FriendshipRequest


user_model = get_user_model()


class FriendListView(ListView):
    template_name = 'friendships/list.html'

    def get_queryset(self):
        return (
            friendships_manager.friends(self.request.user)
            .order_by('-create_date')
        )


class FriendAddView(TemplateView):
    template_name = 'friendships/add.html'
    exception = None

    def post(self, username):
        to_user = get_object_or_404(user_model, username=username)
        try:
            friendships_manager.add_friend(self.request.user, to_user)
        except (Friend.AlreadyExists, FriendshipRequest.AlreadyExists) as exc:
            self.exception = exc.__qualname__.lower()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.exception is not None:
            context['exception'] = self.exception
        return context


class FriendDeleteView(DeleteView):
    template_name = 'friendships/delete.html'
    success_url = reverse_lazy('friendships:list')

    def get_queryset(self):
        return Friend.objects.filter(
            from_user=self.request.user,
            to_user=self.request.kwargs['username']
        )

    def form_valid(self, form):
        success_url = self.get_success_url()
        to_user = self.request.kwargs['username']
        friendships_manager.remove_friend(self.request.user, to_user)
        return HttpResponseRedirect(success_url)
    

class FriendshipRequestListView(ListView):
    template_name = 'friendships/friendship_requests.html'

    def get_queryset(self):
        return (
            friendships_manager.requests(self.request.user)
            .order_by('-create_date')
        )


class SentFriendshipRequestListView(ListView):
    template_name = 'friendships/sent_friendship_requests.html'

    def get_queryset(self):
        return (
            friendships_manager.requests(self.request.user)
            .order_by('-create_date')
        )


class BaseFriendshipRequestActionView(
    SingleObjectTemplateResponseMixin, FormMixin, BaseDetailView
):
    success_url = reverse_lazy('friendships:list')

    def action(self, friendship_request):
        raise NotImplementedError("Provide action method for handling frienship request")

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.action(self.object)
        return HttpResponseRedirect(success_url)


class FriendshipRequestAcceptView(BaseFriendshipRequestActionView):
    template_name = 'friendships/accept_friendship_request.html'

    def action(self, friendship_request):
        friendship_request.accept()


class FriendshipRequestRejectView(BaseFriendshipRequestActionView):
    template_name = 'friendships/accept_friendship_request.html'
    success_url = reverse_lazy('friendships:list')

    def action(self, friendship_request):
        friendship_request.reject()