from lxml import etree

def from_lxml_parse_exception(e):
    out = e

    if isinstance(e, etree.ParseError):
        out = BufferXmlError(e)

    return out

def from_lxml_xpath_exception(e):

    out = XPathError(e)

    if isinstance(e, etree.XPathError):

        if isinstance(e, etree.XPathSyntaxError):
            out = XPathSyntaxError(e)

        if isinstance(e, etree.XPathEvalError):
            out = XPathEvaluationError(e)

            if 'XPATH_UNDEF_PREFIX_ERROR' in str(e.error_log):
                out = XPathNamespaceUndefinedError(e)

    return out

class UnknownError(Exception):
    def __init__(self, e):
        self.inner = e
        self.msg = "An unknown error occurred: " + e.args[0]

class XmlBaseError(Exception):
    def __init__(self, e):
        self.inner = e
        self.msg = e.args[0]

class BufferXmlError(XmlBaseError):
    def __init__(self, e):
        self.inner = e
        self.msg = "Error parsing XML in target buffer: " + wrap_error_message(e.args[0])

class XPathError(XmlBaseError):
    def __init__(self, e):
        self.inner = e
        self.msg = "XPath error: " + wrap_error_message(e.args[0])

class XPathSyntaxError(XPathError):
    def __init__(self, e):
        self.inner = e
        self.msg = "XPath syntax error: " + wrap_error_message(e.args[0])

class XPathEvaluationError(XPathError):
    def __init__(self, e):
        self.inner = e
        self.msg = "XPath evaluation error: " + wrap_error_message(e.args[0])

class XPathNamespaceUndefinedError(XPathEvaluationError):
    def __init__(self, e):
        self.inner = e
        self.msg = "XPath evaluation error: undefined namespace prefix"

def wrap_error_message(msg):
    if msg is not None:
        return msg
    else:
        return "Unknown"
