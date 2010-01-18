'''
Parse and format link headers according to the draft spec
http://tools.ietf.org/id/draft-nottingham-http-link-header-06.txt.

Usage:

>>> import link_header
>>> parse('<http://example.com/foo>; rel="foo", <http://example.com>; rel="up"')
LinkHeader([Link('http://example.com/foo', rel='foo'), Link('http://example.com', rel='up')])
>>> str(LinkHeader([Link("http://example.com/foo", rel="self"),
...                 Link("http://example.com/", rel="up")])
'<http://example.com/foo>; rel="self", <http://example.com/>; rel = "up"'
>>> str(LinkHeader([["http://example.com/foo", [["rel", "self"]]],
...                 ["http://example.com/",    [["rel", "up"]]]])
'<http://example.com/foo>; rel="self", <http://example.com/>; rel = "up"'

For further information see parse(), LinkHeader and Link.
'''

import re

#
# Regexes for link header parsing.  TOKEN and QUOTED in particular should conform to RFC2616.
#
# Acknowledgement: The QUOTED regexp is based on
# http://stackoverflow.com/questions/249791/regexp-for-quoted-string-with-escaping-quotes/249937#249937
#
# Trailing spaces are consumed by each pattern.  The HREF pattern also allows for any leading spaces.
#
HREF   = re.compile(r' *< *([^>]*) *> *;? *')   # note: no attempt to check URI validity
TOKEN  = r'([^()<>@,;:\"\[\]?={}\s]+)'          # non-empty sequence of non-separator characters
QUOTED = r'"((?:[^"\\]|\\.)*)"'                 # double-quoted strings with backslash-escaped double quotes
ATTR   = re.compile(r'%(TOKEN)s *= *(%(TOKEN)s|%(QUOTED)s) *' % locals())
SEMI   = re.compile(r'; *')
COMMA  = re.compile(r', *')

   
def parse(header):
    '''Parse a link header string, returning a LinkHeader object
    >>> parse('<http://example.com/foo>; rel="foo", <http://example.com>; rel="up"')
    LinkHeader([Link('http://example.com/foo', rel='foo'), Link('http://example.com', rel='up')])
    '''
    scanner = _Scanner(header)
    links = []
    while scanner.scan(HREF):
        href = scanner[1]
        attrs = []
        while scanner.scan(ATTR):
            attr_name, token, quoted = scanner[1], scanner[3], scanner[4].replace(r'\"', '"')
            attrs.append([attr_name, token or quoted])
            if not scanner.scan(SEMI):
                break
        links.append(Link(href, attrs))
        if not scanner.scan(COMMA):
            break

    return LinkHeader(links)


class LinkHeader(object):
    '''Represents a sequence of links that can be formatted together as a link header.
    '''
    def __init__(self, links=None):
        '''Initializes a LinkHeader object with a list of Link objects or with
        list of parameters from which Link objects can be created:

        >>> LinkHeader([Link('http://example.com/foo', rel='foo'), Link('http://example.com', rel='up')])
        LinkHeader([Link('http://example.com/foo', rel='foo'), Link('http://example.com', rel='up')])
        >>> LinkHeader([['http://example.com/foo', [['rel', 'foo']]], ['http://example.com', [['rel', 'up']]]])
        LinkHeader([Link('http://example.com/foo', rel='foo'), Link('http://example.com', rel='up')])
        
        The Link objects can be accessed afterwards via the `links` property.
        
        String conversion follows the spec:
        
        >>> str(LinkHeader([Link('http://example.com/foo', rel='foo'), Link('http://example.com', rel='up')]))
        '<http://example.com/foo>; rel="foo", <http://example.com>; rel="up"'
        
        List conversion is json-friendly:
        
        >>> list(LinkHeader([Link('http://example.com/foo', rel='foo'), Link('http://example.com', rel='up')]))
        [['http://example.com/foo', [['rel', 'foo']]], ['http://example.com', [['rel', 'up']]]]
        
        '''

        self.links = [
            link if isinstance(link, Link) else Link(*link)
            for link in links or []]

    def __repr__(self):
        return 'LinkHeader([%s])' % ', '.join(repr(link) for link in self.links)

    def __str__(self):
        '''Formats a link header:
        
        >>> str(LinkHeader([Link('http://example.com/foo', rel='foo'), Link('http://example.com', rel='up')]))
        '<http://example.com/foo>; rel="foo", <http://example.com>; rel="up"'
        '''
        return ', '.join(str(link) for link in self.links)

    def __getitem__(self, key):
        '''Supports list conversion:
        
        >>> list(LinkHeader([Link('http://example.com/foo', rel='foo'), Link('http://example.com', rel='up')]))
        [['http://example.com/foo', [['rel', 'foo']]], ['http://example.com', [['rel', 'up']]]]
        '''
        return list(self.links[key])

class Link(object):
    '''Represents a single link.
    '''
    def __init__(self, href, attr_pairs=None, **kwargs):
        '''Initializes a Link object with an href and attributes either in
        the form of a sequence of key/value pairs &/or as keyword arguments.
        The sequence form allows to be repeated.  Attributes may be accessed
        subsequently via the `attr_pairs` property.
        
        String conversion follows the spec:
        
        >>> str(Link('http://example.com', [('foo', 'bar'), ('foo', 'baz')], rel='self'))
        '<http://example.com>; foo="bar"; foo="baz"; rel="self"'
        
        List conversion is json-friendly:

        >>> list(Link('http://example.com', [('foo', 'bar'), ('foo', 'baz')], rel='self'))
        ['http://example.com', [['foo', 'bar'], ['foo', 'baz'], ['rel', 'self']]]
        '''
        self.href = href
        self.attr_pairs = [
            list(pair)
            for pair in (attr_pairs or []) + kwargs.items()]
    
    def __repr__(self):
        '''
        >>> Link('http://example.com', rel='self')
        Link('http://example.com', rel='self')
        '''
        return 'Link(%s)' % ', '.join(
            [
                repr(self.href)
            ] + [
                "%s=%s" % (pair[0], repr(pair[1]))
                for pair in self.attr_pairs])

    def __str__(self):
        '''Formats a single link:
        
        >>> str(Link('http://example.com/foo', [['rel', 'self']]))
        '<http://example.com/foo>; rel="self"'
        >>> str(Link('http://example.com/foo', [['rel', '"quoted"']]))
        '<http://example.com/foo>; rel="\\\\"quoted\\\\""'
        '''
        return '; '.join(
            ['<%s>' % self.href] + [
                '%s="%s"' % (key, value.replace('"', r'\"'))
                for key, value in self.attr_pairs])

    def __getitem__(self, key):
        '''Supports list conversion:
        
        >>> list(Link('http://example.com', rel='foo'))
        ['http://example.com', [['rel', 'foo']]]
        '''
        return [self.href, self.attr_pairs][key]


class _Scanner(object):
    def __init__(self, buf):
        self.buf = buf
        self.match = None
    
    def __getitem__(self, key):
        return self.match.group(key)
        
    def scan(self, pattern):
        self.match = pattern.match(self.buf)
        if self.match:
            self.buf = self.buf[self.match.end():]
        return self.match 


if __name__ == '__main__':
    import doctest
    doctest.testmod()
