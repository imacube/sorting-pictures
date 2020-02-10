# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2020-02-09
### Added
- `move_file` to carry out the copying of the image file. Currently this does not move, only copies.
- `sort_images` glue logic for running through a source directory of files and copying the known images
  to the new location.

## [0.1.0] 2020-02-07
### Added
- `search_directory` returns a list of the contents in a directory.
- `is_file` to return True or False if something is a file. 
- `get_date_from_filename` for getting a `datetime.datetime` object from a filename.
- Initial test images.
- Script `resize.py` to help with prepping test images.
