"""

# PR2018-04-01
# This doesnt't work in django 2 any more:
# from django.core.urlresolvers import reverse
# changed to
from django.urls import reverse

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import resolve

from ..forms import NewTopicForm
from ..models import Board, Post, Topic
from ..views import new_topic


class NewTopicTests(TestCase):
    def setUp(self):
        Board.objects.create(name='Django', description='Django board.')
        User.objects.create_user(username='john', email='john@doe.com', password='123')
        self.client.login(username='john', password='123')

    def test_new_topic_view_success_status_code(self):
        # PR2018-03-10 use first_board.id instead of kwargs={'pk': 1}, 1 might not refer to the current board
        # url = reverse('new_topic', kwargs={'pk': 1})
        first_board = Board.objects.all().first()
        url = reverse('new_topic', kwargs={'pk': first_board.id})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_new_topic_view_not_found_status_code(self):
        url = reverse('new_topic', kwargs={'pk': 99})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_new_topic_url_resolves_new_topic_view(self):
        view = resolve('/boards/1/new/')
        self.assertEquals(view.func, new_topic)

    def test_new_topic_view_contains_link_back_to_board_topics_view(self):
        # PR2018-03-10 use first_board.id instead of kwargs={'pk': 1}, 1 might not refer to the current board
        first_board = Board.objects.all().first()
        # new_topic_url = reverse('new_topic', kwargs={'pk': 1})
        new_topic_url = reverse('new_topic', kwargs={'pk': first_board.id})
        # board_topics_url = reverse('board_topics', kwargs={'pk': 1})
        board_topics_url = reverse('board_topics', kwargs={'pk': first_board.id})
        response = self.client.get(new_topic_url)
        self.assertContains(response, 'href="{0}"'.format(board_topics_url))

    def test_csrf(self):
        # PR2018-04-01 use first_board.id instead of kwargs={'pk': 1}, 1 might not refer to the current board
        first_board = Board.objects.all().first()
        # PR2018-04-01 was: url = reverse('new_topic', kwargs={'pk': 1})
        url = reverse('new_topic', kwargs={'pk': first_board.id})
        response = self.client.get(url)
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_contains_form(self):
        # PR2018-04-01 use first_board.id instead of kwargs={'pk': 1}, 1 might not refer to the current board
        first_board = Board.objects.all().first()
        # PR2018-04-01 was: url = reverse('new_topic', kwargs={'pk': 1})
        url = reverse('new_topic', kwargs={'pk': first_board.id})
        response = self.client.get(url)
        form = response.context.get('form')
        self.assertIsInstance(form, NewTopicForm)

    def test_contains_form(self):  # <- new test
        first_board = Board.objects.all().first()
        url = reverse('new_topic', kwargs={'pk': first_board.id})
        response = self.client.get(url)
        form = response.context.get('form')
        self.assertIsInstance(form, NewTopicForm)

    def test_new_topic_valid_post_data(self):
        # PR2018-04-01 use first_board.id instead of kwargs={'pk': 1}, 1 might not refer to the current board
        first_board = Board.objects.all().first()
        # PR2018-04-01 was: url = reverse('new_topic', kwargs={'pk': 1})
        url = reverse('new_topic', kwargs={'pk': first_board.id})
        data = {
            'subject': 'Test title',
            'message': 'Lorem ipsum dolor sit amet'
        }
        self.client.post(url, data)
        self.assertTrue(Topic.objects.exists())
        self.assertTrue(Post.objects.exists())

    def test_new_topic_invalid_post_data(self):
        '''
        Invalid post data should not redirect
        The expected behavior is to show the form again with validation errors
        '''
        # PR2018-04-01 use first_board.id instead of kwargs={'pk': 1}, 1 might not refer to the current board
        first_board = Board.objects.all().first()
        # PR2018-04-01 was: url = reverse('new_topic', kwargs={'pk': 1})
        url = reverse('new_topic', kwargs={'pk': first_board.id})
        response = self.client.post(url, {})
        form = response.context.get('form')
        self.assertEquals(response.status_code, 200)
        self.assertTrue(form.errors)

    def test_new_topic_invalid_post_data_empty_fields(self):
        '''
        Invalid post data should not redirect
        The expected behavior is to show the form again with validation errors
        '''
        # PR2018-04-01 use first_board.id instead of kwargs={'pk': 1}, 1 might not refer to the current board
        first_board = Board.objects.all().first()
        # PR2018-04-01 was: url = reverse('new_topic', kwargs={'pk': 1})
        url = reverse('new_topic', kwargs={'pk': first_board.id})
        data = {
            'subject': '',
            'message': ''
        }
        response = self.client.post(url, data)
        self.assertEquals(response.status_code, 200)
        self.assertFalse(Topic.objects.exists())
        self.assertFalse(Post.objects.exists())

"""