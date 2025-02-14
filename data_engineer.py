import csv
import time
import signal
import undetected_chromedriver as uc  
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

# Initialize undetected Chrome WebDriver
options = uc.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--no-sandbox")
options.add_argument("--disable-infobars")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--start-maximized")
options.add_argument("--disable-gpu")

driver = uc.Chrome(options=options)

# Prepare to collect data
freelancer_data = []
scraped_names = set()  # To prevent duplicates
running = True  # Flag to control the loop

def scrape_page():
    """Scrapes the current page for freelancer details."""
    name_elements = driver.find_elements(By.XPATH, '//h5[contains(@class, "name")]/a')
    rate_elements = driver.find_elements(By.XPATH, '//span[@data-test="rate-per-hour"]')
    country_elements = driver.find_elements(By.XPATH, '//p[contains(@class, "location")]')
    job_success_elements = driver.find_elements(By.XPATH, '//span[@data-test="badge-hidden-label"]/preceding-sibling::span')
    skill_elements = driver.find_elements(By.XPATH, '//div[@role="listitem"]/button[@class="air3-token"]')

    page_data = []
    for i in range(len(name_elements)):
        name = name_elements[i].text.strip()
        if name in scraped_names:
            continue  # Skip duplicate names
        
        rate = rate_elements[i].text.strip() if i < len(rate_elements) else "N/A"
        country = country_elements[i].text.strip() if i < len(country_elements) else "N/A"
        job_success = job_success_elements[i].text.strip() if i < len(job_success_elements) else "N/A"

        # Collect skills for each freelancer
        skills = []
        for skill in skill_elements[i * 10:(i + 1) * 10]:  # Assume up to 10 skills per freelancer
            skills.append(skill.text.strip())

        scraped_names.add(name)  # Add to the set to avoid duplicates
        page_data.append([name, rate, country, job_success, ', '.join(skills)])
    
    return page_data

def save_data():
    """Saves the collected data to a CSV file."""
    with open('upwork_data_engineers.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Freelancer Name", "Hourly Rate", "Country", "Job Success", "Skills"])
        writer.writerows(freelancer_data)
    print(f"Saved data for {len(freelancer_data)} freelancers.")

def signal_handler(sig, frame):
    """Handles Ctrl + C to save data before exiting."""
    global running
    print("\nCtrl + C detected. Saving data before exiting...")
    save_data()
    running = False
    driver.quit()
    print("Scraper stopped gracefully.")
    exit(0)

# Register the signal handler
signal.signal(signal.SIGINT, signal_handler)

page_num = 1
while running:
    print(f"Scraping page {page_num}...")
    driver.get(f'https://www.upwork.com/nx/search/talent/?q=data%20engineer&page={page_num}')
    time.sleep(10)  # Wait for Cloudflare to finish its check and load the page fully

    current_page_data = scrape_page()
    if not current_page_data:
        print("No more data found. Exiting...")
        break
    
    freelancer_data.extend(current_page_data)
    save_data()  # Save data after each page
    page_num += 1

# Final save and cleanup
save_data()
driver.quit()
print(f"Scraped data for {len(freelancer_data)} freelancers.")
