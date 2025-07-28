# analyze_collections.py
#!/usr/bin/env python3
"""
Adobe Hackathon Challenge 1B: Persona-Driven PDF Analysis
Extended to support multilingual input for persona and task.
"""

import os
import json
import time
import sys
from pathlib import Path
from typing import List, Dict, Any
import logging
from datetime import datetime
import re
from collections import Counter
import math

# Language detection and translation
from langdetect import detect
from deep_translator import GoogleTranslator

# Import Challenge 1A extractor
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Challenge_1a'))
from process_pdfs import PDFOutlineExtractor

import fitz  # PyMuPDF

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TFIDFAnalyzer:
    def __init__(self):
        self.documents = []
        self.vocab = set()
        self.idf_scores = {}

    def preprocess(self, text):
        text = text.lower()
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text)
        stop_words = set("""the and for are but not you all can had her was one our out day get has him his how man new
            now old see two way who boy did its let put say she too use that with have this will your from they know want
            been good much some time very when come here just like long make many over such take than them well were what""".split())
        return [w for w in words if w not in stop_words]

    def build_vocab(self, docs):
        self.documents = [self.preprocess(d) for d in docs]
        for doc in self.documents:
            self.vocab.update(doc)
        n = len(self.documents)
        for term in self.vocab:
            doc_count = sum(1 for doc in self.documents if term in doc)
            self.idf_scores[term] = math.log(n / (doc_count + 1))

    def tfidf_vector(self, text):
        words = self.preprocess(text)
        counts = Counter(words)
        total = len(words)
        return {t: (counts[t] / total) * self.idf_scores.get(t, 0) for t in self.vocab}

    def cosine(self, v1, v2):
        common = set(v1) & set(v2)
        dot = sum(v1[t] * v2[t] for t in common)
        mag1 = math.sqrt(sum(x**2 for x in v1.values()))
        mag2 = math.sqrt(sum(x**2 for x in v2.values()))
        return dot / (mag1 * mag2) if mag1 and mag2 else 0


class PersonaDrivenAnalyzer:
    def __init__(self):
        self.extractor = PDFOutlineExtractor()
        self.tfidf = TFIDFAnalyzer()

    def extract_pdf(self, path):
        try:
            doc = fitz.open(path)
            content = {"title": self.extractor.extract_title(doc), "outline": [], "sections": [], "full_text": ""}
            parts, section = [], None
            for i in range(len(doc)):
                page = doc[i]
                parts.append(page.get_text())
                blocks = page.get_text("dict")["blocks"]
                for block in blocks:
                    if "lines" in block:
                        for line in block["lines"]:
                            line_text = " ".join(s["text"] for s in line["spans"] if s["text"].strip())
                            fonts = [s["size"] for s in line["spans"] if s["text"].strip()]
                            flags = [s["flags"] for s in line["spans"] if s["text"].strip()]
                            if not line_text.strip(): continue
                            avg_font = sum(fonts)/len(fonts) if fonts else 12
                            is_heading = any(f > 13 or (fl & 16) for f, fl in zip(fonts, flags))
                            if is_heading and len(line_text) < 150:
                                if section:
                                    content["sections"].append(section)
                                section = {"title": line_text.strip(), "page": i+1, "content": "", "subsections": []}
                            elif section:
                                section["content"] += line_text
            if section:
                content["sections"].append(section)
            content["full_text"] = "\n".join(parts)
            doc.close()
            return content
        except Exception as e:
            logger.error(f"PDF error: {path} - {e}")
            return {"title": f"Error: {Path(path).name}", "outline": [], "sections": [], "full_text": ""}

    def analyze(self, input_json_path, pdf_dir):
        with open(input_json_path, 'r') as f:
            input_cfg = json.load(f)

        persona = input_cfg["persona"]["role"]
        task = input_cfg["job_to_be_done"]["task"]

        try:
            detected_lang = detect(persona + " " + task)
            if detected_lang != "en":
                persona = GoogleTranslator(source='auto', target='en').translate(persona)
                task = GoogleTranslator(source='auto', target='en').translate(task)
                logger.info(f"Translated to English: {persona} | {task}")
        except Exception as e:
            logger.warning(f"Language detection failed: {e}")

        docs = input_cfg["documents"]
        all_texts, content_by_file = [], {}
        for doc in docs:
            fpath = os.path.join(pdf_dir, doc["filename"])
            if os.path.exists(fpath):
                cont = self.extract_pdf(fpath)
                content_by_file[doc["filename"]] = cont
                all_texts.append(cont["full_text"] + " ".join(s["title"] + s["content"] for s in cont["sections"]))

        self.tfidf.build_vocab(all_texts)
        query = f"{persona} {task}"
        qvec = self.tfidf.tfidf_vector(query)

        rankings, top_subs = [], []
        for fname, cont in content_by_file.items():
            for sec in cont["sections"]:
                stext = f"{sec['title']} {sec['content']}"
                svec = self.tfidf.tfidf_vector(stext)
                score = self.tfidf.cosine(qvec, svec)
                rankings.append({"document": fname, "section_title": sec["title"], "page_number": sec["page"], "relevance_score": score, "content": sec["content"]})
                if score > 0.1:
                    top_subs.append({"document": fname, "refined_text": sec["content"][:1000], "page_number": sec["page"]})

        rankings.sort(key=lambda x: x["relevance_score"], reverse=True)
        extracted = [{"document": s["document"], "section_title": s["section_title"], "importance_rank": i+1, "page_number": s["page_number"]} for i, s in enumerate(rankings[:5])]
        top_subs = top_subs[:5]

        return {
            "metadata": {
                "input_documents": [d["filename"] for d in docs],
                "persona": input_cfg["persona"]["role"],
                "job_to_be_done": input_cfg["job_to_be_done"]["task"],
                "processing_timestamp": datetime.now().isoformat()
            },
            "extracted_sections": extracted,
            "subsection_analysis": top_subs
        }

def process_collection(dir_path):
    in_file = os.path.join(dir_path, "challenge1b_input.json")
    pdf_dir = os.path.join(dir_path, "PDFs")
    out_file = os.path.join(dir_path, "challenge1b_output.json")
    if not os.path.exists(in_file) or not os.path.exists(pdf_dir):
        logger.error("Missing input files or PDFs")
        return
    analyzer = PersonaDrivenAnalyzer()
    result = analyzer.analyze(in_file, pdf_dir)
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=4, ensure_ascii=False)
    logger.info(f"Output saved to {out_file}")

def main():
    logger.info("Challenge 1B analysis started")
    base = Path("/app/collections")
    if not base.exists():
        base = Path(".")
    for sub in base.iterdir():
        if sub.is_dir() and sub.name.startswith("Collection"):
            logger.info(f"Processing {sub.name}")
            process_collection(str(sub))

if __name__ == "__main__":
    main()
