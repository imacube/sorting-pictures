"""Helper script for preparing images that are used in this repo for testing."""

from PIL import Image

im = Image.open('sample-images/metadata.jpg')
im.resize((1, 1))
im.save('sample-images/metadata.new.jpg', 'JPEG')

img = Image.new('RGB', [1, 1], 1)
img.save('sample-images/no-metadata.jpg', 'JPEG')
