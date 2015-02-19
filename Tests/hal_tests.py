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
        expected = "<" + self._href + ">; rel=" + self._rel + "; title=mytitle"
        actual = str(link)
        self.assertEqual(expected, actual)
        
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
        expected = "<" + self._href + ">; rel=" + self._rel + "; title=mytitle"
        expected = expected + ', <http://example.org>; rel=child; title="title 2"'
        actual = str(links)
        self.assertEqual(expected,actual)
        
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


