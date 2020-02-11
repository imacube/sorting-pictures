"""Tests for sort.py."""
import shutil
from argparse import Namespace
from datetime import datetime
from pathlib import PosixPath
from unittest.mock import patch, call, MagicMock

import pytest

from sort import SortingPictures


@pytest.fixture
def sorting_pictures():
    return SortingPictures()


class TestParseArguments:
    def test_basic(self, sorting_pictures):
        parser = sorting_pictures.parse_arguments()
        args = parser.parse_args('src dest'.split())
        assert args == Namespace(move=False, paths=['src', 'dest'])

    def test_move(self, sorting_pictures):
        parser = sorting_pictures.parse_arguments()
        args = parser.parse_args('--move src dest'.split())
        assert args == Namespace(move=True, paths=['src', 'dest'])

    def test_many_sources(self, sorting_pictures):
        parser = sorting_pictures.parse_arguments()
        args = parser.parse_args('src0 src1 src2 src3 dest'.split())
        assert args == Namespace(move=False, paths=['src0', 'src1', 'src2', 'src3', 'dest'])


class TestGetDateFromFile:
    def test_image_basic(self, sorting_pictures):
        actual = sorting_pictures.get_date_from_filename('IMG_20171022_124203.jpg')

        expected = datetime(year=2017, month=10, day=22, hour=12, minute=42, second=3)

        assert actual == expected

    def test_image_duplicate(self, sorting_pictures):
        actual = sorting_pictures.get_date_from_filename('IMG_20171104_104157_01.jpg')

        expected = datetime(year=2017, month=11, day=4, hour=10, minute=41, second=57)

        assert actual == expected

    def test_screenshot(self, sorting_pictures):
        actual = sorting_pictures.get_date_from_filename('Screenshot_20171007-143321.png')

        expected = datetime(year=2017, month=10, day=7, hour=14, minute=33, second=21)

        assert actual == expected

    def test_video(self, sorting_pictures):
        actual = sorting_pictures.get_date_from_filename('VID_20180724_173611.mp4')

        expected = datetime(year=2018, month=7, day=24, hour=17, minute=36, second=11)

        assert actual == expected

    def test_failure(self, sorting_pictures):
        actual = sorting_pictures.get_date_from_filename('metadata.jpg')

        assert actual is None


class TestIsFile:
    def test_file(self, sorting_pictures):
        assert sorting_pictures.is_file('sample-images/metadata.jpg')

    def test_symlink(self, sorting_pictures):
        assert not sorting_pictures.is_file('sample-images/no-m')
        assert not sorting_pictures.is_file('sample-images/VID')

    def test_dir(self, sorting_pictures):
        assert not sorting_pictures.is_file('sample-images')

    def test_other(self, sorting_pictures):
        assert not sorting_pictures.is_file('/dev/null')


class TestSearchDirectory:
    def test_dir(self, sorting_pictures):
        result = sorting_pictures.search_directory('sample-images')

        assert result == [PosixPath('sample-images/metadata-copy.jpg'), PosixPath('sample-images/VID'),
                          PosixPath('sample-images/no-m'), PosixPath('sample-images/no-metadata.jpg'),
                          PosixPath('sample-images/metadata.jpg'), PosixPath('sample-images/no-metadata'),
                          PosixPath('sample-images/no-metadata/IMG_20171104_104157_01.jpg'),
                          PosixPath('sample-images/no-metadata/IMG_20171022_124203.jpg'),
                          PosixPath('sample-images/no-metadata/Screenshot_20171007-143321.png'),
                          PosixPath('sample-images/no-metadata/IMG_20171104_104157.jpg'),
                          PosixPath('sample-images/no-metadata/VID_20180724_173611.mp4')]


class TestDiffFiles:
    def test_same_hash(self, sorting_pictures):
        assert sorting_pictures.diff_files('sample-images/metadata.jpg', 'sample-images/metadata-copy.jpg') is True

    def test_different_hash(self, sorting_pictures):
        assert sorting_pictures.diff_files('sample-images/metadata.jpg', 'sample-images/no-metadata.jpg') is False


