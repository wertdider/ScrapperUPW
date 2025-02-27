import csv
import json
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import os
import random
import signal
import sys

def init_driver():
    """Initialize Chrome WebDriver."""
    options = uc.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")
    driver = uc.Chrome(options=options)
    return driver

def save_to_csv(data_list):
    """Save the scraped data to a CSV file with minimal quoting."""
    filename = "freelancer_data.csv"
    headers = ["Name", "Hourly Rate", "Country", "Job Success", "Position", "Skills", "Total Jobs", "Total Hours", "About", "Profile URL"]
    
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(headers)
        writer.writerows([[d['name'], d['hourly_rate'], d['country'], d['job_success'], 
                         d['position'], d['skills'], d['total_jobs'], d['total_hours'], 
                         d['about'], d['profile_url']] for d in data_list])
    print(f"Data saved to {filename}")

def save_to_json(data_list):
    """Save the scraped data to a JSON file."""
    filename = "freelancer_data.json"
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump({"freelancers": data_list}, file, indent=2, ensure_ascii=False)
    print(f"Data saved to {filename}")

# def get_profile_details(driver, profile_url):

  
#     """Extract detailed information from a freelancer's profile page using Selenium and bs4."""
#     try:
#         print(f"Navigating to profile: {profile_url}")
#         driver.get(profile_url)
#         time.sleep(2)  # Allow page to render
#         name_elements = driver.find_elements(By.XPATH, "//h2[@itemprop='name' and @data-v-4c3dc5a6]")
#         position_elements = driver.find_elements(By.XPATH, "//h2[@data-v-7b2a5190]")
#         country_elements = driver.find_elements(By.XPATH, "//p[@data-v-93403cd2]]")
#         rate_elements = driver.find_elements(By.XPATH, "//span[@data-v-7b2a5190]")
#         job_success_elements = driver.find_elements(By.XPATH, "//span[@data-v-015e54d8 and @data-test='badge-hidden-label']")
#         name = name_elements[i].text.strip()
#         hourly_rate = rate_elements[i].text.strip() if i < len(rate_elements) else "N/A"
#         country = country_elements[i].text.strip() if i < len(country_elements) else "N/A"
#         job_success = job_success_elements[i].text.strip() if i < len(job_success_elements) else "N/A"
#         position = position_elements[i].text.strip() if i < len(position_elements) else "N/A"
#         soup = BeautifulSoup(driver.page_source, 'html.parser')
        
#         # Scrape About
#         about = "N/A"
#         try:
#             about_elem = soup.select_one("span.text-pre-line.break")
#             about = about_elem.text.strip().replace('\n', ' | ') if about_elem else "N/A"
#             print(f"Scraped About: {about}")
#         except Exception as e:
#             print(f"Error scraping About: {e}")
        
#         # Scrape Total Jobs
#         total_jobs = "N/A"
#         try:
#             total_jobs_elem = soup.select_one("div.col-compact.min-with-75 span.text-base-sm.text-light-on-inverse:-soup-contains('Total jobs')")
#             if total_jobs_elem:
#                 total_jobs_span = total_jobs_elem.find_previous('div', class_='stat-amount h5').find('span')
#                 total_jobs = total_jobs_span.text.strip() if total_jobs_span else "N/A"
#             print(f"Scraped Total Jobs: {total_jobs}")
#         except Exception as e:
#             print(f"Error scraping Total Jobs: {e}")
        
#         # Scrape Total Hours
#         total_hours = "N/A"
#         try:
#             total_hours_elem = soup.select_one("div.col-compact.min-with-75 span.text-base-sm.text-light-on-inverse:-soup-contains('Total hours')")
#             if total_hours_elem:
#                 total_hours_span = total_hours_elem.find_previous('div', class_='stat-amount h5').find('span')
#                 total_hours = total_hours_span.text.strip() if total_hours_span else "N/A"
#             print(f"Scraped Total Hours: {total_hours}")
#         except Exception as e:
#             print(f"Error scraping Total Hours: {e}")
        
