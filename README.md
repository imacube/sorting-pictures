# sorting-pictures
Sort digital pictures into a hierarchical directory structure. 

# sort.py
This script copies files from the source directory to the destination directory. Skipped
files have:
- Unknown file suffix.
- Two files going to the same location with different hashes.
- Unable to parse the datetime stamp from the filename.

By default this copies files, but use the `--move` option to move files.

## Exif and Google JSON Date Options
The `--exif` and `--google-json` options cannot be used together.

Files downloaded from Google Takeout have exif datetime stamps for when it was pulled from Google, not when it was created.
The `--google-json` option looks for JSON files parses those to get the datetime stamp for the file.

The `--exif` option parses out the datetime stamp from the image files exif data.

## Examples
```shell script
source venv/bin/activate

# Single source and destination, copy only
./sort.py sample-images destination-images

# Multiple sources ending with the destination, copy only
./sort.py sample-images sample-images-2 samle-images-3 destination-images

# Same but with move activated
./sort.py --move sample-images destination-images
./sort.py --move sample-images sample-images-2 samle-images-3 destination-images

# Use exif
./sort.py --exif sample-images destination-images

# Use Google JSON File
./sort.py --google-json sample-images destination-images
```

# resize.py
This script is just used to help prepare image files for testing.