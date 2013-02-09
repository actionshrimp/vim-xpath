from lxml import etree

def from_lxml_exception(e):
    if isinstance(e, etree.XPathError):
        if 'XPATH_UNDEF_PREFIX_ERROR' in str(e.error_log):
            return XPathNamespaceUndefinedError(e)

class XPathNamespaceUndefinedError(Exception):
    def __init__(self, e):
        self.inner = e
        self.message = e.message
