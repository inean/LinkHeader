#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
  HAL: A simple module to allow developers to format or encode links
     according to RFC 5988 or trying to follow HAL specifications
     (http://stateless.co/hal_specification.html)
"""

from __future__ import absolute_import

__author__  = "Michael Burrows, Mark Nottingham, Carlos Martín"
__license__ = "See LICENSE file for details"

# Inspect runtime environment
has_itervalues = hasattr({}, 'itervalues')
has_iteritems = hasattr({}, 'iteritems')
has_ifilter = False

# Import Here any required modules for this module.
import re

try:
    from itertools import chain, ifilter
    has_ifilter = True
except ImportError:
    from itertools import chain

__all__ = ['Links', 'Link',]


# Regexes for link header parsing.  TOKEN and QUOTED in particular
# should conform to RFC2616.  Acknowledgement: The QUOTED regexp is
# based on
# http://stackoverflow.com.../regexp-for-quoted-string-with-escaping-quotes
# Trailing spaces are consumed by each pattern.  The RE_HREF pattern
# also allows for any leading spaces.
#

QUOTED        = r'"((?:[^"\\]|\\.)*)"'
TOKEN         = r'([^()<>@,;:\"\[\]?={}\s]+)'

RE_COMMA_HREF = re.compile(r' *,? *< *([^>]*) *> *')
RE_ONLY_TOKEN = re.compile(r'^%(TOKEN)s$' % locals())
RE_ATTR       = re.compile(r'%(TOKEN)s *= *(%(TOKEN)s|%(QUOTED)s) *' % locals())
RE_SEMI       = re.compile(r'; *')
RE_COMMA      = re.compile(r', *')


class LinkError(Exception):
    """Custom exception for link related errors"""

    
#pylint: disable-msg=R0903
class LinksScanner(object):
    """Simple scanner for RFC5988 links"""
    def __init__(self, buf):
        self.buf = buf
        self.match = None
    
    def __getitem__(self, key):
        return self.match.group(key)
        
    def scan(self, pattern):
        """Parse a pattern"""
        self.match = pattern.match(self.buf)
        if self.match:
            self.buf = self.buf[self.match.end():]
        return self.match

        
#pylint: disable-msg=R0903
class Links(object):
    """
    Represents a sequence of links that can be formatted together
    as a link header
    """

    def __init__(self, links):
        self._links = {}
        self.update(links)

    def __iter__(self):
        if has_itervalues:
            return self._links.itervalues()
        else:
            return iter(self._links.values())

    def __len__(self):
        return len(self._links)

    def __repr__(self):
        return 'Links([%s])' % ', '.join(repr(link) for link in self)

    def __str__(self):
        if has_itervalues:
            return ', '.join(str(link) for link in self._links.itervalues())
        else:
            return ', '.join(str(link) for link in self._links.values())

    def rel(self, rel, default=None):
        """Returns Link  associated to relative"""
        return self._links.get(rel, default)

    def to_py(self):
        """Supports dict conversion JSON compatible"""
        if has_itervalues:
            return dict((link.to_py() for link in self._links.itervalues()))
        else:
            return dict((link.to_py() for link in self._links.values()))

    def update(self, links):
        """Update links with links"""
        for link in links:
            if hasattr(link, 'rel') and hasattr(link, 'href'):
                assert 'rel' not in self._links
                self._links[link.rel] = link

    @staticmethod
    def parse(header):
        """Parses a links header string to a Links instance"""
        scanner = LinksScanner(header)
        links   = []
        while header and scanner.scan(RE_COMMA_HREF):
            attrs = {'href': scanner[1]}
            while scanner.scan(RE_SEMI):
                if scanner.scan(RE_ATTR):
                    name, token, quot = scanner[1], scanner[3], scanner[4]
                    attrs[name] = quot.replace(r'\"', '"') if quot else token
            #pylint: disable-msg=W0142
            links.append(Link(**attrs))
        if scanner.buf:
            raise LinkError(
                "link_header.parse() failed near %s",
                repr(scanner.buf))
        return Links(links)
            
                
class Link(object):
    """Represents a single link"""
    
    SINGLE_VALUED_ATTRS = [
        'rel', 'anchor', 'rev', 'media',
        'title', 'type', 'href'
    ]
    MULTI_VALUED_ATTRS  = [
        'hreflang', 'title*'
    ]
    STANDARD_ATTRS = SINGLE_VALUED_ATTRS + MULTI_VALUED_ATTRS

    def __init__(self, href=None, rel=None, **data):
        href = href or data.get('href')
        rel  = rel  or data.get('rel')
        #assert href and rel
        # now update
        data.update((('rel', rel), ('href', href)))
        super(Link, self).__setattr__('_dict', data)

    def __repr__(self):
        if has_ifilter and has_iteritems:
            pairs = ifilter(lambda item: item[0] != 'href', self._dict.iteritems())
        else:
            pairs = filter(lambda item: item[0] != 'href', self._dict.items())

        return 'Link(%s)' % ', '.join(chain(
            (repr(self.href),),
            ("%s=%s" % (key, repr(value),) for key, value in pairs)))

    def __str__(self):
        """Formats a single link"""
        if has_ifilter and has_iteritems:
            pairs = ifilter(lambda item: item[0] != 'href', self._dict.iteritems())
        else:
            pairs = filter(lambda item: item[0] != 'href', self._dict.items())

        return '; '.join(chain(
            ('<%s>' % self.href,),
            (self.str_pair(key, value) for key, value in pairs)))

    def __setattr__(self, key, value):
        key = key if key != 'content_type' else 'type'
        self._dict[key.replace('_', '-')] = value

    def __getattr__(self, key):
        attr = key.lower().replace('_','-')
        attr = attr if attr != 'content-type' else 'type'

        if attr not in self.STANDARD_ATTRS:
            raise AttributeError('No attribute named "%s"' % attr)

        retval = self._dict.get(attr)
        if not retval or len(retval) > 1 or attr in self.MULTI_VALUED_ATTRS:
            return retval
        return retval[0]
        
    def to_py(self):
        """Convert to a json-friendly dct structure"""
        pairs = dict(self._dict)
        return (pairs.pop('rel'), pairs)

    @staticmethod
    def str_pair(key, value):
        """Join a pair of key, paramaters as required by RFC5988"""
        return '%s=%s' % (key, value)                             \
               if RE_ONLY_TOKEN.match(value) or key.endswith('*') \
               else '%s="%s"' % (key, value.replace('"', r'\"'))
    
