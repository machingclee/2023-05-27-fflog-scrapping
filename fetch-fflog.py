from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import re

caps = DesiredCapabilities().CHROME
caps["pageLoadStrategy"] = "eager"
driver = webdriver.Chrome(
    desired_capabilities=caps,
    executable_path="C:\\dev\\chrome-driver\\chromedriver.exe"
)

def control_and_click(anchor):
    ActionChains(driver).key_down(Keys.CONTROL).click(anchor).key_up(Keys.CONTROL).perform()

# default search method to wait: query select all
def wait_element(search_txt, by_method=By.CSS_SELECTOR, seconds=10):
    return WebDriverWait(driver, seconds).until(EC.presence_of_all_elements_located((by_method, search_txt)))

def start_fflog_scrapping(urls, target_player_names, file_location="omega_kills_record.txt"):
    names_matching_regex = re.compile("|".join(target_player_names))
    
    for url in urls:
        driver.get(url)

        reports = wait_element("#reports-table a[href*='/reports']")
        print("Number of reports in this page: {}".format(len(reports)))
        for i in range(0, len(reports)):
            print("handing report", reports[i].text)
            report_anchor = reports[i]
            control_and_click(report_anchor)

            # looking at summary of various pulls
            driver.switch_to.window(driver.window_handles[1])

            # detail of bosses related, we are only interested in those omega kill log:
            rows = wait_element("a[class*='report-overview-boss']")

            omega_kills = [row for row in rows if re.search("TheOmegaProtocolKill", re.sub("\\s", "", row.text)) is not None]

            if len(omega_kills) > 0:
                control_and_click(omega_kills[0])
                driver.switch_to.window(driver.window_handles[2])
                name_anchors = wait_element("#summary-damage-done-scroller-0 tr[role='row'] a.tooltip")
                names = "".join([anchor.text for anchor in name_anchors])
                matched_names = names_matching_regex.findall(names)
                if len(matched_names) > 0:
                    with open(file_location, "a+", encoding="utf-8") as f:
                        line_1 = "target player(s):\t" + ", ".join(matched_names) + "\n"
                        line_2 = "link: \t\t\t\t\t\t" + driver.current_url + "\n"
                        line_3 = "---\n"
                        f.writelines(line_1 + line_2 + line_3)
                    print("Player { "+ ", ".join(matched_names) + " } has been found")
                driver.close()
                driver.switch_to.window(driver.window_handles[1])
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
            else:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])


if __name__ == "__main__":
    base_link = "https://www.fflogs.com/zone/reports?zone=53"
    urls = [base_link] + [base_link + f"&page={i}" for i in range(2, 100)]
        
    target_player_names = ["Kestona Lynsae", "Crowned San"]
    file_location = "omega_kills_record.txt"
    
    start_fflog_scrapping(urls, target_player_names)
