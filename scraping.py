import requests
# from . import utils
import utils
from bs4 import BeautifulSoup
# from selenium import webdriver
import urllib.request
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import os
from selenium import webdriver
import re



# Init a Firefox driver (replace the next line to the path to your own user profile)
firefox_user_path = "~/.mozilla/firefox/gu16idx8.default/"
profile = webdriver.FirefoxProfile(os.path.expanduser(firefox_user_path))

options = Options()
options.set_headless(True)
browser = webdriver.Firefox(profile, options=options)

def get_airbnb_info(url):
    info = {}
    browser.get(url)
    # delay = 3
    # WebDriverWait(browser, delay).until(EC.presence_of_element_loacted(By.Class, '_1thk0tsb'))

    html = browser.page_source
    soup = BeautifulSoup(html, 'html.parser')
    print(soup.title.string)

    # Check that it is a type of page we parse
    if utils.page_type(url) != utils.BNB:
        info['title'] = soup.title.string
        print('failed 1', info)
        return info

    # Get the property's Title
    title = soup.find('h1', {'class': '_fecoyn4'})
    info['title'] = title.text


    get_by_class = lambda parent, c: [tag.text for tag in parent.findAll('span', {'class': c})]
    get_by_all_classes = lambda parent, classes: [get_by_class(parent, c) for c in classes]
    flatten = lambda l : [item for sublist in l for item in sublist]

    # Get information about the rooms and number of guests
    pos_bold_text_classes = ['_12i0h32r', '_fgdupie']  # These seem to unpredictably alternate
    one_up = '_1thk0tsb'
    parent_tags = soup.findAll('div', {'class': one_up})
    pos_room_info = []
    for parent_tag in parent_tags:
        pos_room_info += flatten(get_by_all_classes(parent_tag, pos_bold_text_classes))

    is_info_item = lambda text: text.endswith('guests') or text.endswith('bedroom') or text.endswith('beds') or text.endswith('bath')
    info['rooms'] = []
    for info_item in pos_room_info:
        if is_info_item(info_item) and info_item not in info['rooms']:
            info['rooms'].append(info_item)

    print(info['rooms'])

    # possible_classes = ['_fgdupie', '_12i0h32r']
    # guests = [get_by_class(c) for c in possible_classes]
    # info['rooms'] = flatten(guests)

    # info['rooms'] = []
    # for guest_item in guests:
    #     bullet = guest_item.find('span', {'class': '_12i0h32r'})
    #     if bullet:
    #         info['rooms'].append(str(bullet.text))
    #
    # if len(info['rooms']) < 4 or \
    #         'guests' not in info['rooms'][0] or \
    #         'bedroom' not in info['rooms'][1]:
    #     print('failed', info)
    #     return get_airbnb_info(url)

    # Get images
    images = soup.findAll('img')
    links = [image['src'] for image in images if image['src'].startswith('https://') and '/users/' not in image['src']]
    info['images'] = links

    # Get map image
    map = soup.find('div', {'class': '_1fmyluo4'})
    map_image = map.find('img')
    info['map'] = map_image['src']

    print(info)
    return info


if __name__ == '__main__':
    url ='https://www.airbnb.com/rooms/2306865?'
    # html = requests.get(url)
    # response = urllib.request.urlopen(url)
    # html = response.read().decode('utf-8')

    browser.get(url)
    html = browser.page_source
    #
    # soup = BeautifulSoup(html, 'html.parser')
    # print(soup.prettify())
    print('scraping')
    info = get_airbnb_info(url)
    print('info')





