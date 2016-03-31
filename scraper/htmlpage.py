import sys
from copy import deepcopy
import lxml.etree
import lxml.html
import lxml.html.soupparser
import lxml.html.html5parser
import requests

from .exceptions import FailedToLoadWebPage, RequestsTypeError


def etree2html(etree, tidy):
    """Renders an Element Tree (lxml.etree) as HTML (bytes)"""
    return lxml.etree.tostring(etree, pretty_print=tidy).replace(b'&#13;', b'')


def html2etree(tag_soup, tidy=False):
    """Parses HTML (bytes) & returns an Element Tree (lxml.etree)"""
    parser = lxml.etree.HTMLParser(remove_blank_text=tidy)
    return lxml.html.fromstring(tag_soup, parser=parser)


def request_page(url, **kwargs):
    """A requests wrapper, retrieves Web Page content (bytes) from a URL

    raises: RequestForWebPageFailed, RequestsTypeError
    """
    try:
        response = requests.get(url, **kwargs)
        response.raise_for_status()
    except requests.RequestException:
        raise FailedToLoadWebPage(sys.exc_info()[:2], value=(url, kwargs))
    except TypeError:
        raise RequestsTypeError(sys.exc_info()[:2], value=(url, kwargs))
    else:
        return response.content


def get_request_settings(config):
    """Get requests.get() args & kwargs from scraper config (dict)"""
    cfg = deepcopy(config)
    url = cfg.pop('_url', None)
    return url, {k: v for k, v in cfg.items() if k.startswith('_')}


def load_html_page(config, page=None, url=None):
    """Load HTML from either a file or a URL

    page:   file obj (bytes) with the HTML, if set read/return contents
    config: dict with requests settings (these keys start with an underscore)
            and the xpath expressions (see docs more info)
    url:    sets the URL, will override the config '_url' setting
    """
    if page:
        return page.read()

    requests_url, requests_kwargs = get_request_settings(config)
    return request_page(url if url else requests_url, **requests_kwargs)
