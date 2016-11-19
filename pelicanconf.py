# -*- coding: utf-8 -*- #

"""Pelican configuration"""

from __future__ import unicode_literals

# AUTHOR = u''
AUTHOR = u"omiday ['\u0254:mi:de\u0131]"
SITENAME = u"omiday ['\u0254:mi:de\u0131]"
SITEURL = ''

PATH = 'content'

TIMEZONE = 'America/Edmonton'
DATE_FORMATS = '%B %-d, %Y'
DEFAULT_DATE_FORMAT = '%B %-d, %Y'

DEFAULT_LANG = u'en'
LOCALE = 'en_US.UTF-8'

# Feed generation is usually not desired when developing
# omiday.infrabit.net definitions in publishconf.py
# FEED_DOMAIN = 'http://omiday.infrabit.net'
# FEED_ATOM = None
# FEED_RSS = None
# FEED_ALL_ATOM = 'feeds/all.atom.xml'
# FEED_ALL_RSS = None
# CATEGORY_FEED_ATOM = 'feeds/%s.atom.xml'
# CATEGORY_FEED_RSS = None
# AUTHOR_FEED_ATOM = None
# AUTHOR_FEED_RSS = None
# TAG_FEED_ATOM = None
# TAG_FEED_RSS = None

# Blogroll
# LINKS = (('Pelican', 'http://getpelican.com/'),
#        ('Python.org', 'http://python.org/'),
#        ('Jinja2', 'http://jinja.pocoo.org/'),)

# Social widget
# SOCIAL = (('Site powered by Pelican', 'http://getpelican.com/'),
#           ('Another social link', '#'),)

DEFAULT_PAGINATION = 4

# Uncomment following line if you want document-relative URLs when developing
# RELATIVE_URLS = True

SLUGIFY_SOURCE = 'basename'

DISPLAY_PAGES_ON_MENU = True
DISPLAY_CATEGORIES_ON_MENU = False
DEFAULT_CATEGORY = ''
USE_FOLDER_AS_CATEGORY = True

#
# Docutils
#
# DOCUTILS_SETTINGS = {
#     'exit_status_level': 2,
#     'enable_exit_status': True
# }

#
# Themes
#
THEME = u'themes/tuxlite_tbs_omiday'
#
# tuxlite_tbs
GITHUB_URL = 'https://github.com/omiday/omiday.infrabit.net'

#
# extras (favicon,robots)
#
STATIC_PATHS = ['images', 'extra/robots.txt', 'extra/favicon.ico']
EXTRA_PATH_METADATA = {
    'extra/robots.txt': {'path': 'robots.txt'},
    'extra/favicon.ico': {'path': 'favicon.ico'}
}

#
# PLUGINS
#
PLUGIN_PATHS = ["plugins/tipue_search"]
PLUGINS = ["tipue_search"]
# tipue_search needs search.html (based on 'elegant' theme setup)
TEMPLATE_PAGES = {'search.html': 'search.html'}
