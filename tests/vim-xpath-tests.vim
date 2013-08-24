runtime! tests/support/virtualenv.vim
runtime! plugin/vim-xpath.vim

describe 'vim-xpath'

    it 'should open the xpath search prompt'
        XPathSearchPrompt
        Expect bufexists("XPath Search") to_be_true
    end

    it 'should display a parse error if the buffer isnt valid xml'
        XPathSearchPrompt
        let ll = getloclist(1)
        Expect ll[0].text == 'Error parsing XML in target buffer: Unknown'
    end

end
