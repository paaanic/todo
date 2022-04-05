from django.contrib.auth import get_user_model
from django.forms import CharField, Form, Textarea, TextInput

from . import manager as friendship_manager
from .models import FriendshipRequest


user_model = get_user_model()


class FriendshipRequestForm(Form):
    to_username = CharField(label='Username')
    message = CharField(max_length=255, widget=Textarea(), required=False)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        to_username = self.cleaned_data['to_username']
        self.cleaned_data['to_username'] = to_username.strip()
        cleaned_data = super().clean()
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

        
