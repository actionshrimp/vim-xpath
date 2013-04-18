# vim-xpath [![Build Status](https://api.travis-ci.org/actionshrimp/vim-xpath.png?branch=rewrite)](http://travis-ci.org/actionshrimp/vim-xpath)

A plugin to allow XPath search and evaluation on XML documents being edited in
vim, using the python lxml library.

This branch contains a work in progress rewrite of the plugin. The version in
the master branch currently works, so use that for the time being - this will
be merged into the master branch when ready.

Check the build status to see if the current version is usable - although the
tests are still being setup to work with Travis correctly.

Features of the rewrite:
- [✔] Use the loclist instead of a custom output buffer, for more standard vim
  behavior
- [✔] Handle line numbers on large XML files correctly
- [ ] Reworking of auto-completion functionality
