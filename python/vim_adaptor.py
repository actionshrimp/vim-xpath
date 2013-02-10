try:
    #vim module is only available when run from inside vim
    import vim
except ImportError:
    vim = None
    
from vim_xml_tools import xpath as x
from vim_xml_tools.exceptions import XPathError

VARIABLE_SCOPE = "s:"

def get_current_buffer_string():
    return "\n".join(vim.current.buffer)

def evaluate_xpath_on_current_buffer(xpath):
    loc_list = VimLocListAdaptor()
    loc_list.clear_current_list()
    
    xml = get_current_buffer_string()

    try:
        results = x.evaluate(xml, xpath, {})
        for result in results:
            loc_list.add_result_entry(result["line_number"], result["match"])
    except XPathError as e:
        loc_list.add_error_entry(e.message)

class VimLocListAdaptor(object):

    def clear_current_list(self):
        vim.eval("setloclist(0, [], 'r')")

    def add_result_entry(self, line_number, text):
        bufnr = "'bufnr': {0}, ".format(vim.current.buffer.number)

        lnum = ""
        if line_number is not None:
            lnum = "'lnum': {0}, ".format(line_number)

        text = "'text': '{0}', ".format(text)

        vim.eval("setloclist(0, [{" + bufnr + lnum + text + "}], 'a')")

    def add_error_entry(self, error_text):
        vim.eval(("setloclist(0, [{{" +
                  "'bufnr': {0}, " +
                  "'type': 'E', " +
                  "'text': '{1}'" +
                  "}}], 'a')"
                 ).format(vim.current.buffer.number, error_text))
