try:
    #vim module is only available when run from inside vim
    import vim
except ImportError:
    vim = None

VARIABLE_SCOPE = "s:"

def get_current_buffer_string():
    return "\n".join(vim.current.buffer)

def evaluate_xpath_on_current_buffer(xpath):
    eval_list = []
    eval_list.append("let {0}xpath_results_list = []".format(VARIABLE_SCOPE))
    
    eval_list.append(("let {0}result_dict = " + 
                      "{{bufnr: {1}, lnum: {2}, text: '{3}'}}"
                     ).format(VARIABLE_SCOPE,
                              vim.current.buffer.number, 2, '<Tag>'))
    eval_list.append(("let {0}xpath_results_list += {0}result_dict"
                     ).format(VARIABLE_SCOPE)) 

    for eval_line in eval_list:
        vim.eval(eval_line)
