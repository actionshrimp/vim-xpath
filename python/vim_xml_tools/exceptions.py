from lxml import etree

def from_lxml_exception(e):
    out = e

    if isinstance(e, etree.XPathError):
        out = XPathError(e)

        if 'XPATH_UNDEF_PREFIX_ERROR' in str(e.error_log):
            out = XPathNamespaceUndefinedError(e)

    return out

class XPathError(Exception):
    def __init__(self, e):
        self.inner = e
        self.message = "Error occurred while evaluating XPath: " + e.message

class XPathNamespaceUndefinedError(XPathError):
    def __init__(self, e):
        self.inner = e
        self.message = "XPath contained a namespace prefix that was " + \
            "undefined. Please define it (see :help xml-tools-namespaces)."

