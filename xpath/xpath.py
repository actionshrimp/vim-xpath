#-*- encoding:utf-8 -*-
import re
from lxml import etree

def vimxpath_from_vimbuffer(vimbuf):
	xml = "\n".join(vimbuf[:])
	xpath = VimXPath(xml)
	return xpath

#Refactored OK
class VimXPathInterface(object):

	def __init__(self, vim, results_buffer_name):
		self.buffer_manager = self.build_buffer_manager(vim, results_buffer_name)
		self.searcher = XPathSearcher()

		self.previous = {'xpath': None, 'search_buffer_name': None}

	def build_buffer_manager(self, vim, result_buffer_name):
		buffer_manager = VimBufferManager(vim)
		buffer_manager.define_buffer("results", results_buffer_name)
		return buffer_manager

	def xpath_search(self, search_buffer_name, xpath):
		results = self.get_search_results(search_buffer_name, xpath)
		self.output_results(xpath, results)

		self.previous['xpath'] = xpath
		self.previous['search_buffer_name'] = search_buffer_name

	def get_search_results(self, search_buffer_name, xpath):
		search_buffer = self.buffer_manager.get_buffer(search_buffer_name)
		search_text = self.buffer_manager.get_buffer_content(search_buffer)
		results = self.searcher.search(search_text, xpath)
		return results

	def output_results(self, xpath, results):
		results_buffer = self.buffer_manager.get_defined_buffer("results")
		results_window = self.buffer_manager.get_window(results_buffer)

		width = results_window.width
		formatter = ResultsFormatter(width, xpath, results)
		lines = formatter.get_formatted_lines()

		self.buffer_manager.set_buffer_content(results_buffer, lines)

	def window_resized(self):
		if self.previous['xpath'] is not None:
			self.xpath_search(self.previous['search_buffer_name'], self.previous['xpath'])

#Refactored OK
class VimBufferManager(object):

	def __init__(self, vim):
		self.vim = vim
		self.defined_buffers = {}

	def define_buffer(self, defname, buffer_name):
		self.defined_buffers[defname] = buffer_name

	def get_defined_buffer(self, defname):
		buffer_name = self.defined_buffers[defname]
		return self.get_buffer(buffer_name)

	def get_buffer(self, buffer_name):

		for buf in [b for b in self.vim.buffers if b.name is not None] :
			if buf.name.endswith(buffer_name) and buf:
				return buf

		return None

	def set_buffer_content(self, buffer, lines):
		del buffer[:]
		for l in lines:
			buffer.append(l)

		del buffer[0]

	def get_buffer_content(self, buffer):
		content = "\n".join(buffer)
		return content

	def get_window(self, buffer):
		for w in self.vim.windows:
			if w.buffer.name == buffer.name:
				return w

		return None

class XPathSearcher(object):

	def __init__(self):
		self.cached_search_text = None
		self.xml_tree = None

		self.cache = {'xml': None, 'tree': None, 'eval': None}

	def search(self, xml, xpath):
		try:
			self.build_xml_tree(xml)
	
		except etree.XMLSyntaxError as xmlerr:
			err_text = str(xmlerr)
			error_result = XPathParseErrorResult(err_text)
			return [error_result]

		raw_results = self.cache['eval'](xpath)
		final_results = self.parse_results(raw_results)

		return final_results

	def build_xml_tree(self, xml):
		if self.cache['xml'] != xml:
			self.cache['xml'] = xml
			self.cache['tree'] = etree.XML(xml)
			self.cache['eval'] = etree.XPathEvaluator(self.cache['tree'])

	def parse_results(self, raw_results):
		results = []

		for r in raw_results:
			parsed = self.parse(r)
			results.append(parsed)

		return results

	def parse(self, raw_result):
		parse_class = self.get_parse_class(raw_result)
		parsed = parse_class(raw_result)

		return parsed

	def get_parse_class(self, raw_result):
		result = XPathTagResult
		if isinstance(raw_result, etree._ElementStringResult):
			if raw_result.is_attribute:
				result = XPathAttrResult

		return result

