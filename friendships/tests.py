from django.db.utils import IntegrityError
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase, TransactionTestCase

from . import manager as friendship_manager
from .models import Friend, FriendshipRequest, FriendshipUser


def create_test_friend_relationship(from_user, to_user):
    Friend.objects.create(from_user=from_user, to_user=to_user)
    Friend.objects.create(from_user=to_user, to_user=from_user)


class FriendListViewTest(TestCase):
    def setUp(self):
        pass



class FriendshipUserModelTest(TransactionTestCase):
    def setUp(self):
        self.user1 = FriendshipUser.objects.create(username='user1')
        self.user2 = FriendshipUser.objects.create(username='user2')

    def test_are_friends(self):
        self.assertFalse(self.user1.are_friends(self.user2))
        self.assertFalse(self.user2.are_friends(self.user1))
        create_test_friend_relationship(self.user1, self.user2)
        self.assertTrue(self.user1.are_friends(self.user2))
        self.assertTrue(self.user2.are_friends(self.user1))

    def test_add_friend(self):
        self.user1.add_friend(self.user2)
        FriendshipRequest.objects.get(from_user=self.user1, to_user=self.user2)

        with self.assertRaises(FriendshipRequest.AlreadyExists):
            self.user1.add_friend(self.user2)

        create_test_friend_relationship(self.user1, self.user2)

        with self.assertRaises(Friend.AlreadyExists):
            self.user1.add_friend(self.user2)

    def test_remove_friend(self):
        create_test_friend_relationship(self.user1, self.user2)
        self.user1.remove_friend(self.user2)
        self.assertQuerysetEqual(
            Friend.objects.filter(
                from_user__in=[self.user1, self.user2],
                to_user__in=[self.user1, self.user2]
            ), 
            []
        )


class FriendModelTest(TransactionTestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.user1 = self.user_model.objects.create(username='user1')
        self.user2 = self.user_model.objects.create(username='user2')
        self.friend = Friend.objects.create(
            from_user=self.user1, to_user=self.user2
        )

    def test_create(self):
        self.assertEqual(self.friend.from_user, self.user1)
        self.assertEqual(self.friend.to_user, self.user2)

    def test_create_adds_reverse_object(self):
        reverse_friend = Friend.objects.get(
            from_user=self.user2, to_user=self.user1
        )
        self.assertEqual(reverse_friend.from_user, self.user2)
        self.assertEqual(reverse_friend.to_user, self.user1)

    def test_clean(self):
        friend = Friend(from_user=self.user1, to_user=self.user1)

        with self.assertRaises(ValidationError):
            friend.clean()

    def test_delete(self):
        self.friend.delete()
        with self.assertRaises(Friend.DoesNotExist):
            Friend.objects.get(from_user=self.user2, to_user=self.user1)
        
    def test_friend_unique_constraint(self):
        with self.assertRaises(IntegrityError):
            Friend.objects.create(
                from_user=self.user1, to_user=self.user2
            )

    def test_user_friend_backward_relationship(self):
        user3 = self.user_model.objects.create(username='user3')
        friend2 = Friend.objects.get(
            from_user=self.user2, to_user=self.user1
        )
        friend3 = Friend.objects.create(
            from_user=user3, to_user=self.user1
        )
        self.assertQuerysetEqual(
            self.user1.friends.all(), [friend2, friend3], 
            ordered=False
        )


class FriendshipRequestModelTest(TestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.user1 = self.user_model.objects.create(username='user1')
        self.user2 = self.user_model.objects.create(username='user2')
        self.friendship_request = FriendshipRequest.objects.create(
            from_user=self.user1, to_user=self.user2
        )

    def test_create(self):
        self.assertEqual(self.friendship_request.from_user, self.user1)
        self.assertEqual(self.friendship_request.to_user, self.user2)

    def test_clean(self):
        friendship_request = FriendshipRequest(
            from_user=self.user1, to_user=self.user1
        )
        with self.assertRaises(ValidationError):
            friendship_request.clean()

    def test_accept(self):
        self.friendship_request.accept()
        Friend.objects.get(from_user=self.user1, to_user=self.user2)
        Friend.objects.get(from_user=self.user2, to_user=self.user1)

        with self.assertRaises(FriendshipRequest.DoesNotExist):
            FriendshipRequest.objects.get(from_user=self.user1, to_user=self.user2)

        with self.assertRaises(FriendshipRequest.DoesNotExist):
            FriendshipRequest.objects.get(from_user=self.user2, to_user=self.user1)

    def test_reject(self):
        self.friendship_request.reject()

        with self.assertRaises(FriendshipRequest.DoesNotExist):
            FriendshipRequest.objects.get(from_user=self.user1, to_user=self.user2)

    def test_reject(self):
        pass

    def test_friendship_request_unique_constraint(self):
        with self.assertRaises(IntegrityError):
            FriendshipRequest.objects.create(
                from_user=self.user1, to_user=self.user2
            )

    def test_user_friendship_request_backward_relationship(self):
        user3 = self.user_model.objects.create(username='user3')
        friendship_request2 = FriendshipRequest.objects.create(
            from_user=self.user2, to_user=self.user1
        )
        friendship_request3 = FriendshipRequest.objects.create(
            from_user=user3, to_user=self.user1
        )
        self.assertQuerysetEqual(
            self.user1.friendship_requests.all(), 
            [friendship_request2, friendship_request3], 
            ordered=False
        )
        self.assertQuerysetEqual(
            self.user1.sent_friendship_requests.all(),
            [self.friendship_request], 
        )
