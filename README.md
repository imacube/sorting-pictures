# sorting-pictures
Sort digital pictures into a hierarchical directory structure. 

# sort.py
This script copies files from the source directory to the destination directory. Skipped files are:
- Unknown file suffix.
- Two files going to the same location with different hashes.

```shell script
source venv/bin/activate
./sort.py sample-images destination-images
# or multiple sources ending with the destination
./sort.py sample-images sample-images-2 samle-images-3 destination-images
```

# resize.py
This script is just used to help prepare image files for testing.