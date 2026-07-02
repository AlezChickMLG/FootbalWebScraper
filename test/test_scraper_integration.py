import unittest

from web_scraper import FlashscoreWebScraper
import pytest

class TestIntegrationWebScraper(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scraper = FlashscoreWebScraper()

    @classmethod
    def tearDownClass(cls):
        cls.scraper.browser.close()
        cls.scraper.sync_playwright.stop()

    def setUp(self):
        self.scraper.reset_page()
        self.test_team = "Spania"

    def test_get_team_url_correct(self):
        expected_url = "bLyo6mco"

        url = self.scraper.get_team_url(self.test_team)
        self.assertIsNotNone(url)
        self.assertIn(expected_url, url)

    def test_get_team_url_no_search_results(self):
        url = self.scraper.get_team_url("Cimpanzeii")
        self.assertFalse(url)

    def test_get_team_url_wrong_spelling(self):
        url = self.scraper.get_team_url("Span")
        self.assertIsNone(url)

    def test_navigate_to_team_page(self):
        expected_url = "https://www.flashscore.ro/echipa/spania/bLyo6mco/"

        team_url = self.scraper.get_team_url(self.test_team)
        self.scraper.navigate_to_team_page(team_url)

        self.assertEqual(expected_url, self.scraper.page.url)

    def test_navigate_to_team_results(self):
        expected_url = "https://www.flashscore.ro/echipa/spania/bLyo6mco/rezultate/"

        team_url = self.scraper.get_team_url(self.test_team)
        self.scraper.navigate_to_team_page(team_url)

        try:
            self.scraper.page.wait_for_selector("a.tabs__tab[title='Rezultate']")
            print("A aparut tabul de rezultate", flush=True)
        except Exception as e:
            print("A expirat timeout-ul", flush=True)

        self.scraper.navigate_to_results_page()

        self.assertEqual(expected_url, self.scraper.page.url)

    def test_navigate_to_match(self):
        expected_url = "https://www.flashscore.ro/meci/fotbal/spania-bLyo6mco/uruguay-xMk44orG/?mid=8xM154oS"

        team_url = self.scraper.get_team_url(self.test_team)
        self.scraper.navigate_to_team_page(team_url)

        try:
            self.scraper.page.wait_for_selector("a.tabs__tab[title='Rezultate']")
            print("A aparut tabul de rezultate", flush=True)
        except Exception as e:
            print("A expirat timeout-ul", flush=True)

        self.scraper.navigate_to_results_page()
        self.scraper.navigate_to_match_page(expected_url)

        self.assertEqual(expected_url, self.scraper.page.url)

    def test_navigate_to_match_statistics(self):
        expected_url = "https://www.flashscore.ro/meci/fotbal/spania-bLyo6mco/uruguay-xMk44orG/sumar/statistici/total/?mid=8xM154oS"
        match_url = "https://www.flashscore.ro/meci/fotbal/spania-bLyo6mco/uruguay-xMk44orG/?mid=8xM154oS"

        team_url = self.scraper.get_team_url(self.test_team)
        self.scraper.navigate_to_team_page(team_url)

        try:
            self.scraper.page.wait_for_selector("a.tabs__tab[title='Rezultate']")
            print("A aparut tabul de rezultate", flush=True)
        except Exception as e:
            print("A expirat timeout-ul", flush=True)

        self.scraper.navigate_to_results_page()
        self.scraper.navigate_to_match_page(match_url)
        self.scraper.navigate_to_statistics_tab()

        self.assertEqual(expected_url, self.scraper.page.url)

    '''Helper functions'''
    def navigate_to_team_page_results(self):
        team_url = self.scraper.get_team_url(self.test_team)

        self.scraper.navigate_to_team_page(team_url)

        try:
            self.scraper.page.wait_for_selector("a.tabs__tab[title='Rezultate']")
        except Exception as e:
            print("A expirat timeout-ul")

        self.scraper.navigate_to_results_page()

    def navigate_to_match_statistics(self):
        self.navigate_to_team_page_results()

        match_url = "https://www.flashscore.ro/meci/fotbal/spania-bLyo6mco/uruguay-xMk44orG/?mid=8xM154oS"
        self.scraper.navigate_to_match_page(match_url)

        self.scraper.navigate_to_statistics_tab()
    '''Helper functions'''

    def test_get_all_matches_correct(self):
        self.navigate_to_team_page_results()

        all_matches = self.scraper.get_all_matches()
        self.assertIsNotNone(all_matches)
        self.assertGreater(len(all_matches), 0)

        for match in all_matches:
            self.assertIsInstance(match, dict)
            self.assertIn("home_team", match)
            self.assertIn("away_team", match)
            self.assertIn("match_url", match)
            self.assertIn("start_time", match)

    def test_get_all_statistics_correct(self):
        self.navigate_to_match_statistics()
        statistics = self.scraper.get_statistics()

        self.assertIsNotNone(statistics)
        self.assertIsInstance(statistics, dict)
        self.assertGreater(len(statistics), 0)

if __name__ == "__main__":
    unittest.main()
