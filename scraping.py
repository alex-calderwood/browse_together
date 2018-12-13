from . import utils
# import utils
from bs4 import BeautifulSoup
# from selenium.webdriver.firefox.options import Options
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


chrome_options = Options()
chrome_options.add_argument("--headless")
browser = webdriver.Chrome('/usr/bin/chromedriver', chrome_options=chrome_options)


def scrape_site_info(url):
    info = {}

    # Load the page
    browser.get(url)

    # Initialize BS
    html = browser.page_source
    soup = BeautifulSoup(html, 'html.parser')

    # Do some logging, just in case
    f = open('./log/site.html', 'w')
    f.write(soup.prettify())
    f.close()

    # Get the main image for the page from the meta tag if it exists
    main_image = soup.find('meta', {'property': 'og:image'})
    if main_image:
        info['main_image'] = main_image['content']

    # Check that it is a type of page we parse
    if utils.page_type(url) == utils.BNB:
        return scrape_airbnb(soup, info)
    elif utils.page_type(url) == utils.HOSTEL:
        return scrape_hostel(soup, url, info)
    else:
        info['title'] = soup.title.string
        print('did not parse', info)
        return info


def scrape_hostel(soup, url, info):
    info['title'] = soup.find('h1', {'class': 'main-title'}).text

    # Get images
    image_tags = soup.findAll('img', {'class': 'gallery-image'})
    images = [image['src'] for image in image_tags if image.get('src')]
    images = ['https:' + image for image in images if image.startswith('//')]
    info['images'] = images

    print('images', info['images'])

    # Get price
    listed_prices = soup.findAll('span', {'class': 'rate-type-price'})
    listed_prices = [int(float(price.text.split('$')[1])) for price in listed_prices]
    price_range = (min(listed_prices), max(listed_prices))
    if price_range[0] == price_range[1]:
        info['price'] = '$' + str(price_range[0])
    else:
        info['price'] = '${}-{}'.format(price_range[0], price_range[1])

    # Get rooms
    rooms = soup.findAll('span', {'class': 'room-title'})
    room_types = []
    for room in rooms:
        room = room.text
        room = room.replace('Private', '')
        room = room.replace('Shared', '')
        room = room.replace('Standard', '')
        room = room.replace('Dorm', '')
        room = room.replace('Mixed', '')
        room = room.replace('Female', '')
        room = room.replace('Male', '')
        room = room.replace('Basic', '')
        room = room.replace('\n', '')
        room = room.strip()
        if room not in room_types:
            room_types.append(room)
    info['rooms'] = room_types

    # Get location text
    # info['location'] = soup.find('a', {'class': 'map_link'}).text # A more precise address that doens't look good
    info['location'] = url.split('/')[5]

    # Get map image
    # TODO

    info['site'] = 'Hostelworld'
    return info


def scrape_airbnb(soup, info):
    # Get the property's Title
    title = soup.find('h1', {'class': '_fecoyn4'})
    info['title'] = title.text

    # Define some helper functions
    get_by_class = lambda parent, c: [tag.text for tag in parent.findAll('span', {'class': c})]
    get_by_all_classes = lambda parent, classes: [get_by_class(parent, c) for c in classes]
    flatten = lambda l: [item for sublist in l for item in sublist]

    # Get information about the rooms and number of guests
    pos_bold_text_classes = ['_12i0h32r', '_fgdupie', '_ncwphzu']  # These seem to unpredictably alternate
    one_up = '_1thk0tsb'
    parent_tags = soup.findAll('div', {'class': one_up})
    pos_room_info = []
    for parent_tag in parent_tags:
        pos_room_info += flatten(get_by_all_classes(parent_tag, pos_bold_text_classes))

    is_info_item = lambda text: text.endswith('guest') or text.endswith('guests') or text.endswith('bedrooms') \
                                or text.endswith('bedroom') or text.endswith('beds') or text.endswith('bed') or\
                                text.endswith('bath') or text.endswith('baths') or text.endswith('Studio')
    info['rooms'] = []
    for info_item in pos_room_info:
        if is_info_item(info_item) and info_item not in info.get('rooms'):
            info['rooms'].append(info_item)

    print(info['rooms'])

    # Get price
    price = soup.find('span', {'class': "_doc79r"})
    if price:
        info['price'] = price.text

    # Get images
    images = soup.findAll('img')
    links = [image['src'] for image in images if image['src'].startswith('https://') and '/users/' not in image['src']]
    info['images'] = links

    # Get map image
    map = soup.find('div', {'class': '_59m2yxn'})
    map_image = map.find('img')
    print(map_image)
    try:
        map_image = map_image['src']
    except Exception:
        pass


    info['map'] = map_image

    # Get location text
    location = soup.find('div', {'class': "_ncwphzu"})
    info['location'] = location.text

    info['site'] = 'AirBnB'
    return info


if __name__ == '__main__':
    url ='https://www.airbnb.com/rooms/2306865?'
    browser.get(url)
    html = browser.page_source

    html = browser.page_source
    soup = BeautifulSoup(html, 'html.parser')

    price = soup.find('span', {'class': "_doc79r"})
    print(price.text)

    print('Initialized browser. Beginning scrape.')
    info = scrape_site_info(url)
    print(info)