class ResultsFormatter(object):

	def __init__(self, window_width, xpath, results):

		self.xpath_string = xpath
		self.width = window_width

		results_contain_errors = False

		for r in results:
			if isinstance(r, XPathParseErrorResult):
				results_contain_errors = True
				break

		if results_contain_errors:
			columns = [ReultsFormatterTableColumn('error', 'Parse Error', contract_contents=False)]
		else:
			columns = [
				ResultsFormatterTableColumn('line', 'Line', contract_contents=False, expand_target_pct=5),
				ResultsFormatterTableColumn('tag', 'Tag', expand_target_pct=25),
				ResultsFormatterTableColumn('result', 'Result', expand_target_pct=70),
				]

		#Leave space for column delimiters
		data_width = self.width - (len(columns) + 1)

		self.table = ResultsFormatterTable(data_width, columns)
		self.table.add_results(results)
		self.table.build()

	def get_formatted_lines(self):
		lines = []
		lines += self.build_header()
		lines += self.build_body()
		lines += self.build_footer()

		return lines

	def build_header(self):
		header_lines = []
		
		header_lines.append('┏' + '━'* (self.width-2) + '┓')

		header_text = 'Results: ' + self.xpath_string
		header_lines.append('┃' + header_text + ' ' * (self.width - len(header_text) - 2) + '┃')

		lines = ['┣', '┃', '┣']
		for c in self.table.columns:
			lines[0] += '━' * c.width + '┳'
			lines[1] += c.title + " "*(c.width - len(c.title)) + '┃'
			lines[2] += '━' * c.width + '╋'

		lines[0] = lines[0][:-len('┳')] + '┫'
		lines[2] = lines[2][:-len('┃')] + '┫'

		header_lines.append(lines)

		return header_lines

	def build_body(self):
		body_lines = []

		for r in self.table.rows:
			line = '┃'
			for c in self.table.columns:
				contents = r.cells[c]
				if len(contents) > c.width:
					contents = contents[:c.width-3] + '...'
				else:
					contents += " "*(c.width - len(contents))

				line += contents + '┃'

			body_lines.append(line)

		return body_lines

	def build_footer(self):
		footer_lines = []
		line = '┗'
		for c in self.table.columns:
			line += '━' * c.width + '┻'

		line = line[:-len('┻')] + '┛'

		footer_lines.append(line)
		return footer_lines

class ResultsFormatterTable(object):

	def __init__(self, table_width, columns):

		self.width = table_width

		self.columns = columns
		self.rows = []

	def add_results(self, results):
		for r in results:
			row = ResultsFormatterTableRow(self.columns, r)
			if len(row.cells.keys()) > 0:
				self.rows.append(row)

	def build(self):
		self.calculate_column_data_widths()
		self.derive_column_visibility_from_row_contents()
		self.fit_visible_columns_based_on_column_settings()

	def calculate_column_data_widths(self):
		for col in self.columns:
			for r in self.rows:
				data = r.cells.get(col, 0)
				col.max_data_width = max(col.max_data_width, len(data), len(col.title))

	def derive_column_visibility_from_row_contents(self):
		for r in self.rows:
			for column in r.cells.keys():
				if not(column.visible):
					column.visible = True

	def fit_visible_columns_based_on_column_settings(self):

		self.assign_space_for_non_contractable_columns()

		free_space = self.calculate_free_space()
		self.assign_free_space_to_columns_that_want_it(free_space)

	def assign_space_for_non_contractable_columns(self):
		for col in [c for c in self.columns if not(c.contract_contents)]:
			col.width = col.max_data_width

	def calculate_free_space(self):
		free_space = self.width - sum([c.width for c in self.columns if c.visible])
		return free_space

	def assign_free_space_to_columns_that_want_it(self, free_space):
		while free_space > 0:
			for col in self.columns:
				if col.wants_more_space(self.width):
					if free_space > 0:
						col.width += 1
						free_space -= 1
			
class ResultsFormatterTableColumn(object):
	def __init__(self, name, title, contract_contents=True, expand_target_pct=0):
		self.name = name
		self.title = title
		self.visible = False

		self.width = 0
		self.max_data_width = 0

		self.contract_contents = contract_contents
		self.expand_target_pct = expand_target_pct

	def current_percentage_width(self, table_width):
		return (self.width / float(table_width)) * 100

	def wants_more_space(self, table_width):
		data_is_larger = (self.width < self.max_data_width)
		desired_pct_is_larger = (self.current_percentage_width(table_width) < self.expand_target_pct)
		if (self.visible and (data_is_larger or desired_pct_is_larger)):
			return True
		else:
			return False


