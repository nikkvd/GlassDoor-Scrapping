from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd
import os
from datetime import datetime
import chromedriver_autoinstaller


def scrape_glassdoor_reviews(company_name, email, password,max_page = 5):
    options = webdriver.ChromeOptions()
    options.binary_location = "/usr/bin/chromium"  # Point to Chromium binary
    options.add_argument("--start-maximized")  # Your original argument
    options.add_argument("--headless")  # Required for Streamlit Cloud (no GUI)
    options.add_argument("--no-sandbox")  # Required for containerized environments
    options.add_argument("--disable-dev-shm-usage")  # Avoid shared memory issues
    
    # Initialize the driver with ChromeDriverManager
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    
    # Set up WebDriverWait
    wait = WebDriverWait(driver, 30)
    
    try:
        base_url = "https://www.glassdoor.com"
        print(f"Opening Glassdoor at {base_url}...")
        driver.get(base_url)
        time.sleep(2)
        print("Current URL:", driver.current_url)
        print("Page title:", driver.title)
        
        # with open("page_source_initial.html", "w", encoding="utf-8") as f:
        #     f.write(driver.page_source)
        
        # Step 1: Enter email and click Continue
        email_field = wait.until(EC.presence_of_element_located(
    (By.XPATH, "//input[@type='email' or contains(@placeholder, 'Email')]")))
        email_field.send_keys(email)
        
        print("Locating Continue button...")
        continue_button = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[@data-test='email-form-button']")
        ))
        print(f"Continue button text: '{continue_button.text}'")
        continue_button.click()
        time.sleep(2)
        
        # with open("page_source_after_continue.html", "w", encoding="utf-8") as f:
        #     f.write(driver.page_source)
        print("Current URL after Continue:", driver.current_url)
        
        # Step 2: Enter password and sign in
        print("Locating password field...")
        password_field = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//input[@type='password' or contains(@placeholder, 'Password')]")
        ))
        password_field.send_keys(password)
        
        print("Locating Sign In button...")
        sign_in_button = wait.until(EC.element_to_be_clickable(
            (By.XPATH,  "//div[contains(@class, 'ButtonContainer')]/button[contains(@class, 'Button') and @type='submit']")
        ))
        print(f"Sign In button text: '{sign_in_button.text}'")
        print(f"Sign In button HTML: {sign_in_button.get_attribute('outerHTML')}")
        
        print("Attempting to sign in with click...")
        sign_in_button.click()
        time.sleep(5)
        
        # Post-sign-in checks
        print("Current URL after sign-in:", driver.current_url)
        print("Page title after sign-in:", driver.title)
        
        # with open("page_source_after_signin.html", "w", encoding="utf-8") as f:
        #     f.write(driver.page_source)
        
        # Check if back at email page
        try:
            email_field = driver.find_element(By.XPATH, "//input[@type='email' or contains(@placeholder, 'Email')]")
            print("Email field found after sign-in, login failed!")
            driver.save_screenshot("signin_failed.png")
            time.sleep(10)  # Pause for manual inspection
            raise Exception("Login failed: Returned to email entry page")
        except:
            print("Email field not found, checking for login success...")
        
        # Verify login success
        print("Checking if login succeeded...")
        
        # Wait for page to load
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        print("Login successful, proceeding to search...")
        
        search = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@data-test='search-button']")))
        
        search.click()
        time.sleep(5)
        
        
        search_bar = wait.until(EC.presence_of_element_located((By.ID, "sc.keyword")))
        
        
        # Search for company
        search_bar.send_keys(company_name)
        search_bar.send_keys(Keys.RETURN)
        time.sleep(3)
        
        # Save search results page for debugging
        # print("Current page source after search:")
        # with open("search_results_page.html", "w", encoding="utf-8") as f:
        #     f.write(driver.page_source)
        
        # Print all potential company links for debugging
        print("Debugging company links...")
        elements = driver.find_elements(By.XPATH, "//a[contains(@href, '/Overview/Working-at')]")
        print(f"Found {len(elements)} potential company links")
        for i, element in enumerate(elements):
            print(f"Link {i+1}: {element.text}")
            print(f"HTML: {element.get_attribute('outerHTML')}")
        
        print("Selecting company...")
        try:
            # Find the "Companies" section using the data-test attribute
            companies_section = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//div[@data-test='companies-module']")
            ))
            # Select the first company card within the "Companies" section
            company_link = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//div[@data-test='companies-module']//div[contains(@class, 'CompanyCard_employerCardWrapper__H_LZN')][1]//a")
            ))
            # Extract the company name for logging
            company_name_text = company_link.find_element(By.XPATH, ".//span[contains(@class, 'employer-card_employerName__YXH4h')]").text
            print(f"Found first company card: {company_name_text}")
        except Exception as e:
            print(f"Error selecting the first company card: {str(e)}")
            # Fallback: Try a more generic approach
            company_link = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//div[contains(@class, 'CompanyCard_employerCardWrapper__H_LZN')][1]//a")
            ))
            # Extract the company name for logging (fallback)
            try:
                company_name_text = company_link.find_element(By.XPATH, ".//span[contains(@class, 'employer-card_employerName__YXH4h')]").text
                print(f"Using fallback method, selected first company card: {company_name_text}")
            except:
                print("Using fallback method, but could not extract company name.")

        company_link.click()
        time.sleep(3)
        
        # Save page after clicking company
        # with open("company_page.html", "w", encoding="utf-8") as f:
        #     f.write(driver.page_source)
        
        print("Navigating to reviews...")
        try:
            reviews_tab = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//*[@data-ui-content='Reviews']")
            ))
            reviews_tab.click()
        except:
            # Alternative selector for reviews tab
            try:
                reviews_tab = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//a[contains(@href, '/Reviews/')]")
                ))
                reviews_tab.click()
            except:
                # If direct navigation fails, try building and navigating to reviews URL
                current_url = driver.current_url
                if '/Overview/' in current_url:
                    reviews_url = current_url.replace('/Overview/', '/Reviews/')
                    print(f"Direct navigation to reviews page: {reviews_url}")
                    driver.get(reviews_url)
        
        time.sleep(3)
        
        # Save reviews page
        # with open("reviews_page.html", "w", encoding="utf-8") as f:
        #     f.write(driver.page_source)
        
        all_reviews = []
        print("Scraping reviews...")
        page_number = 1
        while page_number <= max_page:  # Limit to max_pages
            print(f"Scraping page {page_number}...")
            
            # Scroll to the bottom to ensure all reviews are loaded
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # Wait for reviews to load
            try:
                reviews = wait.until(EC.presence_of_all_elements_located(
                        (By.XPATH, "//div[@id='ReviewsFeed']//div[contains(@class, 'module-container_moduleContainer__tpBfv')]")
                ))
                print(f"Found {len(reviews)} reviews on page {page_number}")
            except Exception as e:
                print(f"Error finding reviews on page {page_number}: {str(e)}")
                break
            
            if not reviews:
                print("No reviews found on this page. Stopping.")
                break
            
            for i, review in enumerate(reviews, 1):
                try:
                    print(f"Processing review {i} on page {page_number}...")
                    
                    # Scroll to the review to ensure it's in view
                    driver.execute_script("arguments[0].scrollIntoView(true);", review)
                    time.sleep(0.5)
                    
                    # Expand "Show more" if present
                    try:
                        show_more_button = review.find_element(By.CLASS_NAME, "expand-button_ExpandButton__Wevvg")
                        driver.execute_script("arguments[0].click();", show_more_button)
                        time.sleep(1)
                        print("Clicked 'Show more' button")
                    except:
                        print("No 'Show more' button found")
                    
                    # Extract rating (required field)
                    try:
                        rating = review.find_element(By.XPATH, ".//span[@data-test='review-rating-label']").text
                        
                    except Exception as e:
                        print(f"Error extracting rating for review {i} on page {page_number}: {str(e)}")
                        # Save the HTML of the problematic review for debugging
                        with open(f"problematic_review_page_{page_number}_review_{i}.html", "w", encoding="utf-8") as f:
                            f.write(review.get_attribute("outerHTML"))
                        continue  # Skip this review if rating is missing
                    
                    # Extract title (required field)
                    try:
                        title = review.find_element(By.XPATH, ".//h3[@data-test='review-details-title']").text
                        
                    except Exception as e:
                        print(f"Error extracting title for review {i} on page {page_number}: {str(e)}")
                        continue  # Skip this review if title is missing
                    
                    # Extract date (required field)
                    try:
                        date = review.find_element(By.CLASS_NAME, "timestamp_reviewDate__dsF9n").text
                        
                    except Exception as e:
                        print(f"Error extracting date for review {i} on page {page_number}: {str(e)}")
                        continue  # Skip this review if date is missing
                    
                    # Parse the date to extract the year and compare with the range
                    try:
                        # Date format is "DD Mon YYYY" (e.g., "17 Mar 2025")
                        review_date = datetime.strptime(date, "%d %b %Y")
                        review_year = review_date.year
                        
                    except ValueError as e:
                        print(f"Error parsing date '{date}' for review {i} on page {page_number}: {str(e)}")
                        continue  # Skip this review if date can't be parsed
                    
                    # Extract Pros
                    try:
                        pros = review.find_element(By.XPATH, ".//span[@data-test='review-text-PROS']").text
                        
                    except:
                        pros = "N/A"
                        
                    
                    # Extract Cons
                    try:
                        cons = review.find_element(By.XPATH, ".//span[@data-test='review-text-CONS']").text
                        
                    except:
                        cons = "N/A"
                        
                    
                    # Extract Advice to Management (optional)
                    try:
                        advice = review.find_element(By.XPATH, ".//span[@data-test='review-text-FEEDBACK']").text
                        
                    except:
                        advice = "N/A"
                        
                    
                    all_reviews.append({
                        "rating": rating,
                        "title": title,
                        "date": date,
                        "pros": pros,
                        "cons": cons,
                        "advice": advice
                    })
                    print(f"Successfully extracted review {i}")
                except Exception as e:
                    print(f"Unexpected error extracting review {i} on page {page_number}: {str(e)}")
                    continue
            
            
            
            try:
                next_button = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//button[@data-test='next-page']")
                ))
                if "disabled" in next_button.get_attribute("class"):
                    print("No more pages to scrape.")
                    break
                driver.execute_script("arguments[0].click();", next_button)
                time.sleep(3)
                page_number += 1
            except Exception as e:
                print(f"No more pages or error navigating to next page: {str(e)}")
                break
        
        if not all_reviews:
            print("No reviews were extracted. Check the page source and locators.")
        
        df = pd.DataFrame(all_reviews)
        print(f"Scraped {len(all_reviews)} reviews.")
        return df
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        # driver.save_screenshot("error_screenshot.png")
        return None
    
    finally:
        driver.quit()
