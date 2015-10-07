# vim-xpath

A plugin to allow XPath search and evaluation on XML documents being edited in
vim, using the python lxml library. Open an XML document, run the
:XPathSearchPrompt command, and type an XPath to see it evaluated before your
very eyes. Results appear in the vim location list.

Requires python, vim+python and the python lxml library to be installed. For
full installation/usage instructions, see doc/xpath.txt (:help xpath.txt)

This is a complete rewrite of the old version of the xpath plugin. 
Features of the rewrite:

- [✔] Proper namespace support
- [✔] Use the loclist instead of a custom output buffer, for more standard vim
  behavior
- [✔] Handle line numbers on large XML files correctly
- [ ] Reworking of auto-completion functionality - TBC
