import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import os
import traceback
from request_component import RequestComponent
from pprint import pprint
from playwright._impl._errors import TimeoutError as PlaywrightTimeoutError

class FlashscoreWebScraper:
    def __init__(self, headless=True):
        self.sync_playwright = sync_playwright().start()
        self.browser = self.sync_playwright.chromium.launch(
            headless=headless,
        )
        self.context = self.browser.new_context()
        self.page = self.context.new_page()

        self.flashscore_url = "https://www.flashscore.ro/"
        self.flashscore_url_no_slash = "https://www.flashscore.ro"

        #Incarcare pagina principala
        self.page.goto(self.flashscore_url)
        print("Pagina incarcatata")

        #Acceptare cookie-uri
        self.page.wait_for_selector("#onetrust-accept-btn-handler")
        self.page.click("#onetrust-accept-btn-handler")
        print("Am apasat pe butonul de cookies")

        #componenta care primeste cereri
        self.request_component = RequestComponent()

    def reset_page(self):
        self.page.goto(self.flashscore_url)

    #Intoarce toate echipele recomandate de bara de cautare
    def get_team_url(self, team_name):
        try:
            self.page.click("#search-window")
            print("Am apasat pe buton de cautare pentru a deschide meniul")

            self.page.wait_for_selector(".searchInput__input")
            self.page.fill(".searchInput__input", team_name)
            print(f"Am introdus {team_name} la cautare")

            self.page.wait_for_selector(".searchResult", timeout=10000)
            search_result = self.page.query_selector_all(".searchResult")

            for result in search_result:
                name = result.query_selector(".searchResult__participantName").inner_text()
                # category = result.query_selector(".searchResult__participantCategory").inner_text()
                href = result.get_attribute("href")

                print(f"Checking {name}")

                if name.strip().lower() == team_name.strip().lower():
                    return href

            return None
        except PlaywrightTimeoutError as e:
            print(f"Nu au fost gasite echipe sub denumirea de {team_name}")
            return False

        except Exception as e:
            print(f"Eroare intampinata la gasirea echipei {team_name}")
            return False

    def get_all_matches(self, time_limit=None):
        try:
            all_matches = self.page.query_selector_all(".event__match")
            matches_dict = []

            print(f"Numarul de meciuri: {len(all_matches)}")

            for match in all_matches:
                home_team_element = match.query_selector(".event__homeParticipant span")
                away_team_element = match.query_selector(".event__awayParticipant span")
                start_time_element = match.query_selector(".event__time")
                match_url_element = match.query_selector(".eventRowLink")

                if not match_url_element:
                    continue

                match_url = match_url_element.get_attribute("href")

                match_dict = {
                    "match_url" : match_url
                }

                if home_team_element:
                    home_team = home_team_element.inner_text()
                    match_dict["home_team"] = home_team

                if away_team_element:
                    away_team = away_team_element.inner_text()
                    match_dict["away_team"] = away_team

                if start_time_element:
                    start_time = start_time_element.inner_text()
                    match_dict["start_time"] = start_time

                matches_dict.append(match_dict)

            return matches_dict
        except Exception as e:
            print(f"Am intampinat o eroare la gasirea / procesarea meciurilor: {e}")
            traceback.print_exc()

    def get_statistics(self):
        try:
            self.page.wait_for_selector("div[data-testid='wcl-statistics']")
            statistics = self.page.query_selector_all(".section")

            statistics_dict = {}

            if statistics:
                for section in statistics:
                    individual_statistics = section.query_selector_all("div[data-testid='wcl-statistics']")

                    title_name_statistics = section.query_selector(".sectionHeader")

                    if title_name_statistics is None:
                        print("Eroare: nu a fost gasit title_name_statistics")
                        return

                    title_name = title_name_statistics.inner_text()
                    statistics_dict[title_name] = {}

                    if individual_statistics is None:
                        print("Eroare: nu au fost gasite statisticile individuale")
                        return

                    for individual_statistic in individual_statistics:
                        details = individual_statistic.query_selector("div").query_selector_all("div")

                        if details:
                            home_value_element = details[0].query_selector("span")
                            home_value = home_value_element.inner_text()

                            away_value_element = details[2].query_selector("span")
                            away_value = away_value_element.inner_text()

                            statistic_name_element = details[1].query_selector("span")
                            statistic_name = statistic_name_element.inner_text()

                            statistics_dict[title_name][statistic_name] = {
                                "home": home_value,
                                "away": away_value
                            }
                        
                return statistics_dict
        except Exception as e:
            print(f"Am intampinat o eroare la procesarea statisticilor: {e}")
            traceback.print_exc()

    def navigate_to_team_page(self, team_url):
        full_team_url = f"{self.flashscore_url}{team_url}"
        self.page.goto(full_team_url)
        print(f"Am intrat pe pagina echipei")

    def navigate_to_results_page(self):
        results_href_element = self.page.query_selector("a.tabs__tab[title='Rezultate']")
        results_href = results_href_element.get_attribute("href")

        result_url = f"{self.flashscore_url_no_slash}{results_href}"

        self.page.goto(result_url)
        print("Am deschis sectiunea de rezultate")

    def navigate_to_match_page(self, match_url):
        self.page.goto(match_url)
        print("Am intrat pe pagina meciului")

    def navigate_to_statistics_tab(self):
        all_buttons = self.page.query_selector_all(".filterOver div a")
        statistics_button = all_buttons[1]
        button_href = statistics_button.get_attribute("href")
        self.page.goto(f"{self.flashscore_url_no_slash}{button_href}")
        print("Am ajuns pe pagina de statistici")

    def process_info(self, info, limit=10):
        team_name = info["team"]
        print(f"Prelucram echipa {team_name}")

        #mergem inapoi la pagina principala
        self.reset_page()
        print(f"Am resetat pagina")

        #obtine url echipei
        team_url = self.get_team_url(team_name)

        #verificam daca a returnat un link valid
        if team_url is None:
            print(f"Nu am gasit echipa {team_name}")
            return

        elif team_url is not False:
            #navigam catre pagina echipei
            self.navigate_to_team_page(team_url)

            try:
                self.page.wait_for_selector("a.tabs__tab[title='Rezultate']")
            except Exception as e:
                print("A expirat timeout-ul")

            #navigam catre pagina de rezultate
            self.navigate_to_results_page()

            #obtinem toate meciurile
            matches = self.get_all_matches()

            #procesam meciurile
            self.process_matches(matches, limit)

    def process_matches(self, matches, limit):
        for match_index, match in enumerate(matches):
            if match_index >= limit:
                print("Am terminat de procesat statisticile")
                break

            # print(f"Obtinem statisticile pentru meciul {match['home_team']} - {match['away_team']} disputat la data de {match['start_time']}")
            pprint(match)
            self.navigate_to_match_page(match['match_url'])

            # navigam la tabul statisticilor
            self.navigate_to_statistics_tab()

            # obtinem statisticile
            self.page.wait_for_selector(".section")
            statistics = self.get_statistics()
            pprint(statistics)

            # scriem rezultatele
            if statistics:
                self.write_to_file(team, match, statistics)

            else:
                print("Nu am putat procesa statisticile sau nu exista")

    def write_to_file(self, team_name, match, statistics):
        os.makedirs(f"output/{team_name}", exist_ok=True)

        with open(f"output/{team_name}/{match['home_team']}-{match['away_team']}|{match['start_time'].replace(' ', '-')}", "w") as output_file:
            for (category, all_stats) in statistics.items():
                output_file.write(f"{category}\n")
                for (stat_name, values) in all_stats.items():
                    output_file.write(f"{stat_name}: {values['home']} | {values['away']}\n")
                output_file.write("\n")

    def run(self):
        info = self.request_component.send_info()

        if info:
            self.process_info(info, limit=1)

if __name__ == "__main__":
    web_scraper = FlashscoreWebScraper()
    teams = ["Ecuador"]
    for team in teams:
        web_scraper.process_info({
            "team": team
        })