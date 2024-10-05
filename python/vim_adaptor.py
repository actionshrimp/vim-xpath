try:
    #vim module is only available when run from inside vim
    import vim
except ImportError:
    vim = None

from vim_xpath import xpath as x
from vim_xpath import namespace_prefix_guesser as g
from vim_xpath.exceptions import XPathError

VARIABLE_SCOPE = "s:"

def get_buffer_string(bufnr):
    offset = -1

    #0-indexed buffers object became 1-indexed in vim74
    try:
        vim.buffers[0]
    except ValueError:
        offset = 0
    except KeyError:
        offset = 0

    buffer = vim.buffers[bufnr + offset]
    return "\n".join(buffer)

def evaluate_xpath(bufnr, winnr, xpath, ns_prefixes={}):
    loc_list = VimLocListAdaptor(bufnr, winnr)
    loc_list.clear_current_list()
    loc_list.add_text_entry("Results for: " + xpath)

    xml = get_buffer_string(bufnr).encode()

    try:
        results = x.evaluate(xml, xpath, ns_prefixes)
        if len(results) > 0:
            for result in results:
                result["value"] = result["value"].decode("utf-8")
                loc_list.add_result_entry(result)
        else:
            loc_list.add_error_entry('No results returned')
    except Exception as e:
        if isinstance(e, XPathError) and xpath in ["", "//"]:
            loc_list.add_error_entry('No results returned')
        elif hasattr(e, "msg"):
            loc_list.add_error_entry(e.msg)
        else:
            loc_list.add_error_entry("ERROR: " + repr(e))

def guess_prefixes(bufnr):
    try:
        xml = get_buffer_string(bufnr).encode()
        prefixes = g.guess_prefixes(xml)

        outstr = "let l:ns_prefixes = {"
        for prefix in prefixes:
            outstr += '"{0}": "{1}",'.format(prefix, prefixes[prefix])

        outstr += "}"

        vim.command(outstr)
    except Exception as e:
        vim.command('throw "{0}"'.format(e.msg))

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
            val = result["value"].replace("\"", "\\\"")
            text += ": {0}".format(val)

        text_arg = "'text': \"{0}\", ".format(text)

        vim.eval(("setloclist({0}, [{{{1}}}], 'a')"
                 ).format(self.winnr, bufnr_arg + lnum_arg + text_arg))

    def add_text_entry(self, text):
        escaped = text.replace('"', '\\"')
        vim.eval(("setloclist({0}, [{{" +
                  "'bufnr': {1}, " +
                  "'text': \"{2}\"" +
                  "}}], 'a')"
                 ).format(self.winnr, self.bufnr, escaped))

    def add_error_entry(self, error_text):
        vim.eval(("setloclist({0}, [{{" +
                  "'bufnr': {1}, " +
                  "'type': 'E', " +
                  "'text': \"{2}\"" +
                  "}}], 'a')"
                 ).format(self.winnr, self.bufnr, error_text))
