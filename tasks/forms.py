from django.contrib.auth import get_user_model
from django.forms import (
    CharField, Form, ModelForm, Textarea
)

from .models import Task
from friendships.forms import FriendModelChoiceField

user_model = get_user_model()


class TaskForm(ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'comment', 'expire_date']


class TaskShareForm(Form):
    to_username = FriendModelChoiceField(user=None)
    comment = CharField(max_length=255, widget=Textarea(), required=False)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['to_username'].user = self.user

    def clean(self):
        super().clean()
        self.cleaned_data['to_username'] = \
            self.cleaned_data['to_username'].from_user.username
