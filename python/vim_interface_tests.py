import unittest

import vim_interface as i

class VimModuleCurrentStub(object):
    def __init__(self):
        self.buffer = ""

class VimModuleStub(object):
    def __init__(self):
        self.current = VimModuleCurrentStub()

class VimInterfaceTests(unittest.TestCase):
    def stub_vim_current_buffer(self, buffer_contents):
        i.vim.current.buffer = buffer_contents

    def setUp(self):
        i.vim = VimModuleStub()
        
    def test_buffer_mock(self):
        test_string = "test buffer contents"
        self.stub_vim_current_buffer(test_string)
        self.assertEqual("test buffer contents", i.get_buffer())
