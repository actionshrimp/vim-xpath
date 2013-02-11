from lxml import etree

def from_lxml_exception(e):
    out = e

    if isinstance(e, etree.ParseError):
        out = XmlError(e)

    if isinstance(e, etree.XPathError):
        out = XPathError(e)

        if isinstance(e, etree.XPathSyntaxError):
            out = XPathSyntaxError(e)

        if isinstance(e, etree.XPathEvalError):
            out = XPathEvaluationError(e)

            if 'XPATH_UNDEF_PREFIX_ERROR' in str(e.error_log):
                out = XPathNamespaceUndefinedError(e)

    return out


class XmlToolsError(Exception):
    def __init__(self, e):
        self.inner = e
        self.message = e.message

class XmlError(XmlToolsError):
    def __init__(self, e):
        self.inner = e
        self.message = "XML parse error: " + e.message

class XPathError(XmlToolsError):
    def __init__(self, e):
        self.inner = e
        self.message = "XPath error: " + e.message

class XPathSyntaxError(XPathError):
    def __init__(self, e):
        self.inner = e
        self.message = "XPath syntax error: " + e.message

class XPathEvaluationError(XPathError):
    def __init__(self, e):
        self.inner = e
        self.message = "XPath evaluation error: " + e.message

class XPathNamespaceUndefinedError(XPathEvaluationError):
    def __init__(self, e):
        self.inner = e
        self.message = "XPath evaluation error: undefined namespace prefix"
