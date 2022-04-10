from datetime import timedelta
from itertools import product
from time import sleep
from venv import create

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.forms.models import model_to_dict
from django.test import TestCase, TransactionTestCase
from django.utils import timezone
from django.urls import reverse

from .models import Task, TaskNotification, TaskShare
from friendships.models import Friend


user_model = get_user_model()


def create_test_task(
        *, 
        title="Test title", 
        author, 
        comment="Test comment",
        expire_date=timezone.now()+timedelta(minutes=15)
):
    return Task.objects.create(
        title=title,
        author=author,
        comment=comment,
        expire_date=expire_date
    )   


def create_test_friend(*, user):
    user_friend = user_model.objects.create(username='testfriend')
    Friend.objects.create(from_user=user_friend, to_user=user)
    return user_friend


def create_test_notification(*, task, dt_before_expire=timedelta(minutes=1)):
    return TaskNotification.objects.create(
        task=task,
        dt_before_expire=dt_before_expire
    )


class TaskIndexViewTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create(username='testuser')
        self.client.force_login(self.user)

    def test_url(self):
        response = self.client.get('/tasks/')
        self.assertEqual(response.status_code, 200)

    def test_url_name(self):
        response = self.client.get(reverse('tasks:index'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('tasks:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tasks/index.html')

    def test_login_required(self):
        self.client.logout()
        response = self.client.get(reverse('tasks.index'), follow=True)
        self.assertEqual(response.request['PATH_INFO'], reverse('login'))


class TaskCreateViewTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create(username='testuser')
        self.client.force_login(self.user)
        self.create_form = {
            'title': 'Test title',
            'author': self.user,
            'comment': 'Test comment',
            'expire_date': timezone.now() + timedelta(minutes=15)
        }

    def test_url(self):
        response = self.client.get('/tasks/new/')
        self.assertEqual(response.status_code, 200)

    def test_url_name(self):
        response = self.client.get(reverse('tasks:create'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('tasks:create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tasks/create.html')

    def test_view_creates_task_and_redirects(self):
        response = self.client.post(reverse('tasks:create'), self.create_form)
        self.assertEqual(response.status_code, 302)
        new_task = Task.objects.last()
        self.assertEqual(new_task.title, self.create_form['title'])
        self.assertEqual(new_task.author, self.create_form['author'])
        self.assertEqual(new_task.comment, self.create_form['comment'])
        self.assertEqual(new_task.expire_date, self.create_form['expire_date'])

    def test_login_required(self):
        self.client.logout()
        response = self.client.post(
            reverse('tasks:create'), self.create_form, follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request['PATH_INFO'], reverse('login'))


class TaskRepeatViewTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create(username='testuser')
        self.client.force_login(self.user)
        self.task = create_test_task(author=self.user)
        self.task.done = True
        self.task.save()

    def test_url(self):
        response = self.client.get(f'/tasks/{self.task.id}/repeat/')
        self.assertEqual(response.status_code, 200)

    def test_url_name(self):
        url = reverse('tasks:repeat', args=(self.task.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        url = reverse('tasks:repeat', args=(self.task.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tasks/repeat.html')
        
    def test_view_form_initial_data(self):
        url = reverse('tasks:repeat', args=(self.task.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        initial_data = response.context['form'].initial
        object_dict = model_to_dict(self.task)
        object_form_fields = {k: object_dict[k] for k in initial_data}
        self.assertEqual(object_form_fields, initial_data)

    def test_view_creates_task(self):
        url = reverse('tasks:repeat', args=(self.task.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        initial_data = response.context['form'].initial
        response = self.client.post(url, initial_data)
        self.assertEqual(response.status_code, 302)
        new_task = Task.objects.last()
        self.assertEqual(new_task.title, self.task.title)
        self.assertEqual(new_task.comment, self.task.comment)
        self.assertEqual(new_task.expire_date, self.task.expire_date)

    def test_forbidden_for_active_task(self):
        task = create_test_task(author=self.user)
        url = reverse('tasks:repeat', args=(task.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
        
    def test_login_required(self):
        self.client.logout()
        url = reverse('tasks:repeat', args=(self.task.id,))
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request['PATH_INFO'], reverse('login'))

    def test_no_permission_for_non_author(self):
        self.client.logout()
        user = get_user_model().objects.create(username='notauthor')
        self.client.force_login(user)
        url = reverse('tasks:repeat', args=(self.task.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)


class TaskUpdateViewTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create(username='testuser')
        self.client.force_login(self.user)
        self.task = create_test_task(author=self.user)
        self.update_form = {
            'title': 'New test title',
            'comment': 'New test comment',
            'expire_date': timezone.now() + timedelta(minutes=30)
        }

    def test_url(self):
        response = self.client.get(f'/tasks/{self.task.id}/edit/')
        self.assertEqual(response.status_code, 200)

    def test_url_name(self):
        url = reverse('tasks:update', args=(self.task.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        url = reverse('tasks:update', args=(self.task.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tasks/update.html')

    def test_view_updates_task_and_redirects(self):
        url = reverse('tasks:update', args=(self.task.id,))
        response = self.client.post(url, self.update_form)
        self.assertEqual(response.status_code, 302)
        new_task = Task.objects.last()
        self.assertEqual(new_task.title, self.update_form['title'])
        self.assertEqual(new_task.comment, self.update_form['comment'])
        self.assertEqual(new_task.expire_date, self.update_form['expire_date'])

    def test_login_required(self):
        url = reverse('tasks:update', args=(self.task.id,))
        self.client.logout()
        response = self.client.post(url, self.update_form, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request['PATH_INFO'], reverse('login'))

    def test_no_permission_for_non_author(self):
        url = reverse('tasks:update', args=(self.task.id,))
        self.client.logout()
        user = get_user_model().objects.create(username='notauthor')
        self.client.force_login(user)
        response = self.client.post(url, self.update_form)
        self.assertEqual(response.status_code, 403)


class TaskDeleteViewTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create(username='testuser')
        self.client.force_login(self.user)
        self.task = create_test_task(author=self.user)

    def test_url(self):
        response = self.client.get(f'/tasks/{self.task.id}/delete/')
        self.assertEqual(response.status_code, 200)

    def test_url_name(self):
        url = reverse('tasks:delete', args=(self.task.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        url = reverse('tasks:delete', args=(self.task.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tasks/delete.html')

    def test_view_deletes_task_and_redirects(self):
        url = reverse('tasks:delete', args=(self.task.id,))
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertQuerysetEqual(Task.objects.all(), [])

    def test_login_required(self):
        url = reverse('tasks:delete', args=(self.task.id,))
        self.client.logout()
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request['PATH_INFO'], reverse('login'))

    def test_no_permission_for_non_author(self):
        url = reverse('tasks:delete', args=(self.task.id,))
        self.client.logout()
        user = get_user_model().objects.create(username='notauthor')
        self.client.force_login(user)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 403)


class TaskDoneViewTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create(username='testuser')
        self.client.force_login(self.user)

    def test_url(self):
        task = create_test_task(author=self.user)
        response = self.client.post(f'/tasks/{task.id}/done/')
        self.assertEqual(response.status_code, 302)

    def test_url_name(self):
        task = create_test_task(author=self.user)
        response = self.client.post(reverse('tasks:done', args=(task.id,)))
        self.assertEqual(response.status_code, 302)

    def test_view_makes_task_done(self):
        task = create_test_task(author=self.user)
        response = self.client.post(reverse('tasks:done', args=(task.id,)))
        self.assertEqual(response.status_code, 302)
        task.refresh_from_db()
        self.assertTrue(task.done)

    def test_login_required(self):
        self.client.logout()
        task = create_test_task(author=self.user)
        url = reverse('tasks:done', args=(task.id,))
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request['PATH_INFO'], reverse('login'))

    def test_no_permission_for_non_author(self):
        self.client.logout()
        user = get_user_model().objects.create(username='notauthor')
        self.client.force_login(user)
        task = create_test_task(author=self.user)
        response = self.client.post(reverse('tasks:done', args=(task.id,)))
        self.assertEqual(response.status_code, 403)


class TaskShareCreateViewTest(TransactionTestCase):
    def setUp(self):
        self.user = get_user_model().objects.create(username='testuser')
        self.client.force_login(self.author)
        self.friend = create_test_friend(user=self.user)
        self.task = create_test_task(author=self.user)
        self.create_form = {
            'to_username': self.friend.username
        }

    def test_url(self):
        response = self.client.get(f'/tasks/{self.task.id}/shares/new/')
        self.assertEqual(response.status_code, 200)

    def test_url_name(self):
        url = reverse('tasks:share_create', args=(self.task.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_use_correct_template(self):
        url = reverse('tasks:share_create', args=(self.task.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tasks/task_share_create.html')

    def test_create_task_share(self):
        url = reverse('tasks:share_create', args=(self.task.id,))
        response = self.client.post(url, self.create_form)
        self.assertEqual(response.status_code, 302)
        new_task_share = TaskShare.objects.last()
        self.assertEqual(new_task_share.task, self.task)
        self.assertEqual(new_task_share.to_user, self.friend)

    def test_allowed_to_share_only_with_friend(self):
        not_friend = user_model.objects.create(username='notfriend')
        url = reverse('tasks:share_create', args=(self.task.id,))
        response = self.client.post(url, {'to_username': not_friend.username})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'You can only share tasks with friends')

    def test_allowed_to_share_only_own_or_shared_tasks(self):
        some_other_user = user_model.objects.create(username='someuser')
        task = create_test_task(author=some_other_user)
        url = reverse('tasks:share_create', args=(task.id,))
        response = self.client.post(url, {'to_username': self.friend.username})
        self.assertEqual(response.status_code, 405)
        TaskShare.objects.create(task=task, from_user=some_other_user, to_user=self.user)
        response = self.client.post(url, {'to_username': self.friend.username})
        self.assertEqual(response.status_code, 200)

    def test_login_required(self):
        self.client.logout()
        url = reverse('tasks:share_create', args=(self.task.id,))
        response = self.client.post(url, self.create_form, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request['PATH_INFO'], reverse('login'))


class TaskModelTest(TestCase):
    def setUp(self):
        self.author = get_user_model().objects.create(username='testuser')

    def test_str_repr(self):
        task = create_test_task(author=self.author)
        self.assertEqual(str(task), task.title)

    def test_content(self):
        create_test_task(author=self.author, expire_date=None)
        task = Task.objects.last()
        self.assertEqual(task.title, "Test title")
        self.assertEqual(task.author, self.author)
        self.assertEqual(task.comment, "Test comment")
        self.assertEqual(task.expire_date, None)
        self.assertEqual(task.done, False)

    def test_create_task_with_past_expire_date(self):
        past_date = timezone.now() - timedelta(seconds=1)
        with self.assertRaises(ValidationError):
            create_test_task(author=self.author, expire_date=past_date)

    def test_failed_property(self):
        expire_date = timezone.now() + timedelta(seconds=1)
        task = create_test_task(author=self.author, expire_date=expire_date)
        sleep(2.01)
        self.assertTrue(task.failed)

    def test_active_property(self):
        expire_date = timezone.now() + timedelta(minutes=30)
        task = create_test_task(author=self.author)
        combs = zip(
            product((True, False), (expire_date, None)), 
            [False, False, True, True]
        )
        for (done, expire_date), answer in combs:
            task.done = done
            task.expire_date = expire_date
            self.assertEqual(task.active, answer)


class TaskShareModelTest(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create(username='author')
        self.others = [
            user_model.objects.create(username=f'testuser{i}')
            for i in range(1, 5)
        ]
        self.task = create_test_task(author=self.user)

    def test_str(self):
        user = self.others[0]
        share = TaskShare.objects.create(
            task=self.task,
            from_user=self.user,
            to_user=user
        )
        self.assertEqual(
            str(share), f'{self.user} shares {self.task} with {user}'
        )

    def test_clean(self):
        with self.assertRaises(ValidationError):
            TaskShare.objects.create(
            task=self.task,
            from_user=self.user,
            to_user=self.user
        )
        with self.assertRaises(ValidationError):
            TaskShare.objects.create(
            task=self.task,
            from_user=self.others[0],
            to_user=self.task.author
        )
        TaskShare.objects.create(
            task=self.task,
            from_user=self.task.author,
            to_user=self.others[0]
        )

    def test_save(self):
        task_share = TaskShare(
            task=self.task,
            from_user=self.user,
            to_user=self.others[0]
        )
        task_share.save()

    def test_authors_cant_share_with_themselves(self):
        with self.assertRaises(ValidationError):
            TaskShare.objects.create(
                task=self.task,
                from_user=self.task.author,
                to_user=self.task.author
            )

    def test_user_with_task_share_backward_relationship(self):
        tasks = [create_test_task(author=user) for user in self.others]
        task_shares = [
            TaskShare.objects.create(
                task=task, from_user=task.author, to_user=self.user
            ) for task in tasks
        ]
        self.assertQuerysetEqual(
            self.user.task_shares.all(), task_shares, ordered=False
        )

    def test_task_with_task_share_backward_relationship(self):
        task_shares = [
            TaskShare.objects.create(
                task=self.task, from_user=self.user, to_user=user
            ) for user in self.others
        ]
        self.assertQuerysetEqual(
            self.task.shares.all(), task_shares, ordered=False
        )


class TaskNotificationModelTest(TestCase):
    def setUp(self):
        self.author = get_user_model().objects.create(username='testuser')
    
    def test_str_repr(self):
        task = create_test_task(author=self.author)
        notification = create_test_notification(task=task)
        self.assertEqual(
            str(notification), 
            f'{notification.dt_before_expire} before {task.expire_date}'
        )

    def test_add_notification(self):
        task = create_test_task(author=self.author)
        create_test_notification(
            task=task,
            dt_before_expire=timedelta(minutes=5)
        )
        notification = TaskNotification.objects.last()
        self.assertEqual(notification.task, task)
        self.assertEqual(
            notification.dt_before_expire, timedelta(minutes=5)
        )

    def test_add_notification_to_task_with_no_expire_date(self):
        task = create_test_task(author=self.author, expire_date=None)
        with self.assertRaises(ValidationError):
            create_test_notification(task=task)
