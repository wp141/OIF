import json
import time
import random
import requests
import csv
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from fake_useragent import UserAgent

# Write reviews to reviews.csv
def write_to_csv(reviews):
    try:
        keys = reviews[0].keys()
        with open('reviews.csv', 'w', newline='', encoding='utf-8') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(reviews)
            print(f'{len(reviews)} reviews successfully written to csv file.')

    except Exception as e:
        print(f"Error writing reviews to csv file: {e}")

# Write reviews to json.csv
def write_to_json(reviews):
    try:
        with open('reviews.json', 'w') as output_file:
            json.dump(reviews, output_file)
            print(f'{len(reviews)} reviews successfully written to json file.')

    except Exception as e:
        print(f"Error writing reviews to json file: {e}")

# Scrape SSL Proxies website for list of available proxies
def get_proxies():
    response = requests.get('https://www.sslproxies.org/')
    proxies_str = response.text.split('<textarea class="form-control" readonly="readonly" rows="12" onclick="select(this)">')[1].split("</textarea>")[0]
    proxies_arr = proxies_str.split('\n')

    proxies = []
    for str in proxies_arr:
        if len(str) > 1:
            if str[0].isdigit():
                proxy = str.strip()
                proxies.append(proxy)
                
               
    
    random.shuffle(proxies)
    return proxies

# Ensures page is loaded before further action is taken
def wait_for_page_load(driver, timeout=10):
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )
    except Exception as e:
        print(f"Page did not load: {e}")

# Random delay to avoid bot detection
def random_delay(min_delay=2, max_delay=5):
    delay = random.uniform(min_delay, max_delay)
    print(f"Sleeping for {delay:.2f} seconds.")
    time.sleep(delay)

# Random mouse movement to avoid bot detection
def random_interaction(driver):
    wait_for_page_load(driver)
    max_x, max_y = driver.execute_script("return [window.innerWidth, window.innerHeight];")

    # Ensure random movement within bounds
    while True:
        x = random.randint(10, max_x - 1)
        y = random.randint(10, max_y - 1)

        if 0 < x < max_x and 0 < y < max_y:
            print(f"Performing random action: scrolling to ({x}, {y}) within ({max_x}, {max_y})")
            script = f"window.scrollTo({x}, {y});"
            driver.execute_script(script)
            break
        else:
            print(f"Out of bounds: Tried to move to ({x}, {y}) within ({max_x}, {max_y})")

# Generate random user agent to avoid bot detection
def randomize_user_agent(driver):
    ua = UserAgent()
    user_agent = ua.random
    driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": user_agent})
    print(f'User-Agent set to: {user_agent}')

# Initialise chrome driver with anti-bot detection measures, optional proxy connection
# Does not run in headless mode to avoid detection
def init_driver(proxy=None):
    print("Initialising driver...")
    try:
        if proxy:
            user_agent = UserAgent(browsers=["chrome"])
            options = uc.ChromeOptions()
            options.add_argument(f'--proxy-server=http://{proxy}') # proxy request to obfuscate origin
            options.add_argument(f'user-agent={user_agent.chrome}') # randomise user agent data
            options.add_argument('--disable-blink-features=AutomationControlled') # may assist in avoiding detection according to community consensus
            options.add_argument('--disable-notifications')
            driver = uc.Chrome(enable_cdp_events=True, options=options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})") # helps to appear non-automated
            randomize_user_agent(driver)
            print(f"Driver intialised with proxy {proxy}.")
        else:
            user_agent = UserAgent(browsers=["chrome"])
            options = uc.ChromeOptions()
            options.add_argument(f'user-agent={user_agent.chrome}') # randomise user agent data
            options.add_argument('--disable-blink-features=AutomationControlled') # may assist in avoiding detection according to community consensus
            options.add_argument('--disable-notifications')
            driver = uc.Chrome(enable_cdp_events=True, options=options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})") # helps to appear non-automated
            randomize_user_agent(driver)
            print(f"Driver intialised.")

        return driver
    
    except Exception as e:
        print(f"Error initialising driver: {e}")
        print("Exiting...")
        exit()

