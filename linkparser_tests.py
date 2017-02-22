import unittest
from linkparser import LinkParser


# Class to test the parser for the 'link' meta information returned
# with the GitHub response.
class TestLinksParser(unittest.TestCase):

    def test_empty_string(self):
        lp = LinkParser("")
        self.assertEqual(lp.get_link('next'), '')
        self.assertEqual(lp.get_link('prev'), '')
        self.assertEqual(lp.get_link('last'), '')
        self.assertEqual(lp.get_link('first'), '')

    def test_all_links(self):
        link = '<https://api.github.com/organizations/913567/repos?page=3>; rel="next", <https://api.github.com/organizations/913567/repos?page=5>; rel="last", <https://api.github.com/organizations/913567/repos?page=1>; rel="first", <https://api.github.com/organizations/913567/repos?page=1>; rel="prev"'
        lp = LinkParser(link)
        self.assertEqual(lp.get_link('next'), 'https://api.github.com/organizations/913567/repos?page=3')
        self.assertEqual(lp.get_link('last'), 'https://api.github.com/organizations/913567/repos?page=5')
        self.assertEqual(lp.get_link('prev'), 'https://api.github.com/organizations/913567/repos?page=1')
        self.assertEqual(lp.get_link('first'), 'https://api.github.com/organizations/913567/repos?page=1')

    def test_mal_formed_link_missing_open_angle_bracket(self):
        link = 'https://api.github.com/organizations/913567/repos?page=3>; rel="next"'
        lp = LinkParser(link)
        self.assertEqual(lp.get_link('next'), '')

    def test_mal_formed_link_missing_close_angle_bracket(self):
        link = '<https://api.github.com/organizations/913567/repos?page=3; rel="next"'
        lp = LinkParser(link)
        self.assertEqual(lp.get_link('next'), '')

    def test_mal_formed_link_missin_equal(self):
        link = '<https://api.github.com/organizations/913567/repos?page=3>; rel~"next"'
        lp = LinkParser(link)
        self.assertEqual(lp.get_link('next'), '')


if __name__ == '__main__':
    unittest.main()