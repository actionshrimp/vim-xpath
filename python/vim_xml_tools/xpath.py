from lxml import etree

def evaluate(xml, xpath):

    tree = etree.fromstring(xml)
    evaluated = tree.xpath(xpath)

    out = dict()
    out["line_number"] = evaluated[0].sourceline
    out["display"] = evaluated[0].tag
    return out
