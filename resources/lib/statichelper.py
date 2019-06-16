# -*- coding: utf-8 -*-

# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

''' Implements static functions used elsewhere in the add-on '''

from __future__ import absolute_import, division, unicode_literals
import re

try:  # Python 3
    from html import unescape
except ImportError:  # Python 2
    from HTMLParser import HTMLParser

    def unescape(s):
        ''' Expose HTMLParser's unescape '''
        return HTMLParser().unescape(s)

HTML_MAPPING = [
    (re.compile(r'<(/?)i(|\s[^>]+)>', re.I), '[\\1I]'),
    (re.compile(r'<(/?)b(|\s[^>]+)>', re.I), '[\\1B]'),
    (re.compile(r'<em(|\s[^>]+)>', re.I), '[B][COLOR yellow]'),
    (re.compile(r'</em>', re.I), '[/COLOR][/B]'),
    (re.compile(r'<li>', re.I), '- '),
    (re.compile(r'</?(div|li|p|span|ul)(|\s[^>]+)>', re.I), ''),
    (re.compile('<br>\n{0,1}', re.I), ' '),  # This appears to be specific formatting for VRT NU, but unwanted by us
]


def convert_html_to_kodilabel(text):
    ''' Convert VRT HTML content into Kodit formatted text '''
    for (k, v) in HTML_MAPPING:
        text = k.sub(v, text)
    return unescape(text).strip()


def unique_path(path):
    ''' Create a unique path to be used in VRT favorites '''
    if path.startswith('//www.vrt.be/vrtnu'):
        return path.replace('//www.vrt.be/vrtnu/', '/vrtnu/').replace('.relevant/', '/')
    return path


def program_to_url(program, url_type):
    ''' Convert a program url component (e.g. de-campus-cup) to a short programUrl (e.g. /vrtnu/a-z/de-campus-cup/)
        or to a long programUrl (e.g. //www.vrt.be/vrtnu/a-z/de-campus-cup/)
    '''
    url = None
    if program:
        # short programUrl
        if url_type == 'short':
            url = '/vrtnu/a-z/' + program + '/'
        # long programUrl
        elif url_type == 'long':
            url = '//www.vrt.be/vrtnu/a-z/' + program + '/'
    return url


def url_to_program(url):
    ''' Convert a targetUrl (e.g. //www.vrt.be/vrtnu/a-z/de-campus-cup.relevant/), a short programUrl (e.g. /vrtnu/a-z/de-campus-cup/)
        or a long programUrl (e.g. //www.vrt.be/vrtnu/a-z/de-campus-cup/) to a program url component (e.g. de-campus-cup)
    '''
    program = None
    # targetUrl
    if url.startswith('//www.vrt.be/vrtnu/a-z/') and url.endswith('.relevant/'):
        program = url.replace('//www.vrt.be/vrtnu/a-z/', '').replace('.relevant/', '')
    # short programUrl
    elif url.startswith('/vrtnu/a-z/'):
        program = url.replace('/vrtnu/a-z/', '').rstrip('/')
    # long programUrl
    elif url.startswith('//www.vrt.be/vrtnu/a-z/'):
        program = url.replace('//www.vrt.be/vrtnu/a-z/', '').rstrip('/')
    return program


def shorten_link(url):
    ''' Create a link that is as short as possible '''
    if url is None:
        return None
    if url.startswith('https://www.vrt.be/vrtnu/'):
        # As used in episode search result 'permalink'
        return url.replace('https://www.vrt.be/vrtnu/', 'vrtnu.be/')
    if url.startswith('//www.vrt.be/vrtnu/'):
        # As used in program a-z listing 'targetUrl'
        return url.replace('//www.vrt.be/vrtnu/', 'vrtnu.be/')
    return url


def strip_newlines(text):
    ''' Strip newlines and whitespaces '''
    return text.replace('\n', '').strip()


def add_https_method(url):
    ''' Add HTTPS protocol to URL that lacks it '''
    if url.startswith('//'):
        return 'https:' + url
    if url.startswith('/'):
        return 'https://vrt.be' + url
    return url


def distinct(sequence):
    ''' Create a unique list that has no duplicates '''
    seen = set()
    for s in sequence:
        if s not in seen:
            seen.add(s)
            yield s


def boolean(value):
    ''' Verify if a URL parameter values is a boolean '''
    if value is True:
        return True
    if value in ('True', 'true'):
        return True
    return False


def realpage(page):
    ''' Convert a URL parameter page value into an integer '''
    try:
        page = int(page)
    except TypeError:
        return 1
    if page < 1:
        return 1
    return page