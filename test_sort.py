"""Tests for sort.py."""
import shutil
from argparse import Namespace
from datetime import datetime
from pathlib import PosixPath, Path
from unittest.mock import patch, call

import pytest

from sort import SortingPictures


@pytest.fixture
def sorting_pictures():
    return SortingPictures()


@pytest.fixture
def namespace():
    return Namespace(move=False, collisions=False, suffix=False, parse=False,
                     exif=False, google_json=False,
                     dry_run=False, paths='src dest'.split())


class TestParseArguments:
    def test_basic(self, sorting_pictures, namespace):
        parser = sorting_pictures.parse_arguments()
        args = parser.parse_args('src dest'.split())
        assert args == namespace

    def test_move(self, sorting_pictures, namespace):
        parser = sorting_pictures.parse_arguments()
        args = parser.parse_args('--move src dest'.split())
        namespace.move = True
        assert args == namespace

    def test_many_sources(self, sorting_pictures, namespace):
        parser = sorting_pictures.parse_arguments()
        args = parser.parse_args('src0 src1 src2 src3 dest'.split())
        namespace.paths = 'src0 src1 src2 src3 dest'.split()
        assert args == Namespace(move=False, collisions=False, suffix=False, parse=False, exif=False, google_json=False,
                                 dry_run=False, paths=['src0', 'src1', 'src2', 'src3', 'dest'])

    def test_collisions(self, sorting_pictures, namespace):
        parser = sorting_pictures.parse_arguments()
        args = parser.parse_args('--collisions src dest'.split())
        namespace.collisions = True
        assert args == namespace

    def test_suffix(self, sorting_pictures, namespace):
        parser = sorting_pictures.parse_arguments()
        args = parser.parse_args('--suffix src dest'.split())
        namespace.suffix = True
        assert args == namespace

    def test_exif(self, sorting_pictures, namespace):
        parser = sorting_pictures.parse_arguments()
        args = parser.parse_args('--exif src dest'.split())
        namespace.exif = True
        assert args == namespace

    def test_google_json(self, sorting_pictures, namespace):
        parser = sorting_pictures.parse_arguments()
        args = parser.parse_args('--google-json src dest'.split())
        namespace.google_json = True
        assert args == namespace

    def test_dry_run(self, sorting_pictures, namespace):
        parser = sorting_pictures.parse_arguments()
        args = parser.parse_args('--dry-run src dest'.split())
        namespace.dry_run = True
        assert args == namespace

        parser = sorting_pictures.parse_arguments()
        args = parser.parse_args('--dry-run src dest'.split())
        namespace.dry_run = True
        assert args == namespace


class TestGetGoogleJsonDate:
    def test_good_file(self, sorting_pictures):
        actual = sorting_pictures.get_google_json_date(Path('sample-images/a6a5e930cac831ef4e00255c51872867.jpg'))

        expected = datetime(year=2021, month=3, day=17, hour=11, minute=42, second=42)

        assert actual == expected

    def test_bad_file(self, sorting_pictures):
        actual = sorting_pictures.get_google_json_date(Path('sample-images/not_image_name.jpg'))
        assert actual is None


