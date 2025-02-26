import csv
import time
import random
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

def init_driver():
    """Initializes a fresh undetected Chrome WebDriver."""
    options = uc.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-gpu")
    driver = uc.Chrome(options=options)
    return driver

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
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//h5[contains(@class, "name")]/a'))
            )
            
            name_elements = driver.find_elements(By.XPATH, '//h5[contains(@class, "name")]/a')
            rate_elements = driver.find_elements(By.XPATH, '//span[@data-test="rate-per-hour"]')
            country_elements = driver.find_elements(By.XPATH, '//p[contains(@class, "location")]')
            job_success_elements = driver.find_elements(By.XPATH, '//span[@data-test="badge-hidden-label"]/preceding-sibling::span')
            position_elements = driver.find_elements(By.XPATH, '//div[contains(@class, "air3-line-clamp")]/h4/a')
            
            if not name_elements:
                print(f"No more data found for {category_name}. Exiting...")
                break
            
            num_entries = min(len(name_elements), len(rate_elements), len(country_elements),
                            len(job_success_elements), len(position_elements))
            
            # Get page source for BeautifulSoup
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            for i in range(num_entries):
                name = name_elements[i].text.strip()
                if name in scraped_names:
                    continue
                
                rate = rate_elements[i].text.strip() if i < len(rate_elements) else "N/A"
                country = country_elements[i].text.strip() if i < len(country_elements) else "N/A"
                job_success = job_success_elements[i].text.strip() if i < len(job_success_elements) else "N/A"
                position = position_elements[i].text.strip() if i < len(position_elements) else "N/A"
                
                # Extract skills using BeautifulSoup
                skills = []
                try:
                    # Find all skill containers on the page
                    skill_containers = soup.find_all(class_='air3-token-container')
                    if i < len(skill_containers):
                        skill_container = skill_containers[i]
                        skill_elements = skill_container.find_all(class_='air3-token') if skill_container else []
                        skills = [skill.text.strip() for skill in skill_elements[:-1] if skill.text.strip()]
                except Exception as e:
                    print(f"Error extracting skills for {name}: {e}")
                
                # Print for debugging
                print(f"Extracted skills for {name}: {skills}")
                scraped_names.add(name)
                freelancer_data.append([name, rate, country, job_success, position, ', '.join(skills)])
            
            save_data(category_name, freelancer_data)
            page_num += 1
            time.sleep(random.uniform(1, 3))  # Prevent rate limiting
            
        except WebDriverException as e:
            print(f"WebDriverException occurred: {e}. Restarting browser...")
            driver.quit()
            driver = init_driver()
        except Exception as e:
            print(f"Unexpected error: {e}")
            break
    
    save_data(category_name, freelancer_data)
    try:
        driver.quit()
    except Exception:
        pass
    print(f"Scraping completed for {category_name}. Data saved to upwork_{category_name}.csv.")

def save_data(category_name, data):
    """Saves the collected data to a CSV file."""
    filename = f"upwork_{category_name.replace(' ', '_')}.csv"
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Freelancer Name", "Hourly Rate", "Country", "Job Success", "Position", "Skills"])
        writer.writerows(data)

def main():
    categories = {
        "front_end_developer_americas": "https://www.upwork.com/nx/search/talent/?loc=americas&q=front%20end%20developer"
        # Add more categories as needed, e.g., "photographer_americas", "graphic_designer_americas", etc.
    }
    for category, url in categories.items():
        scrape_category(category, url)

if __name__ == "__main__":
    main()
