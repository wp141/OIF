OIF Ventures Software Engineering Intern Take-Home Task
=======================================================

The task of scraping Tripadvisor's QANTAS review page for 1000 reviews has been accomplished with this program. This includes the bonus task of scraping the individual criteria sections of each review (if it exists). This implementation is interpretable, through this README and also in-code comments, and it is generalisable as it will work for any other similar-format Tripadvisor review page (tested on Virgin Australia as well).

Selenium is used to identify the review containers, which then scrapes each individual portion of the review further using their css selectors. Care has been taken to not include dynamically generated selectors which could cause the program to not be able to find the relevant information for other pages, i.e. rendering the program non-generalisable. The program must attempt to emulate a human visitor to the site, as Tripadvisor has quite strong anti-bot detection, which combined with the fact that there is only approximately 5 reviews per page, slows scraping significantly.

Extracting the data directly from the page manifest (stored in a \<script> tag) was explored (see unused file "manifest.py"), as it is more likely to not trigger bot detection and is more robust in data extraction, but it is not updated by the system beyond the first page, meaning reviews aside from the first page are not able to be collected. This approach is also less generalisable and therefore the standard selenium html element scraping method is employed.

Instructions
-----------
In the project directory, run:
1. `pip3 install requirements.txt`
2. `python3 app.py`

The program will ask you a few configuration questions. To produce the desired results of the take home assessment, input the following to each prompt:
1. `Please enter the Tripadvisor URL you would like to scrape (press ENTER to use default QANTAS page): <ENTER>`
2. `Please enter the number of reviews you would like to scrape from this url: 1000`
3. `Would you like to use slow mode? If you do not, your IP Address may be blocked, preventing future scraping (Y/n): N`
4. `Would you like to attempt to use a proxy? (y/N): N`

As previously mentioned, please note that due to the anti-bot measures specific to Tripadvisor, the scraping must emulate human behaviour and therefore scraping the desired number of reviews (1000) takes a non-trivial length of time. Additionally, the program must sleep on each page to avoid stale exceptions. After the above is run once (assuming answered N for slow mode), your IP address may be blocked temporarily by Tripadvisor, whereas if slow mode is enabled, it is much more unlikely. 

Anti-Detection Strategies
-----------
The program uses two primary strategies to counter Tripadvisor's anti-bot measures:
1. Mimic Human-Like Behaviour: this involves a series of random scrolling movements and delays to act like a human site visitor. The disadvantage of this (especially delays) is that it significantlly slows the scraping process. It is however necessary as without these delays, the scraper is promptly presented with a Captcha, such that even if it is solved by a supervising user, the IP address is still blocked. A level of delays (2-5s) however is necessary for the scraper to work, as the virtual DOM of React (which the site is made with) needs time to populate the new data. Not having this delay results in duplicate reviews being added, and stale element exceptions.
2. Proxies: proxy capability is built into this program, however the current implementation scrapes public proxies from https://www.sslproxies.org/, which are slow and often do not even meet the speed requirement to avoid a timeout. Utilising a robust proxy/proxies would be extremely beneficial in scraping this site. For instance, they could help avoid blocked IPs stopping scraping by cycling proxies.

Robustness
-----------
- If the program (non-proxied) cannot scrape all reviews requested, it will still write all reviews it was able to scrape to the output files.
- If the program (proxied) cannot scrape all reviews requested, it will attempt to use another proxy and try again. The best result will be written to the output files.
- Program checks that it has not already scraped a review before adding it to the review array, by using a "seen" set.
- Proxies are tested using http://httpbin.org/ip to ensure the proxy has been correctly registered with the driver.
- If there are missing values for the individual criteria ratings (i.e. user did not rate that criteria), the criteria values are assigned to -1.
- As previously mentioned, program is generalisable as it can scrape reviews from other similar pages on Tripadvisor, e.g. https://www.tripadvisor.com.au/Airline_Review-d8728931-Reviews-or5-Virgin-Australia.html#REVIEWS
- Comprehensive use of both defensive programming and try-except blocks to prevent uncaught exceptions, and to continue execution in the event of an exception where appropriate.
- The program clicks "read more" for each review prior to scraping it, to ensure the full content of the review, as well as any potential individual criteria ratings are available to be scraped.

Limitations
-----------
- Potential cause for concern is that because the reviews array and "seen" set are kept in memory, if the reviews requested is sufficiently large, program will run out of memory. This can be remedied by iteratively writing each review to the csv and json files, however this may sacrifice scraping speed.
- Currently all data is written to the files as strings as there was no specific requirement regarding the format, however this can easily be changed by casting the relevant variables to an appropriate data type, e.g. ratings to integers.

Data Format
-----------
| Desired Data            | Variable Names         |
|-------------------------|------------------------|
| Rating                  | rating                 |
| Review Title            | review_title           |
| Date of Travel          | travel_date            |
| Seat comfort            | seat_comfort           |
| In-flight Entertainment | inflight_entertainment |
| Customer service        | customer_service       |
| Value for money         | value_for_money        |
| Cleanliness             | cleanliness            |
| Check-in and boarding   | checkin_and_boarding   |
| Food and Beverage       | food_and_beverage      |