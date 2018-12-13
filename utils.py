import requests
from urllib.parse import urlparse, ParseResult

PAGE_TYPES = (BNB, PLUS, HOSTEL) = ("AirBnB", "AirBnBplus", "Hostelworld")


def page_type(url):
    parsed = urlparse(url)
    path = parsed.path.split('/')
    if 'www.airbnb.com' in parsed.netloc and 'rooms' in path:
        if 'plus' in path:
            return PLUS
        else:
            return BNB
    elif 'www.hostelworld.com' in parsed.netloc and 'hosteldetails.php' in path:
        return HOSTEL
    else:
        return None


def url_in_stoplist(url):
    parsed = urlparse(url)
    print('url', parsed)
    if 'localhost:' in parsed.netloc:
        return True
    if 'chrome' in parsed.scheme:
        return True  # Probably some other Chrome Event like newtab
    return False


def validate_url(url):
    response = requests.get(url)
    return response.status_code == 200


def clean(url):
    try:
        validate_url(url)
        return url
    except Exception:

        # parsed = urlparse(url)
        #
        # print(parsed)
        #
        # good_scheme = parsed.scheme in ('http', 'https')
        #
        # scheme = 'http' if not good_scheme else parsed.scheme
        # netloc = parsed.netloc
        # path = parsed.path
        # params = parsed.params
        # query = parsed.query
        #
        # url = ParseResult(scheme, netloc, path, params, query, '').geturl()

        # if validate_url(url):
        #     return url
        # else:
        return None


def validate_group_name(name, stoplist):
    for s in stoplist:
        if s in name:
            return False
    return True


def truncate(url):
    """
    Display only the
    """
    parsed = urlparse(url)

    good_scheme = parsed.scheme in ('http', 'https')

    scheme = 'http' if not good_scheme else parsed.scheme
    netloc = parsed.netloc
    path = parsed.path

    truncated = ParseResult('', netloc, path, '', '', '').geturl()

    # Do some more cleaning
    if truncated.startswith('//'):
        truncated = truncated[2:]

    if truncated.startswith('www.'):
        truncated = truncated[4:]

    if truncated.endswith('/'):
        truncated = truncated[:-1]

    return truncated