class ResultsFormatterTableRow(object):

	def __init__(self, columns, result):
		self.cells = {}
		for c in columns:
			try:
				cell = result.__getattribute__(c.name)
				self.cells[c] = str(cell)
			except AttributeError as inst:
				pass

###	def calculate_column_widths(self, results, window_width):
###
###		columns = {}
###		if ((len(results) == 1) and isinstance(results[0], XPathParseErrorResult)):
###			columns['error'] = window_width
###		else:
###			ideal_columns = self.calculate_ideal_widths(results, window_width)
###
###			if sum(ideal_columns.values()) > window_width:
###				columns = self.scale_ideal_widths_to_fitted_pcts(ideal_columns, window_width)
###			else:
###				columns = ideal_columns
###
###		return columns def calculate_ideal_widths(self, results, available_width):
###		ideal_columns = {}
###		for r in results:
###			for col in self.columns:
###
###				contents = r.__getattribute__(col) 
###				contents_width = len(str(contents))
###
###				ideal_columns[col] = contents_width
###
###		last_sum = None
###
###		while (sum(ideal_columns.values()) < available_width) and (sum(ideal_columns.values()) != last_sum):
###			last_sum = sum(ideal_columns.values())
###			for col in self.columns:
###				pct_width = (ideal_columns.get(col, 999) / float(available_width)) * 100 - 1
###				if pct_width < self.column_fitted_pcts.get(col, 999):
###					ideal_columns[col] += 1
###
###
###		return ideal_columns
###
###	def scale_ideal_widths_to_fitted_pcts(self, ideal_columns, window_width):
###
###		scaled_columns = {}
###		for col in self.columns:
###			scaled_columns[col] = ideal_columns[col]
###
###		last_sum = None
###
###		while (sum(scaled_columns.values()) > window_width) and (sum(scaled_columns.values()) != last_sum):
###			last_sum = sum(scaled_columns.values())
###			for col in self.columns:
###				pct_width = (scaled_columns[col] / float(window_width)) * 100 - 1
###				if pct_width > self.column_fitted_pcts.get(col, 0):
###					scaled_columns[col] -= 1
###
###		return scaled_columns
###
###	def format_header(self, xpath, column_widths):
###		lines = []
###
###		lines.append(xpath)
###
###		divider = '┏'
###		for i, width in enumerate(column_widths.values()):
###			divider += ('━' * width)
###			if (i+1) == len(column_widths):
###				divider += '┓'
###			else:
###				divider += '┳'
###
###		lines.append(divider)
###		return lines
###
###	def format_error(self, result, column_widths):
###		lines = []
###
###		w = column_widths['error']
###		error_text = (result.error[:(w-3)] + '...') if len(result.error) > w else result.error
###		if len(error_text) < w:
###			error_text += (" " *  (w - len(error_text)))
###
###		error_line = '┃%s┃' % error_text
###
###		lines.append(error_line)
###		return lines
###
###	def format_result(self, result, column_widths):
###		lines = []
###
###		result_line = '┃'
###
###		for col in self.columns:
###			w = column_widths[col]
###			text = str(result.__getattribute__(col))
###			col_text = (text[:(w-3)] + '...') if len(text) > w else text
###
###			if len(col_text) < w:
###				col_text += (" " * (w - len(col_text)))
###
###			result_line += '%s┃' % col_text
###
###		lines.append(result_line)
###		return lines
###
###	def format_footer(self, column_widths):
###		lines = []
###
###		divider = '┗'
###		for i, width in enumerate(column_widths.values()):
###			divider += ('━' * width)
###			if (i+1) == len(column_widths):
###				divider += '┛'
###			else:
###				divider += '┻'
###
###		lines.append(divider)
###		return lines


