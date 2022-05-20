from django.core.exceptions import ValidationError
from django.db import IntegrityError

from .models import Friend, FriendshipRequest


def friends(user):
    return Friend.objects.select_related('from_user').filter(to_user=user)


def requests(user):
    return FriendshipRequest.objects.select_related(
        'from_user', 'to_user'
    ).filter(to_user=user)


def sent_requests(user):
    return FriendshipRequest.objects.select_related(
        'from_user', 'to_user'
    ).filter(from_user=user)


def are_friends(user1, user2):
    try:
        Friend.objects.get(from_user=user1, to_user=user2)
        return True
    except Friend.DoesNotExist:
        return False


def add_friend(from_user, to_user, message=""):
    if are_friends(from_user, to_user):
        raise Friend.AlreadyExists("Users are already friends")
    
    try:
        FriendshipRequest.objects.create(
            from_user=from_user, to_user=to_user, message=message
        )
    except IntegrityError:
        raise FriendshipRequest.AlreadyExists(
            f"Friendship request from #{from_user} to #{to_user} already exists"
        )


def remove_friend(from_user, to_user):
    return Friend.objects.get(from_user=from_user, to_user=to_user).delete()