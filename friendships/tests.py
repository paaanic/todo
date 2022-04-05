from xml.dom.minidom import parseString
from django.db.utils import IntegrityError
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase, TransactionTestCase
from django.urls import reverse

from . import manager as friendship_manager
from .models import Friend, FriendshipRequest, FriendshipUser


user_model = get_user_model()


def create_bunch_of_test_users(n_users=3):
    return (
        user_model.objects.create(username=uname) 
        for uname in (f'user{i}' for i in range(1, n_users + 1))
    )


class FriendListViewTest(TransactionTestCase):
    def setUp(self):
        self.user1, self.user2, self.user3 = create_bunch_of_test_users()
        self.client.force_login(self.user1)
        Friend.objects.create(from_user=self.user1, to_user=self.user2)
        Friend.objects.create(from_user=self.user1, to_user=self.user3)

    def test_url(self):
        response = self.client.get('/friends/')
        self.assertEqual(response.status_code, 200)

    def test_url_name(self):
        response = self.client.get(reverse('friendships:list'))
        self.assertEqual(response.status_code, 200)
        
    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('friendships:list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'friendships/list.html')

    def test_login_required(self):
        self.client.logout()
        response = self.client.get(reverse('friendships:list'), follow=True)
        self.assertEqual(response.request['PATH_INFO'], reverse('login'))


class FriendshipRequestCreateViewTest(TransactionTestCase):
    def setUp(self):
        self.user1, self.user2 = create_bunch_of_test_users(2)
        self.client.force_login(self.user1)
        self.create_form = {
            'to_username': self.user2.username
        }

    def test_url(self):
        response = self.client.get(f'/friends/add/')
        self.assertEqual(response.status_code, 200)

    def test_url_name(self):
        response = self.client.get(reverse('friendships:create_friendship_request'))
        self.assertEqual(response.status_code, 200)

    def test_use_correct_template(self):
        response = self.client.get(reverse('friendships:create_friendship_request'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'friendships/add.html')

    def test_add_friendship_request_and_redirect(self):
        url = reverse('friendships:create_friendship_request')
        response = self.client.post(url, self.create_form)
        self.assertEqual(response.status_code, 302)
        are_friends = friendship_manager.are_friends(self.user1, self.user2)
        self.assertFalse(are_friends)
        try:
            FriendshipRequest.objects.get(
                from_user=self.user1, to_user=self.user2
            )
        except FriendshipRequest.DoesNotExist:
            self.fail("Friendship request hasn't been created")

    def test_fail_to_add_friendship_request_if_users_are_friends(self):
        Friend.objects.create(from_user=self.user1, to_user=self.user2)
        url = reverse('friendships:create_friendship_request')
        response = self.client.post(url, self.create_form)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, 
            f"You are already friends with {self.create_form['to_username']}"
        )
        with self.assertRaises(FriendshipRequest.DoesNotExist):
            FriendshipRequest.objects.get(
                from_user=self.user1, to_user=self.user2
            )

    def test_fail_to_add_friendship_request_if_it_exists(self):
        FriendshipRequest.objects.create(
            from_user=self.user1, to_user=self.user2
        )
        url = reverse('friendships:create_friendship_request')
        response = self.client.post(url, self.create_form)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, 
            f"You have already sent a request to {self.create_form['to_username']}"
        )

    def test_login_required(self):
        self.client.logout()
        url = reverse('friendships:create_friendship_request')
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request['PATH_INFO'], reverse('login'))


