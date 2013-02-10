"Prevent script from being loaded multiple times
if exists("g:loaded_xml_tools")
    finish
endif
let g:loaded_xml_tools = 1

"Load the vim adaptor python script
let s:curfile = expand("<sfile>")
let s:curfiledir = fnamemodify(s:curfile, ":h")

let s:pyfile = fnameescape(s:curfiledir . "/../python/main.py")

"Pass script location into script itself as an argument
py import sys
execute "py sys.argv = ['" . s:pyfile . "']"
execute "pyfile " . s:pyfile

command XPath :call XPathSearchPrompt()

function! XPathSearchPrompt()

    inputsave()
    let l:xpath = input("XPath: ", "/")
    inputrestore()
    let l:xpath = escape(l:xpath, "'")
    if !empty(l:xpath)
        execute "py vim_adaptor.evaluate_xpath_on_current_buffer('" . l:xpath . "')"
        lwindow
        if len(getloclist(0)) > 0
            lfirst
        endif
    endif

endf