#         return {
#             'total_jobs': total_jobs,
#             'total_hours': total_hours,
#             'about': about,
#             'name': name,
#             'hourly_rate': hourly_rate,
#             'country': country,
#             'job_success': job_success,
#             'position': position,
#             'profile_url': profile_url
#         }
    
#     except Exception as e:
#         print(f"Error scraping profile {profile_url}: {e}")
#         print("Page source snippet:")
#         print(driver.page_source[:1000])
#         return {'total_jobs': 'N/A', 'total_hours': 'N/A', 'about': 'N/A'}

def get_profile_details(driver, profile_url):
    """Extract detailed information from a freelancer's profile page using Selenium and bs4.
    Opens the profile in a new tab, processes it, then returns to the original tab."""
    try:
        # Open a new tab
        print(f"Opening new tab for profile: {profile_url}")
        driver.execute_script("window.open('');")
        
        # Get all window handles and verify we have at least 2
        handles = driver.window_handles
        if len(handles) < 2:
            print("Failed to open new tab")
            return {
                'name': 'N/A', 'position': 'N/A', 'country': 'N/A',
                'hourly_rate': 'N/A', 'job_success': 'N/A',
                'total_jobs': 'N/A', 'total_hours': 'N/A', 'about': 'N/A',
                'profile_url': profile_url
            }
        
        # Switch to the new tab (should be the last in the list)
        driver.switch_to.window(handles[-1])
        
        # Navigate to the profile URL in the new tab
        print(f"Navigating to {profile_url}")
        driver.get(profile_url)
        time.sleep(3)  # Allow page to render - increased wait time
        
        # Extract profile information - with defensive programming
        profile_data = {
            'name': 'N/A', 'position': 'N/A', 'country': 'N/A',
            'hourly_rate': 'N/A', 'job_success': 'N/A',
            'total_jobs': 'N/A', 'total_hours': 'N/A', 'about': 'N/A',
            'profile_url': profile_url
        }
        
        # Print page title to debug
        print(f"Page title: {driver.title}")
        
        # Extract elements with try/except blocks for each section
        try:
            name_elements = driver.find_elements(By.XPATH, "//h2[@itemprop='name' and @data-v-4c3dc5a6]")
            if name_elements:
                profile_data['name'] = name_elements[0].text.strip()
                print(f"Found name: {profile_data['name']}")
        except Exception as e:
            print(f"Error getting name: {e}")
            
        try:
            position_elements = driver.find_elements(By.XPATH, "//h2[@data-v-7b2a5190]")
            if position_elements:
                profile_data['position'] = position_elements[0].text.strip()
                print(f"Found position: {profile_data['position']}")
        except Exception as e:
            print(f"Error getting position: {e}")
            
        try:
            country_elements = driver.find_elements(By.XPATH, "//p[@data-v-93403cd2]")
            if country_elements:
                profile_data['country'] = country_elements[0].text.strip()
                print(f"Found country: {profile_data['country']}")
        except Exception as e:
            print(f"Error getting country: {e}")
            
        try:
            rate_elements = driver.find_elements(By.XPATH, "//span[@data-v-7b2a5190]")
            if rate_elements:
                profile_data['hourly_rate'] = rate_elements[0].text.strip()
                print(f"Found hourly rate: {profile_data['hourly_rate']}")
        except Exception as e:
            print(f"Error getting hourly rate: {e}")
            
        try:
            job_success_elements = driver.find_elements(By.XPATH, "//span[@data-v-015e54d8 and @data-test='badge-hidden-label']")
            if job_success_elements:
                profile_data['job_success'] = job_success_elements[0].text.strip()
                print(f"Found job success: {profile_data['job_success']}")
        except Exception as e:
            print(f"Error getting job success: {e}")
        
        # Parse page with BeautifulSoup
        try:
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # Scrape About
            try:
                about_elem = soup.select_one("span.text-pre-line.break")
                if about_elem:
                    profile_data['about'] = about_elem.text.strip().replace('\n', ' | ')
                    print(f"Scraped About: {profile_data['about'][:50]}..." if len(profile_data['about']) > 50 else f"Scraped About: {profile_data['about']}")
            except Exception as e:
                print(f"Error scraping About: {e}")
            
            # Scrape Total Jobs
            try:
                total_jobs_elem = soup.select_one("div.col-compact.min-with-75 span.text-base-sm.text-light-on-inverse:-soup-contains('Total jobs')")
                if total_jobs_elem:
                    total_jobs_span = total_jobs_elem.find_previous('div', class_='stat-amount h5').find('span')
                    if total_jobs_span:
                        profile_data['total_jobs'] = total_jobs_span.text.strip()
                        print(f"Scraped Total Jobs: {profile_data['total_jobs']}")
            except Exception as e:
                print(f"Error scraping Total Jobs: {e}")
            
            # Scrape Total Hours
            try:
                total_hours_elem = soup.select_one("div.col-compact.min-with-75 span.text-base-sm.text-light-on-inverse:-soup-contains('Total hours')")
                if total_hours_elem:
                    total_hours_span = total_hours_elem.find_previous('div', class_='stat-amount h5').find('span')
                    if total_hours_span:
                        profile_data['total_hours'] = total_hours_span.text.strip()
                        print(f"Scraped Total Hours: {profile_data['total_hours']}")
            except Exception as e:
                print(f"Error scraping Total Hours: {e}")
                
        except Exception as e:
            print(f"Error in BeautifulSoup parsing: {e}")
        
        # Close the current tab and switch back
        print("Closing profile tab and returning to main tab")
        driver.close()
        
        # Switch back to the main tab (first in the list)
        driver.switch_to.window(driver.window_handles[0])
        
        return profile_data
    
    except Exception as e:
        print(f"Error scraping profile {profile_url}: {e}")
        
        # Make sure we return to the main tab even if there's an error
        try:
            # Check if we have multiple tabs open
            if len(driver.window_handles) > 1:
                # If we're not on the first tab, close current and go back
                if driver.current_window_handle != driver.window_handles[0]:
                    driver.close()
                driver.switch_to.window(driver.window_handles[0])
            print("Successfully returned to main tab after error")
        except Exception as cleanup_error:
            print(f"Error while trying to return to main tab: {cleanup_error}")
        
        return {
            'name': 'N/A', 'position': 'N/A', 'country': 'N/A',
            'hourly_rate': 'N/A', 'job_success': 'N/A',
            'total_jobs': 'N/A', 'total_hours': 'N/A', 'about': 'N/A',
            'profile_url': profile_url
        }




        