class FriendDeleteViewTest(TransactionTestCase):
    def setUp(self):
        self.user1, self.user2 = create_bunch_of_test_users(2)
        self.client.force_login(self.user1)
        Friend.objects.create(from_user=self.user1, to_user=self.user2)

    def test_url(self):
        response = self.client.get(f'/friends/remove/{self.user2.username}/')
        self.assertEqual(response.status_code, 200)

    def test_url_name(self):
        url = reverse('friendships:delete', args=(self.user2.username,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_use_correct_template(self):
        url = reverse('friendships:delete', args=(self.user2.username,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'friendships/delete.html')

    def test_delete_user_friend_and_redirect(self):
        url = reverse('friendships:delete', args=(self.user2.username,))
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        are_friends = friendship_manager.are_friends(self.user1, self.user2)
        self.assertFalse(are_friends)


class FriendshipRequestListView(TestCase):
    def setUp(self):
        self.user1, self.user2, self.user3 = create_bunch_of_test_users()
        self.client.force_login(self.user1)

    def test_url(self):
        response = self.client.get('/friends/requests/')
        self.assertEqual(response.status_code, 200)

    def test_url_name(self):
        response = self.client.get(reverse('friendships:friendship_request_list'))
        self.assertEqual(response.status_code, 200)

    def test_use_correct_template(self):
        response = self.client.get(reverse('friendships:friendship_request_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, 'friendships/friendship_request_list.html'
        )
    
    def test_page_contain_friendship_request_list(self):
        response = self.client.get(reverse('friendships:friendship_request_list'))
        fr1 = FriendshipRequest.objects.create(
            from_user=self.user2, to_user=self.user1
        )
        fr2 = FriendshipRequest.objects.create(
            from_user=self.user3, to_user=self.user1
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, fr1.from_user.username)
        self.assertContains(response, fr2.from_user.username)


class SentFriendshipRequestListView(TestCase):
    def setUp(self):
        self.user1, self.user2, self.user3 = create_bunch_of_test_users()
        self.client.force_login(self.user1)

    def test_url(self):
        response = self.client.get('/friends/requests/sent/')
        self.assertEqual(response.status_code, 200)

    def test_url_name(self):
        url = reverse('friendships:sent_friendship_request_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_use_correct_template(self):
        url = reverse('friendships:sent_friendship_request_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, 'friendships/sent_friendship_request_list.html'
        )
    
    def test_page_contain_friendship_request_list(self):
        response = self.client.get(reverse('friendships:friendship_request_list'))
        fr1 = FriendshipRequest.objects.create(
            from_user=self.user2, to_user=self.user1
        )
        fr2 = FriendshipRequest.objects.create(
            from_user=self.user3, to_user=self.user1
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, fr1.from_user.username)
        self.assertContains(response, fr2.from_user.username)


class FriendshipRequestAcceptViewTest(TransactionTestCase):
    def setUp(self):
        self.user1, self.user2, self.user3 = create_bunch_of_test_users(3)
        self.client.force_login(self.user1)
        self.friend_request = FriendshipRequest.objects.create(
            from_user=self.user2, to_user=self.user1
        )

    def test_url(self):
        url = f'/friends/requests/{self.friend_request.id}/accept/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_url_name(self):
        url = reverse(
            'friendships:accept_friendship_request', 
            args=(self.friend_request.id,)
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_accept(self):
        url = reverse(
            'friendships:accept_friendship_request', 
            args=(self.friend_request.id,)
        )
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        are_friends = friendship_manager.are_friends(self.user1, self.user2)
        self.assertTrue(are_friends)

    def test_forbidden_for_not_receiver(self):
        not_users_friend_request = FriendshipRequest.objects.create(
            from_user=self.user3, to_user=self.user2
        )
        url = reverse(
            'friendships:accept_friendship_request', 
            args=(not_users_friend_request.id,)
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 403)

        self.client.force_login(self.user2)
        url = reverse(
            'friendships:accept_friendship_request', 
            args=(self.friend_request.id,)
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 403)


class FriendshipRequestRejectViewTest(TestCase):
    def setUp(self):
        self.user1, self.user2, self.user3 = create_bunch_of_test_users(3)
        self.client.force_login(self.user1)
        self.friend_request = FriendshipRequest.objects.create(
            from_user=self.user2, to_user=self.user1
        )

    def test_url(self):
        url = f'/friends/requests/{self.friend_request.id}/reject/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_url_name(self):
        url = reverse(
            'friendships:reject_friendship_request', 
            args=(self.friend_request.id,)
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_reject(self):
        url = reverse(
            'friendships:reject_friendship_request', 
            args=(self.friend_request.id,)
        )
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        are_friends = friendship_manager.are_friends(self.user1, self.user2)
        self.assertFalse(are_friends)
        with self.assertRaises(FriendshipRequest.DoesNotExist):
            FriendshipRequest.objects.get(id=self.friend_request.id)

    def test_forbidden_for_not_receiver(self):
        not_users_friend_request = FriendshipRequest.objects.create(
            from_user=self.user3, to_user=self.user2
        )
        url = reverse(
            'friendships:reject_friendship_request', 
            args=(not_users_friend_request.id,)
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 403)

        self.client.force_login(self.user2)
        url = reverse(
            'friendships:reject_friendship_request', 
            args=(self.friend_request.id,)
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 403)


class FriendshipUserModelTest(TransactionTestCase):
    def setUp(self):
        self.user1 = FriendshipUser.objects.create(username='user1')
        self.user2 = FriendshipUser.objects.create(username='user2')

    def test_are_friends(self):
        self.assertFalse(self.user1.are_friends(self.user2))
        self.assertFalse(self.user2.are_friends(self.user1))
        Friend.objects.create(from_user=self.user1, to_user=self.user2)
        self.assertTrue(self.user1.are_friends(self.user2))
        self.assertTrue(self.user2.are_friends(self.user1))

    def test_add_friend(self):
        self.user1.add_friend(self.user2)

        try:
            FriendshipRequest.objects.get(
                from_user=self.user1, to_user=self.user2
            )
        except FriendshipRequest.DoesNotExist:
            self.fail()

        with self.assertRaises(FriendshipRequest.AlreadyExists):
            self.user1.add_friend(self.user2)

        Friend.objects.create(from_user=self.user1, to_user=self.user2)

        with self.assertRaises(Friend.AlreadyExists):
            self.user1.add_friend(self.user2)

    def test_remove_friend(self):
        Friend.objects.create(from_user=self.user1, to_user=self.user2)
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


class FriendshipRequestModelTest(TransactionTestCase):
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
