syntax match CurrentXPathResult /\(\(^|\d.*\%#.*$\)\|\(^|\%#\d.*$\)\|\(^\%#|\d.*$\)\)/
syntax match CurrentNotXPathResult /\(\(^[^|][^\d].*\%#.*$\)\|\(^[^|]\%#\[^d].*$\)\|\(^\%#[^|][^\d].*$\)\)/

hi link CurrentXPathResult Error
