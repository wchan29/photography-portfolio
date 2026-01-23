#!/usr/bin/env python3
"""
Photo processor for portfolio gallery
Compresses images and creates thumbnails with optional watermarking
"""

import argparse
import sys
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
from PIL import Image, ImageDraw, ImageFont

try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False
    print("Note: Install tqdm for progress bars: pip install tqdm")


def process_photo(args_tuple):
    """Process a single photo (must be top-level function for multiprocessing)"""
    filepath, config = args_tuple

    min_path = filepath.with_name(filepath.stem + '.min' + filepath.suffix)

    # Skip if already processed and not forcing
    if not config['force'] and min_path.exists():
        if min_path.stat().st_mtime > filepath.stat().st_mtime:
            return {'status': 'skipped', 'file': filepath.name}

    try:
        img = Image.open(filepath).convert('RGB')
        width, height = img.size

        # Add watermark if requested
        if config.get('watermark') and config.get('watermark_text'):
            img = add_watermark(img, config)

        # Create thumbnail
        ratio = config['min_width'] / width
        new_size = (int(width * ratio), int(height * ratio))

        thumb = img.copy()
        thumb.thumbnail(new_size, Image.Resampling.LANCZOS)

        # Save optimized thumbnail
        thumb.save(
            min_path,
            "JPEG",
            quality=config['quality'],
            optimize=True,
            progressive=True,
            subsampling='4:2:0'  # Better compression for web
        )

        img.close()
        thumb.close()

        return {'status': 'processed', 'file': filepath.name}
    except Exception as e:
        return {'status': 'error', 'file': filepath.name, 'error': str(e)}


def add_watermark(img, config):
    """Add watermark to image"""
    img = img.copy()
    draw = ImageDraw.Draw(img)

    # Try to load custom font, fall back to default if not found
    try:
        font_path = config.get('font_path', './assets/font/Arial.ttf')
        fontsize = config.get('fontsize', 48)
        font = ImageFont.truetype(font_path, fontsize)
    except:
        font = ImageFont.load_default()

    watermark_text = config['watermark_text']

    # Calculate text position (centered bottom)
    bbox = draw.textbbox((0, 0), watermark_text, font=font)
    t_w = bbox[2] - bbox[0]
    t_h = bbox[3] - bbox[1]

    width, height = img.size
    x = (width - t_w) / 2
    y = height - 2 * t_h

    # Light gray watermark (simulates transparency on JPEG)
    fill = (235, 235, 235)

    draw.text((x, y), watermark_text, font=font, fill=fill)
    return img


def find_images(directory, recursive=True):
    """Find all image files in directory"""
    directory = Path(directory)

    if not directory.exists():
        print(f"Error: Directory '{directory}' does not exist")
        sys.exit(1)

    extensions = {'.jpg', '.jpeg', '.JPG', '.JPEG'}

    if recursive:
        images = [
            f for f in directory.rglob('*')
            if f.suffix in extensions and not f.stem.endswith('.min')
        ]
    else:
        images = [
            f for f in directory.glob('*')
            if f.suffix in extensions and not f.stem.endswith('.min')
        ]

    return sorted(images)


def main():
    parser = argparse.ArgumentParser(
        description='Batch process photos for web gallery - creates optimized thumbnails',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Process all images in a folder
  python photo_processor.py assets/2024/Arizona_USA

  # High quality thumbnails with 8 parallel workers
  python photo_processor.py assets/Street --quality 90 --min-width 1600 --workers 8

  # Force reprocess all images (even if thumbnails exist)
  python photo_processor.py assets/2024 --force

  # Add watermark to images
  python photo_processor.py assets/2024 --watermark --watermark-text "© Anson Chan 2024"

  # Process only current directory (not subdirectories)
  python photo_processor.py assets/Street --no-recursive
        '''
    )

    parser.add_argument('directory', help='Directory containing photos')
    parser.add_argument('--min-width', type=int, default=1200,
                       help='Width of thumbnail in pixels (default: 1200)')
    parser.add_argument('--quality', type=int, default=85,
                       help='JPEG quality 1-100 (default: 85)')
    parser.add_argument('--workers', type=int, default=4,
                       help='Number of parallel workers (default: 4)')
    parser.add_argument('--force', action='store_true',
                       help='Force reprocess all images, even if thumbnails exist')
    parser.add_argument('--no-recursive', action='store_true',
                       help='Only process images in the specified directory, not subdirectories')
    parser.add_argument('--watermark', action='store_true',
                       help='Add watermark to original images')
    parser.add_argument('--watermark-text', default='',
                       help='Watermark text (e.g., "© Your Name 2025")')
    parser.add_argument('--font-path', default='./assets/font/Arial.ttf',
                       help='Path to font file for watermark')
    parser.add_argument('--fontsize', type=int, default=48,
                       help='Font size for watermark (default: 48)')

    args = parser.parse_args()

    # Validation
    if args.quality < 1 or args.quality > 100:
        print("Error: Quality must be between 1 and 100")
        sys.exit(1)

    if args.min_width < 100:
        print("Error: Minimum width must be at least 100 pixels")
        sys.exit(1)

    # Find all images
    directory = Path(args.directory)
    images = find_images(directory, recursive=not args.no_recursive)

    if not images:
        print(f"No images found in {directory}")
        print("Make sure you have .jpg or .jpeg files in the directory")
        sys.exit(0)

    print(f"Found {len(images)} images in {directory}")

    if args.watermark and not args.watermark_text:
        print("Warning: --watermark enabled but no --watermark-text provided, skipping watermark")
        args.watermark = False

    # Prepare config
    config = {
        'min_width': args.min_width,
        'quality': args.quality,
        'force': args.force,
        'watermark': args.watermark,
        'watermark_text': args.watermark_text,
        'font_path': args.font_path,
        'fontsize': args.fontsize
    }

    # Show settings
    print(f"\nSettings:")
    print(f"  Thumbnail width: {args.min_width}px")
    print(f"  JPEG quality: {args.quality}")
    print(f"  Parallel workers: {args.workers}")
    print(f"  Force reprocess: {'Yes' if args.force else 'No'}")
    if args.watermark:
        print(f"  Watermark: '{args.watermark_text}'")
    print()

    # Process in parallel with progress bar
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        tasks = [(img, config) for img in images]

        if HAS_TQDM:
            results = list(tqdm(
                executor.map(process_photo, tasks),
                total=len(images),
                desc="Processing",
                unit="img"
            ))
        else:
            results = list(executor.map(process_photo, tasks))
            print(f"Processed {len(results)} images")

    # Summary
    processed = [r for r in results if r['status'] == 'processed']
    skipped = [r for r in results if r['status'] == 'skipped']
    errors = [r for r in results if r['status'] == 'error']

    print(f"\n{'='*60}")
    print(f"Results:")
    print(f"  [+] Processed: {len(processed)} images")
    print(f"  [-] Skipped: {len(skipped)} images (already up to date)")
    if errors:
        print(f"  [!] Errors: {len(errors)} images")
        for err in errors:
            print(f"    - {err['file']}: {err['error']}")
    print(f"{'='*60}")

    print(f"\nThumbnails saved with .min.jpg extension")
    print(f"Total files created: {len(processed)}")


if __name__ == '__main__':
    main()
