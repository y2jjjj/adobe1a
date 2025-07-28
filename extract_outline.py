import os
import json
import fitz  # PyMuPDF

class PDFOutlineExtractor:
    def extract_text_with_formatting(self, pdf_path):
        doc = fitz.open(pdf_path)
        text_blocks = []

        for page_num, page in enumerate(doc):
            blocks = page.get_text("dict")["blocks"]
            for block in blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            if span['text'].strip():
                                text_blocks.append({
                                    'text': span['text'].strip(),
                                    'font_size': span['size'],
                                    'page': page_num + 1
                                })

        doc.close()
        return text_blocks

    def process_pdf(self, pdf_path):
        text_blocks = self.extract_text_with_formatting(pdf_path)

        # Fallback: use biggest text as title
        if not text_blocks:
            return {"title": "Untitled", "outline": []}

        sizes = [b['font_size'] for b in text_blocks if b['font_size'] > 0]
        avg_size = sum(sizes) / len(sizes)
        max_size = max(sizes)

        outline = []
        for b in text_blocks:
            if b['font_size'] >= max_size:
                level = "H1"
            elif b['font_size'] >= avg_size:
                level = "H2"
            else:
                continue  # skip non-heading
            outline.append({
                "text": b["text"],
                "level": level,
                "page": b["page"]
            })

        title = outline[0]["text"] if outline else "Untitled"
        return {
            "title": title,
            "outline": outline
        }

def main():
    input_dir = "/app/input"
    output_dir = "/app/output"
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(input_dir):
        if filename.lower().endswith('.pdf'):
            path = os.path.join(input_dir, filename)
            print(f"📝 Processing {filename}")
            extractor = PDFOutlineExtractor()
            result = extractor.process_pdf(path)
            out_file = filename.replace('.pdf', '.json')
            with open(os.path.join(output_dir, out_file), 'w') as f:
                json.dump(result, f, indent=2)
            print(f"✅ Saved: {out_file}")

if __name__ == "__main__":
    main()
