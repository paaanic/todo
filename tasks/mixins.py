from django.contrib.auth.mixins import UserPassesTestMixin


class UserIsTaskAuthorTestMixin(UserPassesTestMixin):
    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user


class UserIsTaskAuthorNotificationTestMixin(UserPassesTestMixin):
    def test_func(self):
        obj = self.get_object()
        return obj.task.author == self.request.user
