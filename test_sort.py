"""Tests for sort.py."""
import shutil
from datetime import datetime
from pathlib import PosixPath

from sort import get_date_from_filename, search_directory, is_file, move_file, sort_images, diff_files


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


class TestIsFile:
    def test_file(self):
        file_path = 'sample-images/metadata.jpg'
        assert is_file(file_path)

    def test_symlink(self):
        assert not is_file('sample-images/no-m')
        assert not is_file('sample-images/VID')

    def test_dir(self):
        assert not is_file('sample-images')

    def test_other(self):
        assert not is_file('/dev/null')


class TestSearchDirectory:
    def test_dir(self):
        result = search_directory('sample-images')

        assert result == [PosixPath('sample-images/metadata-copy.jpg'), PosixPath('sample-images/VID'),
                          PosixPath('sample-images/no-m'), PosixPath('sample-images/no-metadata.jpg'),
                          PosixPath('sample-images/metadata.jpg'), PosixPath('sample-images/no-metadata'),
                          PosixPath('sample-images/no-metadata/IMG_20171104_104157_01.jpg'),
                          PosixPath('sample-images/no-metadata/IMG_20171022_124203.jpg'),
                          PosixPath('sample-images/no-metadata/Screenshot_20171007-143321.png'),
                          PosixPath('sample-images/no-metadata/IMG_20171104_104157.jpg'),
                          PosixPath('sample-images/no-metadata/VID_20180724_173611.mp4')]


class TestDiffFiles:
    def test_same_hash(self):
        assert diff_files('sample-images/metadata.jpg', 'sample-images/metadata-copy.jpg') is True

    def test_different_hash(self):
        assert diff_files('sample-images/metadata.jpg', 'sample-images/no-metadata.jpg') is False


class TestMoveFile:
    def test_move_file(self, tmp_path):
        src = tmp_path / 'src'
        src.mkdir(parents=True, exist_ok=True)
        src_file = src / 'metadata.jpg'
        shutil.copy2('sample-images/metadata.jpg', src_file)

        dest_file = tmp_path / 'dest' / 'metadata-dest.jpg'

        assert not dest_file.exists()
        assert move_file(src_file, dest_file) is True
        assert dest_file.exists()

    def test_file_exists_same_hash(self, tmp_path):
        src = tmp_path / 'src'
        src.mkdir(parents=True, exist_ok=True)
        src_file = src / 'metadata.jpg'
        shutil.copy2('sample-images/metadata.jpg', src_file)

        dest_file = tmp_path / 'dest' / 'metadata-dest.jpg'

        assert not dest_file.exists()
        move_file(src_file, dest_file)
        assert dest_file.exists()

        assert move_file(src_file, dest_file) is True

    def test_file_exists_different_hash(self, tmp_path):
        src = tmp_path / 'src'
        src.mkdir(parents=True, exist_ok=True)
        src_file = src / 'metadata.jpg'
        shutil.copy2('sample-images/metadata.jpg', src_file)

        dest_file = tmp_path / 'dest' / 'metadata-dest.jpg'

        assert not dest_file.exists()
        move_file(src_file, dest_file)
        assert dest_file.exists()

        src_file = src / 'no-metadata.jpg'
        shutil.copy2('sample-images/no-metadata.jpg', src_file)

        assert move_file(src_file, dest_file) is False


class TestSortImages:
    def test_successful_run(self, tmp_path):
        src = tmp_path / 'src'
        dest = tmp_path / 'dest'

        if src.exists():
            shutil.rmtree(src)
        if dest.exists():
            shutil.rmtree(dest)

        shutil.copytree('sample-images', src, symlinks=True)

        sort_images(src, dest)

        result = search_directory(dest)
        result = [p.relative_to(tmp_path) for p in result]

        assert result == [PosixPath('dest/2018-07'), PosixPath('dest/2017-11'), PosixPath('dest/2017-10'),
                          PosixPath('dest/2018-07/VID_20180724_173611.mp4'),
                          PosixPath('dest/2017-11/IMG_20171104_104157.jpg'),
                          PosixPath('dest/2017-10/IMG_20171007_143321.png'),
                          PosixPath('dest/2017-10/IMG_20171022_124203.jpg')]

    def test_unknown_suffix(self, tmp_path):
        src = tmp_path / 'src'
        dest = tmp_path / 'dest'

        if src.exists():
            shutil.rmtree(src)
        if dest.exists():
            shutil.rmtree(dest)

        src.mkdir(parents=True, exist_ok=True)

        bad_suffix = src / 'IMG_20170102_030405.UNKNOWN_FOOBAR'
        bad_suffix.touch()

        sort_images(src, dest)
        result = search_directory(dest)

        assert result == list()
