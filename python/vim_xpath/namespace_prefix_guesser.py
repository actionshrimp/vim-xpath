from lxml import etree

class PrefixGuessingError(Exception):
    def __init__(self, e):
        self.inner = e
        self.message = "An error occurred while guessing namespace prefixes: "\
           + "{0} - {1}".format(e.__class__.__name__, e.message)

def guess_prefixes(xml):
    try:
        return _guess_prefixes(xml)
    except Exception as e:
        wrapped = PrefixGuessingError(e)
        raise wrapped

def _guess_prefixes(xml):
    """Attempt to create a rough prefix -> url mapping based on an input XML.
    The tree is traversed depth first, and the first node to define the
    prefix 'claims' it with URL assosciated with that prefix in that node.
    The first prefixless namespace found is given the prefix 'default'. """

    prefixes = {}

    tree = etree.fromstring(xml)

    for el in tree.iter():
        node_prefixes = el.nsmap
        if node_prefixes is not None:
            for prefix in node_prefixes.keys():
                url = node_prefixes[prefix]

                if prefix is None:
                    prefix = "default"

                if not prefix in prefixes:
                    prefixes[prefix] = url

    return prefixes
