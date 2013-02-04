import re
from lxml import etree

LIBXML2_MAX_LINE = 65534

def evaluate(xml, xpath, namespaces=dict()):
    """Evaluate an xpath against some xml. 
    Reports line numbers correctly on xml with over 65534 lines"""

    tree = etree.fromstring(xml)
    tree_matches = tree.xpath(xpath, namespaces=namespaces)

    if not(isinstance(tree_matches, list)):
        tree_matches = [tree_matches]

    matches = []
    line_compress_required = False

    for match in tree_matches:
        output_match = tree_match_to_output_match(match, namespaces)

        if (output_match["line_number"] is None) or \
                output_match["line_number"] <= LIBXML2_MAX_LINE:
            #Only keep matches which are in the line range that libxml2
            #actually reports correctly
            matches.append(output_match)
        else:
            #If there are any higher range matches, we will have to 'compress lines'
            line_compress_required = True
            break;

    if line_compress_required:
        #Compress the inital line range 1-65534 into a single line,
        #to give us correct line numbers on the next 65534 lines.
        line_compressed_xml = xml.replace("\n", "", LIBXML2_MAX_LINE)

        #Re-evaluate with the new source XML recursively,
        #to handle all higher line ranges
        line_compressed_matches = evaluate(line_compressed_xml, xpath)

        #Only take matches which we haven't already found, as the higher range
        #evaluations will have incorrect line numbers for matches in lower ranges
        #(the sourceline will be 1 for all lower range matches)
        new_output_matches = line_compressed_matches[len(matches):]

        for output_match in new_output_matches:
            #As we've compressed a bunch of lines down to 1 line, we need to
            #offset the line number of the results to compensate for this
            output_match["line_number"] += LIBXML2_MAX_LINE
            matches.append(output_match)

    return matches

def tree_match_to_output_match(match, namespaces):
    """Convert an lxml xpath match to a result output dictionary"""
    out = dict()
    out["line_number"] = output_line_number(match)
    out["match_type"] = output_match_type(match)
    out["match_text"] = output_match_text(match, namespaces)
    out["value_text"] = output_value_text(match)

    return out

def output_line_number(match):
    """Return an output source line for a particular match result"""
    sourceline = None

    if isinstance(match, etree._Element):
        sourceline = match.sourceline

    if isinstance(match, etree._ElementStringResult):
        parent = match.getparent()
        if parent is not None:
            sourceline = parent.sourceline

    return sourceline

def output_match_type(match):
    """Return an output 'type' for a particular match result"""
    match_type = "?"

    if isinstance(match, etree._Element):
        match_type = "Node"

    elif isinstance(match, etree._ElementStringResult):
        if match.is_attribute:
            match_type = "Attribute"
        else:
            match_type = "String"

    elif isinstance(match, bool):
        match_type = "Boolean"

    return match_type

def output_match_text(match, namespaces):
    """Text representing the match of the XPath"""
    match_text = ""

    if isinstance(match, etree._Element):
        match_text = prefixed_name_from_absolute_name(match.tag, namespaces)

    elif isinstance(match, etree._ElementStringResult):
        if match.is_attribute:
            match_text = "@" + match.attrname

    if match_text is None:
        match_text = ""

    return match_text

def output_value_text(match):
    """Text representing the value of the XPath"""
    value_text = ""

    if isinstance(match, etree._Element):
        value_text = match.text

    elif isinstance(match, etree._ElementStringResult):
        value_text = match

    elif isinstance(match, str):
        value_text = match

    elif isinstance(match, bool):
        value_text = str(match)

    if value_text is None:
        value_text = ""

    return value_text

def prefixed_name_from_absolute_name(name, namespaces):
    """Convert an lxml {namespaceuri}Name to prefix:Name,
    with prefixes defined in the namespaces dictionary"""
    regex_match = re.search('^\{(.*)\}', name)
    if regex_match:
        uri = regex_match.group(1)
        uri_with_braces = regex_match.group(0)

        prefix = [k for k, v in namespaces.items() if v == uri][0]
        prefixed = name.replace(uri_with_braces, "{0}:".format(prefix))

        return prefixed
    return name
