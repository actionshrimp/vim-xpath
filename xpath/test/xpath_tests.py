import unittest2

from xpath import VimXPath

class TestVimXPATH(unittest2.TestCase):

	def setUp(self):
		xml = self.read_xml_file('test/test.xml')
		self.x = VimXPath(xml)

	def read_xml_file(self, filename):
		f = open(filename)
		return f.read()

	def xpath(self, xpath):
		return self.x.evaluate_xpath(xpath)

	def test_result_line_number(self):
		results = self.xpath('//TagTests/TagStub')
		self.assertEquals(len(results), 1)

		r = results[0]
		self.assertEquals(r.line, 3)

	def test_result_tag_stub(self):
		results = self.xpath('//TagTests/TagStub')
		self.assertEquals(len(results), 1)

		r = results[0]
		self.assertEquals(r.line, 3)
		self.assertEquals(r.tag, 'TagStub')
		self.assertEquals(r.result, None)

	def test_result_text(self):
		results = self.xpath('//TagTests/TagWithValue')
		self.assertEquals(len(results), 1)

		r = results[0]
		self.assertEquals(r.line, 4)
		self.assertEquals(r.tag, 'TagWithValue')
		self.assertEquals(r.result, 'Value')

	def test_result_attribute(self):
		results = self.xpath('//TagTests/TagWithAttributes/@att1')
		self.assertEquals(len(results), 1)

		r = results[0]
		self.assertEquals(r.line, 5)
		self.assertEquals(r.tag, 'TagWithAttributes')
		self.assertEquals(r.result, '@att1: Attribute 1')

	def test_result_attribute_with_matching_text(self):
		results_att1 = self.xpath('//TagTests/TagWithAttributesWithSameText/@att1')
		results_att2 = self.xpath('//TagTests/TagWithAttributesWithSameText/@att2')

		self.assertEquals(len(results_att1), 1)
		self.assertEquals(len(results_att2), 1)

		r1 = results_att1[0]
		r2 = results_att2[0]
		
		self.assertEquals(r1.result, '@att1: Text')
		self.assertEquals(r2.result, '@att2: Text')

	def test_result_attribute_with_multiple_matches(self):
		multiple = self.xpath('//TagTests/TagWithAttributesWithSameText/@*')
		self.assertEqual(len(multiple), 2)
		results = [r.result for r in multiple]
		self.assertListEqual(results, ['@att1: Text', '@att2: Text'])

		multiple = self.xpath('//TagTests/TagWithAttributesWithSameText/@att1|//TagTests/TagWithAttributesWithSameText/@att2')
		self.assertEqual(len(multiple), 2)
		results = [r.result for r in multiple]
		self.assertListEqual(results, ['@att1: Text', '@att2: Text'])