class TestGetDateFromFile:
    def test_get_datetime(self, sorting_pictures):
        actual = sorting_pictures.get_date_from_filename(Path('IMG_20171022_124203.jpg'))

        expected = datetime(year=2017, month=10, day=22, hour=12, minute=42, second=3)

        assert actual == expected

    def test_image_duplicate(self, sorting_pictures):
        actual = sorting_pictures.get_date_from_filename(Path('IMG_20171104_104157_01.jpg'))

        expected = datetime(year=2017, month=11, day=4, hour=10, minute=41, second=57)

        assert actual == expected

    def test_screenshot(self, sorting_pictures):
        actual = sorting_pictures.get_date_from_filename(Path('Screenshot_20171007-143321.png'))

        expected = datetime(year=2017, month=10, day=7, hour=14, minute=33, second=21)

        assert actual == expected

    def test_video(self, sorting_pictures):
        actual = sorting_pictures.get_date_from_filename(Path('VID_20180724_173611.mp4'))

        expected = datetime(year=2018, month=7, day=24, hour=17, minute=36, second=11)

        assert actual == expected

    def test_failure(self, sorting_pictures):
        actual = sorting_pictures.get_date_from_filename(Path('metadata.jpg'))

        assert actual is None

    def test_image_tilde(self, sorting_pictures):
        actual = sorting_pictures.get_date_from_filename(Path('IMG_20171022_124203~2.jpg'))

        expected = datetime(year=2017, month=10, day=22, hour=12, minute=42, second=3)

        assert actual == expected

    def test_image_metadata(self, sorting_pictures):
        actual = sorting_pictures.get_date_from_exif(Path('sample-images/metadata.jpg'))

        expected = datetime(year=2022, month=2, day=27, hour=12, minute=9, second=35)

        assert actual == expected


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

        assert sorted(result) == sorted(
            [
                PosixPath('sample-images/IMG_20171022_010203_01.jpg'),
                PosixPath('sample-images/IMG_20171022_124203.unknown_suffix'),
                PosixPath('sample-images/IMG_NO_PARSE.jpg'),
                PosixPath('sample-images/VID'),
                PosixPath('sample-images/a6a5e930cac831ef4e00255c51872867.jpg.json'),
                PosixPath('sample-images/metadata-copy.jpg'),
                PosixPath('sample-images/metadata.jpg'),
                PosixPath('sample-images/no-m'),
                PosixPath('sample-images/no-metadata'),
                PosixPath('sample-images/no-metadata/20170112_110943-ANIMATION.gif'),
                PosixPath('sample-images/no-metadata/20171022_010203.jpg'),
                PosixPath('sample-images/no-metadata/IMG_20171022_124203.jpg'),
                PosixPath('sample-images/no-metadata/IMG_20171022_124203_01.jpg'),
                PosixPath('sample-images/no-metadata/IMG_20171104_104157.jpg'),
                PosixPath('sample-images/no-metadata/IMG_20171104_104157_01.jpg'),
                PosixPath('sample-images/no-metadata/IMG_20171104_104158~.jpg'),
                PosixPath('sample-images/no-metadata/IMG_20181001_124203.gif'),
                PosixPath('sample-images/no-metadata/IMG~20171104~104159~.jpg'),
                PosixPath('sample-images/no-metadata/Screenshot_20171007-143321.png'),
                PosixPath('sample-images/no-metadata/VID_20180724_173611.mp4'),
                PosixPath('sample-images/no-metadata.jpg'),
                PosixPath('sample-images/not_image_name.jpg.json'),
            ]
        )


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
        dest = tmp_path / 'dest'

        if src.exists():
            shutil.rmtree(src)
        if dest.exists():
            shutil.rmtree(dest)

        src.mkdir(parents=True, exist_ok=True)
        src_file = src / 'metadata.jpg'
        dest_file = dest / 'metadata-dest.jpg'

        shutil.copy2('sample-images/metadata.jpg', src_file)

        assert not dest_file.exists()
        sorting_pictures.move_file(src_file, dest_file)
        assert dest_file.exists()

        shutil.copy2('sample-images/no-metadata.jpg', src_file)
        assert sorting_pictures.move_file(src_file, dest_file) is True
        assert (dest_file.parent / ('%s-%d%s' % (dest_file.stem, 1, dest_file.suffix))).exists()
        assert sorting_pictures.move_file(src_file, dest_file) is True

        shutil.copy2('sample-images/no-metadata/IMG_20171022_124203_01.jpg', src_file)
        assert sorting_pictures.move_file(src_file, dest_file) is True
        assert (dest_file.parent / ('%s-%d%s' % (dest_file.stem, 2, dest_file.suffix))).exists()
        assert sorting_pictures.move_file(src_file, dest_file) is True

    def test_src_file_is_dir(self, sorting_pictures, tmp_path):
        src = tmp_path / 'src'
        src.mkdir(parents=True, exist_ok=True)
        src_file = src / 'metadata.jpg'
        src_file.mkdir()

        dest_file = tmp_path / 'dest' / 'metadata-dest.jpg'

        assert src_file.is_dir()
        assert not dest_file.exists()
        sorting_pictures.move_file(src_file, dest_file)
        assert not dest_file.exists()

    def test_dest_file_is_dir(self, sorting_pictures, tmp_path):
        src = tmp_path / 'src'
        src.mkdir(parents=True, exist_ok=True)
        src_file = src / 'metadata.jpg'
        shutil.copy2('sample-images/metadata.jpg', src_file)

        dest = tmp_path / 'dest'
        dest.mkdir(parents=True, exist_ok=True)

        assert dest.is_dir()
        assert not sorting_pictures.move_file(src_file, dest)

    def test_src_file_is_symlink(self, sorting_pictures, tmp_path):
        src = tmp_path / 'src'
        src.mkdir(parents=True, exist_ok=True)
        src_file = src / 'metadata.jpg'
        shutil.copy2('sample-images/metadata.jpg', src_file)
        src_file = src / 'metadata-symlink.jpg'
        src_file.symlink_to(src / 'metadata.jpg')

        dest_file = tmp_path / 'dest' / 'metadata-dest.jpg'

        assert src_file.is_symlink()
        assert not dest_file.exists()
        sorting_pictures.move_file(src_file, dest_file)
        assert not dest_file.exists()

    def test_dest_file_is_symlink(self, sorting_pictures, tmp_path):
        src = tmp_path / 'src'
        src.mkdir(parents=True, exist_ok=True)
        src_file = src / 'metadata.jpg'
        shutil.copy2('sample-images/metadata.jpg', src_file)

        dest = tmp_path / 'dest'
        dest.mkdir(parents=True, exist_ok=True)
        dest = dest / 'metadata-dest.jpg'
        shutil.copy2('sample-images/metadata.jpg', dest)
        dest_symlink = tmp_path / 'dest' / 'metadata-symlink.jpg'
        dest_symlink.symlink_to(dest)

        assert dest.is_file()
        assert dest_symlink.is_symlink()
        assert not sorting_pictures.move_file(src_file, dest_symlink)


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

        assert sorted(result) == sorted([PosixPath('dest/2017-01'),
                                         PosixPath('dest/2017-01/IMG_20170112_110943.gif'),
                                         PosixPath('dest/2017-10'),
                                         PosixPath('dest/2017-10/IMG_20171007_143321.png'),
                                         PosixPath('dest/2017-10/IMG_20171022_010203.jpg'),
                                         PosixPath('dest/2017-10/IMG_20171022_124203-1.jpg'),
                                         PosixPath('dest/2017-10/IMG_20171022_124203.jpg'),
                                         PosixPath('dest/2017-11'),
                                         PosixPath('dest/2017-11/IMG_20171104_104157.jpg'),
                                         PosixPath('dest/2017-11/IMG_20171104_104158.jpg'),
                                         PosixPath('dest/2017-11/IMG_20171104_104159.jpg'),
                                         PosixPath('dest/2018-07'),
                                         PosixPath('dest/2018-07/VID_20180724_173611.mp4'),
                                         PosixPath('dest/2018-10'),
                                         PosixPath('dest/2018-10/IMG_20181001_124203.gif')])

        log = sorting_pictures.log
        log['parse'] = [p.relative_to(tmp_path) for p in log['parse']]
        log['suffix'] = [p.relative_to(tmp_path) for p in log['suffix']]
        log['collisions'] = [(p_s.relative_to(tmp_path), p_d.relative_to(tmp_path)) for (p_s, p_d) in log['collisions']]
        log['exif'] = [p.relative_to(tmp_path) for p in log['exif']]
        log['google_json_date'] = [p.relative_to(tmp_path) for p in log['google_json_date']]

        expected = {'collisions': [(PosixPath('src/IMG_20171022_010203_01.jpg'),
                                    PosixPath('dest/2017-10/IMG_20171022_010203.jpg'))],
                    'exif': [],
                    'google_json_date': [],
                    'parse': [PosixPath('src/metadata-copy.jpg'),
                              PosixPath('src/IMG_NO_PARSE.jpg'),
                              PosixPath('src/no-metadata.jpg'),
                              PosixPath('src/metadata.jpg'), ],
                    'suffix': [PosixPath('src/VID'),
                               PosixPath('src/IMG_20171022_124203.unknown_suffix'),
                               PosixPath('src/a6a5e930cac831ef4e00255c51872867.jpg.json'),
                               PosixPath('src/not_image_name.jpg.json'),
                               ]}
        log = {k: sorted(v) for k, v in log.items()}
        expected = {k: sorted(v) for k, v in expected.items()}

        assert log == expected

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

        assert sorted(result) == sorted([PosixPath('dest/2017-01'),
                                         PosixPath('dest/2017-01/IMG_20170112_110943.gif'),
                                         PosixPath('dest/2017-10'),
                                         PosixPath('dest/2017-10/IMG_20171007_143321.png'),
                                         PosixPath('dest/2017-10/IMG_20171022_010203.jpg'),
                                         PosixPath('dest/2017-10/IMG_20171022_124203-1.jpg'),
                                         PosixPath('dest/2017-10/IMG_20171022_124203.jpg'),
                                         PosixPath('dest/2017-11'),
                                         PosixPath('dest/2017-11/IMG_20171104_104157.jpg'),
                                         PosixPath('dest/2017-11/IMG_20171104_104158.jpg'),
                                         PosixPath('dest/2017-11/IMG_20171104_104159.jpg'),
                                         PosixPath('dest/2018-07'),
                                         PosixPath('dest/2018-07/VID_20180724_173611.mp4'),
                                         PosixPath('dest/2018-10'),
                                         PosixPath('dest/2018-10/IMG_20181001_124203.gif')])

        result = sorting_pictures.search_directory(src)
        result = [p.relative_to(tmp_path) for p in result]
        assert sorted(result) == sorted([PosixPath('src/metadata-copy.jpg'),
                                         PosixPath('src/IMG_20171022_010203_01.jpg'),
                                         PosixPath('src/VID'),
                                         PosixPath('src/IMG_20171022_124203.unknown_suffix'),
                                         PosixPath('src/IMG_NO_PARSE.jpg'),
                                         PosixPath('src/no-m'),
                                         PosixPath('src/no-metadata.jpg'),
                                         PosixPath('src/metadata.jpg'),
                                         PosixPath('src/no-metadata'),
                                         PosixPath('src/a6a5e930cac831ef4e00255c51872867.jpg.json'),
                                         PosixPath('src/not_image_name.jpg.json'),
                                         ])

        log = sorting_pictures.log
        log['parse'] = [p.relative_to(tmp_path) for p in log['parse']]
        log['suffix'] = [p.relative_to(tmp_path) for p in log['suffix']]
        log['collisions'] = [(p_s.relative_to(tmp_path), p_d.relative_to(tmp_path)) for (p_s, p_d) in log['collisions']]
        log['exif'] = [p.relative_to(tmp_path) for p in log['exif']]
        log['google_json_date'] = [p.relative_to(tmp_path) for p in log['google_json_date']]
        expected = {'collisions': [(PosixPath('src/IMG_20171022_010203_01.jpg'),
                                    PosixPath('dest/2017-10/IMG_20171022_010203.jpg'))],
                    'exif': [],
                    'google_json_date': [],
                    'parse': [PosixPath('src/metadata-copy.jpg'),
                              PosixPath('src/IMG_NO_PARSE.jpg'),
                              PosixPath('src/no-metadata.jpg'),
                              PosixPath('src/metadata.jpg'), ],
                    'suffix': [PosixPath('src/VID'),
                               PosixPath('src/IMG_20171022_124203.unknown_suffix'),
                               PosixPath('src/a6a5e930cac831ef4e00255c51872867.jpg.json'),
                               PosixPath('src/not_image_name.jpg.json'),
                               ]}

        log = {k: sorted(v) for k, v in log.items()}
        expected = {k: sorted(v) for k, v in expected.items()}
        assert log == expected

    def test_successful_run_exif(self, sorting_pictures, tmp_path):
        src = tmp_path / 'src'
        dest = tmp_path / 'dest'

        if src.exists():
            shutil.rmtree(src)
        if dest.exists():
            shutil.rmtree(dest)

        shutil.copytree('sample-images', src, symlinks=True)

        sorting_pictures.sort_images(src, dest, move=True, exif=True)

        result = sorting_pictures.search_directory(dest)
        result = [p.relative_to(tmp_path) for p in result]

        assert sorted(result) == sorted(
            [
                PosixPath('dest/2017-01'),
                PosixPath('dest/2017-01/IMG_20170112_110943.gif'),
                PosixPath('dest/2017-10'),
                PosixPath('dest/2017-10/IMG_20171007_143321.png'),
                PosixPath('dest/2017-10/IMG_20171022_010203.jpg'),
                PosixPath('dest/2017-10/IMG_20171022_124203-1.jpg'),
                PosixPath('dest/2017-10/IMG_20171022_124203.jpg'),
                PosixPath('dest/2017-11'),
                PosixPath('dest/2017-11/IMG_20171104_104157.jpg'),
                PosixPath('dest/2017-11/IMG_20171104_104158.jpg'),
                PosixPath('dest/2017-11/IMG_20171104_104159.jpg'),
                PosixPath('dest/2018-07'),
                PosixPath('dest/2018-07/VID_20180724_173611.mp4'),
                PosixPath('dest/2018-10'),
                PosixPath('dest/2018-10/IMG_20181001_124203.gif'),
                PosixPath('dest/2022-02'),
                PosixPath('dest/2022-02/IMG_20220227_120935.jpg'),
            ]
        )

        result = sorting_pictures.search_directory(src)
        result = [p.relative_to(tmp_path) for p in result]
        assert sorted(result) == sorted(
            [
                PosixPath('src/IMG_20171022_010203_01.jpg'),
                PosixPath('src/VID'),
                PosixPath('src/IMG_20171022_124203.unknown_suffix'),
                PosixPath('src/IMG_NO_PARSE.jpg'),
                PosixPath('src/no-m'),
                PosixPath('src/no-metadata.jpg'),
                PosixPath('src/no-metadata'),
                PosixPath('src/a6a5e930cac831ef4e00255c51872867.jpg.json'),
                PosixPath('src/not_image_name.jpg.json'),
            ])

        log = sorting_pictures.log
        log['parse'] = [p.relative_to(tmp_path) for p in log['parse']]
        log['suffix'] = [p.relative_to(tmp_path) for p in log['suffix']]
        log['collisions'] = [(p_s.relative_to(tmp_path), p_d.relative_to(tmp_path)) for (p_s, p_d) in log['collisions']]
        log['exif'] = [p.relative_to(tmp_path) for p in log['exif']]
        log['google_json_date'] = [p.relative_to(tmp_path) for p in log['google_json_date']]
        expected = {'collisions': [(PosixPath('src/IMG_20171022_010203_01.jpg'),
                                    PosixPath('dest/2017-10/IMG_20171022_010203.jpg'))],
                    'exif': [PosixPath('src/IMG_NO_PARSE.jpg'),
                             PosixPath('src/no-metadata.jpg')],
                    'google_json_date': [],
                    'parse': [PosixPath('src/metadata-copy.jpg'),
                              PosixPath('src/IMG_NO_PARSE.jpg'),
                              PosixPath('src/no-metadata.jpg'),
                              PosixPath('src/metadata.jpg'), ],
                    'suffix': [PosixPath('src/VID'),
                               PosixPath('src/IMG_20171022_124203.unknown_suffix'),
                               PosixPath('src/a6a5e930cac831ef4e00255c51872867.jpg.json'),
                               PosixPath('src/not_image_name.jpg.json'),
                               ]}

        log = {k: sorted(v) for k, v in log.items()}
        expected = {k: sorted(v) for k, v in expected.items()}
        assert log == expected

    def test_successful_run_google_json_date(self, sorting_pictures, tmp_path):
        src = tmp_path / 'src'
        dest = tmp_path / 'dest'

        if src.exists():
            shutil.rmtree(src)
        if dest.exists():
            shutil.rmtree(dest)

        shutil.copytree('sample-images', src, symlinks=True)

        sorting_pictures.sort_images(src, dest, move=True, google_json_date=True)

        result = sorting_pictures.search_directory(dest)
        result = [p.relative_to(tmp_path) for p in result]

        assert sorted(result) == sorted(
            [
                PosixPath('dest/2017-01'),
                PosixPath('dest/2017-01/IMG_20170112_110943.gif'),
                PosixPath('dest/2017-10'),
                PosixPath('dest/2017-10/IMG_20171007_143321.png'),
                PosixPath('dest/2017-10/IMG_20171022_010203.jpg'),
                PosixPath('dest/2017-10/IMG_20171022_124203-1.jpg'),
                PosixPath('dest/2017-10/IMG_20171022_124203.jpg'),
                PosixPath('dest/2017-11'),
                PosixPath('dest/2017-11/IMG_20171104_104157.jpg'),
                PosixPath('dest/2017-11/IMG_20171104_104158.jpg'),
                PosixPath('dest/2017-11/IMG_20171104_104159.jpg'),
                PosixPath('dest/2018-07'),
                PosixPath('dest/2018-07/VID_20180724_173611.mp4'),
                PosixPath('dest/2018-10'),
                PosixPath('dest/2018-10/IMG_20181001_124203.gif'),
            ]
        )

        result = sorting_pictures.search_directory(src)
        result = [p.relative_to(tmp_path) for p in result]
        assert sorted(result) == sorted(
            [
                PosixPath('src/IMG_20171022_010203_01.jpg'),
                PosixPath('src/VID'),
                PosixPath('src/IMG_20171022_124203.unknown_suffix'),
                PosixPath('src/IMG_NO_PARSE.jpg'),
                PosixPath('src/no-m'),
                PosixPath('src/no-metadata.jpg'),
                PosixPath('src/no-metadata'),
                PosixPath('src/a6a5e930cac831ef4e00255c51872867.jpg.json'),
                PosixPath('src/metadata-copy.jpg'),
                PosixPath('src/metadata.jpg'),
                PosixPath('src/not_image_name.jpg.json'),
            ])

        log = sorting_pictures.log
        log['parse'] = [p.relative_to(tmp_path) for p in log['parse']]
        log['suffix'] = [p.relative_to(tmp_path) for p in log['suffix']]
        log['collisions'] = [(p_s.relative_to(tmp_path), p_d.relative_to(tmp_path)) for (p_s, p_d) in log['collisions']]
        log['exif'] = [p.relative_to(tmp_path) for p in log['exif']]
        log['google_json_date'] = [p.relative_to(tmp_path) for p in log['google_json_date']]
        expected = {'collisions': [(PosixPath('src/IMG_20171022_010203_01.jpg'),
                                    PosixPath('dest/2017-10/IMG_20171022_010203.jpg'))],
                    'exif': [],
                    'google_json_date': [PosixPath('src/IMG_NO_PARSE.jpg'),
                                         PosixPath('src/metadata-copy.jpg'),
                                         PosixPath('src/metadata.jpg'),
                                         PosixPath('src/no-metadata.jpg')],
                    'parse': [PosixPath('src/metadata-copy.jpg'),
                              PosixPath('src/IMG_NO_PARSE.jpg'),
                              PosixPath('src/no-metadata.jpg'),
                              PosixPath('src/metadata.jpg'), ],
                    'suffix': [PosixPath('src/VID'),
                               PosixPath('src/IMG_20171022_124203.unknown_suffix'),
                               PosixPath('src/a6a5e930cac831ef4e00255c51872867.jpg.json'),
                               PosixPath('src/not_image_name.jpg.json'),
                               ]}

        log = {k: sorted(v) for k, v in log.items()}
        expected = {k: sorted(v) for k, v in expected.items()}
        assert log == expected

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

        log = sorting_pictures.log
        log['suffix'] = [p.relative_to(tmp_path) for p in log['suffix']]
        assert log == {
            'parse': [],
            'exif': [],
            'google_json_date': [],
            'suffix': [PosixPath('src/IMG_20170102_030405.UNKNOWN_FOOBAR')],
            'collisions': []}

    def test_run_copy_dry_run(self, sorting_pictures, tmp_path):
        src = tmp_path / 'src'
        dest = tmp_path / 'dest'

        if src.exists():
            shutil.rmtree(src)
        if dest.exists():
            shutil.rmtree(dest)

        shutil.copytree('sample-images', src, symlinks=True)

        sorting_pictures.sort_images(src, dest, dry_run=True)

        result = sorting_pictures.search_directory(dest)
        result = [p.relative_to(tmp_path) for p in result]

        assert result == []

        log = sorting_pictures.log
        log['parse'] = [p.relative_to(tmp_path) for p in log['parse']]
        log['suffix'] = [p.relative_to(tmp_path) for p in log['suffix']]
        log['collisions'] = [(p_s.relative_to(tmp_path), p_d.relative_to(tmp_path)) for (p_s, p_d) in log['collisions']]
        log['exif'] = [p.relative_to(tmp_path) for p in log['exif']]
        log['google_json_date'] = [p.relative_to(tmp_path) for p in log['google_json_date']]

        expected = {'collisions': [(PosixPath('src/IMG_20171022_010203_01.jpg'),
                                    PosixPath('dest/2017-10/IMG_20171022_010203.jpg'))],
                    'exif': [],
                    'google_json_date': [],
                    'parse': [PosixPath('src/metadata-copy.jpg'),
                              PosixPath('src/IMG_NO_PARSE.jpg'),
                              PosixPath('src/no-metadata.jpg'),
                              PosixPath('src/metadata.jpg'), ],
                    'suffix': [PosixPath('src/VID'),
                               PosixPath('src/IMG_20171022_124203.unknown_suffix'),
                               PosixPath('src/a6a5e930cac831ef4e00255c51872867.jpg.json'),
                               PosixPath('src/not_image_name.jpg.json'),
                               ]}

        log = {k: sorted(v) for k, v in log.items()}
        expected = {k: sorted(v) for k, v in expected.items()}

        assert log == expected

    def test_run_move_dry_run(self, sorting_pictures, tmp_path):
        src = tmp_path / 'src'
        dest = tmp_path / 'dest'

        if src.exists():
            shutil.rmtree(src)
        if dest.exists():
            shutil.rmtree(dest)

        shutil.copytree('sample-images', src, symlinks=True)

        sorting_pictures.sort_images(src, dest, move=True, dry_run=True)

        result = sorting_pictures.search_directory(dest)
        result = [p.relative_to(tmp_path) for p in result]

        assert result == []

        log = sorting_pictures.log
        log['parse'] = [p.relative_to(tmp_path) for p in log['parse']]
        log['suffix'] = [p.relative_to(tmp_path) for p in log['suffix']]
        log['collisions'] = [(p_s.relative_to(tmp_path), p_d.relative_to(tmp_path)) for (p_s, p_d) in log['collisions']]
        log['exif'] = [p.relative_to(tmp_path) for p in log['exif']]
        log['google_json_date'] = [p.relative_to(tmp_path) for p in log['google_json_date']]

        expected = {'collisions': [(PosixPath('src/IMG_20171022_010203_01.jpg'),
                                    PosixPath('dest/2017-10/IMG_20171022_010203.jpg'))],
                    'exif': [],
                    'google_json_date': [],
                    'parse': [PosixPath('src/metadata-copy.jpg'),
                              PosixPath('src/IMG_NO_PARSE.jpg'),
                              PosixPath('src/no-metadata.jpg'),
                              PosixPath('src/metadata.jpg'), ],
                    'suffix': [PosixPath('src/VID'),
                               PosixPath('src/IMG_20171022_124203.unknown_suffix'),
                               PosixPath('src/a6a5e930cac831ef4e00255c51872867.jpg.json'),
                               PosixPath('src/not_image_name.jpg.json'),
                               ]}

        log = {k: sorted(v) for k, v in log.items()}
        expected = {k: sorted(v) for k, v in expected.items()}

        assert log == expected


