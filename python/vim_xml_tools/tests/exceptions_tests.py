import unittest
from lxml import etree

from vim_xml_tools.exceptions import from_lxml_exception
from vim_xml_tools.exceptions import XPathNamespaceUndefinedError
from vim_xml_tools.exceptions import XPathError

class ExceptionsTests(unittest.TestCase):

    def setUp(self):
        self.tree = etree.fromstring("<Root><Tag/></Root>")

    def test_undefined_namespace_in_xpath_error_is_converted(self):
        error = None
        try:
            self.tree.xpath("//a:Tag")
        except Exception as e:
            error = e

        converted = from_lxml_exception(error)
        self.assertIsInstance(converted, XPathNamespaceUndefinedError)

    def test_xpath_syntax_error_is_converted(self):
        error = None
        try:
            self.tree.xpath("//A/Bad/XPa()th")
        except Exception as e:
            error = e

        converted = from_lxml_exception(error)
        self.assertIsInstance(converted, XPathError)
