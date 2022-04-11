from django.contrib.auth import get_user_model
from django.forms import CharField, Form, ModelForm, Textarea

from .models import Task
from friendships.manager import are_friends


user_model = get_user_model()


class TaskForm(ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'comment', 'expire_date']


class TaskShareForm(Form):
    to_username = CharField(label='Username')
    comment = CharField(max_length=255, widget=Textarea())

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        super().clean()
        to_username = self.cleaned_data.get('to_username')

        try:
            to_user = user_model.objects.get(username=to_username)
        except user_model.DoesNotExist:
            self.add_error(
                'to_username', 'You can only share tasks with friends'
            )
        else:
            if self.user == to_user:
                self.add_error(
                    'to_username', 'You cannot share task with yourself'
                )
            elif not are_friends(self.user, to_user):
                self.add_error(
                    'to_username', 'You can only share tasks with friends'
                )
