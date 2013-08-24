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
        self.message = "An unknown error occurred: " + e.message

class XmlBaseError(Exception):
    def __init__(self, e):
        self.inner = e
        self.message = e.message

class BufferXmlError(XmlBaseError):
    def __init__(self, e):
        self.inner = e
        self.message = "Error parsing XML in target buffer: " + wrap_error_message(e.message)

class XPathError(XmlBaseError):
    def __init__(self, e):
        self.inner = e
        self.message = "XPath error: " + wrap_error_message(e.message)

class XPathSyntaxError(XPathError):
    def __init__(self, e):
        self.inner = e
        self.message = "XPath syntax error: " + wrap_error_message(e.message)

class XPathEvaluationError(XPathError):
    def __init__(self, e):
        self.inner = e
        self.message = "XPath evaluation error: " + \
                                                wrap_error_message(e.message)

class XPathNamespaceUndefinedError(XPathEvaluationError):
    def __init__(self, e):
        self.inner = e
        self.message = "XPath evaluation error: undefined namespace prefix"

def wrap_error_message(msg):
    if msg is not None:
        return msg
    else:
        return "Unknown"
