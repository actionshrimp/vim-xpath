import unittest

import vim_adaptor as a

class VimModuleBufferStub(list):

    def __init__(self):
        self.number = 0
        
    def set_contents(self, contents_string):
        self[:] = contents_string.split("\n")

class VimModuleCurrentStub(object):

    def __init__(self):
        self.buffer = VimModuleBufferStub()

class VimModuleStub(object):

    evaluated = []
    
    def __init__(self):
        self.current = VimModuleCurrentStub()
        VimModuleStub.evaluated = []
        
    def eval(self, vim_command):
        VimModuleStub.evaluated.append(vim_command)

class VimAdaptorTests(unittest.TestCase):

    def stub_vim_current_buffer(self, buffer_contents):
        a.vim.current.buffer.set_contents(buffer_contents)

    def setUp(self):
        a.vim = VimModuleStub()
        
    def test_buffer_mock(self):
        test_string = "test buffer contents"
        self.stub_vim_current_buffer(test_string)
        self.assertEqual("test buffer contents", 
                         a.get_current_buffer_string())

    def test_xpath_evaluation(self):
        test_xml = "<Root>\n<Tag/>\n<Tag/>\n</Root>"
        self.stub_vim_current_buffer(test_xml)
        a.evaluate_xpath_on_current_buffer("//Tag")
        self.assertEqual("setloclist(0, [], 'r')", VimModuleStub.evaluated[0])
        
        self.assertEqual("setloclist(0, [{" +
                         "'bufnr': 0, " +
                         "'lnum': 2, " +
                         "'text': '<Tag>', " +
                         "}], 'a')",
                         VimModuleStub.evaluated[1])
        
        self.assertEqual("setloclist(0, [{" +
                         "'bufnr': 0, " +
                         "'lnum': 3, " +
                         "'text': '<Tag>', " +
                         "}], 'a')",
                         VimModuleStub.evaluated[2])

    def test_xpath_with_undefined_namespace_errors(self):
        test_xml = "<Root xmlns:ns='test.org'><ns:Tag/></Root>"
        self.stub_vim_current_buffer(test_xml)

        a.evaluate_xpath_on_current_buffer('//vimns:Tag')

        self.assertEqual("setloclist(0, [{" +
                         "'bufnr': 0, " +
                         "'type': 'E', " +
                         "'text': 'Undefined namespace prefix in XPath'" +
                         "}], 'a')",
                         VimModuleStub.evaluated[1])

    def test_xpath_which_doesnt_return_a_line_number(self):
        text_xml = "<Root><Tag/></Root>"
        self.stub_vim_current_buffer(text_xml)

        a.evaluate_xpath_on_current_buffer("'test string'")

        self.assertEqual("setloclist(0, [{" +
                         "'bufnr': 0, " +
                         "'text': 'string: test string', " +
                         "}], 'a')",
                         VimModuleStub.evaluated[1])
