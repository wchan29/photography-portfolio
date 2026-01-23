# Photo Processor

A fast, parallel photo processing tool for creating optimized thumbnails for your portfolio gallery.

## Features

- **Fast parallel processing** - Process multiple images simultaneously
- **Smart caching** - Only reprocess images that have changed
- **Progress tracking** - Real-time progress bars
- **Automatic thumbnail creation** - Creates `.min.jpg` versions for faster page loads
- **Optional watermarking** - Add copyright text to images
- **Optimized output** - Progressive JPEG with optimized compression

## Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

## Basic Usage

```bash
# Process all images in a folder (creates .min.jpg thumbnails)
python photo_processor.py assets/2024/Arizona_USA

# Process with custom quality and width
python photo_processor.py assets/Street --quality 90 --min-width 1600

# Use 8 parallel workers for faster processing
python photo_processor.py assets/2024 --workers 8

# Force reprocess all images (even if thumbnails already exist)
python photo_processor.py assets/2024 --force
```

## Advanced Options

```bash
# Add watermark to images
python photo_processor.py assets/2024 --watermark --watermark-text "© Anson Chan 2024"

# Process only current directory (not subdirectories)
python photo_processor.py assets/Street --no-recursive

# Custom font and size for watermark
python photo_processor.py assets/2024 --watermark \
  --watermark-text "© 2024" \
  --font-path "./assets/font/CustomFont.ttf" \
  --fontsize 60
```

## Options Reference

| Option | Default | Description |
|--------|---------|-------------|
| `--min-width` | 1200 | Width of thumbnail in pixels |
| `--quality` | 85 | JPEG quality (1-100) |
| `--workers` | 4 | Number of parallel workers |
| `--force` | False | Reprocess all images |
| `--no-recursive` | False | Don't process subdirectories |
| `--watermark` | False | Add watermark to images |
| `--watermark-text` | "" | Watermark text |
| `--font-path` | ./assets/font/Arial.ttf | Path to font file |
| `--fontsize` | 48 | Font size for watermark |

## Workflow

### Recommended Workflow for New Photos

1. **Add photos to your folder structure**
   ```
   assets/2025/NewTrip/photo1.jpg
   assets/2025/NewTrip/photo2.jpg
   ```

2. **Process the photos**
   ```bash
   python photo_processor.py assets/2025/NewTrip --quality 85
   ```

3. **Open gallery_editor.html** and import the folder

4. **The editor will automatically use .min.jpg thumbnails** for preview

5. **Export to JSON** and add to gallery-config.json

### Batch Processing Multiple Folders

```bash
# Process all images in assets folder and subdirectories
python photo_processor.py assets --workers 8

# This will create thumbnails for:
# - assets/Street/*.jpg → assets/Street/*.min.jpg
# - assets/2024/Arizona_USA/*.jpg → assets/2024/Arizona_USA/*.min.jpg
# - assets/2025/NewTrip/*.jpg → assets/2025/NewTrip/*.min.jpg
```

## Performance Tips

- **Use more workers** for folders with many images: `--workers 8`
- **Lower quality** for web galleries: `--quality 80` (smaller files, minimal quality loss)
- **Larger thumbnails** for high-res displays: `--min-width 1600`
- The script **automatically skips** images that haven't changed (unless `--force` is used)

## Output

For each image like `photo.jpg`, the script creates:
- `photo.min.jpg` - Optimized thumbnail (default 1200px width, 85% quality)

The gallery editor and index.html automatically use `.min.jpg` files when available, falling back to the original if not found.

## Troubleshooting

**"No images found"**
- Make sure you have `.jpg` or `.jpeg` files in the directory
- Check that files don't already end with `.min.jpg`

**Watermark not showing**
- Make sure the font file exists at the specified path
- Try a darker color by editing the `fill` value in `add_watermark()` function

**"Out of memory" errors**
- Reduce `--workers` to use less parallel processing
- Process folders separately instead of all at once

## Integration with Gallery Editor

The photo processor works seamlessly with `gallery_editor.html`:

1. Process photos first with `photo_processor.py`
2. Open `gallery_editor.html` in browser
3. Import the folder - it will automatically detect and use `.min.jpg` thumbnails
4. Organize photos into groups
5. Export JSON and add to `gallery-config.json`

---

**Note:** This script only creates thumbnails. Original high-resolution images remain unchanged (unless watermarking is enabled).
