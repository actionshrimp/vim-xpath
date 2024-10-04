import unittest

from .helpers.file_helpers import read_sample_xml

from vim_xpath import namespace_prefix_guesser

class NamespacePrefixGuesserTests(unittest.TestCase):

    def test_single_namespace_prefix_is_guessed(self):
        xml = read_sample_xml("single_namespace.xml")
        prefixes = namespace_prefix_guesser.guess_prefixes(xml)

        self.assertEqual("http://onlyPrefix.com", prefixes["onlyPrefix"])

    def test_default_namespace_is_called_default(self):
        xml = read_sample_xml("namespaces.xml")
        prefixes = namespace_prefix_guesser.guess_prefixes(xml)

        self.assertEqual("http://someurl.org", prefixes["default"])
        self.assertEqual("http://anotherurl.org", prefixes["ns"])

    def test_first_node_to_define_prefix_claims_it(self):
        xml = read_sample_xml("reused_namespace.xml")
        prefixes = namespace_prefix_guesser.guess_prefixes(xml)

        self.assertEqual("http://firsturl.org", prefixes["ns"])

    def test_first_node_depth_first_to_define_prefix_claims_it(self):
        xml = read_sample_xml("reused_namespace.xml")
        prefixes = namespace_prefix_guesser.guess_prefixes(xml)

        self.assertEqual("http://thirdurl.org", prefixes["another"])

    def test_malformed_xml_throws_error(self):
        xml = read_sample_xml("malformed.xml")

        with self.assertRaises(namespace_prefix_guesser.PrefixGuessingError):
            prefixes = namespace_prefix_guesser.guess_prefixes(xml)
