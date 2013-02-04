import unittest, sys

from helpers.file_helpers import read_sample_xml

from vim_xml_tools import xpath

class XPathTests(unittest.TestCase):
    def test_node_xpath(self):
        evaluated = xpath.evaluate("<Root/>", "//Root")

        self.assertEqual("Root", evaluated[0]["match_text"])
        self.assertEqual(1, evaluated[0]["line_number"])

    def test_deeper_node_xpath(self):
        evaluated = xpath.evaluate("<Root><Tag/></Root>", "//Tag")

        self.assertEqual("Tag", evaluated[0]["match_text"])
        self.assertEqual(1, evaluated[0]["line_number"])

    def test_multiline_xml(self):
        xml = read_sample_xml("tests/samples/simple.xml")
        evaluated = xpath.evaluate(xml, "//Tag")

        self.assertEqual("Tag", evaluated[0]["match_text"])
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

    def test_namespaces(self):
        namespaces = dict()
        namespaces["a"] = "http://someurl.org"
        namespaces["b"] = "http://anotherurl.org"

        xml = read_sample_xml("tests/samples/namespaces.xml")
        evaluatedA = xpath.evaluate(xml, "//a:Tag", namespaces)
        evaluatedB = xpath.evaluate(xml, "//b:Tag", namespaces)

        self.assertEqual(3, evaluatedA[0]["line_number"])
        self.assertEqual("a:Tag", evaluatedA[0]["match_text"])

        self.assertEqual(4, evaluatedB[0]["line_number"])
        self.assertEqual("b:Tag", evaluatedB[0]["match_text"])

    def test_node(self):
        xml = read_sample_xml("tests/samples/simple.xml")
        evaluated = xpath.evaluate(xml, "//Tag")

        self.assertEqual("Node", evaluated[0]["match_type"])
        self.assertEqual(3, evaluated[0]["line_number"])
        self.assertEqual("Tag", evaluated[0]["match_text"])
        self.assertEqual("", evaluated[0]["value_text"])

    def test_attribute(self):
        xml = read_sample_xml("tests/samples/simple.xml")
        evaluated = xpath.evaluate(xml, "//TagWithAttribute/@attribute")

        self.assertEqual("Attribute", evaluated[0]["match_type"])
        self.assertEqual(5, evaluated[0]["line_number"])
        self.assertEqual("@attribute", evaluated[0]["match_text"])
        self.assertEqual("attribute text", evaluated[0]["value_text"])

    def test_text(self):
        xml = read_sample_xml("tests/samples/simple.xml")
        evaluated = xpath.evaluate(xml, "//TagWithText/text()")

        self.assertEqual("String", evaluated[0]["match_type"])
        self.assertEqual(4, evaluated[0]["line_number"])
        self.assertEqual("", evaluated[0]["match_text"])
        self.assertEqual("element text", evaluated[0]["value_text"])

    def test_parentless_text(self):
        xml = read_sample_xml("tests/samples/simple.xml")
        evaluated = xpath.evaluate(xml, "'hello there'")

        self.assertEqual("String", evaluated[0]["match_type"])
        self.assertEqual(None, evaluated[0]["line_number"])
        self.assertEqual("", evaluated[0]["match_text"])
        self.assertEqual("hello there", evaluated[0]["value_text"])
