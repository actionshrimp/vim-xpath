import unittest
from lxml import etree

from vim_xml_tools.exceptions import from_lxml_exception
from vim_xml_tools.exceptions import XPathNamespaceUndefinedError

class ExceptionsTests(unittest.TestCase):

    def test_undefined_namespace_in_xpath_error_is_converted(self):
        tree = etree.fromstring("<Root><Tag/></Root>")
        error = None
        try:
            tree.xpath("//a:Tag")
        except Exception as e:
            error = e

        converted = from_lxml_exception(error)

        self.assertIsInstance(converted, XPathNamespaceUndefinedError)
