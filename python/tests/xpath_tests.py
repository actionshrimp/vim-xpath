import unittest

from vim_xml_tools import xpath

class XPathTests(unittest.TestCase):
    def test_node_xpath(self):
        evaluated = xpath.evaluate("<Root>", "//Root")

        self.assertEqual(0, evaluated["line_number"])
        self.assertEqual("Root", evaluated["display"])
