# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- Log of files not copied or moved.
- `--collisions` argument to print move collisions.

### Changed
- Refactored into a class.
- Moved all Namespace builds into a fixture.

### Fixed
- `move_file` now checks if source exists, destination exists and if so that the destination is an actual file
  before calling `diff_files`.

## [0.6.0] - 2020-02-10
### Added
- CLI `--help` and related arguments.
- `--move` option. Default is copy, but this CLI option activates copy instead.

### Fixed
- Added missing docstrings.

## [0.5.1] - 2020-02-10
### Fixed
- Source and destination paths in `main` need to be `Path` objects.

## [0.5.0] - 2020-02-10
### Added
- Logic to handle multiple source directories at one time.

## [0.4.0] - 2020-02-10
### Fixed
- If not enough arguments are passed, print help message *and exit*.

## [0.3.0] - 2020-02-09
### Added
- Method to hash two files and return boolean if same/differ.
- `main` method for calls from the CLI.

### Changed
- If a destination file exists and the hash of the source and destination files differ then skip it. If the
  hash is the same, then proceed (currently copy is called, but later it will be move so this will eliminate
  the source file). 

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
