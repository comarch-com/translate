#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2009 Zuza Software Foundation
#
# This file is part of the Translate Toolkit.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

"""
Contains general placeable implementations. That is placeables that does not
fit into any other sub-category.
"""

import re

__all__ = ['AltAttrPlaceable', 'XMLEntityPlaceable', 'XMLTagPlaceable', 'parsers', 'to_general_placeables']

from translate.storage.placeables.base import G, Ph, StringElem


def regex_parse(cls, pstr):
    """A parser method to extract placeables from a string based on a regular
        expression. Use this function as the C{@parse()} method of a placeable
        class."""
    if cls.regex is None:
        return None
    matches = []
    oldend = 0
    for match in cls.regex.finditer(pstr):
        start, end = match.start(), match.end()
        if oldend != start:
            matches.append(StringElem(pstr[oldend:start]))
        matches.append(cls([pstr[start:end]]))
        oldend = end
    if oldend != len(pstr) and matches:
        matches.append(StringElem(pstr[oldend:]))
    return matches or None


class AltAttrPlaceable(G):
    """Placeable for the "alt=..." attributes inside XML tags."""

    regex = re.compile(r'alt=".*?"')
    parse = classmethod(regex_parse)


class FormattingPlaceable(Ph):
    """Placeable representing string formatting variables."""

    iseditable = False
    regex = re.compile(r"%[\-\+0\s\#]{0,1}(\d+){0,1}(\.\d+){0,1}[hlI]{0,1}[cCdiouxXeEfgGnpsS]{1}")
    parse = classmethod(regex_parse)


class UrlPlaceable(Ph):
    """Placeable handling URI."""

    regex = re.compile(r"([0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}|(((news|telnet|nttp|file|http|ftp|https)://)|(www|ftp)[-A-Za-z0-9]*\\.)[-A-Za-z0-9\\.]+)(:[0-9]*)?")
    # This one ismore complex and handles trailing paths, ideally these should be combined.
    #regex = re.compile(r"([0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}|(((news|telnet|nttp|file|http|ftp|https)://)|(www|ftp)[-A-Za-z0-9]*\\.)[-A-Za-z0-9\\.]+)(:[0-9]*)?/[-A-Za-z0-9_\\$\\.\\+\\!\\*\\(\\),;:@&=\\?/~\\#\\%]*[^]'\\.}>\\),\\\"]")
    parse = classmethod(regex_parse)


class FilePlaceable(Ph):
    """Placeable handling file locations."""

    regex = re.compile("(~/|/|\\./)([-A-Za-z0-9_\\$\\.\\+\\!\\*\\(\\),;:@&=\\?/~\\#\\%]|\\\\)+")
    parse = classmethod(regex_parse)


class EmailPlaceable(Ph):
    """Placeable handling emails."""

    regex = re.compile("((mailto:)|)[-A-Za-z0-9\\.]+@[-A-Za-z0-9\\.]+")
    parse = classmethod(regex_parse)


class PunctuationPlaceable(Ph):
    """Placeable handling punctuation."""

    iseditable = False
    regex = re.compile(r'[\(\)\[\]\{\}\,\.\-\!\:\;\'\"]+')
    parse = classmethod(regex_parse)


class XMLEntityPlaceable(Ph):
    """Placeable handling XML entities (C{&xxxxx;}-style entities)."""

    iseditable = False
    regex = re.compile(r'&\S+?;')
    parse = classmethod(regex_parse)


class XMLTagPlaceable(Ph):
    """Placeable handling XML tags."""

    iseditable = False
    regex = re.compile(r'<(\w+)(\s(\w*=".*?")?)*>|</(\w+)>')
    parse = classmethod(regex_parse)


def to_general_placeables(tree, classmap={G: (AltAttrPlaceable,), Ph: (XMLEntityPlaceable, XMLTagPlaceable, UrlPlaceable, FilePlaceable, EmailPlaceable, PunctuationPlaceable)}):
    if not isinstance(tree, StringElem):
        return tree

    newtree = None

    for baseclass, gclasslist in classmap.items():
        if isinstance(tree, baseclass):
            gclass = [c for c in gclasslist if c.parse(unicode(tree))]
            if gclass:
                newtree = gclass[0]()

    if newtree is None:
        newtree = tree.__class__()

    newtree.id = tree.id
    newtree.rid = tree.rid
    newtree.xid = tree.xid
    newtree.sub = []

    for subtree in tree.sub:
        newtree.sub.append(to_general_placeables(subtree))

    return newtree

parsers = [
    XMLTagPlaceable.parse,
    AltAttrPlaceable.parse,
    XMLEntityPlaceable.parse,
    FormattingPlaceable.parse,
    UrlPlaceable.parse,
    FilePlaceable.parse,
    EmailPlaceable.parse,
    PunctuationPlaceable.parse,
]