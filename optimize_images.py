import os
from PIL import Image
import piexif
from pathlib import Path

def optimize_image(input_path, output_path, max_size=(800, 800), quality=85):
    """Optimize a single image with size and quality reduction"""
    try:
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with Image.open(input_path) as img:
            # Remove EXIF data
            try:
                img_without_exif = Image.new(img.mode, img.size)
                img_without_exif.putdata(list(img.getdata()))
                img = img_without_exif
            except:
                pass
            
            # Convert RGBA to RGB if necessary
            if img.mode == 'RGBA':
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])
                img = background
            
            # Resize if larger than max_size
            if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Create progressive JPEG
            img.save(output_path, 'JPEG', quality=quality, optimize=True, progressive=True)
            
        return True
    except Exception as e:
        print(f"Error optimizing {input_path}: {str(e)}")
        return False

def optimize_directory(input_dir, output_dir):
    """Optimize all images in a directory"""
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    # Create output directory
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Track statistics
    stats = {
        'processed': 0,
        'failed': 0,
        'total_size_before': 0,
        'total_size_after': 0
    }
    
    # Get list of image files (excluding the output directory)
    image_files = [
        f for f in input_path.glob('*')
        if f.suffix.lower() in ['.jpg', '.jpeg', '.png']
        and 'optimized' not in str(f)
    ]
    
    # Process all images
    for img_path in image_files:
        output_file = output_path / img_path.name
        
        # Get original file size
        original_size = img_path.stat().st_size
        stats['total_size_before'] += original_size
        
        # Optimize image
        if optimize_image(str(img_path), str(output_file)):
            stats['processed'] += 1
            stats['total_size_after'] += output_file.stat().st_size
        else:
            stats['failed'] += 1
    
    # Print statistics
    print(f"\nOptimization complete:")
    print(f"Processed: {stats['processed']} images")
    print(f"Failed: {stats['failed']} images")
    
    if stats['total_size_before'] > 0:
        size_before_mb = stats['total_size_before'] / (1024 * 1024)
        size_after_mb = stats['total_size_after'] / (1024 * 1024)
        reduction = ((stats['total_size_before'] - stats['total_size_after']) / stats['total_size_before']) * 100
        
        print(f"\nTotal size before: {size_before_mb:.2f} MB")
        print(f"Total size after: {size_after_mb:.2f} MB")
        print(f"Size reduction: {reduction:.1f}%")

if __name__ == '__main__':
    # Fix the path to correctly point to the static directory
    base_dir = Path(__file__).resolve().parent
    input_dir = base_dir / 'static' / 'images'
    output_dir = base_dir / 'static' / 'images' / 'optimized'
    
    if not input_dir.exists():
        print(f"Input directory not found: {input_dir}")
        print("Creating directory structure...")
        input_dir.mkdir(parents=True, exist_ok=True)
    
    print("Starting image optimization...")
    optimize_directory(input_dir, output_dir)