import os
import tempfile
import unittest

from web_scraper import FlashscoreWebScraper
from unittest.mock import patch, MagicMock


class TestFlashscoreWebScraperUnit(unittest.TestCase):
    def setUp(self):
        self.scraper = FlashscoreWebScraper.__new__(FlashscoreWebScraper)
        self.scraper.flashscore_url = "https://www.flashscore.ro/"
        self.scraper.flashscore_url_no_slash = "https://www.flashscore.ro"
        self.scraper.page = MagicMock()

        self.team_name = "Romania"
        self.match = {
            "home_team": "Romania",
            "away_team": "Franta",
            "start_time": "32.06. 20:00",
            "match_url": "https://www.flashscore.ro/meci/fotbal/romania-abc/franta-def/?mid=ghi"
        }

        self.statistics = {
            "TOP STATISTICI": {
                "Goluri asteptate (xG)": {
                    "home": "0",
                    "away": "10"
                }
            }
        }

    def test_reset_page(self):
        self.scraper.reset_page()
        self.scraper.page.goto.assert_called_once_with(self.scraper.flashscore_url)

    def test_navigation_to_team_page(self):
        #Capul verde
        test_url = "https://www.flashscore.ro/echipa/capul-verde/MocyWdm7/"
        team_url = "echipa/capul-verde/MocyWdm7/"

        self.scraper.navigate_to_team_page(team_url)
        self.scraper.page.goto.assert_called_once_with(test_url)

    def test_navigation_to_results_page(self):
        #Capul verde
        test_url = "https://www.flashscore.ro/echipa/capul-verde/MocyWdm7/rezultate/"

        mock_element = MagicMock()
        mock_element.get_attribute.return_value = "/echipa/capul-verde/MocyWdm7/rezultate/"
        self.scraper.page.query_selector.return_value = mock_element

        self.scraper.navigate_to_results_page()

        self.scraper.page.goto.assert_called_once_with(test_url)

    def test_navigation_to_match_page(self):
        #Capul verde cu spania
        match_url = "https://www.flashscore.ro/meci/fotbal/capul-verde-MocyWdm7/spania-bLyo6mco/?mid=Iiqjm5Pq"

        self.scraper.navigate_to_match_page(match_url)
        self.scraper.page.goto.assert_called_once_with(match_url)

    def test_navigation_to_statistics_tab(self):
        # Capul verde cu spania
        expected_result = "https://www.flashscore.ro/meci/fotbal/capul-verde-MocyWdm7/spania-bLyo6mco/sumar/statistici/?mid=Iiqjm5Pq"

        mock_element = MagicMock()
        mock_button = MagicMock()

        mock_button.get_attribute.return_value = "/meci/fotbal/capul-verde-MocyWdm7/spania-bLyo6mco/sumar/statistici/?mid=Iiqjm5Pq"
        mock_element = [None, mock_button]

        self.scraper.page.query_selector_all.return_value = mock_element

        self.scraper.navigate_to_statistics_tab()
        self.scraper.page.goto.assert_called_once_with(expected_result)

    def test_create_directory(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            with patch("os.makedirs") as mock_makedirs:
                with patch("builtins.open", unittest.mock.mock_open()) as mock_file:
                    self.scraper.write_to_file(self.team_name, self.match, self.statistics)

                    mock_makedirs.assert_called_once_with(f"output/{self.team_name}", exist_ok=True)

                    mock_file.assert_called_once()

    def test_write_correct_content(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            original_dir = os.getcwd()
            os.chdir(tmp_dir)

            try:
                self.scraper.write_to_file(self.team_name, self.match, self.statistics)

                expected_path = (f"output/{self.team_name}/{self.match['home_team']}"
                                 f"-{self.match['away_team']}|{self.match['start_time'].replace(' ', '-')}")
                self.assertTrue(os.path.exists(expected_path))

                with open(expected_path, "r") as f:
                    content = f.read()

                # verificam categoriile
                for category in self.statistics.keys():
                    self.assertIn(category, content)

                # verificam statisticile
                for category, stats in self.statistics.items():
                    for stat_name, values in stats.items():
                        self.assertIn(stat_name, content)
                        self.assertIn(f"{values['home']} | {values['away']}", content)

            finally:
                os.chdir(original_dir)

if __name__ == "__main__":
    unittest.main()


