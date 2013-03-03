import unittest

from helpers.file_helpers import read_sample_xml

from vim_xml_tools import namespace_prefix_guesser

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
