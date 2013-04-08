try:
    #vim module is only available when run from inside vim
    import vim
except ImportError:
    vim = None
    
from vim_xpath import xpath as x
from vim_xpath import namespace_prefix_guesser as g
from vim_xpath.exceptions import XmlToolsError

VARIABLE_SCOPE = "s:"

def get_buffer_string(bufnr):
    buffer = vim.buffers[bufnr-1]
    return "\n".join(buffer)

def evaluate_xpath(bufnr, winnr, xpath, ns_prefixes={}):
    loc_list = VimLocListAdaptor(bufnr, winnr)
    loc_list.clear_current_list()
    
    xml = get_buffer_string(bufnr)

    try:
        results = x.evaluate(xml, xpath, ns_prefixes)
        if len(results) > 0:
            for result in results:
                loc_list.add_result_entry(result)
        else:
            loc_list.add_error_entry('No results returned')
    except XmlToolsError as e:
        loc_list.add_error_entry(e.message)

def guess_prefixes(bufnr):
    try:
        xml = get_buffer_string(bufnr)
        prefixes = g.guess_prefixes(xml)

        outstr = "let l:ns_prefixes = {"
        for prefix in prefixes:
            outstr += '"{0}": "{1}",'.format(prefix, prefixes[prefix])

        outstr += "}"

        vim.command(outstr)
    except Exception as e:
        vim.command('echo "{0}"'.format(e.message))

class VimLocListAdaptor(object):

    def __init__(self, bufnr, winnr):
        self.bufnr = bufnr
        self.winnr = winnr

    def clear_current_list(self):
        vim.eval("setloclist({0}, [], 'r')".format(self.winnr))

    def add_result_entry(self, result):
        bufnr_arg = "'bufnr': {0}, ".format(self.bufnr)

        lnum_arg = ""
        if result["line_number"] is not None:
            lnum_arg = "'lnum': {0}, ".format(result["line_number"])

        text = result["match"]
        if result["value"] != "":
            text += ": {0}".format(result["value"])

        text_arg = "'text': '{0}', ".format(text)

        vim.eval(("setloclist({0}, [{{{1}}}], 'a')"
                 ).format(self.winnr, bufnr_arg + lnum_arg + text_arg))

    def add_error_entry(self, error_text):
        vim.eval(("setloclist({0}, [{{" +
                  "'bufnr': {1}, " +
                  "'type': 'E', " +
                  "'text': '{2}'" +
                  "}}], 'a')"
                 ).format(self.winnr, self.bufnr, error_text))