class TestMoveFile:
    def test_copy_file(self, sorting_pictures, tmp_path):
        src = tmp_path / 'src'
        src.mkdir(parents=True, exist_ok=True)
        src_file = src / 'metadata.jpg'
        shutil.copy2('sample-images/metadata.jpg', src_file)

        dest_file = tmp_path / 'dest' / 'metadata-dest.jpg'

        assert not dest_file.exists()
        assert sorting_pictures.move_file(src_file, dest_file) is True
        assert dest_file.exists()

    def test_move_file(self, sorting_pictures, tmp_path):
        src = tmp_path / 'src'
        src.mkdir(parents=True, exist_ok=True)
        src_file = src / 'metadata.jpg'
        shutil.copy2('sample-images/metadata.jpg', src_file)

        dest_file = tmp_path / 'dest' / 'metadata-dest.jpg'

        assert src_file.exists()
        assert not dest_file.exists()
        assert sorting_pictures.move_file(src_file, dest_file, move=True) is True
        assert not src_file.exists()
        assert dest_file.exists()

    def test_file_exists_same_hash(self, sorting_pictures, tmp_path):
        src = tmp_path / 'src'
        src.mkdir(parents=True, exist_ok=True)
        src_file = src / 'metadata.jpg'
        shutil.copy2('sample-images/metadata.jpg', src_file)

        dest_file = tmp_path / 'dest' / 'metadata-dest.jpg'

        assert not dest_file.exists()
        sorting_pictures.move_file(src_file, dest_file)
        assert dest_file.exists()

        assert sorting_pictures.move_file(src_file, dest_file) is True

    def test_file_exists_different_hash(self, sorting_pictures, tmp_path):
        src = tmp_path / 'src'
        src.mkdir(parents=True, exist_ok=True)
        src_file = src / 'metadata.jpg'
        shutil.copy2('sample-images/metadata.jpg', src_file)

        dest_file = tmp_path / 'dest' / 'metadata-dest.jpg'

        assert not dest_file.exists()
        sorting_pictures.move_file(src_file, dest_file)
        assert dest_file.exists()

        src_file = src / 'no-metadata.jpg'
        shutil.copy2('sample-images/no-metadata.jpg', src_file)

        assert sorting_pictures.move_file(src_file, dest_file) is False


class TestSortImages:
    def test_successful_run_copy(self, sorting_pictures, tmp_path):
        src = tmp_path / 'src'
        dest = tmp_path / 'dest'

        if src.exists():
            shutil.rmtree(src)
        if dest.exists():
            shutil.rmtree(dest)

        shutil.copytree('sample-images', src, symlinks=True)

        sorting_pictures.sort_images(src, dest)

        result = sorting_pictures.search_directory(dest)
        result = [p.relative_to(tmp_path) for p in result]

        assert result == [PosixPath('dest/2018-07'), PosixPath('dest/2017-11'), PosixPath('dest/2017-10'),
                          PosixPath('dest/2018-07/VID_20180724_173611.mp4'),
                          PosixPath('dest/2017-11/IMG_20171104_104157.jpg'),
                          PosixPath('dest/2017-10/IMG_20171007_143321.png'),
                          PosixPath('dest/2017-10/IMG_20171022_124203.jpg')]

    def test_successful_run_move(self, sorting_pictures, tmp_path):
        src = tmp_path / 'src'
        dest = tmp_path / 'dest'

        if src.exists():
            shutil.rmtree(src)
        if dest.exists():
            shutil.rmtree(dest)

        shutil.copytree('sample-images', src, symlinks=True)

        sorting_pictures.sort_images(src, dest, move=True)

        result = sorting_pictures.search_directory(dest)
        result = [p.relative_to(tmp_path) for p in result]

        assert result == [PosixPath('dest/2018-07'), PosixPath('dest/2017-11'), PosixPath('dest/2017-10'),
                          PosixPath('dest/2018-07/VID_20180724_173611.mp4'),
                          PosixPath('dest/2017-11/IMG_20171104_104157.jpg'),
                          PosixPath('dest/2017-10/IMG_20171007_143321.png'),
                          PosixPath('dest/2017-10/IMG_20171022_124203.jpg')]

        result = sorting_pictures.search_directory(src)
        result = [p.relative_to(tmp_path) for p in result]
        assert result == [PosixPath('src/metadata-copy.jpg'), PosixPath('src/VID'), PosixPath('src/no-m'),
                          PosixPath('src/no-metadata.jpg'), PosixPath('src/metadata.jpg'), PosixPath('src/no-metadata')]

    def test_unknown_suffix(self, sorting_pictures, tmp_path):
        src = tmp_path / 'src'
        dest = tmp_path / 'dest'

        if src.exists():
            shutil.rmtree(src)
        if dest.exists():
            shutil.rmtree(dest)

        src.mkdir(parents=True, exist_ok=True)

        bad_suffix = src / 'IMG_20170102_030405.UNKNOWN_FOOBAR'
        bad_suffix.touch()

        sorting_pictures.sort_images(src, dest)
        result = sorting_pictures.search_directory(dest)

        assert result == list()


