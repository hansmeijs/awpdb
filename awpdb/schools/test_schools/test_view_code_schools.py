"""

# PR2018-04-01
# This doesnt't work in django 2 any more:
# from django.core.urlresolvers import reverse
# changed to
from django.urls import reverse
from django.test import TestCase
from django.urls import resolve

from ..models import Board
from ..views import board_topics


class BoardTopicsTests(TestCase):
    def setUp(self):
        Board.objects.create(name='Django', description='Django board.')

    def test_board_topics_view_success_status_code(self):
        # PR2018-04-01 use first_board.id instead of kwargs={'pk': 1}, 1 might not refer to the current board
        first_board = Board.objects.all().first()
        # PR2018-04-01 was: url = reverse('board_topics', kwargs={'pk': 1})
        url = reverse('board_topics', kwargs={'pk': first_board.id})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_board_topics_view_not_found_status_code(self):
        url = reverse('board_topics', kwargs={'pk': 99})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_board_topics_url_resolves_board_topics_view(self):
        # PR2018-04-01 this one works, first_board not needed
        view = resolve('/boards/1/')
        self.assertEquals(view.func, board_topics)

    def test_board_topics_view_contains_navigation_links(self):
        # PR2018-04-01 use first_board.id instead of kwargs={'pk': 1}, 1 might not refer to the current board
        first_board = Board.objects.all().first()

        #file = open('logfile.txt', 'a')
        #file.write('\ntest_board_topics_view_contains_navigation_links:\n')
        #c = Board.objects.count()
        #file.write('Count boards: ' + str(c) + '\n')
        #file.write('first_board: ' + str(first_board.id) + ' - ' +  first_board.name + '\n')
        # log: Count boards: 1
        # log: first_board: 2 - Django

        # PR2018-04-01 was: board_topics_url = reverse('board_topics', kwargs={'pk': 1})
        board_topics_url = reverse('board_topics', kwargs={'pk': first_board.id})
        # file.write('board_topics_url: ' + board_topics_url + '\n')
        # log: board_topics_url: /boards/2/

        homepage_url = reverse('home')
        #file.write('homepage_url: ' + homepage_url + '\n')
        # log:  homepage_url: /

        new_topic_url = reverse('new_topic', kwargs={'pk': first_board.id}) # was: new_topic_url = reverse('new_topic', kwargs={'pk': 1})
        # file.write('new_topic_url: ' + new_topic_url + '\n')
        # log: new_topic_url: / boards / 2 / new /

        response = self.client.get(board_topics_url)

        #hm = 'href="{0}"'.format(homepage_url)
        ##nw = 'href="{0}"'.format(new_topic_url)
        #file.write('response: ' +  hm + '\n')
        #file.write('response: ' +  nw + '\n')
        # file.close()
        # log: response: href = "/"
        # log: response: href = "/boards/2/new/"

        self.assertContains(response, 'href="{0}"'.format(homepage_url))
        self.assertContains(response, 'href="{0}"'.format(new_topic_url))


"""