class TestMain:
    @patch('sort.SortingPictures.sort_images')
    @patch('sort.SortingPictures.parse_arguments')
    def test_basic(self, mock_parser, mock_sort_images, sorting_pictures, namespace):
        mock_parser.return_value.parse_args.return_value = namespace
        sorting_pictures.main()

        mock_sort_images.assert_called_with(PosixPath('src'), PosixPath('dest'), move=False,
                                            exif=False, google_json_date=False, dry_run=False)

    @patch('sort.SortingPictures.sort_images')
    @patch('sort.SortingPictures.parse_arguments')
    def test_basic_exif_true(self, mock_parser, mock_sort_images, sorting_pictures, namespace):
        namespace.exif = True
        mock_parser.return_value.parse_args.return_value = namespace
        sorting_pictures.main()

        mock_sort_images.assert_called_with(PosixPath('src'), PosixPath('dest'), move=False,
                                            exif=True, google_json_date=False, dry_run=False)

    @patch('sort.SortingPictures.sort_images')
    @patch('sort.SortingPictures.parse_arguments')
    def test_basic_google_json_true(self, mock_parser, mock_sort_images, sorting_pictures, namespace):
        namespace.google_json = True
        mock_parser.return_value.parse_args.return_value = namespace
        sorting_pictures.main()

        mock_sort_images.assert_called_with(PosixPath('src'), PosixPath('dest'), move=False,
                                            exif=False, google_json_date=True, dry_run=False)

    @patch('sys.exit')
    @patch('sort.SortingPictures.parse_arguments')
    def test_basic_exif_and_google_json_date(self, mock_parser, mock_exit, sorting_pictures, namespace):
        namespace.exif = True
        namespace.google_json = True
        mock_parser.return_value.parse_args.return_value = namespace
        sorting_pictures.main()
        mock_exit.assert_called_once_with(1)

    @patch('sort.SortingPictures.sort_images')
    @patch('sort.SortingPictures.parse_arguments')
    def test_basic_dry_run(self, mock_parser, mock_sort_images, sorting_pictures, namespace):
        namespace.dry_run = True
        mock_parser.return_value.parse_args.return_value = namespace
        sorting_pictures.main()

        mock_sort_images.assert_called_with(PosixPath('src'), PosixPath('dest'), move=False,
                                            exif=False, google_json_date=False, dry_run=True)

    @patch('sort.SortingPictures.sort_images')
    @patch('sort.SortingPictures.parse_arguments')
    def test_basic_move(self, mock_parser, mock_sort_images, sorting_pictures, namespace):
        namespace.move = True
        mock_parser.return_value.parse_args.return_value = namespace
        sorting_pictures.main()

        mock_sort_images.assert_called_with(PosixPath('src'), PosixPath('dest'), move=True,
                                            exif=False, google_json_date=False, dry_run=False)

    @patch('sort.SortingPictures.sort_images')
    @patch('sort.SortingPictures.parse_arguments')
    def test_multi_src(self, mock_parser, mock_sort_images, sorting_pictures, namespace):
        namespace.paths = 'src0 src1 src2 dest'.split()
        mock_parser.return_value.parse_args.return_value = namespace
        sorting_pictures.main()

        assert mock_sort_images.call_args_list == [
            call(PosixPath('src0'), PosixPath('dest'), move=False, exif=False, google_json_date=False, dry_run=False),
            call(PosixPath('src1'), PosixPath('dest'), move=False, exif=False, google_json_date=False, dry_run=False),
            call(PosixPath('src2'), PosixPath('dest'), move=False, exif=False, google_json_date=False, dry_run=False)]

    @patch('sort.SortingPictures.sort_images')
    @patch('sort.SortingPictures.parse_arguments')
    def test_multi_src_move(self, mock_parser, mock_sort_images, sorting_pictures, namespace):
        namespace.move = True
        namespace.paths = 'src0 src1 src2 dest'.split()
        mock_parser.return_value.parse_args.return_value = namespace
        sorting_pictures.main()

        assert mock_sort_images.call_args_list == [
            call(PosixPath('src0'), PosixPath('dest'), move=True, exif=False, google_json_date=False, dry_run=False),
            call(PosixPath('src1'), PosixPath('dest'), move=True, exif=False, google_json_date=False, dry_run=False),
            call(PosixPath('src2'), PosixPath('dest'), move=True, exif=False, google_json_date=False, dry_run=False),
        ]

    @patch('sys.exit')
    @patch('sort.SortingPictures.parse_arguments')
    def test_bad_order(self, mock_parser, mock_exit, sorting_pictures, namespace):
        namespace.paths = 'src0 src1 src2 dest --collisions'.split()
        mock_parser.return_value.parse_args.return_value = namespace
        sorting_pictures.main()
        mock_exit.assert_called_once_with(1)

        mock_exit.reset_mock()

        namespace.paths = 'src0 src1 --collisions src2 dest'.split()
        mock_parser.return_value.parse_args.return_value = namespace
        sorting_pictures.main()
        mock_exit.assert_called_once_with(1)

    @patch('sys.exit')
    @patch('sort.SortingPictures.sort_images')
    @patch('sort.SortingPictures.parse_arguments')
    def test_too_few_args(self, mock_parser, mock_sort_images, mock_exit, sorting_pictures, namespace):
        namespace.paths = 'src'.split()
        mock_parser.return_value.parse_args.return_value = namespace
        sorting_pictures.main()

        mock_sort_images.assert_not_called()
        mock_exit.assert_called_once_with(1)

    @patch('builtins.print')
    @patch('sort.SortingPictures.sort_images')
    @patch('sort.SortingPictures.parse_arguments')
    def test_collisions_true(self, mock_parser, mock_sorting_pictures, mock_print, sorting_pictures, namespace):
        namespace.collisions = True
        mock_parser.return_value.parse_args.return_value = namespace
        sorting_pictures.log['collisions'] = [('a', 'b')]
        sorting_pictures.log['suffix'] = ['a.UNKNOWN']
        sorting_pictures.log['parse'] = ['metadata.jpg']
        sorting_pictures.main()

        assert mock_print.mock_calls == [call('collisions', 'a', 'b')]

    @patch('builtins.print')
    @patch('sort.SortingPictures.sort_images')
    @patch('sort.SortingPictures.parse_arguments')
    def test_suffix_true(self, mock_parser, mock_sorting_pictures, mock_print, sorting_pictures, namespace):
        namespace.suffix = True
        mock_parser.return_value.parse_args.return_value = namespace
        sorting_pictures.log['collisions'] = [('a', 'b')]
        sorting_pictures.log['suffix'] = ['a.UNKNOWN']
        sorting_pictures.log['parse'] = ['metadata.jpg']
        sorting_pictures.main()

        assert mock_print.mock_calls == [call('suffix', 'a.UNKNOWN')]

    @patch('builtins.print')
    @patch('sort.SortingPictures.sort_images')
    @patch('sort.SortingPictures.parse_arguments')
    def test_parse_true(self, mock_parser, mock_sorting_pictures, mock_print, sorting_pictures, namespace):
        namespace.parse = True
        mock_parser.return_value.parse_args.return_value = namespace
        sorting_pictures.log['collisions'] = [('a', 'b')]
        sorting_pictures.log['suffix'] = ['a.UNKNOWN']
        sorting_pictures.log['parse'] = ['metadata.jpg']
        sorting_pictures.main()

        assert mock_print.mock_calls == [call('parse', 'metadata.jpg')]

    @patch('builtins.print')
    @patch('sort.SortingPictures.sort_images')
    @patch('sort.SortingPictures.parse_arguments')
    def test_all_output_options(self, mock_parser, mock_sorting_pictures, mock_print, sorting_pictures, namespace):
        namespace.collisions = True
        namespace.suffix = True
        namespace.parse = True
        mock_parser.return_value.parse_args.return_value = namespace
        sorting_pictures.log['collisions'] = [('a', 'b')]
        sorting_pictures.log['suffix'] = ['a.UNKNOWN']
        sorting_pictures.log['parse'] = ['metadata.jpg']
        sorting_pictures.main()

        assert mock_print.mock_calls == [call('collisions', 'a', 'b'),
                                         call('suffix', 'a.UNKNOWN'),
                                         call('parse', 'metadata.jpg')]
