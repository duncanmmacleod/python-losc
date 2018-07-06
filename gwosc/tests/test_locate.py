# -*- coding: utf-8 -*-
# Copyright Duncan Macleod 2018
#
# This file is part of GWOSC.
#
# GWOSC is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# GWOSC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with GWOSC.  If not, see <http://www.gnu.org/licenses/>.

"""Tests for :mod:`gwosc.locate`
"""

__author__ = 'Duncan Macleod <duncan.macleod@ligo.org>'

import os.path

from .. import (
    locate,
    urls as gwosc_urls,
    utils,
)


def test_get_urls():
    # test simple fetch for S6 data returns only files within segment
    detector = 'L1'
    start = 934000000
    end = 934100000
    span = (start, end)
    urls = locate.get_urls(detector, start, end)
    for url in urls:
        assert os.path.basename(url).startswith(
            '{}-{}'.format(detector[0], detector))
        assert utils.segments_overlap(
            utils.url_segment(url), span)


def test_get_event_urls(gw150914_urls):
    # find latest version by brute force
    latestv = sorted(
        gwosc_urls.URL_REGEX.match(
            os.path.basename(u['url'])).groupdict()['version'] for
        u in gw150914_urls)[-1]

    event = 'GW150914'
    urls = locate.get_event_urls(event)
    for url in urls:
        assert url.endswith('.hdf5')  # default format
        assert '_4_' in url  # default sample rate
        assert '_{}-'.format(latestv) in url  # highest matched version

    urls = locate.get_event_urls(event, version=1)
    for url in urls:
        assert '_V1-' in url