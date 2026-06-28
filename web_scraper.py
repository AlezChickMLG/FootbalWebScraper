import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import os
import traceback
from request_component import RequestComponent
from pprint import pprint

class FlashscoreWebScraper:
    def __init__(self):
        self.sync_playwright = sync_playwright().start()
        self.browser = self.sync_playwright.chromium.launch(
            headless=True,
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
    def get_team_url(self, team):
        try:
            self.page.click("#search-window")
            print("Am apasat pe buton de cautare pentru a deschide meniul")

            self.page.wait_for_selector(".searchInput__input")
            self.page.fill(".searchInput__input", team)
            print(f"Am introdus {team} la cautare")

            self.page.wait_for_selector(".searchResult")
            search_result = self.page.query_selector_all(".searchResult")

            for result in search_result:
                name = result.query_selector(".searchResult__participantName").inner_text()
                # category = result.query_selector(".searchResult__participantCategory").inner_text()
                href = result.get_attribute("href")

                if name.strip().lower() == team.strip().lower():
                    return href

            return None
        except Exception as e:
            print(f"Eroare intampinata la gasirea echipei {team}")
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
            self.page.wait_for_selector(".section")
            statistics = self.page.query_selector_all(".section")

            statistics_dict = {}

            #os.makedirs(f"matches_{team}", exist_ok=True)
            #with open(f"matches_{team}/output_txt_{home_team_name}-{away_team_name}|{start_time.replace(' ', '-')}""w") as output_file:

            if statistics:
                for section in statistics:
                    individual_statistics = section.query_selector_all("div[data-testid='wcl-statistics']")

                    title_name_statistics = section.query_selector(".sectionHeader")

                    if title_name_statistics is None:
                        print("Eroare: nu a fost gasit title_name_statistics")
                        return

                    title_name = title_name_statistics.inner_text()
                    statistics_dict[title_name] = {}

                    #output_file.write(f"{title_name}\n")
                    #print(f"{title_name}")

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

    def process_info(self, info, limit=1):
        team = info["team"]
        print(f"Prelucram echipa {team}")

        #mergem inapoi la pagina principala
        self.reset_page()
        print(f"Am resetat pagina")

        #obtine url echipei
        team_url = self.get_team_url(team)

        #verificam daca a returnat un link valid
        if team is None:
            print(f"Nu am gasit echipa {team}")
            return

        elif team is not False:
            full_team_url = f"{self.flashscore_url}{team_url}"
            self.page.goto(full_team_url)
            print(f"Am intrat pe pagina echipei {team}")

            self.page.wait_for_selector("a.tabs__tab[title='Rezultate']")
            results_href_element = self.page.query_selector("a.tabs__tab[title='Rezultate']")
            results_href = results_href_element.get_attribute("href")

            result_url = f"{self.flashscore_url_no_slash}{results_href}"

            self.page.goto(result_url)
            print("Am deschis sectiunea de rezultate")

            #obtinem toate meciurile
            matches = self.get_all_matches()

            if matches:
                for match_index, match in enumerate(matches):
                    if match_index >= limit:
                        break

                    #print(f"Obtinem statisticile pentru meciul {match['home_team']} - {match['away_team']} disputat la data de {match['start_time']}")
                    pprint(match)
                    self.page.goto(match['match_url'])
                    print("Am intrat pe pagina meciului")

                    #navigam la tabul statisticilor
                    all_buttons = self.page.query_selector(".filterOver").query_selector("div").query_selector_all("a")
                    statistics_button = all_buttons[1]
                    button_href = statistics_button.get_attribute("href")
                    self.page.goto(f"{self.flashscore_url_no_slash}{button_href}")
                    print("Am ajuns pe pagina de statistici")

                    #obtinem statisticile
                    self.page.wait_for_selector(".section")
                    statistics = self.get_statistics()
                    pprint(statistics)

                    #scriem rezultatele
                    self.write_to_file(team, match, statistics)

                    #ne intoarcem la pagina meciurilor
                    # self.page.goto(result_url)
                    # print("M-am intors pe pagina de rezultate")

    def write_to_file(self, team, match, statistics):
        os.makedirs(f"output/{team}", exist_ok=True)

        with open(f"output/{team}/{match['home_team']}-{match['away_team']}|{match['start_time'].replace(' ', '-')}", "w") as output_file:
            for (category, all_stats) in statistics.items():
                output_file.write(f"{category}\n")
                for (stat_name, values) in all_stats.items():
                    output_file.write(f"{stat_name}: {values['home']} | {values['away']}\n")
                output_file.write("\n")




    def run(self):
        info = self.request_component.send_info()

        if info:
            self.process_info(info)

# team_url = f"{flashscore_url}{href}"
# page.goto(team_url)
# print(f"Am deschis pagina echipei {team}")

# page.goto(match_url)
# print("Am intrat pe meci")

if __name__ == "__main__":
    web_scraper = FlashscoreWebScraper()
    web_scraper.process_info({
        "team": "Spania"
    })