# Test proxy can be connected to
def test_proxy(proxy):
    try:
        response = requests.get("http://httpbin.org/ip", proxies={"http": f"http://{proxy}", "https": f"https://{proxy}"}, timeout=10)
        print("Proxy is working:", response.text)
        return True
    except Exception as e:
        print("Proxy test failed:", e)
        return False
    
# Scrape reviews for each page by finding all review containers, breaking them down into their elements, and creating dictionary for each
def scrape_reviews(url, num_reviews, proxy, slow):
    if proxy:
        print(f"Trying proxy {proxy}...")
        if not test_proxy(proxy):
            print(f"Proxy {proxy} unavailable.")
            return []
    
        driver = init_driver(proxy)
    else:
        driver = init_driver()

    driver.get(url)
   
    reviews = []
    seen = set()
    try:
        while len(reviews) < num_reviews:
            wait_for_page_load(driver)
            if slow: random_delay()
            try:
                WebDriverWait(driver=driver, timeout=20).until(
                        EC.presence_of_element_located((By.XPATH, '//div[@data-reviewid]'))
                    )
                print("Review containers found.")
                
            except Exception as e:
                # Captcha likely encountered
                print(f"Error finding review containers: IP Blocked or Invalid URL provided")
                break
            
            random_interaction(driver)

            review_containers = driver.find_elements(By.XPATH, '//div[@data-reviewid]')
            if not review_containers:
                # No reviews on this page
                print("No review containers found after waiting.")
                break

            for container in review_containers:
                if len(reviews) >= num_reviews:
                    break
                try:
                    read_more_button = container.find_element(By.CSS_SELECTOR, 'span[class$="_S Z"]')
                    driver.execute_script("arguments[0].click();", read_more_button)
                    if slow: random_delay()
                    random_interaction(driver)

                    rating_element = container.find_element(By.XPATH, './/span[contains(@class, "ui_bubble_rating")]')
                    review_rating = rating_element.get_attribute('class').split('_')[-1][0]
                    review_title = container.find_element(By.CSS_SELECTOR, 'a[class$="Qwuub"]').text
                    review_content = container.find_element(By.CSS_SELECTOR, 'span[class$="H4 _a"]').text
                    travel_date = container.find_element(By.CSS_SELECTOR, 'span[class$="_R Me S4 H3"]').text.split(": ")[1]
                
                    criteria_ratings_divs = container.find_elements(By.CSS_SELECTOR, 'div[class$="S2 H2"]')
                    criteria_dict = dict()
                    if criteria_ratings_divs:
                        for criteria_div in criteria_ratings_divs:
                            rating_element = criteria_div.find_element(By.XPATH, './/span[contains(@class, "ui_bubble_rating")]')
                            rating = rating_element.get_attribute('class').split('_')[-1][0]
                            criteria_dict[criteria_div.text] = rating
                    else:
                        print("Review has no individual criteria ratings.")

                    review_dict = {
                        "rating": review_rating,
                        "review_title": review_title,
                        "review_content": review_content,
                        "travel_date": travel_date,
                        "legroom": criteria_dict.get("Legroom", -1),
                        "seat_comfort": criteria_dict.get("Seat comfort", -1),
                        "inflight_entertainment": criteria_dict.get("In-flight Entertainment", -1),
                        "customer_service": criteria_dict.get("Customer service", -1),
                        "value_for_money": criteria_dict.get("Value for money", -1),
                        "cleanliness": criteria_dict.get("Cleanliness", -1),
                        "checkin_and_boarding": criteria_dict.get("Check-in and boarding", -1),
                        "food_and_beverage": criteria_dict.get("Food and Beverage", -1)
                    }

                    review_tuple = (review_title, review_content)
                    if review_tuple in seen:
                        print("Review is duplicate.")
                        continue
                    else:
                        seen.add(review_tuple)

                    reviews.append(review_dict)
                    print(f"Added review \"{review_title}\".")

                    if len(reviews) == num_reviews:
                        driver.quit()
                        return reviews

                    if slow: random_delay()
                    wait_for_page_load(driver)

                except Exception as e:
                    print(f"Error extracting data from container {review_containers.index(container)}, error: {e}")

            print(f"Scraped {len(reviews)}/{num_reviews} reviews so far.")

            try:
                random_interaction(driver)
                WebDriverWait(driver=driver, timeout=20).until(
                        EC.presence_of_element_located((By.XPATH, '//div[@data-reviewid]'))
                    )
                next_button = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.XPATH, '//a[contains(@class, "ui_button nav next primary")]'))
                )
                
                next_button.click()
                print("Clicked next button.")
                wait_for_page_load(driver)
                WebDriverWait(driver=driver, timeout=20).until(
                        EC.presence_of_element_located((By.XPATH, '//div[@data-reviewid]'))
                    )
                
                random_delay()

            except Exception as e:
                print(f"Error clicking next button: {str(e)}")
                break

        
        if len(reviews) == num_reviews:
            driver.quit()
            return reviews

    except Exception as e:
        print(f"Error during scraping: {e}")

    finally:
        driver.quit()
        time.sleep(random.uniform(1, 5))
    
    return reviews

