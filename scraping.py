import requests
from . import utils
# import utils
from bs4 import BeautifulSoup


def get_airbnb_info(url):

    info = {}
    html = requests.get(url)
    soup = BeautifulSoup(html.text, 'html.parser')

    # Check that it is a type of page we parse
    if utils.page_type(url) != utils.BNB:
        info['title'] = soup.title.string
        return info


    # Get the property's Title
    title = soup.find('h1', {'class': '_fecoyn4'})
    info['title'] = title.text

    # Get information about the rooms and number of guests
    rooms = soup.findAll('div', {'class': '_qtix31'})
    info['rooms'] = []
    for g in rooms:
        l = g.find('span', {'class': '_12i0h32r'})
        if l:
            info['rooms'].append(l.text)

    if len(info['rooms']) < 4 or \
            'guests' not in info['rooms'][0] or \
            'bedroom' not in info['rooms'][1]:
        return get_airbnb_info(url)

    return info


if __name__ == '__main__':
    url = 'https://www.airbnb.com/rooms/5258799?location=Montana%2C%20United%20States&s=Z7YC5VKy#neighborhood'
    html = requests.get(url)

    soup = BeautifulSoup(html.text, 'html.parser')

    info = {}

    rooms = soup.findAll('div', {'class': '_qtix31'})
    info['rooms'] = []
    for g in rooms:
        l = g.find('span', {'class': '_12i0h32r'})
        if l:
            print(l)
            info['rooms'].append(l.text)

    print(info)