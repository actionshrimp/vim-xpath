from lxml import etree

def from_lxml_exception(e):
    out = e

    if isinstance(e, etree.XPathError):
        out = XPathError(e)

        if 'XPATH_UNDEF_PREFIX_ERROR' in str(e.error_log):
            out = XPathNamespaceUndefinedError(e)

    return out

class XPathNamespaceUndefinedError(Exception):
    def __init__(self, e):
        self.inner = e
        self.message = e.message

class XPathError(Exception):
    def __init__(self, e):
        self.inner = e
        self.message = e.message
