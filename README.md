# vim-xpath [![Build Status](https://api.travis-ci.org/actionshrimp/vim-xpath.png?branch=master)](http://travis-ci.org/actionshrimp/vim-xpath)

A plugin to allow XPath search and evaluation on XML documents being edited in
vim, using the python lxml library.

For installation/usage instructions, see doc/xpath.txt

This is a complete rewrite of the old version of the xpath plugin. 
Features of the rewrite:

- [✔] Proper namespace support
- [✔] Use the loclist instead of a custom output buffer, for more standard vim
  behavior
- [✔] Handle line numbers on large XML files correctly
- [ ] Reworking of auto-completion functionality - TBC
