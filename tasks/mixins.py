from re import A
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import ImproperlyConfigured


class UserIsTaskAuthorTestMixin(UserPassesTestMixin):
    def test_func(self):
        task = self.get_object()
        return task.author == self.request.user


class UserIsTaskShareToUserTestMixin(UserPassesTestMixin):
    def test_func(self):
        task_share = self.get_object()
        return task_share.to_user == self.request.user


class UserIsInTaskSharesUsersTestMixin(UserPassesTestMixin):
    def test_func(self):
        task = self.get_object()
        print(self.request.user, '\n', task.shares.all().values_list('to_user', flat=True))
        return (
            self.request.user.id
            in task.shares.all().values_list('to_user', flat=True)
        )


def UserPassesAnyTestMixin(*test_mixins):
    test_funcs = []
    for test_mixin in test_mixins:
        if not issubclass(test_mixin, UserPassesTestMixin):
            raise TypeError("You should only pass subclasses of UserPassesTestMixin")
        test_funcs.append(getattr(test_mixin, 'test_func'))
        
    def test_func(self):
        return any([test_func(self) for test_func in self.test_funcs])
            
    return type(
        '_UserPassesAnyTestMixin',
        (UserPassesTestMixin,),
        {
            'test_funcs': test_funcs,
            'test_func': test_func
        }
    )


def UserPassesAllTestsMixin(*test_mixins):
    test_funcs = []
    for test_mixin in test_mixins:
        if not issubclass(test_mixin, UserPassesTestMixin):
            raise TypeError("You should only pass subclasses of UserPassesTestMixin")
        test_funcs.append(getattr(test_mixin, 'test_func'))
        
    def test_func(self):
        return all([test_func(self) for test_func in self.test_funcs])
            
    return type(
        '_UserPassesAllTestsMixin',
        (UserPassesTestMixin,),
        {
            'test_funcs': test_funcs,
            'test_func': test_func
        }
    )
