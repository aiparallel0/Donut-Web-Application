# -*- coding: utf-8 -*-
"""
Batch Processing Module for DONUT Receipt Parser
Efficiently process multiple receipt images in parallel
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Union, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from datetime import datetime

import torch
from PIL import Image
from tqdm import tqdm

# Import from main application
try:
    from donut_minimal import load_model, parse_receipt, processor, model, device
    import config
except ImportError:
    # Fallback for standalone usage
    import sys
    sys.path.append(str(Path(__file__).parent))
    from donut_minimal import load_model, parse_receipt, processor, model, device
    import config


class BatchReceiptProcessor:
    """
    Batch processor for multiple receipt images
    Handles parallel processing, error recovery, and result aggregation
    """

    def __init__(self, batch_size: int = None, num_workers: int = None):
        """
        Initialize batch processor

        Args:
            batch_size: Number of images to process in parallel (default from config)
            num_workers: Number of worker threads (default from config)
        """
        self.batch_size = batch_size or config.BATCH_SIZE
        self.num_workers = num_workers or config.NUM_WORKERS
        self.results = []
        self.errors = []
        self.stats = {
            "total": 0,
            "successful": 0,
            "failed": 0,
            "total_time": 0,
            "avg_time": 0
        }

        # Ensure model is loaded
        if model is None or processor is None:
            print("Loading model for batch processing...")
            load_model()

    def process_directory(self,
                         input_dir: Union[str, Path],
                         output_dir: Optional[Union[str, Path]] = None,
                         recursive: bool = False,
                         show_progress: bool = True) -> Dict:
        """
        Process all images in a directory

        Args:
            input_dir: Directory containing receipt images
            output_dir: Directory to save results (optional)
            recursive: Search subdirectories
            show_progress: Show progress bar

        Returns:
            Dictionary with results and statistics
        """
        input_dir = Path(input_dir)

        if not input_dir.exists():
            raise FileNotFoundError(f"Input directory not found: {input_dir}")

        # Find all image files
        image_paths = self._find_images(input_dir, recursive)

        if not image_paths:
            print(f"No images found in {input_dir}")
            return {"results": [], "stats": self.stats}

        print(f"Found {len(image_paths)} images to process")

        # Process images
        results = self.process_batch(image_paths, show_progress=show_progress)

        # Save results if output directory specified
        if output_dir:
            self._save_results(results, output_dir)

        return {
            "results": results,
            "stats": self.stats,
            "errors": self.errors
        }

    def process_batch(self,
                     image_paths: List[Union[str, Path]],
                     show_progress: bool = True) -> List[Dict]:
        """
        Process a batch of images

        Args:
            image_paths: List of image file paths
            show_progress: Show progress bar

        Returns:
            List of results dictionaries
        """
        results = []
        self.stats["total"] = len(image_paths)
        start_time = time.time()

        # Process in batches with progress bar
        iterator = range(0, len(image_paths), self.batch_size)
        if show_progress:
            iterator = tqdm(iterator, desc="Processing receipts", unit="batch")

        for i in iterator:
            batch = image_paths[i:i + self.batch_size]
            batch_results = self._process_single_batch(batch)
            results.extend(batch_results)

        # Calculate statistics
        self.stats["total_time"] = time.time() - start_time
        self.stats["successful"] = sum(1 for r in results if "error" not in r)
        self.stats["failed"] = len(results) - self.stats["successful"]
        self.stats["avg_time"] = self.stats["total_time"] / len(results) if results else 0

        self.results = results
        return results

    def _process_single_batch(self, image_paths: List[Path]) -> List[Dict]:
        """Process a single batch of images in parallel"""
        results = []

        # Use ThreadPoolExecutor for parallel processing
        with ThreadPoolExecutor(max_workers=min(self.num_workers, len(image_paths))) as executor:
            # Submit all tasks
            future_to_path = {
                executor.submit(self._process_single_image, path): path
                for path in image_paths
            }

            # Collect results as they complete
            for future in as_completed(future_to_path):
                path = future_to_path[future]
                try:
                    result = future.result()
                    result["image_path"] = str(path)
                    result["filename"] = path.name
                    results.append(result)
                except Exception as e:
                    error_result = {
                        "image_path": str(path),
                        "filename": path.name,
                        "error": f"Processing failed: {str(e)}"
                    }
                    results.append(error_result)
                    self.errors.append(error_result)

        return results

    def _process_single_image(self, image_path: Path) -> Dict:
        """
        Process a single image

        Args:
            image_path: Path to image file

        Returns:
            Result dictionary
        """
        try:
            # Load image
            image = Image.open(image_path).convert("RGB")

            # Process with main parser
            result = parse_receipt(image)

            # Add metadata
            result["processed_at"] = datetime.now().isoformat()

            # Clear cache if configured
            if config.CLEAR_CACHE_AFTER_INFERENCE and torch.cuda.is_available():
                torch.cuda.empty_cache()

            return result

        except Exception as e:
            return {
                "error": str(e),
                "error_type": type(e).__name__
            }

    def _find_images(self, directory: Path, recursive: bool) -> List[Path]:
        """Find all image files in directory"""
        image_paths = []

        pattern = "**/*" if recursive else "*"

        for ext in config.SUPPORTED_FORMATS:
            image_paths.extend(directory.glob(f"{pattern}{ext}"))
            image_paths.extend(directory.glob(f"{pattern}{ext.upper()}"))

        return sorted(image_paths)

    def _save_results(self, results: List[Dict], output_dir: Union[str, Path]):
        """Save batch results to output directory"""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save individual results
        for result in results:
            if "filename" in result:
                filename = Path(result["filename"]).stem
                output_file = output_dir / f"{filename}_{timestamp}.json"

                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(result, f, indent=config.JSON_INDENT, ensure_ascii=config.JSON_ENSURE_ASCII)

        # Save summary
        summary_file = output_dir / f"batch_summary_{timestamp}.json"
        summary = {
            "timestamp": timestamp,
            "stats": self.stats,
            "total_files": len(results),
            "successful": self.stats["successful"],
            "failed": self.stats["failed"],
            "errors": self.errors
        }

        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        print(f"\nResults saved to: {output_dir}")
        print(f"Summary: {summary_file}")

    def print_summary(self):
        """Print processing summary"""
        print("\n" + "="*60)
        print("BATCH PROCESSING SUMMARY")
        print("="*60)
        print(f"Total images:     {self.stats['total']}")
        print(f"Successful:       {self.stats['successful']}")
        print(f"Failed:           {self.stats['failed']}")
        print(f"Total time:       {self.stats['total_time']:.2f}s")
        print(f"Average per image: {self.stats['avg_time']:.2f}s")
        print(f"Throughput:       {self.stats['total'] / self.stats['total_time']:.2f} images/sec")
        print("="*60)


def main():
    """Command-line interface for batch processing"""
    import argparse

    parser = argparse.ArgumentParser(description="Batch process receipt images with DONUT")
    parser.add_argument("input_dir", help="Directory containing receipt images")
    parser.add_argument("-o", "--output", help="Output directory for results")
    parser.add_argument("-r", "--recursive", action="store_true", help="Search subdirectories")
    parser.add_argument("-b", "--batch-size", type=int, help="Batch size")
    parser.add_argument("-w", "--workers", type=int, help="Number of worker threads")
    parser.add_argument("--no-progress", action="store_true", help="Disable progress bar")

    args = parser.parse_args()

    # Create processor
    processor = BatchReceiptProcessor(
        batch_size=args.batch_size,
        num_workers=args.workers
    )

    # Process directory
    try:
        results = processor.process_directory(
            input_dir=args.input_dir,
            output_dir=args.output,
            recursive=args.recursive,
            show_progress=not args.no_progress
        )

        # Print summary
        processor.print_summary()

        # Print sample results
        if results["results"]:
            print("\nSample result:")
            print(json.dumps(results["results"][0], indent=2))

        # Print errors if any
        if processor.errors:
            print(f"\n⚠ {len(processor.errors)} errors occurred:")
            for error in processor.errors[:5]:  # Show first 5 errors
                print(f"  - {error['filename']}: {error['error']}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
