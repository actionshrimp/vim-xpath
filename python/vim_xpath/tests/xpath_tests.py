import unittest

from .helpers.file_helpers import read_sample_xml

from vim_xpath import xpath
from vim_xpath.exceptions import XPathError, BufferXmlError

class XPathTests(unittest.TestCase):

    def test_node_line_number(self):
        evaluated = xpath.evaluate("<Root/>", "//Root")
        self.assertEqual(1, evaluated[0]["line_number"])

    def test_multiline_xml(self):
        xml = read_sample_xml("simple.xml")
        evaluated = xpath.evaluate(xml, "//Tag")

        self.assertEqual(3, evaluated[0]["line_number"])

    def test_large_xml_line_number(self):
        #Reported that lxml cuts off sourceline at 65535 due to
        #libxml2 limitation https://bugs.launchpad.net/lxml/+bug/674775
        xml = read_sample_xml("very_large.xml")
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

        xml = read_sample_xml("namespaces.xml")
        evaluatedA = xpath.evaluate(xml, "//a:Tag", namespaces)
        evaluatedB = xpath.evaluate(xml, "//b:Tag", namespaces)

        self.assertEqual(3, evaluatedA[0]["line_number"])
        self.assertEqual(4, evaluatedB[0]["line_number"])

    def test_node(self):
        xml = read_sample_xml("simple.xml")
        evaluated = xpath.evaluate(xml, "//Tag")

        self.assertEqual(3, evaluated[0]["line_number"])
        self.assertEqual("<Tag>", evaluated[0]["match"])
        self.assertEqual("", evaluated[0]["value"])

    def test_attribute(self):
        xml = read_sample_xml("simple.xml")
        evaluated = xpath.evaluate(xml, "//TagWithAttribute/@attribute")

        self.assertEqual(5, evaluated[0]["line_number"])
        self.assertEqual("@attribute", evaluated[0]["match"])
        self.assertEqual("attribute text", evaluated[0]["value"])

    def test_text(self):
        xml = read_sample_xml("simple.xml")
        evaluated = xpath.evaluate(xml, "//TagWithText/text()")

        self.assertEqual(4, evaluated[0]["line_number"])
        self.assertEqual("string", evaluated[0]["match"])
        self.assertEqual("element text", evaluated[0]["value"])

    def test_parentless_text(self):
        xml = read_sample_xml("simple.xml")
        evaluated = xpath.evaluate(xml, "'hello there'")

        self.assertEqual(None, evaluated[0]["line_number"])
        self.assertEqual("string", evaluated[0]["match"])
        self.assertEqual("hello there", evaluated[0]["value"])

    def test_boolean(self):
        xml = read_sample_xml("simple.xml")
        evaluated = xpath.evaluate(xml, 
                        "//TagWithAttribute/@attribute = 'attribute text'")

        self.assertEqual(None, evaluated[0]["line_number"])
        self.assertEqual("boolean", evaluated[0]["match"])
        self.assertEqual("true()", evaluated[0]["value"])

    def test_numeric(self):
        xml = read_sample_xml("simple.xml")
        evaluated = xpath.evaluate(xml, "number(//TagWithNumeric)")

        self.assertEqual(None, evaluated[0]["line_number"])
        self.assertEqual("numeric", evaluated[0]["match"])
        self.assertEqual(250, float(evaluated[0]["value"]))

    def test_undefined_namespace_throws_wrapped_exception(self):
        xml = read_sample_xml("simple.xml")

        with self.assertRaises(XPathError):
            xpath.evaluate(xml, "//blarg:Tag")

    def test_bad_xpath_throws_wrapped_exception(self):
        xml = read_sample_xml("simple.xml")

        with self.assertRaises(XPathError):
            xpath.evaluate(xml, "//bla()rg")

    def test_bad_buffer_throws_wrapped_exception(self):
        xml = "<malformed"

        with self.assertRaises(BufferXmlError):
            xpath.evaluate(xml, "//xpath")
