"""Sort photos from the source directory into the destination directory."""
import argparse
import hashlib
import shutil
import sys
from datetime import datetime
from pathlib import Path


class SortingPictures:
    def __init__(self):
        self.log = dict()
        for key in 'parse_date suffix collisions'.split():
            self.log[key] = list()

    @staticmethod
    def parse_arguments():
        """Parse command line arguments."""

        parser = argparse.ArgumentParser(
            description="""Sort image files based on filename timestamp into year-month folders.""")
        parser.add_argument('--move', action='store_true', required=False, default=False,
                            help="Move files instead of copying them (default action is to copy).")
        parser.add_argument('--collisions', action='store_true', required=False, default=False,
                            help='Print out source and destination files with collisions.')
        parser.add_argument('paths', nargs=argparse.REMAINDER, help='source source source ... destination')

        return parser

    @staticmethod
    def get_date_from_filename(filename):
        """Derive the images timestamp from the filename.

        :param filename: Filename of the image file.
        :return: datetime.datetime
        """

        f = filename.split('.')[0]
        f = f.replace('-', '_')
        f = f.split('_')[1:3]
        f = ''.join(f)

        try:
            return datetime.strptime(f, '%Y%m%d%H%M%S')
        except ValueError:
            return None

    @staticmethod
    def search_directory(sp):
        """Return the contents of a directory.

        :param sp: Path to search.
        :return: list of directory contents.
        """

        return [x for x in Path(sp).rglob('*')]

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

    def move_file(self, src_file, dest_file, move=False):
        """Move a file from the src to the dest.

        :param src_file: Source path.
        :param dest_file: Destination path.
        :param move: True to move files, False to copy them.
        :return: None
        """

        src = Path(src_file)
        dest = Path(dest_file)

        dest.parent.mkdir(parents=True, exist_ok=True)

        if not src.is_file():
            return False
        if dest.exists() and (
                not self.is_file(dest) or
                not self.diff_files(src, dest)
        ):
            return False

        if move:
            shutil.move(src, dest)
        else:
            shutil.copy2(src, dest)

        return True

    def sort_images(self, src_path, dest_path, move=False):
        """Sort files from the source path into the destination path.

        :param src_path: Path to read the files from.
        :param dest_path: Path to write files to.
        :param move: True to move files, False to copy them.
        :return:
        """

        for src in self.search_directory(src_path):
            if not self.is_file(src):
                continue
            d = self.get_date_from_filename(src.name)
            if d is None:
                self.log['parse_date'].append(src)
                continue

            if src.suffix.lower() in ['.jpg', '.png']:
                prefix = 'IMG_'
            elif src.suffix.lower() in ['.mp4']:
                prefix = 'VID_'
            else:
                self.log['suffix'].append(src)
                continue

            dest = dest_path / d.strftime('%Y-%m') / (prefix + d.strftime('%Y%m%d_%H%M%S') + src.suffix)

            if not self.move_file(src, dest, move):
                self.log['collisions'].append((src, dest))

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

        dest_path = Path(args.paths[-1])

        for src_path in [Path(p) for p in args.paths[:-1]]:
            self.sort_images(src_path, dest_path, move=args.move)

        if args.collisions:
            for f in self.log['collisions']:
                print(f)


if __name__ == '__main__':
    sorting_pictures = SortingPictures()
    sorting_pictures.main()
