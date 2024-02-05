FROM python:3.12-slim AS jbig2enc_builder

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
FROM ubuntu:23.10

# Install runtime dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ocrmypdf \
    tesseract-ocr \
    tesseract-ocr-deu \
    tesseract-ocr-eng \
    rclone \
    git \
    python3-venv \
    samba && \
    rm -rf /var/lib/apt/lists/*

# Copy jbig2enc artifacts from the builder stage
COPY --from=jbig2enc_builder /usr/src/jbig2enc/src/.libs/libjbig2enc* /usr/local/lib/
COPY --from=jbig2enc_builder /usr/src/jbig2enc/src/jbig2 /usr/local/bin/
COPY --from=jbig2enc_builder /usr/src/jbig2enc/src/*.h /usr/local/include/

# Set working directory and copy Python dependencies
WORKDIR /usr/src/pysyncocr/src/
COPY requirements.txt ./

# Set up Samba
RUN mkdir -p /var/run/samba /var/lib/samba/private
COPY smb.conf /etc/samba/smb.conf

# Create a virtual environment
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY src/ ./

# Expose the Flask port
EXPOSE 5000

# Command to run the Flask application
CMD ["/opt/venv/bin/python", "main.py"]
