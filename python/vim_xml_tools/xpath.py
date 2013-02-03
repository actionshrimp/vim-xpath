from StringIO import StringIO
from lxml import etree

LIBXML2_MAX_LINE = 65534

def evaluate(xml, xpath):
    tree = etree.fromstring(xml)
    tree_matches = tree.xpath(xpath)

    matches = []
    fold_required = False

    for match in tree_matches:
        if match.sourceline <= LIBXML2_MAX_LINE:
            output_match = tree_match_to_output_match(match, 0)
            matches.append(output_match)
        else:
            fold_required = True
            break;

    if fold_required:
        xml_folded = xml.replace("\n", "", LIBXML2_MAX_LINE)

        folded_matches = evaluate(xml_folded, xpath)

        new_output_matches = folded_matches[len(matches):]

        for output_match in new_output_matches:
            output_match["line_number"] += LIBXML2_MAX_LINE
            matches.append(output_match)

    return matches

def tree_match_to_output_match(match, fold_offset):
    out = dict()
    out["line_number"] = match.sourceline + fold_offset
    out["display_text"] = match.tag

    return out
