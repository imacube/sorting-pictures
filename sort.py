#!/usr/bin/env python3

"""Sort photos from the source directory into the destination directory."""
import argparse
import hashlib
import json
import re
import shutil
import sys
from datetime import datetime
from PIL import Image
from PIL import UnidentifiedImageError
from pathlib import Path

from tqdm import tqdm


class SortingPictures:
    date_replace = re.compile(r'[-~]')
    date_pattern = re.compile(r'(\d{8}_\d{6})')

    def __init__(self):
        self.log = dict()
        for key in 'parse suffix collisions exif google_json_date processed'.split():
            self.log[key] = list()

        self.ignore = set('.DS_Store .thumbnails'.split())

    @staticmethod
    def parse_arguments():
        """Parse command line arguments."""

        parser = argparse.ArgumentParser(
            description="""Sort image files based on filename timestamp into year-month folders.
            Do not use --exif and --google-json together!""")
        parser.add_argument('--move', action='store_true', required=False, default=False,
                            help="Move files instead of copying them (default action is to copy).")
        parser.add_argument('--collisions', action='store_true', required=False, default=False,
                            help='Print out source and destination files with collisions.')
        parser.add_argument('--suffix', action='store_true', required=False, default=False,
                            help='Print out source files with unknown suffixes (extension).')
        parser.add_argument('--parse', action='store_true', required=False, default=False,
                            help='Print out source files with filenames that could not be parsed.')
        parser.add_argument('--exif', action='store_true', required=False, default=False,
                            help='Look for EXIF datetime stamps in files. DO NOT USE WITH --google-json!')
        parser.add_argument('--google-json', action='store_true', required=False, default=False,
                            help='Use Google JSON files that contain information on individual image files to get datetime stamp. DO NOT USE WITH --exif!')
        parser.add_argument('--dryrun', action='store_true', required=False, default=False,
                            help='Do not actually copy or move files.')
        parser.add_argument('paths', nargs=argparse.REMAINDER, help='source source source ... destination')

        return parser

    @classmethod
    def get_google_json_date(cls, filename):
        """Extract the image creation date from Google Photos JSON file.

        :param filename: Filename of the JSON file to load.
        :return: datetime.datetime
        """
        json_filename = filename.parent / Path(filename.name + '.json')

        if not json_filename.is_file():
            return None

        with open(json_filename) as in_file:
            try:
                data = json.load(in_file)
            except UnicodeDecodeError:
                return None

            if data['title'] != json_filename.name[:-5]:
                return None

            return datetime.fromtimestamp(int(data['photoTakenTime']['timestamp']))

    @classmethod
    def get_date_from_exif(cls, filename):
        """Get the timestamp from the file's exif data.

        :param filename: Filename of the image file.
        :return: datetime.datetime
        """
        try:
            exif = Image.open(filename).getexif()
        except UnidentifiedImageError:
            return None
        timestamp = exif.get(306)
        if timestamp is None:
            return None
        try:
            return datetime.strptime(timestamp, '%Y:%m:%d %H:%M:%S')
        except ValueError:
            raise
    
    @classmethod
    def get_date_from_xmp(cls, filename):
        """Get the timestamp from the file's exif xmp data.

        :param filename: Filename of the image file.
        :return: datetime.datetime
        """
        try:
            with Image.open(filename) as img:
                if not hasattr(img, 'applist'):
                    return None
                for segment, content in img.applist:
                    if b'\x00' not in content:
                        continue
                    marker, body = content.split(b'\x00', 1)
                    if segment == 'APP1' and marker == b'http://ns.adobe.com/xap/1.0/':
                        body = body.decode('utf-8')
                        pattern = re.compile('exif:DateTimeOriginal="(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+\d{2}:\d{2})')
                        timestamp = pattern.search(body)
                        if timestamp is None:
                            continue
                        timestamp = timestamp.group(1)
                        return datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S%z')
        except UnidentifiedImageError:
            pass
        return None

    @classmethod
    def get_date_from_filename(cls, filename):
        """Derive the images timestamp from the filename.

        :param filename: Filename of the image file.
        :return: datetime.datetime
        """
        f = cls.date_replace.sub('_', str(filename))
        match = cls.date_pattern.search(f)
        if match is None:
            return None

        try:
            return datetime.strptime(match.group(0), '%Y%m%d_%H%M%S')
        except ValueError:
            return None

    def search_directory(self, sp):
        """Return the contents of a directory.

        :param sp: Path to search.
        :return: list of directory contents.
        """

        return [x for x in Path(sp).rglob('*') if not set(x.parts) & self.ignore]

    @staticmethod
    def is_file(file_path):
        """Check if the path is a file or something else.

        :param file_path: Path to check.
        :return: True if it is a file, False otherwise.
        """

        p = Path(file_path)

        if p.is_symlink():
            return False
        elif p.is_file():
            return True
        elif p.is_dir():
            return False
        else:
            return False

    def diff_files(self, src_file, dest_file):
        """Hash two files and see if they are the same or not.

        :param src_file: Source file.
        :param dest_file: Destination file.
        :return: True if hash matches, False if different.
        """

        src_hash, dest_hash = hashlib.sha512(), hashlib.sha512()

        with open(src_file, 'rb') as file_in:
            for block in iter(lambda: file_in.read(4096), b''):
                src_hash.update(block)

        with open(dest_file, 'rb') as file_in:
            for block in iter(lambda: file_in.read(4096), b''):
                dest_hash.update(block)

        return src_hash.hexdigest() == dest_hash.hexdigest()

    def move_file(self, src_file, dest_file, move=False, dryrun=False):
        """Move or copy a file from the src to the dest.

        :param src_file: Source path.
        :param dest_file: Destination path.
        :param move: True to move files, False to copy them.
        :param dryrun: If True then files will not be copied or moved.
        :return: None
        """

        src = Path(src_file)
        dest = Path(dest_file)

        if not self.is_file(src):
            return False
        if dest.exists():
            if not self.is_file(dest):
                return False
            elif not dryrun:
                index = 1
                stem = dest.stem
                suffix = dest.suffix
                while dest.exists() and not self.diff_files(src, dest):
                    dest = dest.parent / ('%s-%d%s' % (stem, index, suffix))
                    index += 1

        if dryrun:
            self.log['processed'].append(src) 
            return True

        dest.parent.mkdir(parents=True, exist_ok=True)
        if move:
            shutil.move(src, dest)
        else:
            shutil.copy2(src, dest)

        return True

    def sort_images(self, src_path, dest_path, move=False, exif=False, google_json_date=False, dryrun=False):
        """Sort files from the source path into the destination path.

        :param src_path: Path to read the files from.
        :param dest_path: Path to write files to.
        :param move: True to move files, False to copy them.
        :param exif: True to look for exif data to get datetime stamp.
        :param google_json_date: True to look for Google JSON files with image data.
        :param dryrun: If True then copy or move will be skipped.
        :return:
        """

        def process_file(file_timestamp):
            dest = dest_path / file_timestamp.strftime('%Y-%m') / (
                        prefix + file_timestamp.strftime('%Y%m%d_%H%M%S') + src.suffix)

            if not self.move_file(src, dest, move, dryrun):
                self.log['collisions'].append((src, dest))

        for src in tqdm(self.search_directory(src_path)):
            if src.is_dir():
                continue

            if src.suffix.lower() in {'.dng', '.jpg', '.jpeg', '.gif', '.png', '.nef', '.xmp'}:
                prefix = 'IMG_'
            elif src.suffix.lower() in {'.mp4', '.mov'}:
                prefix = 'VID_'
            else:
                self.log['suffix'].append(src)
                continue

            d = self.get_date_from_filename(src.name)
            if d is not None:
                process_file(d)
                continue
            else:
                self.log['parse'].append(src)

            if exif:
                d = self.get_date_from_exif(src)
                if d is None:
                    d = self.get_date_from_xmp(src)
                if d is not None:
                    process_file(d)
                    continue
                else:
                    self.log['exif'].append(src)

            if google_json_date:
                d = self.get_google_json_date(src)
                if d is not None:
                    process_file(d)
                    continue
                else:
                    self.log['google_json_date'].append(src)

    def main(self):
        """Main method to be called by CLI.

        :return:
        """

        parser = self.parse_arguments()
        args = parser.parse_args()
        if len(args.paths) < 2:
            parser.print_help()
            sys.exit(1)

        for key in self.log:
            if '--%s' % str(key) in args.paths:
                print('--%s must come before source and destination paths.' % str(key))
                sys.exit(1)

        if args.exif and args.google_json:
            parser.print_help()
            sys.exit(1)

        dest_path = Path(args.paths[-1])

        for src_path in [Path(p) for p in args.paths[:-1]]:
            self.sort_images(src_path, dest_path, move=args.move, exif=args.exif, google_json_date=args.google_json,
                             dryrun=args.dryrun)

        if args.dryrun:
            print('processed', len(self.log['processed']))

        if args.collisions:
            for s, d in self.log['collisions']:
                print('collisions', s, d)
        if args.exif:
            for s in self.log['exif']:
                print('exif', s)
        if args.suffix:
            for s in self.log['suffix']:
                print('suffix', s)
        if args.parse:
            for s in self.log['parse']:
                print('parse', s)
        if args.google_json:
            for s in self.log['google_json_date']:
                print('google_json_date', s)


if __name__ == '__main__':
    sorting_pictures = SortingPictures()
    sorting_pictures.main()
