"""Tests for sort.py."""
from datetime import datetime

from sort import get_date_from_filename


class TestGetDateFromFile:
    def test_image_basic(self):
        actual = get_date_from_filename('IMG_20171022_124203.jpg')

        expected = datetime(year=2017, month=10, day=22, hour=12, minute=42, second=3)

        assert actual == expected

    def test_image_duplicate(self):
        actual = get_date_from_filename('IMG_20171104_104157_01.jpg')

        expected = datetime(year=2017, month=11, day=4, hour=10, minute=41, second=57)

        assert actual == expected

    def test_screenshot(self):
        actual = get_date_from_filename('Screenshot_20171007-143321.png')

        expected = datetime(year=2017, month=10, day=7, hour=14, minute=33, second=21)

        assert actual == expected

    def test_video(self):
        actual = get_date_from_filename('VID_20180724_173611.mp4')

        expected = datetime(year=2018, month=7, day=24, hour=17, minute=36, second=11)

        assert actual == expected

    def test_failure(self):
        actual = get_date_from_filename('metadata.jpg')

        assert actual is None
