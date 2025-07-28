# PDF Structured Outline Extractor (Adobe Hackathon 1A)

## Overview

This solution **automatically extracts a hierarchical outline** (Title, H1, H2, H3 headings and their page numbers) from PDF documents, outputting results as specification-compliant JSON files.  
Optimized for **accuracy, speed, and generality**—no PDF-specific rules or network calls.

## Features

- **Accurate heading detection** using a multi-feature approach (font size, boldness, position, font name, sentence structure).
- **Handles standard and complex PDFs**; robust to line fragmentation, noisy layout, and various heading conventions.
- **Conforms to hackathon requirements**  
  - Max runtime: ≤10 seconds (50p PDF)  
  - Model/code size: <200MB  
  - CPU only, offline, runs in Docker (amd64)  
  - Processes all `/app/input/*.pdf`, outputs `/app/output/*.json`  
- **Bonus:** Multilingual normalization for improved handling of non-English PDFs.

## Project Structure

```
.
├── src/
│   └── extract_outline.py        # Main extraction script
├── requirements.txt              # Python dependencies (PyMuPDF)
├── Dockerfile                    # For reproducible builds/execution
├── input/                        # Place your PDF files here (mounted in docker)
├── output/                       # JSON output appears here (mounted in docker)
└── README.md                     # This file
```

## Installation & Usage

### **1. Build the Docker image (Required)**
Ensure Docker is installed and running.  
From the project root:
```bash
docker build --platform linux/amd64 -t pdf_outline_extractor_1a .
```

### **2. Prepare Input/Output Folders**
Place your PDF files (≤50 pages each) in the `input/` directory:
```bash
mkdir -p input output
# Copy or move PDF files to input/
```

### **3. Run the Extractor**
```bash
docker run --rm \
  -v "$PWD/input:/app/input" \
  -v "$PWD/output:/app/output" \
  --network none \
  pdf_outline_extractor_1a
```
- Each `filename.pdf` in `input/` produces a corresponding `filename.json` in `output/`.

## Output Format Example

```json
{
  "title": "Understanding AI",
  "outline": [
    { "level": "H1", "text": "Introduction",      "page": 1 },
    { "level": "H2", "text": "What is AI?",       "page": 2 },
    { "level": "H3", "text": "History of AI",     "page": 3 }
  ]
}
```

## Approach

- **PDF Parsing:** Uses [PyMuPDF](https://pymupdf.readthedocs.io/) for fast extraction of text and layout metadata, fully offline.
- **Heading Detection:**  
  - Combines font size (statistical z-scoring), bold/italic style, font name, text length, and punctuation cues for robust section detection.
  - Adjacent heading fragments (caused by PDF line breaks) are merged using y-position and font similarity.
- **Title Extraction:**  
  - Selects the largest, top-most text block on the first page, excluding body lines and fragments.
- **Outline Structuring:**  
  - Each detected heading is assigned a hierarchical level (`H1`, `H2`, `H3`) and deduplicated for clarity.
- **Multilingual Handling:**  
  - Unicode normalization and whitespace cleanup included; basic support for non-English character sets.

## Dependencies

- Python 3.8+  
- PyMuPDF==1.23.0  
- Standard libraries: os, json, re, unicodedata

To install manually:
```
pip install -r requirements.txt
```

## Constraints & Best Practices

- Handles any PDF (up to 50 pages); no per-document hardcoding.
- Model/code footprint <200MB.
- Strictly CPU-only, no GPU or network dependency.
- All processing occurs inside the container.
- For best accuracy, test on a variety of document types.

## Troubleshooting

- If output JSON is empty, ensure your PDF uses selectable, extractable text (not only scanned images).
- For edge cases (e.g., very fragmented headings), tune merging thresholds in the script as needed.

## Contact

For queries or feedback, please contact Yuvraj Kumar yuvraj.kr2022@gmail.com or open an issue in your private workspace.

**Built for Adobe India Hackathon 2025 — Connecting the Dots, Round 1A.**  
*Ready for direct evaluation via the provided Docker instructions.*

---
