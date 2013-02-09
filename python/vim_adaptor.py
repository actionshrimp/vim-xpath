try:
    #vim module is only available when run from inside vim
    import vim
except ImportError:
    vim = None
    
from vim_xml_tools import xpath as x

VARIABLE_SCOPE = "s:"

def get_current_buffer_string():
    return "\n".join(vim.current.buffer)

def evaluate_xpath_on_current_buffer(xpath):
    eval_list = []
    eval_list.append("let {0}xpath_results_list = []".format(VARIABLE_SCOPE))
    
    xml = get_current_buffer_string()
    for result in x.evaluate(xml, xpath, {}):
        
        eval_list.append(("let {0}result_dict = " + 
                          "{{bufnr: {1}, lnum: {2}, text: '{3}{4}'}}"
                         ).format(VARIABLE_SCOPE,
                                  vim.current.buffer.number, 
                                  result["line_number"], 
                                  result["match"],
                                  result["value"]))
                         
        eval_list.append(("let {0}xpath_results_list += {0}result_dict"
                         ).format(VARIABLE_SCOPE)) 

    eval_list.append(("setloclist(0, {0}xpath_results_list, 'r')"
                     ).format(VARIABLE_SCOPE))

    for eval_line in eval_list:
        vim.eval(eval_line)
