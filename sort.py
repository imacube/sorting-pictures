"""Sort photos from the source directory into the destination directory."""
from datetime import datetime


def get_date_from_filename(filename):
    """Derive the images timestamp from the filename.

    :param filename: Filename of the image file.
    :return: datetime object
    """

    f = filename.split('.')[0]
    f = f.replace('-', '_')
    f = f.split('_')[1:3]
    f = ''.join(f)

    try:
        return datetime.strptime(f, '%Y%m%d%H%M%S')
    except ValueError:
        return None
