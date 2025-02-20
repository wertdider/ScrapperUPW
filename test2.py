import csv
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, '//h5[contains(@class, "name")]/a'))
            )
            
            name_elements = driver.find_elements(By.XPATH, '//h5[contains(@class, "name")]/a')
            rate_elements = driver.find_elements(By.XPATH, '//span[@data-test="rate-per-hour"]')
            country_elements = driver.find_elements(By.XPATH, '//p[contains(@class, "location")]')
            job_success_elements = driver.find_elements(By.XPATH, '//span[@data-test="badge-hidden-label"]/preceding-sibling::span')
            position_elements = driver.find_elements(By.XPATH, '//div[contains(@class, "air3-line-clamp")]/h4/a')
            skill_containers = driver.find_elements(By.XPATH, '//div[@class="air3-token-container"]')
            
            if not name_elements:
                print(f"No more data found for {category_name}. Exiting...")
                break
            
            num_entries = min(len(name_elements), len(rate_elements), len(country_elements),
                            len(job_success_elements), len(position_elements), len(skill_containers))
            
            for i in range(num_entries):
                name = name_elements[i].text.strip()
                if name in scraped_names:
                    continue
                
                rate = rate_elements[i].text.strip() if i < len(rate_elements) else "N/A"
                country = country_elements[i].text.strip() if i < len(country_elements) else "N/A"
                job_success = job_success_elements[i].text.strip() if i < len(job_success_elements) else "N/A"
                position = position_elements[i].text.strip() if i < len(position_elements) else "N/A"
                
                # Extract skills (visible and hidden)
                skills = []
                if i < len(skill_containers):
                    try:
                        # Visible skills
                        skill_elements = skill_containers[i].find_elements(By.XPATH, './/div[contains(@class, "air3-token-wrap")]/button')
                        visible_skills = [skill.text.strip() for skill in skill_elements if skill.text.strip()]
                        
                        # Hidden skills (adjust XPath and ensure accessibility)
                        hidden_skill_elements = skill_containers[i].find_elements(By.XPATH, './/div[contains(@class, "air3-token-wrap") and contains(@class, "d-none")]/button')
                        hidden_skills = [skill.text.strip() for skill in hidden_skill_elements if skill.text.strip()]
                        
                        # Combine and deduplicate skills
                        skills = list(set(visible_skills + hidden_skills))
                        
                        # If hidden skills might be dynamically loaded, try revealing them
                        if not hidden_skills:
                            try:
                                more_button = skill_containers[i].find_element(By.XPATH, './/button[contains(@class, "air3-btn") and contains(text(), "more")]')
                                driver.execute_script("arguments[0].click();", more_button)
                                time.sleep(1)  # Wait for hidden skills to load
                                hidden_skill_elements = skill_containers[i].find_elements(By.XPATH, './/div[contains(@class, "air3-token-wrap") and contains(@class, "d-none")]/button')
                                hidden_skills = [skill.text.strip() for skill in hidden_skill_elements if skill.text.strip()]
                                skills = list(set(visible_skills + hidden_skills))
                            except NoSuchElementException:
                                pass  # No "Show more" button found
                        
                    except Exception as e:
                        print(f"Error extracting skills for {name}: {e}")
                
                print(f"Extracted skills for {name}: {skills}")
                scraped_names.add(name)
                freelancer_data.append([name, rate, country, job_success, position, ', '.join(skills)])
            
            save_data(category_name, freelancer_data)
            page_num += 1
            
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
        "front_end_developer": "https://www.upwork.com/nx/search/talent/?q=front%20end%20developer"
    }
    for category, url in categories.items():
        scrape_category(category, url)

if __name__ == "__main__":
    main()