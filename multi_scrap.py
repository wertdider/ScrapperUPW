import csv
import time
import signal
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from concurrent.futures import ThreadPoolExecutor

def init_driver():
    """Initializes a fresh undetected Chrome WebDriver."""
    options = uc.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-gpu")
    return uc.Chrome(options=options)

def scrape_category(category_name, url):
    """Scrapes freelancers for a given job category."""
    driver = init_driver()
    freelancer_data = []
    scraped_names = set()
    page_num = 1
    
    while True:
        try:
            print(f"Scraping {category_name} - Page {page_num}...")
            driver.get(f"{url}&page={page_num}")
            time.sleep(10)  # Wait for Cloudflare check
            
            name_elements = driver.find_elements(By.XPATH, '//h5[contains(@class, "name")]/a')
            rate_elements = driver.find_elements(By.XPATH, '//span[@data-test="rate-per-hour"]')
            country_elements = driver.find_elements(By.XPATH, '//p[contains(@class, "location")]')
            job_success_elements = driver.find_elements(By.XPATH, '//span[@data-test="badge-hidden-label"]/preceding-sibling::span')
            skill_elements = driver.find_elements(By.XPATH, '//div[@role="listitem"]/button[@class="air3-token"]')
            
            if not name_elements:
                print(f"No more data found for {category_name}. Exiting...")
                break
            
            for i in range(len(name_elements)):
                name = name_elements[i].text.strip()
                if name in scraped_names:
                    continue  # Skip duplicates
                
                rate = rate_elements[i].text.strip() if i < len(rate_elements) else "N/A"
                country = country_elements[i].text.strip() if i < len(country_elements) else "N/A"
                job_success = job_success_elements[i].text.strip() if i < len(job_success_elements) else "N/A"
                skills = [skill.text.strip() for skill in skill_elements[i * 10:(i + 1) * 10]]
                
                scraped_names.add(name)
                freelancer_data.append([name, rate, country, job_success, ', '.join(skills)])
            
            save_data(category_name, freelancer_data)
            page_num += 1
            
        except WebDriverException as e:
            print(f"WebDriverException occurred: {e}. Restarting browser...")
            driver.quit()
            driver = init_driver()  # Restart browser if it crashes
        except Exception as e:
            print(f"Unexpected error: {e}")
            break
    
    driver.quit()
    print(f"Scraping completed for {category_name}. Data saved to upwork_{category_name}.csv.")

def save_data(category_name, data):
    """Saves the collected data to a CSV file."""
    filename = f"upwork_{category_name.replace(' ', '_')}.csv"
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Freelancer Name", "Hourly Rate", "Country", "Job Success", "Skills"])
        writer.writerows(data)

def main():
    categories = {
        "front_end_developer": "https://www.upwork.com/nx/search/talent/?q=front%20end%20developer",
        "backend_developer": "https://www.upwork.com/nx/search/talent/?q=backend%20developer",
        "ai_developer": "https://www.upwork.com/nx/search/talent/?q=ai%20developer",
        "data_science": "https://www.upwork.com/nx/search/talent/?q=data%20science",
        "deep_learning": "https://www.upwork.com/nx/search/talent/?q=deep%20learning",
        "machine_learning": "https://www.upwork.com/nx/search/talent/?q=machine%20learning"
    }
    
    with ThreadPoolExecutor(max_workers=3) as executor:  # Adjust concurrency if needed
        for category, url in categories.items():
            executor.submit(scrape_category, category, url)

if __name__ == "__main__":
    main()
