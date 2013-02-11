"Prevent script from being loaded multiple times
if exists("g:loaded_xml_tools")
    finish
endif
let g:loaded_xml_tools = 1

"Load the vim adaptor python script
let s:curfile = expand("<sfile>")
let s:curfiledir = fnamemodify(s:curfile, ":h")

let s:pyfile = fnameescape(s:curfiledir . "/../python/main.py")

let s:xpath_search_history = []

"Pass script location into script itself as an argument
py import sys
execute "py sys.argv = ['" . s:pyfile . "']"
execute "pyfile " . s:pyfile

command XPath :call XPathSearchPrompt()

function! XPathSearchPrompt()

    let l:active_window = winnr()
    let l:active_buffer = winbufnr(l:active_window)

    execute "echo setloclist(" . l:active_window . ", [{" .
                \ "'bufnr': " . l:active_buffer . "," .
                \ "'text': 'Start typing an XPath to search'}])"

    lopen

    above 1split 'XPath Search'
    set buftype=nofile
    setlocal noswapfile
    setlocal nonumber
    let l:search_window = winnr()
    let l:search_buffer = winbufnr(l:search_window)

    execute "au CursorMovedI <buffer> :silent call <SID>XPathChanged(" .
        \ l:search_buffer . ", " .
        \ l:active_buffer . ", " .
        \ l:active_window . ")"

    execute "nnoremap <buffer> <silent> <Return> :call XPathComplete(" .
        \ l:search_buffer . ", " .
        \ l:active_buffer . ", " .
        \ l:active_window . ")<CR>"

    execute "inoremap <buffer> <silent> <Return> <Esc>:call XPathComplete(" .
        \ l:search_buffer . ", " .
        \ l:active_buffer . ", " .
        \ l:active_window . ")<CR>"

    startinsert
endf

"Called when the XPath is finished (by hitting return)
function! XPathComplete(search_buffer, active_buffer, active_window)
    let l:xpath = s:XPathInSearchBuffer(a:search_buffer)
    call s:XPathEvaluate(l:xpath, a:active_buffer, a:active_window)
    let s:xpath_search_history += [l:xpath]

    silent bwipe
    silent lfirst
endf

"Called when the contents of the search buffer changes at all
function! s:XPathChanged(search_buffer, active_buffer, active_window)
    let l:lines = getbufline(a:search_buffer, 1, "$")
    "Delete any lines apart from the first one
    if len(l:lines) > 1
        silent 2,$d
    endif

    let l:xpath = s:XPathInSearchBuffer(a:search_buffer)
    call s:XPathEvaluate(l:xpath, a:active_buffer, a:active_window)
endf

"Get the XPath out of a search buffer
function! s:XPathInSearchBuffer(search_buffer)
    return getbufline(a:search_buffer, 1)[0]
endf

"Evaluate an XPath via the python vim adaptor
function! s:XPathEvaluate(xpath, active_buffer, active_window)
    let l:xpath = escape(a:xpath, "'")
    execute "py vim_adaptor.evaluate_xpath(" .
        \ a:active_buffer . ", " .
        \ a:active_window . ", " .
        \ "'" . l:xpath . "')"
endf
