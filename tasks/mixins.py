from django.contrib.auth.mixins import UserPassesTestMixin


class UserIsTaskAuthorTestMixin(UserPassesTestMixin):
    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user
        

class UserIsTaskShareToUserTestMixin(UserPassesTestMixin):
    def test_func(self):
        task_share = self.get_object()
        return task_share.to_user == self.request.user