#OLD
#class VimXPath(object):
#	def __init__(self, xml):
#		self.result_properties = ['line', 'tag', 'result']
#		self.column_names = {'line': 'Line', 'tag': 'Tag', 'result': 'XPath Result'}
#		self.default_column_widths = {'line': 5, 'tag': 10, 'result': 20}
#		self.result_padding = 5
#		self.parse_errors = []
#
#		try:
#			self.tree = etree.XML(xml)
#			self.xpath_evaluator = etree.XPathEvaluator(self.tree)
#		except Exception as inst:
#			self.parse_errors.append(str(inst))
#
#	def load_results(self, xpath, vim, results_buffer_name):
#
#		b = find_buffer(vim, results_buffer_name)
#		if b is not None:
#			results = self.results_buffer_from_xpath(xpath, w.width)
#
#		del b[:]
#
#		for r in results:
#			b.append(r)
#
#		del b[0]
#
#	def find_buffer(self, vim, buffer_name):
#
#		for w in vim.windows:
#
#			path_name = w.buffer.name
#			name = path_name.split('/')[-1]
#
#			if name == buffer_name:
#				return w.buffer
#
#		return None
#
#	def results_buffer_from_xpath(self, xpath, width):
#		bufout = []
#
#		if len(self.parse_errors) == 0:
#			bufout += self.build_search_header(xpath, width)
#
#			try:
#				results = self.evaluate_xpath(xpath)
#				bufout += self.build_results_buffer(results, width)
#
#			except Exception as inst:
#				bufout.append(str(inst))
#		else:
#			bufout += self.build_parse_error_message(width)
#		
#		return bufout
#
#	def build_parse_error_message(self, width):
#		bufout = []
#		bufout.append('—' * width)
#		bufout.append('XML Validation Error')
#		bufout.append('—' * width)
#		bufout += self.parse_errors
#		return bufout
#
#	def build_search_header(self, xpath, width):
#		bufout = []
#		bufout.append('—' * width)
#		bufout.append('Results: ' + xpath)
#		bufout.append('—' * width)
#		return bufout
#
#	def evaluate_xpath(self, xpath):
#		self.results = self.xpath_evaluator(xpath)
#		self.parsed_results = [self.parse_result(xpath, r) for r in self.results]
#		return self.parsed_results
#
#	def build_results_buffer(self, results, width):
#		bufout = []
#		if len(results) > 0:
#			column_max = self.calculate_max_column_widths(results)
#
#			header_row = self.build_column_headers(column_max)
#			bufout += header_row
#
#			for i, r in enumerate(results):
#				if i < 99:
#					result_row = self.build_result_row(column_max, r)
#					bufout += result_row
#				elif i == 99:
#					result_row = ['More than 100 results, please narrow your XPATH...']
#					bufout += result_row
#				else:
#					pass
#
#
#		else:
#			bufout.append('No results.')
#
#		return bufout
#
#
#	def calculate_max_column_widths(self, results):
#		column_max = {}
#		for prop in self.result_properties:
#			column_max[prop] = self.default_column_widths[prop]
#			for r in results:
#				col_width = len(str(r.__getattribute__(prop))) + self.result_padding
#				if col_width > column_max[prop]:
#					column_max[prop] = col_width
#
#		return column_max
#
#	def build_column_headers(self, column_widths):
#		output_list = []
#		header_break = []
#		for prop in self.result_properties:
#			output_list.append(column_widths[prop])
#			header_break.append(column_widths[prop])
#
#			output_list.append('|' + self.column_names[prop])
#			header_break.append('|' + '—'*(column_widths[prop] - 1))
#
#		headers = "%-*s %-*s %-*s" % tuple(output_list)
#		header_break = "%-*s %-*s %-*s" % tuple(header_break)
#		return [headers, header_break]
#
#	def build_result_row(self, column_widths, result_row):
#		output_list = []
#		for prop in self.result_properties:
#			output_list.append(column_widths[prop])
#			if result_row.__getattribute__(prop) is not None:
#				propout = str(result_row.__getattribute__(prop))
#				propout = propout.replace("\n", "")
#				output_list.append('|' + propout)
#			else:
#				output_list.append('|-')
#
#		row = "%-*s %-*s %-*s" % tuple(output_list)
#		return [row]


class XPathResult(object):
	def __init__(self, el):
		self.line = self.build_line(el)
		self.tag = self.build_tag(el)
		self.result = self.build_result(el)

	def build_line(self, el):
		pass

	def build_tag(self, el):
		pass

	def build_result(self, el):
		pass

class XPathParseErrorResult(XPathResult):
	def __init__(self, error):
		self.error = error

class XPathNodeResult(XPathResult):
	def build_line(self, el):
		return el.sourceline

	def build_tag(self, el):
		return el.tag

class XPathTagResult(XPathNodeResult):
	def build_result(self, el):
		text = ""
		if el.text is not None:
			text = el.text

		if re.sub("\s", "", text) == "":
			attrib_string = ""
			for a in el.attrib.keys():
				attrib_string += "@" + a + ": \"" + el.attrib[a] + "\" "
			
			return attrib_string
		else:
			return text
		#except:
		#	return None

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

