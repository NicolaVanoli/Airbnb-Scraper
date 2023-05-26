import requests
import sys
import json
from bs4 import BeautifulSoup

location = "Manerba-del-garda"
checkin_date = "2023-06-14" # YYYY-MM-DD
checkout_date = "2023-06-18" # YYYY-MM-DD


page_url = "https://www.airbnb.it/s/{}/homes?tab_id=home_tab&refinement_paths%5B%5D=%2Fhomes&flexible_trip_lengths%5B%5D=one_week&monthly_start_date=2023-06-01&monthly_length=3&price_filter_input_type=0&price_filter_num_nights=5&channel=EXPLORE&query={}&date_picker_type=calendar&checkin={}&checkout={}&flexible_date_search_filter_type=0&source=structured_search_input_header&search_type=autocomplete_click".format(location, location, checkin_date, checkout_date)

print(page_url)
def scrape_page(page_url):
    """Extracts HTML from a webpage"""
    
    answer = requests.get(page_url)
    content = answer.content
    soup = BeautifulSoup(content, features='html.parser')
    
    return soup

def extract_listing(page_url):
    """Extracts listings from an Airbnb search page"""
    
    page_soup = scrape_page(page_url)
    listings = page_soup.findAll("div", {"class": "c4mnd7m"})

    return listings

def extract_element_data(soup, params):
    """Extracts data from a specified HTML element"""
    
    # 1. Find the right tag
    if 'class' in params:
        elements_found = soup.find_all(params['tag'], params['class'])
    else:
        elements_found = soup.find_all(params['tag'])
        
    # 2. Extract text from these tags
    if 'get' in params:
        element_texts = [el.get(params['get']) for el in elements_found]
    else:
        element_texts = [el.get_text() for el in elements_found]
        
    # 3. Select a particular text or concatenate all of them
    tag_order = params.get('order', 0)
    if tag_order == -1:
        output = '**__**'.join(element_texts)
    else:
        output = element_texts[tag_order]
    
    return output


RULES_SEARCH_PAGE = {
    'prices': {'tag': 'div', 'class': '_tt122m'},
    'name': {'tag': 'span', 'class': 't6mzqp7 dir dir-ltr'},
    'type': {'tag': 'div', 'class': 't1jojoys', 'order': 0},
}


listing_soups = extract_listing(page_url)


features_list = []

print('Processing page 0')

for listing in listing_soups:
    
    features_dict = {}
    for feature in RULES_SEARCH_PAGE:
        features_dict[feature] = extract_element_data(listing, RULES_SEARCH_PAGE[feature])
    features_list.append(features_dict)



def find_next_page_url(page_url):
    page_soup = scrape_page(page_url)
    next_page_url = page_soup.find('a', {'aria-label': 'Avanti'})
    # Check if the element is found
    if next_page_url:
        return 'https://www.airbnb.it' + next_page_url.get('href')
    else:
        return None


count= 0
while True:
    count += 1
    page_url = find_next_page_url(page_url)
    if page_url is None:
        for el in features_list:
            print(el)
        print(f'\nI found {len(features_list)} listings\n')
        break

    print(f'Processing page {count}')
    listing_soups = extract_listing(page_url)
    for listing in listing_soups:
        
        features_dict = {}
        for feature in RULES_SEARCH_PAGE:
            features_dict[feature] = extract_element_data(listing, RULES_SEARCH_PAGE[feature])
        features_list.append(features_dict)

with open('list.json', 'w') as json_file:
    json.dump(features_list, json_file)

# import time
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# driver = webdriver.Chrome()
# url = "https://www.airbnb.it/s/Venezia--Italy/homes?tab_id=home_tab&refinement_paths%5B%5D=%2Fhomes&flexible_trip_lengths%5B%5D=one_week&monthly_start_date=2023-06-01&monthly_length=3&price_filter_input_type=0&price_filter_num_nights=5&channel=EXPLORE&query=Venezia%2C%20Italy&place_id=ChIJKUgTyxaqfkcREH-QFYcJBwM&date_picker_type=calendar&checkin=2023-06-14&checkout=2023-06-18&flexible_date_search_filter_type=0&source=structured_search_input_header&search_type=autocomplete_click"
# driver.get(url)

# # Scroll to the bottom of the page
# while True:
#     # Scroll down to the bottom
#     driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

#     # Check if the button is visible
#     try:
#         button = driver.find_element(By.XPATH, "//a[@aria-label='Avanti']")
#         if button.is_displayed():
#             # Get the href value of the element
#             href = button.get_attribute("href")
#             break
#     except:
#         pass

# # Open the href
# driver.get(href)

# # Collect the HTML content of the new page
# new_page_html = driver.page_source

# # Process or scrape the collected HTML content as desired
# time.sleep(45)
# # Close the WebDriver
# driver.quit()