class TestMain:
    @patch('sort.SortingPictures.sort_images')
    @patch('sort.SortingPictures.parse_arguments')
    def test_basic(self, mock_parser, mock_sort_images, sorting_pictures):
        mock_parser.return_value.parse_args.return_value = Namespace(move=False, paths='src dest'.split())
        sorting_pictures.main()

        mock_sort_images.assert_called_with(PosixPath('src'), PosixPath('dest'), move=False)

    @patch('sort.SortingPictures.sort_images')
    @patch('sort.SortingPictures.parse_arguments')
    def test_basic_move(self, mock_parser, mock_sort_images, sorting_pictures):
        mock_parser.return_value.parse_args.return_value = Namespace(move=True, paths='src dest'.split())
        sorting_pictures.main()

        mock_sort_images.assert_called_with(PosixPath('src'), PosixPath('dest'), move=True)

    @patch('sort.SortingPictures.sort_images')
    @patch('sort.SortingPictures.parse_arguments')
    def test_multi_src(self, mock_parser, mock_sort_images, sorting_pictures):
        mock_parser.return_value.parse_args.return_value = Namespace(move=False, paths='src0 src1 src2 dest'.split())
        sorting_pictures.main()

        assert mock_sort_images.call_args_list == [call(PosixPath('src0'), PosixPath('dest'), move=False),
                                                   call(PosixPath('src1'), PosixPath('dest'), move=False),
                                                   call(PosixPath('src2'), PosixPath('dest'), move=False)]

    @patch('sort.SortingPictures.sort_images')
    @patch('sort.SortingPictures.parse_arguments')
    def test_multi_src_move(self, mock_parser, mock_sort_images, sorting_pictures):
        mock_parser.return_value.parse_args.return_value = Namespace(move=True, paths='src0 src1 src2 dest'.split())
        sorting_pictures.main()

        assert mock_sort_images.call_args_list == [call(PosixPath('src0'), PosixPath('dest'), move=True),
                                                   call(PosixPath('src1'), PosixPath('dest'), move=True),
                                                   call(PosixPath('src2'), PosixPath('dest'), move=True)]

    @patch('sys.exit')
    @patch('sort.SortingPictures.parse_arguments')
    def test_bad_order(self, mock_parser, mock_exit, sorting_pictures):
        mock_parser.return_value.parse_args.return_value = Namespace(move=False,
                                                                     paths='src0 src1 src2 dest --move'.split())
        sorting_pictures.main()
        mock_exit.assert_called_once_with(1)

        mock_parser.return_value.parse_args.return_value = Namespace(move=False,
                                                                     paths='src0 src1 --move src2 dest'.split())
        mock_exit.reset_mock()
        sorting_pictures.main()
        mock_exit.assert_called_once_with(1)

    @patch('sys.exit')
    @patch('sort.SortingPictures.sort_images')
    @patch('sort.SortingPictures.parse_arguments')
    def test_too_few_args(self, mock_parser, mock_sort_images, mock_exit, sorting_pictures):
        mock_parser.return_value.parse_args.return_value = Namespace(move=False, paths='src'.split())
        sorting_pictures.main()

        mock_sort_images.assert_not_called()
        mock_exit.assert_called_once_with(1)
