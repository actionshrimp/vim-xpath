"Prevent script from being loaded multiple times
if exists("g:skip_xpath")
    finish
endif

"Check python is installed
if !has("python3")
    if !exists("g:quiet_xpath")
        echo 'vim-xpath requires vim to be compiled with python support, and '
                    \ . 'python to be installed. To stop this message from '
                    \ . 'appearing, either install python, uninstall this plugin '
                    \ . 'or add the line "let g:skip_xpath = 1" to your vimrc.'
    endif

    finish
endif

"Check python lxml library is installed
let s:no_lxml = 0

py3 << EOF
import vim
try:
    import lxml
except ImportError:
    vim.command('let s:no_lxml = 1')
EOF

if s:no_lxml
    if !exists("g:quiet_xpath")
        echo 'vim-xpath requires the lxml python library (http://lxml.de) to be '
                    \ . 'installed. To stop this message from appearing, either '
                    \ . 'install lxml, uninstall this plugin or add the line '
                    \ . '"let g:skip_xpath = 1" to your vimrc.'
    endif

    finish
endif

"Load the vim adaptor python script
let s:curfile = expand("<sfile>")
let s:curfiledir = fnamemodify(s:curfile, ":h")

let s:xpath_search_history = []

" 24.02.16 sfx2k
" Fix #12: join path-elements with python
py3 << EOF
import vim
import os

main_file = os.path.join(os.path.split(vim.eval('s:curfiledir'))[0], 'python', 'main.py')
sys.argv = [main_file]
vim.command("let s:pyfile='" + main_file + "'")
EOF

"Pass script location into script itself as an argument
execute "py3file " . s:pyfile

function! xpath#XPathGuessPrefixes()
    let l:active_window = winnr()
    let l:active_buffer = winbufnr(l:active_window)

    try
        execute "py3 vim_adaptor.guess_prefixes(" . l:active_buffer . ")"
        call XPathSetBufferPrefixes(l:ns_prefixes)
    catch
    endtry
endf

function! XPathSetBufferPrefixes(ns_prefixes)
    if !exists("g:ns_prefixes")
        let b:ns_prefixes = a:ns_prefixes
    else
        let b:ns_prefixes = copy(g:ns_prefixes)
        for prefix in keys(a:ns_prefixes)
            "Global prefixes always 'win'
            if !has_key(b:ns_prefixes, prefix)
                let b:ns_prefixes[prefix] = a:ns_prefixes[prefix]
            else
                let b:ns_prefixes[prefix . "_buf"] = a:ns_prefixes[prefix]
            endif
        endfor
    endif
endf

function! xpath#XPathShowBufferPrefixes()
    if !exists("b:ns_prefixes")
        call xpath#XPathGuessPrefixes()
    endif

    let l:ns_prefixes = s:XPathGetBufferPrefixes()

    let l:loclist = []
    for key in keys(l:ns_prefixes)
        let l:entry = {'text': key . ': ' . l:ns_prefixes[key]}
        let l:loclist += [l:entry]
    endfor

    call setloclist(winnr(), l:loclist)
    lopen
    wincmd w
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

function! xpath#XPathSearchPrompt()

    if !exists("b:ns_prefixes")
        call xpath#XPathGuessPrefixes()
    endif

    let l:active_window = winnr()
    let l:active_buffer = winbufnr(l:active_window)

    execute "echo setloclist(" . l:active_window . ", [{" .
                \ "'bufnr': " . l:active_buffer . "," .
                \ "'text': 'Start typing an XPath to search'}])"

    lopen

    above 1split XPath\ Search
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
    call XPathEvaluate(l:xpath, a:active_buffer, a:active_window)
    let s:xpath_search_history += [l:xpath]

    silent! bwipe
    silent! lfirst
    silent! lnext
endf

"Called when the contents of the search buffer changes at all
function! s:XPathChanged(search_buffer, active_buffer, active_window)
    let l:lines = getbufline(a:search_buffer, 1, "$")
    "Delete any lines apart from the first one
    if len(l:lines) > 1
        silent! 2,$d
    endif

    let l:xpath = s:XPathInSearchBuffer(a:search_buffer)
    call XPathEvaluate(l:xpath, a:active_buffer, a:active_window)
endf

"Get the XPath out of a search buffer
function! s:XPathInSearchBuffer(search_buffer)
    return getbufline(a:search_buffer, 1)[0]
endf

"Evaluate an XPath via the python vim adaptor
function! XPathEvaluate(xpath, active_buffer, active_window)
    let l:ns_prefixes = getbufvar(a:active_buffer, "ns_prefixes")
    let l:xpath = escape(a:xpath, "'\\")
    execute "py3 vim_adaptor.evaluate_xpath(" .
        \ a:active_buffer . ", " .
        \ a:active_window . ", " .
        \ "'" . l:xpath . "', " .
        \ string(l:ns_prefixes) . ")"
endf

function! XPathHistoryPopup()
    call complete(1, reverse(s:xpath_search_history))
    return ''
endf

let g:skip_xpath = 1
