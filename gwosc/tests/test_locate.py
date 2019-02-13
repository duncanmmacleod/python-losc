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

import os.path

import pytest

from .. import (
    locate,
    urls as gwosc_urls,
    utils,
)
from gwpy.timeseries import TimeSeries
from gwosc import datasets

__author__ = 'Duncan Macleod <duncan.macleod@ligo.org>'


@pytest.mark.remote
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

    # test fetch for GW170817 data
    assert len(locate.get_urls('L1', 1187007040, 1187009088, tag='CLN')) == 1

    # assert no hits raises exception
    with pytest.raises(ValueError):  # no data in 1980
        locate.get_urls(detector, 0, 1)
    with pytest.raises(ValueError):  # no Virgo data for S6
        locate.get_urls('V1', start, end)


@pytest.mark.remote
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
        
def test_get_urls_bilby():
    psd_offset = -1024   # default values used in bilby
    psd_duration = 100   # to estimate the psd data.
    for event in datasets.find_datasets(type='event'):
        try:
            gps_time = datasets.event_gps(event)
            test = TimeSeries.fetch_open_data('L1',gps_time+psd_offset,gps_time+psd_offset+psd_duration)
            print('Data found for', event)
        except:
            try:
                test = TimeSeries.fetch_open_data('L1',gps_time+psd_offset,gps_time+psd_offset+psd_duration, tag='CLN')
                print('Tag required for', event)
            except: 
                pytest.fail('No data found for', event) 
