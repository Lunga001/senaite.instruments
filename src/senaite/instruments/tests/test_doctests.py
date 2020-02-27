# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.INSTRUMENTS
#
# Copyright 2018 by it's authors.

import doctest

import unittest2 as unittest

from Testing import ZopeTestCase as ztc
from os.path import join

from .base import SimpleTestCase
from pkg_resources import resource_listdir

rst_filenames = [f for f in resource_listdir('senaite.instruments', "/docs")
                 if f.endswith('.rst')]

doctests = [join("../docs", filename) for filename in rst_filenames]


def test_suite():
    suite = unittest.TestSuite()
    for doctestfile in doctests:
        suite.addTests([
            ztc.ZopeDocFileSuite(
                doctestfile,
                test_class=SimpleTestCase,
                optionflags=doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE,
            ),
        ])
    return suite
