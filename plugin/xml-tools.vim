"Prevent script from being loaded multiple times
if exists("g:loaded_xml_tools")
    finish
endif
let g:loaded_xml_tools = 1

if !has("python")
    echo 'vim-xpath requires vim to be compiled with python support, and python to be installed'
endif

"Load the vim adaptor python script
let s:curfile = expand("<sfile>")
let s:curfiledir = fnamemodify(s:curfile, ":h")

let s:pyfile = fnameescape(s:curfiledir . "/../python/main.py")

let s:xpath_search_history = []

"Pass script location into script itself as an argument
py import sys
execute "py sys.argv = ['" . s:pyfile . "']"
execute "pyfile " . s:pyfile

command XPathSearchPrompt :call XPathSearchPrompt()
command XPathGuessPrefixes :call XPathGuessPrefixes()
command XPathShowPrefixes :call XPathShowBufferPrefixes()

function! XPathGuessPrefixes()
    let l:active_window = winnr()
    let l:active_buffer = winbufnr(l:active_window)

    execute "py vim_adaptor.guess_prefixes(" . l:active_buffer . ")"
    call XPathSetBufferPrefixes(l:ns_prefixes)
endf

function! XPathSetBufferPrefixes(ns_prefixes)
    if !exists("g:ns_prefixes")
        let b:ns_prefixes = a:ns_prefixes
    else
        let b:ns_prefixes = copy(g:ns_prefixes)
        for prefix in keys(a:ns_prefixes)
            "Global prefixes always 'win'
            if !has_prefix(b:ns_prefixes, prefix)
                let b:ns_prefixes[prefix] = a:ns_prefixes[prefix]
            else
                let b:ns_prefixes[prefix . "_buf"] = a:ns_prefixes[prefix]
            endif
        endfor
    endif
endf

function! XPathShowBufferPrefixes()
    let l:ns_prefixes = s:XPathGetBufferPrefixes()

    let l:loclist = []
    for key in keys(l:ns_prefixes)
        let l:entry = {'text': key . ': ' . l:ns_prefixes[key]}
        let l:loclist += [l:entry]
    endfor

    call setloclist(winnr(), l:loclist)
endf

function! s:XPathGetBufferPrefixes()
    let l:ns_prefixes = {}
    if exists("g:ns_prefixes")
        let l:ns_prefixes = g:ns_prefixes
    endif
    if exists("b:ns_prefixes")
        let l:ns_prefixes = b:ns_prefixes
    endif

    return l:ns_prefixes
endf

function! XPathSearchPrompt()

    if !exists("b:ns_prefixes")
        call XPathGuessPrefixes()
    endif

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

    setlocal updatetime=200
    execute "au CursorHold,CursorHoldI <buffer> :silent call " .
        \ "<SID>XPathChanged(" .
        \ l:search_buffer . ", " .
        \ l:active_buffer . ", " .
        \ l:active_window . ")"

"    execute \"au CompleteDone <buffer> :silent call <SID>XPathChanged(\" .
"        \ l:search_buffer . \", \" .
"        \ l:active_buffer . \", \" .
"        \ l:active_window . \")\"

    execute "au BufLeave <buffer> :silent call XPathComplete(" .
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

    inoremap <buffer> <silent> <C-h> <C-R>=XPathHistoryPopup()<CR>

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
    let l:ns_prefixes = getbufvar(a:active_buffer, "ns_prefixes")
    let l:xpath = escape(a:xpath, "'")
    execute "py vim_adaptor.evaluate_xpath(" .
        \ a:active_buffer . ", " .
        \ a:active_window . ", " .
        \ "'" . l:xpath . "', " .
        \ string(l:ns_prefixes) . ")"
endf

function! XPathHistoryPopup()
    call complete(1, reverse(s:xpath_search_history))
    return ''
endf
