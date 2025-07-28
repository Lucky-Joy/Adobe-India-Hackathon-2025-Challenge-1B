# test_performance.py (Updated for Multilingual-aware pipeline)
import time
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from analyze_collections import PersonaDrivenAnalyzer
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

def test_collection_performance(collection_dir: str, max_time: float = 60.0) -> dict:
    input_file = os.path.join(collection_dir, "challenge1b_input.json")
    pdfs_dir = os.path.join(collection_dir, "PDFs")

    if not os.path.exists(input_file) or not os.path.exists(pdfs_dir):
        return {"error": f"Required files not found in {collection_dir}"}

    analyzer = PersonaDrivenAnalyzer()
    start_time = time.time()
    result = analyzer.analyze_collection(input_file, pdfs_dir)
    processing_time = time.time() - start_time

    valid = all(k in result for k in ["metadata", "extracted_sections", "subsection_analysis"])
    return {
        "collection": collection_dir,
        "time": processing_time,
        "valid_structure": valid,
        "result_preview": result.get("metadata", {})
    }

def run_tests():
    print("\n=== Running Challenge 1B Performance Tests ===")
    base = Path('.')
    for c in base.iterdir():
        if c.is_dir() and c.name.startswith("Collection"):
            r = test_collection_performance(str(c))
            print(f"\n📁 {r['collection']}:")
            print(f"⏱️ Time: {r['time']:.2f}s")
            print(f"✅ Structure: {r['valid_structure']}")
            print(f"📄 Metadata: {json.dumps(r['result_preview'], indent=2)}")

if __name__ == "__main__":
    run_tests()