from django.forms import ModelForm, DateTimeField

from .models import Task


class TaskForm(ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'comment', 'expire_date']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['expire_date'].input_formats = [r'%d/%m/%Y, %H:%M']
