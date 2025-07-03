import os
import csv
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC 
from webdriver_manager.chrome import ChromeDriverManager 

# Define both CT and NY cities
CT_CITIES = [
    "Ansonia", "Beacon Falls", "Bethany", "Branford", "Cheshire", "Derby",
    "East Haven", "Guilford", "Hamden", "Madison", "Meriden", "Middlebury",
    "New Haven", "North Branford", "North Haven", "Orange", "Oxford", "Prospect",
    "Seymour", "Shelton", "Southbury", "Wallingford", "Waterbury", "West Haven",
    "Woodbridge", "Bethel", "Bridgeport", "Brookfield", "Danbury", "Darien",
    "Easton", "Fairfield", "Greenwich", "Monroe", "New Canaan", "Newtown",
    "Norwalk", "Redding", "Ridgefield", "Shelton", "Sherman", "Stamford",
    "Stratford", "Trumbull", "Weston", "Westport", "Wilton", "New Fairfield",
]

NY_CITIES = [
    "Yonkers", "New Rochelle", "Mount Vernon", "White Plains", "Peekskill", "Rye",
    "Bedford", "Bedford Hills", "Katonah", "Cortlandt", "Buchanan", "Croton-on-Hudson",
    "Eastchester", "Bronxville", "Tuckahoe", "Greenburgh", "Ardsley", "Dobbs Ferry",
    "Elmsford", "Hastings-on-Hudson", "Irvington", "Tarrytown", "Harrison", "Lewisboro",
    "Mamaroneck", "Larchmont", "Mamaroneck village", "Mount Kisco", "Mount Pleasant",
    "Briarcliff Manor", "Pleasantville", "Sleepy Hollow", "New Castle", "Chappaqua",
    "Millwood", "North Castle", "Armonk", "North Salem", "Ossining", "Ossining village",
    "Pelham", "Pelham village", "Pelham Manor", "Pound Ridge", "Rye Town", "Port Chester",
    "Rye Brook", "Scarsdale", "Somers", "Yorktown", "Jefferson Valley-Yorktown", "Crompond",
    "Lake Mohegan", "Shrub Oak", "Yorktown Heights"
]

# Function to run scraper for a given state and city list
def run_scraper(state_code, TARGET_CITIES):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.110 Safari/537.36")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get("https://www.amtamassage.org/find-massage-therapist/")
        print("Page loaded successfully.")
        time.sleep(random.uniform(2, 4))

        search_box = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "keyword")))
        search_box.clear()
        search_box.send_keys("Massage")
        print("Keyword 'Massage' entered.")
        time.sleep(random.uniform(1.5, 3))

        location_box = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "location")))
        location_box.clear()
        location_box.send_keys(state_code)
        print(f"Location '{state_code}' entered.")
        time.sleep(random.uniform(1.5, 3))

        search_button = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, "//button[@class='btn-primary']")))
        search_button.click()
        print("Search button clicked.")
        time.sleep(random.uniform(5, 7))

        master_file = "amta.csv"
        new_file = "amta_newprof.csv"
        new_professionals = []

        existing_profiles = set()
        if os.path.exists(master_file):
            with open(master_file, "r", newline="") as f:
                reader = csv.reader(f)
                next(reader, None)
                existing_profiles.update(tuple(row) for row in reader)

        while True:
            profiles = driver.find_elements(By.XPATH, "//a[contains(@href, '/famt/')]")
            addresses = driver.find_elements(By.XPATH, "//div[contains(@class, 'find-a-mr-results-list-item-address')]")
            print(f"Profiles found on this page: {len(profiles)}")

            for profile, address in zip(profiles, addresses):
                try:
                    name = profile.text.strip()
                    city_elements = address.find_elements(By.TAG_NAME, "p")
                    city = city_elements[-1].text.strip() if len(city_elements) > 1 else ""
                    print(f"Name found: {name}")
                    print(f"City found: {city}")

                    if any(city.startswith(c) for c in TARGET_CITIES):
                        website = ""
                        try:
                            profile.click()
                            print(f"Entering profile of {name}...")
                            time.sleep(random.uniform(2, 4))
                            website_element = WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((By.XPATH, "//span[contains(text(),'Website:')]/a"))
                            )
                            website = website_element.get_attribute("href").strip()
                            print(f"Website found: {website}")
                        except Exception:
                            print(f"No website found for {name}, {city}")

                        professional = (name, city, website)

                        if professional not in existing_profiles:
                            new_professionals.append(professional)
                            existing_profiles.add(professional)
                            print(f"New professional found: {name}, {city}, {website}")

                        driver.back()
                        time.sleep(random.uniform(2, 4))

                except Exception as e:
                    print(f"Error processing profile: {e}")

            try:
                next_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(@class,'pagination-arrows-item') and .//span[contains(text(),'Next Page')]]"))
                )
                next_button.click()
                print("Moving to the next page.")
                time.sleep(random.uniform(5, 7))
            except Exception:
                print("No more pages to process or pagination error.")
                break

        # Overwrite new_file with only current new professionals
        with open(new_file, "w", newline="") as f_new:
            new_writer = csv.writer(f_new)
            new_writer.writerow(["Name", "City", "Website"])
            for professional in new_professionals:
                new_writer.writerow(professional)

        # Append new professionals to master_file
        if new_professionals:
            with open(master_file, "a", newline="") as f_master:
                master_writer = csv.writer(f_master)
                for professional in new_professionals:
                    master_writer.writerow(professional)
                    print(f"Saved to CSV: {professional}")

    except Exception as e:
        print(f"Error during search: {e}")

    finally:
        driver.quit()

# Run CT first, then NY
run_scraper("CT", CT_CITIES)
run_scraper("NY", NY_CITIES)