# sorting-pictures
Sort digital pictures into a hierarchical directory structure. 

# sort.py
This script copies files from the source directory to the destination directory. Skipped
files have:
- Unknown file suffix.
- Two files going to the same location with different hashes.
- Unable to parse the datetime stamp from the filename.

By default this copies files, but use the `--move` option to move files. 

```shell script
source venv/bin/activate
./sort.py sample-images destination-images
# or multiple sources ending with the destination
./sort.py sample-images sample-images-2 samle-images-3 destination-images
# to move
./sort.py --move sample-images destination-images
./sort.py --move sample-images sample-images-2 samle-images-3 destination-images
```

# resize.py
This script is just used to help prepare image files for testing.