let s:scriptfile = expand("<sfile>")
execute "pyfile ".fnameescape(fnamemodify(s:scriptfile, ":h"). "/../xpathsearch/xpath.py")

let s:xpathbuffer = -1
let s:xpathtreebuffer = -1
let s:xpathresultsbuffer = -1
let s:xpathresultsbufferlinesize = 104
let s:lastxpath = ""
let s:lastline = -1
let s:resultsheadersize = -1

py import vim, time, re
py lasttime = 0

function! XPathResultsCursorlineCheck()
	let l:curline = line('.')
	if (l:curline > s:resultsheadersize)
		setlocal cursorline
	else
		setlocal nocursorline
	endif
endfunction


function! CreateXPathSplit()
	let l:bname = 'xpath_search_results'
	let l:bufnr = bufnr('^'.bname.'$')

	if l:bufnr > -1
		let l:winnr = bufwinnr(l:bufnr)
		if l:winnr > -1 
			exe l:winnr . 'wincmd w' 
		else
			below 10new
			exe 'buffer' . l:bufnr
		endif
	else
		below 10new
		setlocal buftype=nofile bufhidden=hide noswapfile
		exe 'file ' . l:bname
		setlocal syntax=xpathsearch
		nmap <buffer> <cr> :call XPathJumpToResult()<cr>
		nmap <buffer> X :q<cr>
		autocmd CursorMoved <buffer> :call XPathResultsCursorlineCheck()

		py resultsheadersize = len(xpath.build_search_header(':-)')) + len(xpath.build_column_headers(xpath.default_column_widths))
		py vim.command("let s:resultsheadersize = %d" % resultsheadersize)

	endif

	let l:curwinnr = bufwinnr(s:xpathbuffer)
	exe l:curwinnr . 'wincmd w'

	let l:bufnr = bufnr('^'.bname.'$')
	return l:bufnr

endfunction

let s:changecounter = -1

function! XPathSearch(xpath)
	let s:xpathbuffer = bufnr('%')
	py path = vim.eval("a:xpath")
	
	if ((changenr() > s:changecounter) || (s:xpathtreebuffer != s:xpathbuffer))
		let s:changecounter = changenr()
		let s:treexpathbuffer = s:xpathbuffer
		"xml has changed, regenerate the xml tree
		py b = vim.current.buffer
		py xpath = VimXPath("\n".join(b[:]))
	endif

	let l:bufoutnr = CreateXPathSplit()
	if (s:xpathresultsbuffer != l:bufoutnr)
		let s:xpathresultsbuffer = l:bufoutnr
		py bufoutnr = int(vim.eval("l:bufoutnr")) - 1
		py listed = [(i, buf.name) for i, buf in enumerate(vim.buffers)]
		py bufout = vim.buffers[bufoutnr]
		py linesize = int(vim.eval("s:xpathresultsbufferlinesize"))
		py del bufout[:]
		py <<EOF
whitespace = ""
for i in range(100):
	whitespace += " "

for i in range(linesize):
	bufout.append(whitespace)
EOF
	endif

	py results = xpath.results_buffer_from_xpath(path)
	py <<EOF
for i, result in enumerate(results):
	bufout[i] = result

for i in range(len(results), linesize+1):
	bufout[i] = whitespace
EOF

endfunction

function! XPathSearchPrompt()
	let l:xpath = ''

	while (1 == 1)
		echo 'XSEARCH: ' . l:xpath
		let l:char = getchar()

		"End when enter is pressed
		if (l:char == 13)
			let s:lastxpath = l:xpath
			call XPathSearch(l:xpath)

			let l:curwinnr = bufwinnr(s:xpathresultsbuffer)
			exe l:curwinnr . 'wincmd w'
			exe (s:resultsheadersize+1)

			break
		endif

		if (l:char == 27)
			break
		endif

		if (l:char == "\<Up>")
			let l:xpath = s:lastxpath
		endif

		if (l:char == "\<Down>")
			let s:lastxpath = l:xpath
			let l:xpath = ""
		endif

		if (l:char == "\<BS>")
			if len(l:xpath) > 1
				let l:xpath = l:xpath[:-2]
			else
				let l:xpath = ''
			endif
		else
			let l:strchar = nr2char(l:char)
			let l:xpath = l:xpath . l:strchar
		endif
		call XPathSearch(l:xpath)
		redraw
	endwhile
endfunction

function! XPathJumpToResult()

	py curline = vim.current.buffer[vim.current.window.cursor[0]-1]
	py <<EOF
try:
	resultline = re.match("^\|(\d+).*$", curline).groups()[0]
except:
	resultline = '-1'
EOF

	py vim.command('let l:resultline = %s' % resultline)
	if l:resultline > 0
		let l:curwinnr = bufwinnr(s:xpathbuffer)
		exe l:curwinnr . 'wincmd w'
		exe ':'.l:resultline
	endif

endfunction

nnoremap X :call XPathSearchPrompt()<cr>
