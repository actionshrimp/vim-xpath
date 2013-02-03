import unittest, sys

from helpers.file_helpers import read_sample_xml

from vim_xml_tools import xpath

class XPathTests(unittest.TestCase):
    def test_node_xpath(self):
        evaluated = xpath.evaluate("<Root/>", "//Root")

        self.assertEqual("Root", evaluated[0]["display_text"])
        self.assertEqual(1, evaluated[0]["line_number"])

    def test_deeper_node_xpath(self):
        evaluated = xpath.evaluate("<Root><Tag/></Root>", "//Tag")

        self.assertEqual("Tag", evaluated[0]["display_text"])
        self.assertEqual(1, evaluated[0]["line_number"])

    def test_multiline_xml(self):
        xml = read_sample_xml("tests/samples/simple.xml")
        evaluated = xpath.evaluate(xml, "//Tag")

        self.assertEqual("Tag", evaluated[0]["display_text"])
        self.assertEqual(3, evaluated[0]["line_number"])

    def test_large_xml_line_number(self):
        #Reported that lxml cuts off sourceline at 65535 due to
        #libxml2 limitation https://bugs.launchpad.net/lxml/+bug/674775

        xml = read_sample_xml("tests/samples/very_large.xml")
        evaluated = xpath.evaluate(xml, "//Match")

        self.assertEqual(3, evaluated[0]["line_number"])
        self.assertEqual(65534, evaluated[1]["line_number"])
        self.assertEqual(65535, evaluated[2]["line_number"])
        self.assertEqual(70000, evaluated[3]["line_number"])
        self.assertEqual(135532, evaluated[4]["line_number"])
        self.assertEqual(135533, evaluated[5]["line_number"])
        self.assertEqual(139998, evaluated[6]["line_number"])
