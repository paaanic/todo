from django.contrib.auth import get_user_model
from django.forms import CharField, Form, ModelChoiceField, Textarea

from . import manager as friendship_manager
from .models import FriendshipRequest
from .widgets import SelectFriendWidget


user_model = get_user_model()


class FriendshipRequestForm(Form):
    to_username = CharField(label='Username')
    message = CharField(max_length=255, widget=Textarea(), required=False)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        
        to_username = self.cleaned_data.get('to_username')
        if to_username is None: 
            self.add_error(
                'to_username', 'Username field is required'
            )
            return 

        self.cleaned_data['to_username'] = to_username.strip()
        to_username = cleaned_data['to_username']

        try:
            to_user = user_model.objects.get(username=to_username)
        except user_model.DoesNotExist:
            return

        if to_user == self.user:
            self.add_error(
                'to_username', f"You can't send a request to yourself"
            )
            return

        if friendship_manager.are_friends(self.user, to_user):
            self.add_error(
                'to_username', f'You are already friends with {to_username}'
            )
            return
        
        try:
            FriendshipRequest.objects.get(from_user=self.user, to_user=to_user)
        except FriendshipRequest.DoesNotExist:
            return
        else:
            self.add_error(
                'to_username', f'You have already sent a request to {to_username}'
            )


class FriendModelChoiceField(ModelChoiceField):
    def __init__(self, user, **kwargs):
        self._user = user
        super().__init__(
            queryset=None,
            label='Select friend',
            empty_label=None,
            initial=None,
            widget=SelectFriendWidget(), **kwargs)

    def label_from_instance(self, obj):
        return obj.from_user.username

    @property
    def user(self):
        return self._user

    @user.setter
    def user(self, value):
        self._user = value
        if self._user is not None:
            self.queryset = self._user.friends.all()