import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from config import LOGIN_SITE, TRAINING_SITE
from utils import parse_rest_time, log

def scrape_training_plan(email, password):
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  #uncomment to run without window

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    wait = WebDriverWait(driver, 15)

    try:

        log("Logging in...")

        driver.get(LOGIN_SITE)

        wait.until(EC.presence_of_element_located((By.NAME, "email")))

        driver.find_element(By.NAME, "email").send_keys(email)
        driver.find_element(By.NAME, "password").send_keys(password)
        driver.find_element(By.CLASS_NAME, "submit").click()

        time.sleep(3)

        log("Logged in")
        log("Gathering exercise plan...")

        driver.get(TRAINING_SITE)

        wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "ul.skewed-menu > li.skewed-menu__item")
            )
        )

        day_items = driver.find_elements(
            By.CSS_SELECTOR, "ul.skewed-menu > li.skewed-menu__item"
        )

        log(f"Found {len(day_items)} days")

        all_exercises = {}

        for i in range(len(day_items)):
            day_items = driver.find_elements(
                By.CSS_SELECTOR, "ul.skewed-menu > li.skewed-menu__item"
            )
            item = day_items[i]

            subtitle = (
                item.find_element(By.CLASS_NAME, "skewed-menu__subtitle")
                .text.strip()
                .lower()
            )

            if subtitle in ["odpoczynek", "aktywny"]:
                log(f"Day {i+1}: {subtitle.upper()} (skipping)")
                continue

            log(f"Day {i+1}: WORKOUT - processing...")

            button = item.find_element(By.TAG_NAME, "button")
            driver.execute_script("arguments[0].click();", button)

            # wait to load more than one training cards
            wait.until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, "div[class*='exerciseCard']")
                )
            )

            # optional scroll for React lazy-load
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(0.5)

            cards = driver.find_elements(
                By.CSS_SELECTOR,
                "div[class*='exerciseCard'], div[class*='restCard']"
            )

            log(f"Found {len(cards)} cards")

            day_exercises = []
            last_exercise = None

            for card in cards:

                class_attr = card.get_attribute("class")

                # ==========================
                # IF EXERCISE
                # ==========================
                if "exerciseCard" in class_attr:
                    try:
                        title_elem = card.find_element(By.CSS_SELECTOR, "div[class*='title']")
                        lines = title_elem.text.split("\n")
                        exercise_name = lines[-1].strip()

                        warm_up_sets = None
                        working_sets = None

                        # warmup sets
                        try:
                            warmup_elem = card.find_element(
                                By.CSS_SELECTOR,
                                "div[class*='warmUpSeriesWrapper'] > div[class*='series']"
                                )
                            warm_up_sets = int(warmup_elem.text.strip())
                        except:
                            warm_up_sets = None

                        # working sets
                        try:
                            working_elem = card.find_element(
                                By.CSS_SELECTOR,
                                "div[class*='seriesWrapper']:not([class*='warmUpSeriesWrapper']) > div[class*='series']"
                                )
                            working_sets = int(working_elem.text.strip())
                        except:
                            working_sets = None

                        # reps
                        reps = []
                        repeat_elems = card.find_elements(By.CSS_SELECTOR, "li[class*='repeat']")
                        for rep in repeat_elems:
                            txt = rep.text.strip()
                            try:
                                reps.append(int(txt))
                            except:
                                reps.append(txt)

                        # rest between sets
                        try:
                            rest_elem = card.find_element(By.CSS_SELECTOR, "div[class*='seriesPause']")
                            rest_between_sets = rest_elem.text.strip()
                        except:
                            rest_between_sets = "?"

                        rest_min, rest_max = parse_rest_time(rest_between_sets)

                        exercise_data = {
                            "exercise": exercise_name,
                            "warm_up_sets": warm_up_sets,
                            "working_sets": working_sets,
                            "reps": reps,
                            "rest_between_sets": rest_between_sets,
                            "rest_between_sets_min": rest_min,
                            "rest_between_sets_max": rest_max,
                            "rest_after_exercise_min": None,
                            "rest_after_exercise_max": None
                        }

                        day_exercises.append(exercise_data)
                        last_exercise = exercise_data

                    except Exception as e:
                        log("Exercise error:", e)

                # ==========================
                # IF REST BETWEEN EXERCISES
                # ==========================
                elif "restCard" in class_attr:
                    if not last_exercise:
                        continue

                    try:
                        time_elem = card.find_element(By.CSS_SELECTOR, "div[class*='time']:not([class*='timer'])")
                        rest_text = driver.execute_script("return arguments[0].textContent;", time_elem).strip()
                        
                        if rest_text:
                            rest_min, rest_max = parse_rest_time(rest_text + " sek.")
                            last_exercise["rest_after_exercise_min"] = rest_min
                            last_exercise["rest_after_exercise_max"] = rest_max
                            
                    except Exception as e:
                        log(f"Error processing rest card: {e}")

            log(f"Saved {len(day_exercises)} exercises")

            all_exercises[f"Day {i+1}"] = day_exercises

        return all_exercises

    finally:
        driver.quit()
