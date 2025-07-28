# test_specific_collection.py (Updated for Multilingual-aware pipeline)
import sys
import os
import json
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Challenge_1a'))
sys.path.append('.')

from analyze_collections import PersonaDrivenAnalyzer

def test_specific_collection(collection_name):
    print(f"=== TESTING CHALLENGE 1B with {collection_name} ===")
    collection_dir = collection_name
    input_file = os.path.join(collection_dir, "challenge1b_input.json")
    pdfs_dir = os.path.join(collection_dir, "PDFs")

    if not os.path.exists(input_file):
        print(f"❌ Input file not found: {input_file}")
        return

    if not os.path.exists(pdfs_dir):
        print(f"❌ PDFs directory not found: {pdfs_dir}")
        return

    with open(input_file, 'r') as f:
        input_config = json.load(f)

    print(f"👤 Persona: {input_config['persona']['role']}")
    print(f"🎯 Task: {input_config['job_to_be_done']['task']}")
    print(f"📚 Documents: {len(input_config['documents'])}")

    analyzer = PersonaDrivenAnalyzer()
    print("⏳ Running analysis...")
    result = analyzer.analyze_collection(input_file, pdfs_dir)

    print("\n📊 RESULTS:")
    print(f"📅 Timestamp: {result['metadata']['processing_timestamp']}")
    print(f"📑 Sections: {len(result['extracted_sections'])}")
    print(f"📝 Subsections: {len(result['subsection_analysis'])}")

    for i, s in enumerate(result['extracted_sections'][:3]):
        print(f"{i+1}. {s['section_title']} (Page {s['page_number']} in {s['document']})")

    for i, sub in enumerate(result['subsection_analysis'][:2]):
        print(f"\nRefined from {sub['document']} (Page {sub['page_number']}):\n{sub['refined_text'][:150]}...")

    output_file = f"test_output_{collection_name.replace(' ', '_').lower()}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Output saved to {output_file}")

if __name__ == "__main__":
    for c in ["Collection 1", "Collection 2", "Collection 3"]:
        if os.path.exists(c):
            test_specific_collection(c)
            print("\n" + "="*80 + "\n")
        else:
            print(f"❌ Collection not found: {c}")