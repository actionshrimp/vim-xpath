import unittest

from helpers.file_helpers import read_sample_xml

from vim_xml_tools import xpath

class XPathTests(unittest.TestCase):
    def test_node_xpath(self):
        evaluated = xpath.evaluate("<Root/>", "//Root")

        self.assertEqual("Root", evaluated["display"])
        self.assertEqual(1, evaluated["line_number"])

    def test_deeper_node_xpath(self):
        evaluated = xpath.evaluate("<Root><Tag/></Root>", "//Tag")

        self.assertEqual("Tag", evaluated["display"])
        self.assertEqual(1, evaluated["line_number"])

    def test_multiline_xml(self):
        xml = read_sample_xml("tests/samples/simple.xml")
        evaluated = xpath.evaluate(xml, "//Tag")

        self.assertEqual("Tag", evaluated["display"])
        self.assertEqual(3, evaluated["line_number"])

    def test_large_xml_line_number(self):
        #Reported that lxml cuts off sourceline at 65535 due to
        #libxml2 limitation https://bugs.launchpad.net/lxml/+bug/674775

        xml = read_sample_xml("tests/samples/very_large.xml")
        evaluated = xpath.evaluate(xml, "//Last")

        self.assertEqual("Last", evaluated["display"])
        self.assertEqual(70000, evaluated["line_number"])

