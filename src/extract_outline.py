import os
import json
import fitz  # PyMuPDF
import unicodedata
import re
import psutil
import time

class PDFOutlineExtractor:
    def __init__(self):
        self.outline = []

    def normalize_text(self, text):
        text = unicodedata.normalize('NFKD', text)
        text = text.replace('\ufeff', '')
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def extract_text_with_formatting(self, pdf_path):
        doc = fitz.open(pdf_path)
        text_blocks = []

        for page_num, page in enumerate(doc):
            blocks = page.get_text("dict")["blocks"]
            for block in blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        line_text = ''
                        size = 0
                        bold = False
                        y = 0
                        for span in line["spans"]:
                            clean_text = self.normalize_text(span['text'])
                            if clean_text:
                                line_text += clean_text + ' '
                                size = max(size, span['size'])
                                bold = bold or bool(span['flags'] & 2**4)
                                y = span['bbox'][1]
                        clean_text = self.normalize_text(line_text)
                        if clean_text:
                            text_blocks.append({
                                'text': clean_text,
                                'font_size': size,
                                'is_bold': bold,
                                'page': page_num + 1,
                                'y': y
                            })

        doc.close()
        return text_blocks

    def is_heading_candidate(self, text):
        if not text.strip():
            return False
        if all(c in ' .-–—' for c in text.strip()):
            return False
        if len(text.strip()) < 4:
            return False
        if len(text.split()) > 12:
            return False
        return True

    def merge_consecutive(self, items):
        merged = []
        prev = None
        for item in items:
            if prev and abs(item['y'] - prev['y']) < 8 and item['page'] == prev['page']:
                # Avoid merging if already part of previous text
                if item['text'] not in prev['text']:
                    prev['text'] += ' ' + item['text']
                    prev['text'] = self.normalize_text(prev['text'])
            else:
                if prev:
                    merged.append(prev)
                prev = item
        if prev:
            merged.append(prev)
        return merged

    def process_pdf(self, pdf_path):
        start = time.time()
        mem_start = psutil.Process().memory_info().rss / 1024 / 1024

        text_blocks = self.extract_text_with_formatting(pdf_path)
        if not text_blocks:
            return {"title": "Untitled", "outline": []}

        sizes = [b['font_size'] for b in text_blocks]
        avg_size = sum(sizes) / len(sizes)
        max_size = max(sizes)

        outline = []
        for b in text_blocks:
            if not self.is_heading_candidate(b['text']):
                continue

            size = b['font_size']
            level = None

            if size >= max_size:
                level = "H1"
            elif size >= avg_size * 1.15:
                level = "H2"
            elif b['is_bold'] and size >= avg_size:
                level = "H3"

            if level:
                outline.append({
                    "text": b["text"],
                    "level": level,
                    "page": b["page"],
                    "y": b["y"]
                })

        outline.sort(key=lambda x: (x["page"], x["y"]))
        outline = self.merge_consecutive(outline)

        # De-duplicate
        seen = set()
        cleaned = []
        for item in outline:
            key = (item["text"].lower(), item["page"])
            if key not in seen:
                seen.add(key)
                cleaned.append({
                    "text": item["text"],
                    "level": item["level"],
                    "page": item["page"]
                })

        title = cleaned[0]["text"] if cleaned else "Untitled"

        mem_end = psutil.Process().memory_info().rss / 1024 / 1024
        print(f"⏱️ Time: {time.time() - start:.2f}s | 🧠 RAM: {mem_end - mem_start:.2f}MB")
        print(f"📘 Title: {title}")
        print("📚 Outline:")
        for o in cleaned:
            print(f"  • [{o['level']}] {o['text']} (Page {o['page']})")

        return {
            "title": title,
            "outline": cleaned
        }

def main():
    input_dir = "/app/input"
    output_dir = "/app/output"
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(input_dir):
        if filename.lower().endswith('.pdf'):
            path = os.path.join(input_dir, filename)
            print(f"\n📄 Processing: {filename}")
            extractor = PDFOutlineExtractor()
            result = extractor.process_pdf(path)
            out_file = filename.replace('.pdf', '.json')
            with open(os.path.join(output_dir, out_file), 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"✅ Saved: {out_file}")

if __name__ == "__main__":
    main()
