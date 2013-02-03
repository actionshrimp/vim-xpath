from lxml import etree

LIBXML2_MAX_LINE = 65534

def evaluate(xml, xpath):
    """Evaluate an xpath against some xml. 
    Reports line numbers correctly on xml with over 65534 lines"""

    tree = etree.fromstring(xml)
    tree_matches = tree.xpath(xpath)

    matches = []
    line_compress_required = False

    for match in tree_matches:
        if match.sourceline <= LIBXML2_MAX_LINE:
            #Only keep matches which are in the line range that libxml2
            #actually reports correctly
            output_match = tree_match_to_output_match(match)
            matches.append(output_match)
        else:
            #If there are any higher range matches, we will have to 'fold'
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

def tree_match_to_output_match(match):
    """Convert an lxml xpath match to a result output dictionary"""
    out = dict()
    out["line_number"] = match.sourceline
    out["display_text"] = match.tag

    return out
