# PR2018-04-01
# This doesnt't work in django 2 any more:
# from django.core.urlresolvers import reverse
# changed to: from django.urls import reverse
# PR2018-04-14
#reverse(viewname, urlconf=None, args=None, kwargs=None, current_app=None)

"""
from django.urls import reverse
from django.test import TestCase
from django.urls import resolve

from ..models import Board
from ..views import home


# PR2018-03-18 DeprecationWarning: assertEquals will be deprecated, please use assertEqual instead.
class HomeTests(TestCase):
    # PR2018-03-10
    def setUp(self):
        self.board = Board.objects.create(name='Django', description='Django board.')
        url = reverse('home')
        self.response = self.client.get(url)

    def test_home_view_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_home_url_resolves_home_view(self):
        view = resolve('/')
        self.assertEqual(view.func, home)
# PR2018-04-11
#    def test_home_view_contains_link_to_topics_page(self):
#        board_topics_url = reverse('board_topics', kwargs={'pk': self.board.pk})
#        self.assertContains(self.response, 'href="{0}"'.format(board_topics_url))

        #file = open('logfile.txt', 'a')
        #file.write('\ntest_home_view_contains_link_to_topics_page:\n')
        #c = Board.objects.count()
        #first_board = Board.objects.all().first()
        #file.write('Count boards: ' + str(c) + '\n')
        #file.write('first_board: ' + str(first_board.id) + ' - ' +  first_board.name + '\n')
        #file.write('board_topics_url: ' + board_topics_url + '\n')
        #file.write('response: ' +  str(self.response.status_code) + '\n')
        #file.close()

"""