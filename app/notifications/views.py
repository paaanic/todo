from django.db import transaction
from django.http import HttpResponseRedirect
from django.views.generic.edit import CreateView


class NotificationBaseCreateView(CreateView):
    fields = ['datetime', 'dispatchers']

    def form_valid(self, form):
        self.object = form.save()
        transaction.on_commit(self.object.register)
        return HttpResponseRedirect(self.get_success_url())