# Allow custom uer input => allows generalisation
def retrieve_input():
    url = ""
    num_reviews = 0
    slow = True
    proxy = False

    while True:
        url = input("Please enter the Tripadvisor URL you would like to scrape (press ENTER to use default QANTAS page): ").strip()
        if url == "":
            url = "https://www.tripadvisor.com.au/Airline_Review-d8729133-Reviews-Qantas.html#REVIEWS"
            break
        elif not url.startswith("https://www.tripadvisor.com.au/"):
            print("Invalid URL, URL must start with 'https://www.tripadvisor.com.au/'.")
        else:
            break
    
    while True:
        num_reviews = input("Please enter the number of reviews you would like to scrape from this url: ").strip()
        if not num_reviews.isdigit() or int(num_reviews) <= 0:
            ("Invalid number, please enter a positive integer.")
        else:
            break
    
    while True:
        slow = input("Would you like to use slow mode? If you do not, your IP Address may be blocked, preventing future scraping (Y/n): ").strip()
        if slow.lower() not in ["n", "y"]:
            print("Invalid selection, please enter Y or N")
        else:
            if slow.lower() == "n":
                slow = False
            else:
                slow = True
            break

    while True:
        proxy = input("Would you like to attempt to use a proxy? (y/N): ").strip()
        if proxy.lower() not in ["n", "y"]:
            print("Invalid selection, please enter Y or N")
        else:
            if proxy.lower() == "n":
                proxy = False
            else:
                proxy = True
            break

    return url.strip(), int(num_reviews.strip()), slow, proxy

def main(url="https://www.tripadvisor.com.au/Airline_Review-d8729133-Reviews-Qantas.html#REVIEWS", num_reviews=10, slow=True, proxy=False):
    url, num_reviews, slow, proxy = retrieve_input()
    best_reviews = []

    if proxy:
        proxies = get_proxies()
    
        for proxy in proxies:
            if len(best_reviews) > 0:
                print("Retrying...")

            reviews = scrape_reviews(url, num_reviews, proxy, slow)

            if len(reviews) == num_reviews:
                best_reviews = reviews
                break
            elif len(reviews) > len(best_reviews):
                print(f"Proxy {proxy} only scraped {len(reviews)}/{num_reviews} reviews for url {url}")
                best_reviews = reviews
            else:
                print(f"Proxy {proxy} failed to scrape reviews for url {url}")
    else:
        start_time = time.time()
        best_reviews = scrape_reviews(url, num_reviews, proxy, slow)
        elapsed = time.time() - start_time
        print(f"Scraping finished after {round(elapsed)}s")

    
    if len(best_reviews) == num_reviews:
        print("Writing reviews to files...")
        write_to_csv(best_reviews)
        write_to_json(best_reviews)
        print(f"Successfully scraped {num_reviews}/{num_reviews} reviews from {url} and wrote them to files.")
        
    elif (len(best_reviews)) > 0:
        print("Writing reviews to files...")
        write_to_csv(best_reviews)
        write_to_json(best_reviews)
        print(f"Only scraped {len(best_reviews)}/{num_reviews} reviews for url {url} and wrote them to files.")

    else:
        print("Failed to scrape reviews, exiting...")

    print("Exiting...")
    return

if __name__ == "__main__":
    main()