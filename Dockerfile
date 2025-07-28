FROM --platform=linux/amd64 python:3.9-slim

WORKDIR /app

# Install system dependencies for PyMuPDF
RUN apt-get update && apt-get install -y gcc g++ && apt-get clean

# Install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./

# Create input/output folders
RUN mkdir -p /app/input /app/output

# Run the extractor
CMD ["python", "extract_outline.py"]

