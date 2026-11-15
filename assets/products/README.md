# Product photos (optional)

Each product in `assets/catalogs.js` can have its own picture. It's optional: a product without one
still shows, with the retailer's picture (`"image"`) or, if there is none, a quiet placeholder icon.

## How to add one

1. Put the file in this folder, named after the product: lowercase, words joined by hyphens,
   for example `bowflex-adjustable-dumbbell-set.webp`.
2. In `assets/catalogs.js`, add a `"photo"` line to that product (in every country that lists it):

   ```
   "photo": "assets/products/bowflex-adjustable-dumbbell-set.webp",
   ```

   `"photo"` wins over `"image"`. No rebuild is needed for `catalogs.js`, but bump `VERSION` in
   `tools/build_site.py` and rebuild so browsers fetch the new file list.

## Format

- **Shape:** square (1:1). The picture is shown in a fixed square box and is never cropped or stretched
  (it's fitted inside), so a non-square picture just gets empty space around it.
- **Size:** 640 × 640 px, WebP or JPG, under 60 KB.
- **Look:** the product on a plain white or very light background, filling most of the frame.
- **Rights:** only pictures you took yourself or are allowed to use. For Amazon products, follow the
  Associates rules for product images.

Pictures load lazily (only when scrolled near), and a broken or missing file falls back to the placeholder.
