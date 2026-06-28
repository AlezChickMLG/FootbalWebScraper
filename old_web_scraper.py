# import requests
# from bs4 import BeautifulSoup
# from playwright.sync_api import sync_playwright
# import os
# import traceback
#
# flashscore_url = "https://www.flashscore.ro/"
# flashscore_url_no_slash = "https://www.flashscore.ro"
# spain_uruguay_match = "https://www.flashscore.ro/meci/fotbal/spania-bLyo6mco/uruguay-xMk44orG/sumar/statistici/total/?mid=8xM154oS"
#
# team = input("Which team to choose: ")
#
# def gather_statistics(page, home_team_name, away_team_name, start_time):
#     page.wait_for_selector(".section")
#     statistics = page.query_selector_all(".section")
#
#     os.mkdir(f"matches_{team}")
#
#     with open(f"matches_{team}/output_txt_{home_team_name}-{away_team_name}|{start_time.replace(' ', '-')}",
#               "w") as output_file:
#
#         for section in statistics:
#             individual_statistics = section.query_selector_all("div[data-testid='wcl-statistics']")
#             title_name_statistics = section.query_selector(".sectionHeader")
#             title_name = title_name_statistics.inner_text()
#
#             output_file.write(f"{title_name}\n")
#             print(f"{title_name}")
#
#             for individual_statistic in individual_statistics:
#                 details = individual_statistic.query_selector("div").query_selector_all("div")
#
#                 home_value_element = details[0].query_selector("span")
#                 home_value = home_value_element.inner_text()
#
#                 away_value_element = details[2].query_selector("span")
#                 away_value = away_value_element.inner_text()
#
#                 statistic_name_element = details[1].query_selector("span")
#                 statistic_name = statistic_name_element.inner_text()
#
#                 output_file.write(f"{statistic_name}: {home_value} | {away_value}\n")
#                 print(f"{statistic_name}: {home_value} | {away_value}")
#
#             output_file.write("\n")
#
# def main():
#     with sync_playwright() as p:
#         browser = p.chromium.launch(
#             headless=True,
#         )
#         context = browser.new_context()
#         page = context.new_page()
#
#         page.goto(flashscore_url)
#         print("Pagina incarcatata")
#
#         page.wait_for_selector("#onetrust-accept-btn-handler")
#         page.click("#onetrust-accept-btn-handler")
#         print("Am apasat pe butonul de cookies")
#
#         page.click("#search-window")
#         print("Am apasat pe buton de cautare pentru a deschide meniul")
#
#         page.wait_for_selector(".searchInput__input")
#         page.fill(".searchInput__input", team)
#         print(f"Am introdus {team} la cautare")
#
#         page.wait_for_selector(".searchResult")
#         search_result = page.query_selector_all(".searchResult")
#         print("Am obtinut rezultatele cautarii")
#
#         for result in search_result:
#             try:
#                 name = result.query_selector(".searchResult__participantName").inner_text()
#                 category = result.query_selector(".searchResult__participantCategory").inner_text()
#                 href = result.get_attribute("href")
#
#                 print(f"Name: {name} | Category: {category}")
#
#                 if name.strip().lower() == team.strip().lower():
#                     print("Echipa gasita")
#
#                     team_url = f"{flashscore_url}{href}"
#                     page.goto(team_url)
#                     print(f"Am deschis pagina echipei {team}")
#
#                     page.wait_for_selector("a.tabs__tab[title='Rezultate']")
#                     results_href_element = page.query_selector("a.tabs__tab[title='Rezultate']")
#                     results_href = results_href_element.get_attribute("href")
#                     print(f"results href: {results_href}")
#
#                     result_url = f"{flashscore_url_no_slash}{results_href}"
#
#                     page.goto(result_url)
#                     print("Am deschis sectiunea de rezultate")
#
#                     all_matches = page.query_selector_all(".event__match")
#
#                     #for match in all_matches:
#                     match = all_matches[0]
#                     print("Incep sa extrag datele despre meciuri")
#
#                     home_team_element = match.query_selector(".event__homeParticipant")
#                     home_team_name = home_team_element.query_selector("div").query_selector("div").query_selector(
#                         "span").inner_text()
#
#                     away_team_element = match.query_selector(".event__awayParticipant")
#                     away_team_name = away_team_element.query_selector("div").query_selector("div").query_selector(
#                         "span").inner_text()
#
#                     start_time_element = match.query_selector(".event__time")
#                     start_time = start_time_element.inner_text()
#
#                     match_url_element = match.query_selector(".eventRowLink")
#                     match_url = match_url_element.get_attribute("href")
#
#                     page.goto(match_url)
#                     print("Am intrat pe meci")
#
#                     all_buttons = page.query_selector(".filterOver").query_selector("div").query_selector_all("a")
#                     for button in all_buttons:
#                         button_href = button.get_attribute("href")
#                         if "statistici" in button_href:
#                             page.goto(f"{flashscore_url_no_slash}{button_href}")
#                             print("Am ajuns pe pagina de statistici")
#
#                             print(f"{home_team_name} - {away_team_name} : {start_time}")
#                             gather_statistics(page, home_team_name, away_team_name, start_time)
#
#                         break
#                     break
#             except Exception as e:
#                 traceback.print_exc()
#
#         input()
#
#         browser.close()
#
# if __name__ == "__main__":
#     main()