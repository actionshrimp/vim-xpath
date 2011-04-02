echohl Error
if !(has("python"))
	echo "XPath plugin not loaded due to no python support."
else

	py import vim, re

	let s:scriptfile = expand("<sfile>")
	execute "pyfile ".fnameescape(fnamemodify(s:scriptfile, ":h"). "/../xpath/xpath.py")

	py vim.command("let lxml_imported = " + str(LXML_IMPORTED))

	if !(lxml_imported)
		echo "XPath plugin not loaded - python lxml is required"
	else
		echohl None
		"Used to track the results buffer
		let s:results_buffer_name = 'xpath_search_results'
		let s:result_pattern = '^┃\(\d\+\).*$'

		nnoremap X :call XPathSearchPrompt()<cr>

		function! XPathSearchPrompt()

			let s:search_buffer = bufnr('%')
			silent call XPathResultsSplit(s:search_buffer)

			call inputsave()
			let l:xpath = input("XPath: ", "//", "customlist,XPathSearchPromptCompletion")
			call inputrestore()

			if l:xpath != ""
				call XPathSearch(l:xpath, s:search_buffer)
				call JumpToFirstXPathResult()
			endif

		endfunction

		function! XPathSearchPromptCompletion(lead, line, pos)


			"call XPathSearch(a:line, s:search_buffer)
			py xpath = vim.eval("a:line")
			py search_buffer_name = vim.eval("bufname('%')")
			py completions = xpath_interface.get_completions(search_buffer_name, xpath)

			py vim.command("let l:complist = " + str(completions))

			redraw

			return l:complist

		endfunction

		function! XPathSearch(xpath, search_buffer)

			let l:search_window = bufwinnr(a:search_buffer)

			let [l:results_buffer, l:results_window] = XPathResultsSplit(a:search_buffer)
			
			py xpath = vim.eval("a:xpath")
			py search_buffer_name = vim.eval("bufname('%')")

			py xpath_interface.xpath_search(search_buffer_name, xpath)

		endfunction

		function! JumpToFirstXPathResult()

			let l:results_buffer = bufnr('^' . s:results_buffer_name . '$')
			let l:search_window = bufwinnr(l:results_buffer)
			exe l:search_window . 'wincmd w'

			call search(s:result_pattern)

		endfunction

		function! XPathResultsSplit(search_buffer)

			let l:not_loaded = -1

			let l:results_buffer = bufnr('^' . s:results_buffer_name . '$')
			
			"Create a results buffer if one doesn't exist
			if l:results_buffer == l:not_loaded
				let l:results_buffer = CreateXPathResultsBuffer(s:results_buffer_name)

				py results_buffer_name = vim.eval('s:results_buffer_name')
				py xpath_interface = VimXPathInterface(vim, results_buffer_name)

			endif

			let l:results_window = bufwinnr(l:results_buffer)

			"Create a results window if one doesn't exist
			if l:results_window == l:not_loaded
				let l:results_window = CreateXPathResultsWindow(l:results_buffer)
			endif

			call SetupXPathResultsWindow(l:results_window, a:search_buffer)

			return [l:results_buffer, l:results_window]

		endfunction

		function! CreateXPathResultsBuffer(results_buffer_name)
			exe 'badd ' . a:results_buffer_name
			let l:results_buffer = bufnr('^' . a:results_buffer_name . '$')
			return l:results_buffer
		endfunction

		function! CreateXPathResultsWindow(results_buffer)
			below 10new
			exe 'buffer ' . a:results_buffer
			let l:results_window = bufwinnr(a:results_buffer)
			return l:results_window
		endfunction

		function! SetupXPathResultsWindow(results_window, search_buffer)
			exe a:results_window . 'wincmd w'

			call SetupXPathResultsBuffer(a:search_buffer)
			
			let l:search_window = bufwinnr(a:search_buffer)
			exe l:search_window . 'wincmd w'
		endfunction

		function! SetupXPathResultsBuffer(search_buffer)
			"These commands must be called when the 
			"current window is the results window
			setlocal buftype=nofile bufhidden=hide noswapfile syntax=xpathresults nowrap

			nmap <buffer> <silent> X :q<cr>
			autocmd CursorMoved <buffer> :call XPathResultsCursorlineCheck()
			autocmd VimResized <buffer> :py xpath_interface.window_resized()

			exe "nmap <buffer> <silent> <cr> :call XPathJumpToResult(" . a:search_buffer . ")<cr>"
		endfunction

		function! XPathJumpToResult(search_buffer)

			let l:current_line = getline('.')
			let l:line_number_pattern_results = matchlist(l:current_line, s:result_pattern)
			try

				let l:result_line = l:line_number_pattern_results[1]

				let l:search_window = bufwinnr(a:search_buffer)
				exe l:search_window . 'wincmd w'

				exe l:result_line
				normal zv

			catch /E684:/
			endtry

		endfunction

		function! XPathResultsCursorlineCheck()

			let l:syntax_under_cursor = synIDattr(synID(line("."), col("."), 1), "name")

			if (l:syntax_under_cursor == 'CurrentXPathResult')
				setlocal cursorline
			else
				setlocal nocursorline
			endif
		endfunction

	endif
endif
echohl None
