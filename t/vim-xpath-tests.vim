version
runtime! plugin/vim-xpath.vim

describe 'vim-xpath'

    it 'should open the xpath search prompt'
        XPathSearchPrompt
        Expect bufexists("XPath Search") to_be_true
    end

end
