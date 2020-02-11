"""Sort photos from the source directory into the destination directory."""
import hashlib
import shutil
import sys
from datetime import datetime
from pathlib import Path


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


def search_directory(sp):
    """Return the contents of a directory.

    :param sp: Path to search.
    :return: list of directory contents.
    """

    return [x for x in Path(sp).rglob('*')]


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


def diff_files(src_file, dest_file):
    """Hash two files and see if they are the same or not.

    :param src_file:
    :param dest_file:
    :return:
    """
    # return run_hash(path_to_file, hashlib.sha512()).hexdigest()

    src_hash, dest_hash = hashlib.sha512(), hashlib.sha512()

    with open(src_file, 'rb') as file_in:
        for block in iter(lambda: file_in.read(4096), b''):
            src_hash.update(block)

    with open(dest_file, 'rb') as file_in:
        for block in iter(lambda: file_in.read(4096), b''):
            dest_hash.update(block)

    return src_hash.hexdigest() == dest_hash.hexdigest()


def move_file(src_file, dest_file):
    """Move a file from the src to the dest.

    :param src_file: source path
    :param dest_file: destination path
    :return: None
    """

    src = Path(src_file)
    dest = Path(dest_file)

    dest.parent.mkdir(parents=True, exist_ok=True)

    if is_file(dest) and not diff_files(src, dest):
        return False

    shutil.copy2(src, dest)

    return True


def sort_images(src_path, dest_path):
    """Sort files from the source path into the destination path.

    :param src_path: Path to read the files from.
    :param dest_path: Path to write files to.
    :return:
    """

    for src in search_directory(src_path):
        if not is_file(src):
            continue
        d = get_date_from_filename(src.name)
        if d is None:
            continue

        if src.suffix.lower() in ['.jpg', '.png']:
            prefix = 'IMG_'
        elif src.suffix.lower() in ['.mp4']:
            prefix = 'VID_'
        else:
            continue

        dest = dest_path / d.strftime('%Y-%m') / (prefix + d.strftime('%Y%m%d_%H%M%S') + src.suffix)

        move_file(src, dest)


def main():
    """Main method for this, typically called by

    :return:
    """

    if len(sys.argv) < 3:
        print('''Expecting two arguments:\nsource_directory destination_directory''')
        sys.exit(1)

    src_path, dest_path = [Path(p) for p in sys.argv[1:3]]

    sort_images(src_path, dest_path)


if __name__ == '__main__':
    main()