def save_and_exit(signal_received=None, frame=None):
    """Handle Ctrl+C signal and save data before exiting."""
    print("\nScript interrupted with Ctrl+C. Saving data...")
    save_to_csv(freelancer_data)
    save_to_json(freelancer_data)
    print("Data saved. Exiting...")
    sys.exit(0)

def scrape_freelancers():
    """Scrape data for all freelancers across multiple pages using Selenium and bs4."""
    global freelancer_data
    freelancer_data = []
    max_pages = 5  # Adjust this number based on how many pages you want to scrape
    
    # Register the signal handler for Ctrl+C
    signal.signal(signal.SIGINT, save_and_exit)
    
    driver = init_driver()
    
    try:
        for page in range(1, max_pages + 1):
            # Navigate to the search page for the current page
            search_url = f"https://www.upwork.com/nx/search/talent/?loc=americas&q=front%20end%20developer&page={page}"
            print(f"Opening search page: {search_url}")
            driver.get(search_url)
            
            # Wait for freelancers to load
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, '//h5[contains(@class, "name")]/a'))
            )
            
            # Get all freelancer elements
            name_elements = driver.find_elements(By.XPATH, '//h5[contains(@class, "name")]/a')
            rate_elements = driver.find_elements(By.XPATH, '//span[@data-test="rate-per-hour"]')
            country_elements = driver.find_elements(By.XPATH, '//p[contains(@class, "location")]')
            job_success_elements = driver.find_elements(By.XPATH, '//span[@data-test="badge-hidden-label"]/preceding-sibling::span')
            position_elements = driver.find_elements(By.XPATH, '//div[contains(@class, "air3-line-clamp")]/h4/a')
            
            print(f"Found {len(name_elements)} freelancers on page {page}")
            
            if not name_elements:
                print(f"No more freelancers found on page {page}. Stopping.")
                break
            
            # Parse search page with BeautifulSoup for skills
            search_soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            num_entries = min(len(name_elements), len(rate_elements), len(country_elements),
                             len(job_success_elements), len(position_elements))
            
            for i in range(num_entries):
                try:
                    profile_url = name_elements[i].get_attribute('href')
                    # name = name_elements[i].text.strip()
                   
                    # hourly_rate = rate_elements[i].text.strip() if i < len(rate_elements) else "N/A"
                    # country = country_elements[i].text.strip() if i < len(country_elements) else "N/A"
                    # job_success = job_success_elements[i].text.strip() if i < len(job_success_elements) else "N/A"
                    # position = position_elements[i].text.strip() if i < len(position_elements) else "N/A"
                    
                    print(f"Scraping freelancer: {profile_url} (URL: {profile_url})")
                    
                    # Scrape Skills from search page
                    skills = []
                    try:
                        skill_containers = search_soup.select(f'div:nth-child({i+1}) .air3-token-container')
                        if skill_containers:
                            skill_elements = skill_containers[0].select('.air3-token')
                            skills = [skill.text.strip() for skill in skill_elements[:-1] if skill.text.strip()]
                        else:
                            skills = 'N/A'
                        print(f"Scraped Skills: {skills}")
                    except Exception as e:
                        print(f"Error scraping Skills for {profile_url}: {e}")
                    
                    # Get detailed profile information
                    profile_details = get_profile_details(driver, profile_url)
                    
                    # Combine all data
                    freelancer = {
                        'name': profile_details[name],
                        'hourly_rate': profile_details[hourly_rate],
                        'country': profile_details[country],
                        'job_success': profile_details[job_success],
                        'position': profile_details[position],
                        'skills': ', '.join(skills) if skills else "N/A",
                        'total_jobs': profile_details['total_jobs'],
                        'total_hours': profile_details['total_hours'],
                        'about': profile_details['about'],
                        'profile_url': profile_url
                    }
                    
                    freelancer_data.append(freelancer)
                    print(f"Completed scraping {profile_url} - Data: {freelancer}")
                    time.sleep(random.uniform(2, 5))  # Polite delay to avoid rate limiting
                
                except Exception as e:
                    print(f"Error processing freelancer {i+1} on page {page}: {e}")
                    continue
        
            # Add extra delay between pages
            time.sleep(random.uniform(5, 10))  # Longer delay between page navigations
        
        # Save data
        save_to_csv(freelancer_data)
        save_to_json(freelancer_data)
        
        # Print summary
        print("\nFinal Results for All Freelancers Across Pages:")
        for freelancer in freelancer_data:
            print(f"Name: {freelancer['name']}")
            print(f"Hourly Rate: {freelancer['hourly_rate']}")
            print(f"Country: {freelancer['country']}")
            print(f"Job Success: {freelancer['job_success']}")
            print(f"Position: {freelancer['position']}")
            print(f"Skills: {freelancer['skills']}")
            print(f"Total Jobs: {freelancer['total_jobs']}")
            print(f"Total Hours: {freelancer['total_hours']}")
            print(f"About: {freelancer['about']}")
            print(f"Profile URL: {freelancer['profile_url']}")
            print("---")
        
    except KeyboardInterrupt:
        print("\nScript interrupted with Ctrl+C. Saving data...")
        save_to_csv(freelancer_data)
        save_to_json(freelancer_data)
        print("Data saved. Exiting...")
    except Exception as e:
        print(f"Unexpected error: {e}")
        print("Page source snippet:")
        print(driver.page_source[:1000])
        save_to_csv(freelancer_data)
        save_to_json(freelancer_data)
    
    finally:
        try:
            driver.quit()
            print("Driver closed.")
        except OSError as e:
            print(f"Ignored cleanup error (common with undetected_chromedriver): {e}")
        except Exception as e:
            print(f"Error closing driver: {e}")
        save_to_csv(freelancer_data)
        save_to_json(freelancer_data)

if __name__ == "__main__":
    scrape_freelancers()