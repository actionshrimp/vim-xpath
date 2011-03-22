#-*- coding: utf-8 -*-
import re
from lxml import etree

class VimXPath(object):
	def __init__(self, buf):
		self.result_properties = ['line', 'tag', 'result']
		self.column_names = {'line': 'Line', 'tag': 'Tag', 'result': 'XPath Result'}
		self.default_column_widths = {'line': 5, 'tag': 10, 'result': 20}
		self.result_padding = 5
		self.parse_errors = []

		try:
			self.tree = etree.XML(buf)
			self.xpath_evaluator = etree.XPathEvaluator(self.tree)
		except Exception as inst:
			self.parse_errors.append(str(inst))
	

	def results_buffer_from_xpath(self, xpath):
		bufout = []

		if len(self.parse_errors) == 0:
			bufout += self.build_search_header(xpath)

			try:
				results = self.evaluate_xpath(xpath)
				bufout += self.build_results_buffer(results)

			except Exception as inst:
				bufout.append(str(inst))
		else:
			bufout += self.build_parse_error_message()
		
		return bufout

	def build_parse_error_message(self):
		bufout = []
		bufout.append('—————')
		bufout.append('XML Validation Error')
		bufout.append('—————')
		bufout += self.parse_errors
		return bufout

	def build_search_header(self, xpath):
		bufout = []
		bufout.append('—————')
		bufout.append('Results: ' + xpath)
		bufout.append('—————')
		return bufout

	def evaluate_xpath(self, xpath):
		self.results = self.xpath_evaluator(xpath)
		self.parsed_results = [self.parse_result(xpath, r) for r in self.results]
		return self.parsed_results

	def build_results_buffer(self, results):
		bufout = []
		if len(results) > 0:
			column_max = self.calculate_max_column_widths(results)

			header_row = self.build_column_headers(column_max)
			bufout += header_row

			for i, r in enumerate(results):
				if i < 99:
					result_row = self.build_result_row(column_max, r)
					bufout += result_row
				elif i == 99:
					result_row = ['More than 100 results, please narrow your XPATH...']
					bufout += result_row
				else:
					pass


		else:
			bufout.append('No results.')

		return bufout

	def parse_result(self, xpath, result):
		parse_class = XPathTagResult
		if isinstance(result, etree._ElementStringResult):
			parse_class = self.get_string_element_class(result)

		return parse_class(xpath, result)

	def get_string_element_class(self, result):
		if result.is_attribute:
			return XPathAttrResult

	def calculate_max_column_widths(self, results):
		column_max = {}
		for prop in self.result_properties:
			column_max[prop] = self.default_column_widths[prop]
			for r in results:
				col_width = len(str(r.__getattribute__(prop))) + self.result_padding
				if col_width > column_max[prop]:
					column_max[prop] = col_width

		return column_max

	def build_column_headers(self, column_widths):
		output_list = []
		header_break = []
		for prop in self.result_properties:
			output_list.append(column_widths[prop])
			header_break.append(column_widths[prop])

			output_list.append('|' + self.column_names[prop])
			header_break.append('|' + '—'*(column_widths[prop] - 1))

		headers = "%-*s %-*s %-*s" % tuple(output_list)
		header_break = "%-*s %-*s %-*s" % tuple(header_break)
		return [headers, header_break]

	def build_result_row(self, column_widths, result_row):
		output_list = []
		for prop in self.result_properties:
			output_list.append(column_widths[prop])
			if result_row.__getattribute__(prop) is not None:
				propout = str(result_row.__getattribute__(prop))
				propout = propout.replace("\n", "")
				output_list.append('|' + propout)
			else:
				output_list.append('|-')

		row = "%-*s %-*s %-*s" % tuple(output_list)
		return [row]


class XPathResult(object):
	def __init__(self, search, el):
		self.search = search
		self.line = self.build_line(el)
		self.tag = self.build_tag(el)
		self.result = self.build_result(el)

	def build_line(self, el):
		pass

	def build_tag(self, el):
		pass

	def build_result(self, el):
		pass

class XPathNodeResult(XPathResult):
	def build_line(self, el):
		return el.sourceline

	def build_tag(self, el):
		return el.tag

class XPathTagResult(XPathNodeResult):
	def build_result(self, el):
		try:
			if re.sub("\s", "", el.text) == "":
				return None
			else:
				return el.text
		except:
			return None

class XPathStringResult(XPathResult):
	def build_line(self, el):
		parent = el.getparent()
		return parent.sourceline

	def build_tag(self, el):
		parent = el.getparent()
		return parent.tag

class XPathAttrResult(XPathStringResult):
	def build_result(self, el):
		return '@' + el.attrname + ': ' + str(el)
