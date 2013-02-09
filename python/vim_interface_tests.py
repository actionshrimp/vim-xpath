import unittest

import vim_interface as i

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

class VimInterfaceTests(unittest.TestCase):

    def stub_vim_current_buffer(self, buffer_contents):
        i.vim.current.buffer.set_contents(buffer_contents)

    def setUp(self):
        i.vim = VimModuleStub()
        
    def test_buffer_mock(self):
        test_string = "test buffer contents"
        self.stub_vim_current_buffer(test_string)
        self.assertEqual("test buffer contents", 
                         i.get_current_buffer_string())

    def test_xpath_evaluation(self):
        test_xml = "<Root>\n<Tag/>\n<Tag/>\n</Root>"
        self.stub_vim_current_buffer(test_xml)
        i.evaluate_xpath_on_current_buffer("//Tag")
        self.assertEqual("let s:xpath_results_list = []", 
                         VimModuleStub.evaluated[0])
        
        self.assertEqual("let s:result_dict = " +
                         "{bufnr: 0, lnum: 2, text: '<Tag>'}",
                         VimModuleStub.evaluated[1])
        self.assertEqual("let s:xpath_results_list += s:result_dict",
                         VimModuleStub.evaluated[2])
        
        self.assertEqual("let s:result_dict = " +
                         "{bufnr: 0, lnum: 3, text: '<Tag>'}",
                         VimModuleStub.evaluated[3])
        self.assertEqual("let s:xpath_results_list += s:result_dict",
                         VimModuleStub.evaluated[4])
        
        self.assertEqual("setloclist(0, s:xpath_results_list, 'r')",
                         VimModuleStub.evaluated[5])
