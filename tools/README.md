# Articles

The article pages (`strength-training-basics.html` and the others), `articles.html`,
the "Read online" lists on `training.html` and `nutrition.html`, and `sitemap.xml`
are generated from the Markdown files in `content/articles/`.

To change or add an article:

1. Edit or add a `.md` file in `content/articles/` (copy an existing one for the header format).
2. For a new article, add its slug to `ORDER` in `tools/build_articles.py`.
3. Run `pip install markdown` once, then `python3 tools/build_articles.py` from the repository root.
4. Commit the `.md` file and the regenerated `.html` files together.

Don't edit the generated `.html` article files by hand: the next build overwrites them.
