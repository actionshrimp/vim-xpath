import unittest

from helpers.file_helpers import read_sample_xml

from vim_xml_tools import xpath

class XPathTests(unittest.TestCase):
    def test_node_xpath(self):
        evaluated = xpath.evaluate("<Root/>", "//Root")

        self.assertEqual(1, evaluated["line_number"])
        self.assertEqual("Root", evaluated["display"])

    def test_deeper_node_xpath(self):
        evaluated = xpath.evaluate("<Root><Tag/></Root>", "//Tag")

        self.assertEqual(1, evaluated["line_number"])
        self.assertEqual("Tag", evaluated["display"])

    def test_multiline_xml(self):
        xml = read_sample_xml("tests/samples/simple.xml")
        evaluated = xpath.evaluate(xml, "//Tag")

        self.assertEqual(3, evaluated["line_number"])
        self.assertEqual("Tag", evaluated["display"])
