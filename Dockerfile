FROM python:3.10-slim AS jbig2enc_builder

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    automake \
    libtool \
    libleptonica-dev \
    zlib1g-dev \
    git \
    ca-certificates

# Clone and build jbig2enc
WORKDIR /usr/src/jbig2enc
RUN git clone https://github.com/agl/jbig2enc .
RUN ./autogen.sh && ./configure && make

# Intermediate stage to copy jbig2enc artifacts
FROM python:3.10-slim

# Install runtime dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ocrmypdf \
    tesseract-ocr \
    tesseract-ocr-deu \
    tesseract-ocr-eng \
    rclone \
    git \
    samba && \
    rm -rf /var/lib/apt/lists/*

# Copy jbig2enc artifacts from the builder stage
COPY --from=jbig2enc_builder /usr/src/jbig2enc/src/.libs/libjbig2enc* /usr/local/lib/
COPY --from=jbig2enc_builder /usr/src/jbig2enc/src/jbig2 /usr/local/bin/
COPY --from=jbig2enc_builder /usr/src/jbig2enc/src/*.h /usr/local/include/

# Set working directory and copy Python dependencies
WORKDIR /usr/src/pysyncocr/src/
COPY requirements.txt .

# Activate virtual environment
RUN python -m venv .venv
RUN . .venv/bin/activate

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY src/ ./

# Expose the Flask port
EXPOSE 5000

# Command to run the Flask application
CMD ["python", "main.py"]
