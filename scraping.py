from . import utils
# import utils
from bs4 import BeautifulSoup
from selenium.webdriver.firefox.options import Options
import os
from selenium import webdriver

# Init a Firefox driver (replace the next line to the path to your own user profile)
firefox_user_path = "~/.mozilla/firefox/gu16idx8.default/"
profile = webdriver.FirefoxProfile(os.path.expanduser(firefox_user_path))

options = Options()
options.set_headless(True)
browser = webdriver.Firefox(profile, options=options)

def get_airbnb_info(url):
    info = {}

    # Load the page
    browser.get(url)

    # Initialize BS
    html = browser.page_source
    soup = BeautifulSoup(html, 'html.parser')

    # Get the main image for the page from the meta tag if it exists
    main_image = soup.find('meta', {'property': 'og:image'})
    if main_image:
        info['main_image'] = main_image['content']

    # Check that it is a type of page we parse
    if utils.page_type(url) != utils.BNB:
        info['title'] = soup.title.string
        print('did not parse', info)
        return info

    # Get the property's Title
    title = soup.find('h1', {'class': '_fecoyn4'})
    info['title'] = title.text

    # Define some helper functions
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

    # Get location text
    location = soup.find('div', {'class': "_ncwphzu"})
    info['location'] = location.text

    return info


if __name__ == '__main__':
    url ='https://www.airbnb.com/rooms/2306865?'
    # browser.get(url)
    # html = browser.page_source
    #
    # html = browser.page_source
    # soup = BeautifulSoup(html, 'html.parser')
    #
    # location = soup.find('div', {'class': "_ncwphzu"})
    #
    # print(location.text)

    print('Initialized browser. Beginning scrape.')
    info = get_airbnb_info(url)
    print(info)





