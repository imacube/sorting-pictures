"""Sort photos from the source directory into the destination directory."""
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
