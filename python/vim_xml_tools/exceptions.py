from lxml import etree

def from_lxml_exception(e):
    out = e

    if isinstance(e, etree.XPathError):
        out = XPathError(e)

        if isinstance(e, etree.XPathSyntaxError):
            out = XPathSyntaxError(e)

        if isinstance(e, etree.XPathEvalError):
            out = XPathEvaluationError(e)

            if 'XPATH_UNDEF_PREFIX_ERROR' in str(e.error_log):
                out = XPathNamespaceUndefinedError(e)

    return out

class XPathError(Exception):
    def __init__(self, e):
        self.inner = e
        self.message = e.message

class XPathSyntaxError(XPathError):
    def __init__(self, e):
        self.inner = e
        self.message = "Syntax error in XPath: " + e.message

class XPathEvaluationError(XPathError):
    def __init__(self, e):
        self.inner = e
        self.message = "Error occurred while evaluating XPath: " + e.message

class XPathNamespaceUndefinedError(XPathEvaluationError):
    def __init__(self, e):
        self.inner = e
        self.message = "Undefined namespace prefix in XPath"
