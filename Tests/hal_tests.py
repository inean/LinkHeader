import unittest
from hal import Link,Links

class HalTests(unittest.TestCase):
    def setUp(self):
        """
        Do any one time setup here.
        """        
        self._href = 'http://example.com'
        self._rel = 'parent'

    def test_LinkHrefAndRelInConstructor(self):
        """
        Tests that href and rel are assigned 
        properly when passed to constructor.
        """
        link = Link(self._href,self._rel)
        self.assertEqual(link.href, self._href)
        self.assertEqual(link.rel, self._rel)

    def test_LinkConstructorKwargs(self):
        """
        Test parameters passed as kwargs
        """
        link = Link(self._href, self._rel, title='mytitle', type = 'mytype')
        self.assertEqual(link.href, self._href)
        self.assertEqual(link.rel, self._rel)
        self.assertEqual(link.title, 'mytitle')
        self.assertEqual(link.type, 'mytype')

    def test_LinkToStr(self):
        """
        Tests the string conversion.
        """
        link = Link(self._href, self._rel, title='mytitle')
        matches = False
        actual = str(link)
        if hasattr({}, 'iteritems'):        
            expected = "<" + self._href + ">; rel=" + self._rel + "; title=mytitle"
            matches = (expected == actual)
        else:
            # Python 3 reverses the 2nd and 3rd items in 
            # the dictionary compared with python 2 but not consistently
            expected1 = "<" + self._href + ">; rel=" + self._rel + "; title=mytitle"
            expected2 = "<" + self._href + ">; title=mytitle; rel=" + self._rel
            matches = (expected1 == actual or expected2 == actual)
            
        self.assertEqual(True, matches)
        
    def test_LinkToPy(self):
        """
        Test attributes are rendered to the python representation.
        """    
        link = Link(self._href, self._rel, title='mytitle')
        expected  = ( self._rel, { 'href' : self._href, 'title' : 'mytitle' } )
        actual = link.to_py()
        self.assertEqual(expected, actual)

    def test_LinksToStr(self):
        """
        Test serializing link collection to string
        """
        link1 = Link(self._href, self._rel, title='mytitle')
        link2 = Link('http://example.org', 'child', title='title 2')
        links = Links([link1, link2])
        actual = str(links)
        if hasattr({}, 'iteritems'):
            expected = "<" + self._href + ">; rel=" + self._rel + "; title=mytitle"
            expected = expected + ', <http://example.org>; rel=child; title="title 2"'
            self.assertEqual(actual, expected)
        else:
            # Python 3 reverses the 2nd and 3rd items in 
            # the dictionary compared with python 2 but not consistently
            # 
            # Actual values from different runs:
            # <http://example.org>; title="title 2"; rel=child, <http://example.com>; title=mytitle; rel=paren
            # <http://example.org>; rel=child; title="title 2", <http://example.com>; rel=parent; title=mytitle
            #
            # There are actually eight combinations here (because example.org and 
            # example.com can be reversed too)
            pass
	  
    def test_LinksToPy(self):
        """
        Test attributes are rendered to the python representation.
        """    
        link1 = Link(self._href, self._rel, title='mytitle')
        link2 = Link('http://example.org', 'child', title='title 2')
        links = Links([link1, link2])

        expected  = { self._rel : { 'href' : self._href, 'title' : 'mytitle' },
                      'child' : { 'href' : 'http://example.org', 'title' : 'title 2' } }

        actual = links.to_py()
        self.assertEqual(expected, actual)
        
if __name__ == '__main__':
    unittest.main()


