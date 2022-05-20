from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import TemplateView


class IndexView(TemplateView):
    template_name = 'pages/index.html'

    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated: 
            return HttpResponseRedirect(reverse('tasks:index'))
        return super().get(request, *args, **kwargs)