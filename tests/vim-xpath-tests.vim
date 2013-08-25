runtime! tests/support/virtualenv.vim
runtime! plugin/vim-xpath.vim

describe 'vim-xpath'

    it 'should open the xpath search prompt'
        XPathSearchPrompt
        call feedkeys("\<CR>")
        Expect bufexists("XPath Search") to_be_true
        q
    end

    it 'should display a parse error if the buffer isnt valid xml'
        call XPathEvaluate("//test", 1, 1)
        let ll = getloclist(1)
        Expect ll[1].text == 'Error parsing XML in target buffer: Unknown'
    end

    it 'should display an xpath error if the xpath is malformed'
        e python/vim_xpath/tests/samples/api_response.xml
        call XPathEvaluate("//some()rubbish", 1, 1)
        let ll = getloclist(1)
        Expect ll[1].text == 'XPath syntax error: Invalid expression'
    end

    it 'should display results if the xpath is legit'
        e python/vim_xpath/tests/samples/api_response.xml
        call XPathEvaluate("//track/title", 1, 1)
        let ll = getloclist(1)
        Expect ll[1].text == '<title>: Tap Out'
        Expect len(ll) == 12
    end
end


