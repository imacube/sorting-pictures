# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.13.0]
### Changed
- If `ffprobe` excit code is non-zero just skip the file

### Fixed
- Catch `datetime.fromisoformat()` calls
  - Print the filename and timestamp
  - Continue on to the next possible entry to try

## [0.12.0]
### Added
- Added support for video files that have their creation date stored in the
- Added output of total files that would have been processed
- Added alternate xmp parsing to seek alternate exif timestamp
- Added `.dng`, `.nef`, `.xmp` file extensions
- Print files that exif couldn't be parssed out of when using `--exif`
- Print `--google-json` argument prints out files it coulnd't process

### Changed
- Altered processed list to have a src -> dest type output
- Refactored code
  - Replaced single quotes with double quotes for surrounding strings
  - Long single line method calls replaced with multiline equivelant

### Fixed
- Issues with `--google-json` option
- Added check for exepcted binary field in xmp data

### Added
- exif metadata parsing.
- Google JSON files with image metadata from Google Takeout can now be parsed.
- `README.md` examples for the new `--exif` and `--google-json` options.

### Changed
- By default the script will run, no `--run` required.
- `README.md` examples.

### Fixed
- Handle UnidentifiedImageError exceptions when using `--exif` option

## [0.11.0] - 2020-05-31
### Changed
- `--dryrun` replaced with `--run`. The script now defaults to a dry run mode and requires the `--run` argument to
  actually take action on files.

## [0.10.0] - 2020-05-31
### Added
- Test for `--collisions`, `--suffix`, and `--parase` used at the same time.
- Added `--dryrun`.
- Added `.gif' suffix.
- List of file and directory names to ignore.
- Added suffix `.mov`.

### Changed
- `sort_images` first checks if the source image is a directory and skips it if true.
- Suffix checked before the filename is parsed for a datetime stamp.
- Change datetime stamp parsing to be more robust.

### Fixed
- Collisions not being populated.
- Tests.

## [0.9.0] - 2020-02-13
### Added
- `--suffix` argument to print out unknown suffixes.
- `--parse` argument to print out filenames that could not be parsed.

### Fixed
- Tests for `move_file` if the source is a directory or symlink.
- Tests for `--collisions` and `--move` in `TestParserArguments`.

## [0.8.0] - 2020-02-12
### Added
- Added progress bar.

## [0.7.0] - 2020-02-12
### Added
- Log of files not copied or moved.
- `--collisions` argument to print move collisions.
- Collisions that have a different hash will have an index number appended to
  the name before the suffix in the format `-%d`. For example: `IMG_20200212_090807-1.jpg`.
- Added tilde (`~`) to replacement list in image filenames.

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
