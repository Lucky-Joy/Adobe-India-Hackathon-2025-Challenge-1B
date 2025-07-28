# Challenge 1B - Approach Explanation

## 🔍 Objective
To extract the most relevant and insightful subsections from a set of research papers, based on a given **persona** and a **job-to-be-done** task, and present them in a structured, useful format.

---

## 🧠 Core Strategy

### Step 1: PDF Parsing via Challenge 1A
- Reuses and integrates our Challenge 1A PDF outline extractor.
- For each document, generates structured section hierarchies (`title`, `H1`, `H2`, `H3`).

### Step 2: Multilingual Support (New ✅)
- **Input Handling**: Detects language of persona role and task description using `langdetect`.
- **Translation**: Automatically translates non-English inputs to English using `argos-translate`.
- Ensures compatibility with documents regardless of input language.

### Step 3: Section Matching
- For each PDF:
  - Parses JSON outline.
  - Extracts text blocks associated with each heading.
  - Filters sections/subsections that contain terms semantically relevant to persona/task.

### Step 4: Relevance Ranking
- Implements TF-IDF based scoring across all document sections.
- Selects top-scoring sections.
- Optionally re-ranks based on sentence-level cosine similarity to input task.

### Step 5: Output Structuring
- Outputs a dictionary with:
  - Metadata (persona, task, timestamp)
  - Extracted top-level sections
  - Subsection analysis (title, refined text, original document, score)

---

## 🔄 Multilingual Input Design
| Component | Approach |
|----------|----------|
| Language Detection | `langdetect.detect()` |
| Translation | `argos-translate` (offline, deterministic) |
| Language Scope | Spanish, German, French, Hindi, etc. to English |
| Output | English only (for now) |

---

## ⚙️ Architecture Overview
- `analyze_collections.py` → Entry point, orchestration, multilingual pre-processing.
- `PDFOutlineExtractor` → Reuses Challenge 1A logic.
- `TFIDFAnalyzer` → Matches persona/task to relevant document sections.
- `test_specific_collection.py` & `test_performance.py` → Validation scripts.

---

## 🧪 Testing Strategy
- Collection-specific tests for correctness.
- Batch tests for speed and accuracy.
- Manual input tests in Spanish, French, and German.

---

## ✅ Benefits of Our Solution
- Multilingual input capability without heavy models.
- Offline-ready using argos-translate.
- Modular, scalable, and directly integratable with Task 1A.
- Accurate section and subsection extraction using multi-factor matching.

---

## 📦 Output Sample
```json
{
  "metadata": {
    "persona": "Research Analyst",
    "task": "Evaluate methods for extracting medical features",
    "processing_timestamp": "2025-07-23T14:55:00"
  },
  "extracted_sections": [ ... ],
  "subsection_analysis": [ ... ]
}