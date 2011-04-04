syntax match XPathResult /^|\d\+.*$/
syntax match CurrentXPathResult /\(\(^|\d\+.*\%#.*$\)\|\(^|\%#\d\+.*$\)\|\(^\%#|\d\+.*$\)\)/

hi link CurrentXPathResult Error
