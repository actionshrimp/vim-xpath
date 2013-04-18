version
runtime! plugin/vim-xpath.vim

describe 'vim-xpath'

    it 'should open the xpath search prompt'
        cd %:p:h
        e ../python/vim_xpath/tests/samples/simple.xml
        XPathSearchPrompt
    end

end
