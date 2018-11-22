import requests
from urllib.parse import urlparse, ParseResult


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


def truncate(url):
    """
    Display only the
    """
    parsed = urlparse(url)

    print(parsed)

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