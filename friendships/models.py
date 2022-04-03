from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, models
from django.db.models import Q


AUTH_USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')


class FriendshipUser(get_user_model()):
    class Meta:
        proxy = True

    def are_friends(self, other):
        try:
            Friend.objects.get(from_user=self, to_user=other)
            return True
        except Friend.DoesNotExist:
            return False

    def add_friend(self, other):
        if self.are_friends(other):
            raise Friend.AlreadyExists("Users are already friends")

        try:
            FriendshipRequest.objects.create(
                from_user=self, to_user=other
            )
        except IntegrityError:
            raise FriendshipRequest.AlreadyExists(
                f"Friendship request from #{self} to #{other} already exists"
            )

    def remove_friend(self, to_user):
        friend = Friend.objects.get(from_user=self, to_user=to_user)
        friend.delete()
        friend_reverse = Friend.objects.get(from_user=to_user, to_user=self)
        friend_reverse.delete()


class FriendshipRequest(models.Model):
    from_user = models.ForeignKey(
        AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_friendship_requests'
    )
    to_user = models.ForeignKey(
        AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='friendship_requests'
    )
    message = models.CharField(max_length=255, blank=True)
    create_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['from_user', 'to_user'],
                name='unique_friendship_request'
            )
        ]

    class AlreadyExists(Exception):
        pass

    def __str__(self):
        return (
            f'Friendship request from #{self.from_user.id} to #{self.to_user.id}'
        )

    def clean(self):
        if self.from_user == self.to_user:
            raise ValidationError("Users can't create a friendship request to themselves")
        
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def accept(self):
        Friend.objects.create(from_user=self.to_user, to_user=self.from_user)
        Friend.objects.create(from_user=self.from_user, to_user=self.to_user)

        self.delete()

        FriendshipRequest.objects.filter(
            from_user=self.to_user, to_user=self.from_user
        ).delete()

    def reject(self):
        self.delete()


class Friend(models.Model):
    from_user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    to_user = models.ForeignKey(
        AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='friends'
    )
    create_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['from_user', 'to_user'],
                name='unique_friend'
            )
        ]

    class AlreadyExists(Exception):
        pass

    def __str__(self):
        return f'User #{self.from_user.id} is friend with user #{self.to_user.id}'

    def clean(self):
        if self.from_user == self.to_user:
            raise ValidationError("Users can't be friends with themselves")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
        # Try to create reverse friend object
        try:
            Friend.objects.create(from_user=self.to_user, to_user=self.from_user)
        except IntegrityError:
            pass
        

    def delete(self, *args, **kwargs):
        return Friend.objects.filter(
            Q(from_user=self.from_user, to_user=self.to_user) |
            Q(from_user=self.to_user, to_user=self.from_user)
        ).delete()
