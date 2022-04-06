from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import Form
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import View, DeleteView, DetailView, ListView, TemplateView
from django.views.generic.detail import SingleObjectMixin, SingleObjectTemplateResponseMixin
from django.views.generic.edit import FormMixin, ProcessFormView

from . import manager as friendships_manager
from .forms import FriendshipRequestForm
from .mixins import UserIsFriendshipRequestReceiverTestMixin
from .models import Friend, FriendshipRequest


user_model = get_user_model()


class FriendIndexView(LoginRequiredMixin, TemplateView):
    template_name = 'friendships/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['friends_list'] = (
            friendships_manager.friends(self.request.user)
            .order_by('-create_date')
        )
        context['friend_requests'] = (
            friendships_manager.requests(self.request.user)
            .order_by('-create_date')
        )
        context['sent_friend_requests'] = (
            friendships_manager.sent_requests(self.request.user)
            .order_by('-create_date')
        )
        return context


class FriendListView(LoginRequiredMixin, ListView):
    template_name = 'friendships/list.html'

    def get_queryset(self):
        return (
            friendships_manager.friends(self.request.user)
            .order_by('-create_date')
        )


class FriendshipRequestCreateView(
    LoginRequiredMixin,
    SingleObjectTemplateResponseMixin,
    FormMixin,
    ProcessFormView
):
    model = FriendshipRequest
    form_class = FriendshipRequestForm
    template_name = 'friendships/add.html'
    success_url = reverse_lazy('friendships:sent_friendship_request_list')
        
    def get(self, request, *args, **kwargs):
        self.object = None
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        to_username = form.cleaned_data.get('to_username')
        msg = form.cleaned_data.get('message')
        try:
            to_user = user_model.objects.get(username=to_username)
            friendships_manager.add_friend(self.request.user, to_user, msg)
        except user_model.DoesNotExist:
            pass
        return HttpResponseRedirect(self.get_success_url())


class FriendDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'friendships/delete.html'
    success_url = reverse_lazy('friendships:list')
    slug_field = 'to_user__username'
    slug_url_kwarg = 'username'

    def get_queryset(self):
        return Friend.objects.filter(from_user=self.request.user)
    

class FriendshipRequestListView(LoginRequiredMixin, ListView):
    template_name = 'friendships/friendship_request_list.html'
    context_object_name = 'friend_requests'

    def get_queryset(self):
        return (
            friendships_manager.requests(self.request.user)
            .order_by('-create_date')
        )


class SentFriendshipRequestListView(LoginRequiredMixin, ListView):
    template_name = 'friendships/sent_friendship_request_list.html'
    context_object_name = 'sent_friend_requests'

    def get_queryset(self):
        return (
            friendships_manager.sent_requests(self.request.user)
            .order_by('-create_date')
        )


class FriendshipRequestDetailView(DetailView):
    model = FriendshipRequest
    template_name = 'friendships/friendship_request_detail.html'
    context_object_name = 'friend_req'


class BaseFriendshipRequestActionView(
    FormMixin, SingleObjectMixin, View
):
    model = FriendshipRequest
    form_class = Form
    success_url = reverse_lazy('friendships:list')

    def action(self, friendship_request):
        raise NotImplementedError("Provide action method for handling friendship request")

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


class FriendshipRequestAcceptView(
    LoginRequiredMixin,
    UserIsFriendshipRequestReceiverTestMixin,
    BaseFriendshipRequestActionView
):
    def action(self, friendship_request):
        friendship_request.accept()


class FriendshipRequestRejectView(
    LoginRequiredMixin,
    UserIsFriendshipRequestReceiverTestMixin,
    BaseFriendshipRequestActionView
):
    def action(self, friendship_request):
        friendship_request.reject()