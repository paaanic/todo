from datetime import timedelta
from time import sleep

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Task, TaskNotification


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


def create_test_notification(*, task, dt_before_expire=timedelta(minutes=1)):
    return TaskNotification.objects.create(
        task=task,
        dt_before_expire=dt_before_expire
    )


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
        task = create_test_task(author=self.author, expire_date=expire_date)
        self.assertTrue(task.active)
        task.done = True
        self.assertFalse(task.active)
        task.done = False
        task.expire_date = None
        self.assertTrue(task.active)


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
