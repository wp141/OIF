'''
def scrape_reviews_manifest(url, num_reviews, proxy):
    driver = init_driver(proxy)
    driver.get(url)

    wait_for_page_load(driver)
    html = driver.page_source
    manifest_data = rf'{re.findall(r"pageManifest:({.+?})};", html, re.DOTALL)[0]}'
    manifest_json = json.loads(rf'{manifest_data}')
    manifest_results = manifest_json["urqlCache"]["results"]
    reviews_cache_id = -1

    # print(manifest_results)
    for result in manifest_results:
        try:
           
           data_str = manifest_results[result]["data"]
           data_dict = json.loads(rf'{data_str}')
           reviews = data_dict["locations"][0]["reviewListPage"]["reviews"]
           reviews_cache_id = result
           print(f"Found cache ID of reviews: {reviews_cache_id}")
           break
        except Exception as e:
            continue
    
    if reviews_cache_id == -1:
        print("Unable to find reviews in manifest.")
        return []
    
    reviews_arr = []
    while len(reviews_arr) != num_reviews:
        random_interaction(driver)
        
        html = driver.page_source
        data = re.findall(r"pageManifest:({.+?})};", html, re.DOTALL)[0]
        data = rf'{data}'
        reviews_json = json.loads(data)
        data_str = (reviews_json["urqlCache"]["results"][reviews_cache_id]["data"])
        reviews_dict = json.loads((rf'{data_str}'))
        reviews = reviews_dict["locations"][0]["reviewListPage"]["reviews"]

        for review in reviews:
            if len(reviews_arr) == num_reviews:
                break

            criteria_arr = review["additionalRatings"]
            criteria_dict = {}
            for rating_dict in criteria_arr:
                label = rating_dict["ratingLabel"]
                rating = rating_dict["rating"]
                criteria_dict[label] = rating

            review_dict = {
                "rating": review["rating"],
                "review_title": review["title"],
                "review_content": review["text"],
                "travel_date": review["tripInfo"]["stayDate"],
                "legroom": criteria_dict.get("Legroom", -1),
                "seat_comfort": criteria_dict.get("Seat comfort", -1),
                "inflight_entertainment": criteria_dict.get("In-flight Entertainment", -1),
                "customer_service": criteria_dict.get("Customer service", -1),
                "value_for_money": criteria_dict.get("Value for money", -1),
                "cleanliness": criteria_dict.get("Cleanliness", -1),
                "checkin_and_boarding": criteria_dict.get("Check-in and boarding", -1),
                "food_and_beverage": criteria_dict.get("Food and Beverage", -1)
            }

            reviews_arr.append(review_dict)

        try:
            print(f"Scraped {len(reviews_arr)}/{num_reviews} so far.")
            random_interaction(driver)
            next_button = WebDriverWait(driver=driver, timeout=10).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@data-reviewid]'))
                )

            
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//a[contains(@class, "ui_button nav next primary")]'))
            )
            next_button.click()
            random_delay()

        except Exception as e:
            print(f"Error clicking next button: {str(e)}")
            driver.quit()
            break


    driver.quit()
    return reviews_arr
'''