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

# List of target cities to filter professionals
TARGET_CITIES = [
    "Ansonia", "Beacon Falls", "Bethany", "Branford", "Cheshire", "Derby",
    "East Haven", "Guilford", "Hamden", "Madison", "Meriden", "Middlebury",
    "New Haven", "North Branford", "North Haven", "Orange", "Oxford", "Prospect",
    "Seymour", "Shelton", "Southbury", "Wallingford", "Waterbury", "West Haven",
    "Woodbridge", "Bethel", "Bridgeport", "Brookfield", "Danbury", "Darien",
    "Easton", "Fairfield", "Greenwich", "Monroe", "New Canaan", "Newtown",
    "Norwalk", "Redding", "Ridgefield", "Shelton", "Sherman", "Stamford",
    "Stratford", "Trumbull", "Weston", "Westport", "Wilton", "New Fairfield",
]

# Configure browser options
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.110 Safari/537.36")

# Create the driver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

try:
    # Navigate to AMTA search page
    driver.get("https://www.amtamassage.org/find-massage-therapist/")
    print("Page loaded successfully.")
    time.sleep(random.uniform(2, 4))

    # Enter "Massage" in the keyword field
    search_box = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "keyword")))
    search_box.clear()
    search_box.send_keys("Massage")
    print("Keyword 'Massage' entered.")
    time.sleep(random.uniform(1.5, 3))

    # Enter "CT" in the location field
    location_box = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "location")))
    location_box.clear()
    location_box.send_keys("CT")
    print("Location 'CT' entered.")
    time.sleep(random.uniform(1.5, 3))

    # Click the search button
    search_button = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, "//button[@class='btn-primary']")))
    search_button.click()
    print("Search button clicked.")
    time.sleep(random.uniform(5, 7))

    # Configure CSV files
    master_file = "amta.csv"
    new_file = "amta_newprof.csv"
    new_professionals = []

    # Load existing profiles to avoid duplicates
    existing_profiles = set()
    if os.path.exists(master_file):
        with open(master_file, "r", newline="") as f:
            reader = csv.reader(f)
            next(reader, None)  # Skip header
            existing_profiles.update(tuple(row) for row in reader)

    # Add headers if files are empty or don't exist
    if not os.path.exists(master_file) or os.path.getsize(master_file) == 0:
        with open(master_file, "w", newline="") as f_master:
            master_writer = csv.writer(f_master)
            master_writer.writerow(["Name", "City", "Website"])
    if not os.path.exists(new_file) or os.path.getsize(new_file) == 0:
        with open(new_file, "w", newline="") as f_new:
            new_writer = csv.writer(f_new)
            new_writer.writerow(["Name", "City", "Website"])

    # Scrape profiles across all pages
    while True:
        profiles = driver.find_elements(By.XPATH, "//a[contains(@href, '/famt/')]")
        addresses = driver.find_elements(By.XPATH, "//div[contains(@class, 'find-a-mr-results-list-item-address')]")
        print(f"Profiles found on this page: {len(profiles)}")

        for profile, address in zip(profiles, addresses):
            try:
                # Extract name
                name = profile.text.strip()
                
                # Extract city (last <p> within the address container)
                city_elements = address.find_elements(By.TAG_NAME, "p")
                city = city_elements[-1].text.strip() if len(city_elements) > 1 else ""
                print(f"Name found: {name}")
                print(f"City found: {city}")

                # Filter by target city
                if any(city.startswith(c) for c in TARGET_CITIES):
                    # Attempt to get the website
                    website = ""
                    try:
                        profile.click()
                        print(f"Entering profile of {name}...")
                        time.sleep(random.uniform(2, 4))

                        # Look for the website link
                        website_element = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, "//span[contains(text(),'Website:')]/a"))
                        )
                        website = website_element.get_attribute("href").strip()
                        print(f"Website found: {website}")
                    except Exception:
                        print(f"No website found for {name}, {city}")

                    # Prepare the professional's data
                    professional = (name, city, website)

                    # Add to the list of new professionals if not already in the master file
                    if professional not in existing_profiles:
                        new_professionals.append(professional)
                        existing_profiles.add(professional)  # Update to avoid duplicate checking
                        print(f"New professional found: {name}, {city}, {website}")

                    # Return to the results page
                    driver.back()
                    time.sleep(random.uniform(2, 4))

            except Exception as e:
                print(f"Error processing profile: {e}")

        # Try to move to the next page
        try:
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class,'pagination-arrows-item') and .//span[contains(text(),'Next Page')]]"))
            )
            next_button.click()
            print("Moving to the next page.")
            time.sleep(random.uniform(5, 7))
        except Exception:
            print("No more pages to process or pagination error.")
            break  # Exit the loop if no more pages

    # Save new professionals to CSV
    with open(new_file, "w", newline="") as f_new:
        new_writer = csv.writer(f_new)
        new_writer.writerow(["Name", "City", "Website"])
        if new_professionals:  # Only write if there are new professionals
            with open(master_file, "a", newline="") as f_master:
                master_writer = csv.writer(f_master)
                for professional in new_professionals:
                    master_writer.writerow(professional)
                    new_writer.writerow(professional)
                    print(f"Saved to CSV: {professional}")

except Exception as e:
    print(f"Error during search: {e}")

finally:
    driver.quit()