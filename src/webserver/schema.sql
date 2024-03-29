DROP TABLE IF EXISTS `scanneddata`;

CREATE TABLE scanneddata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_name TEXT NOT NULL,
    created DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    modified DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    file_status TEXT NOT NULL DEFAULT 'Pending',
    previewimage_path TEXT,
    local_filepath TEXT,
    remote_filepath TEXT,
    remote_connection_id TEXT,
    pdf_pages INTEGER DEFAULT 0,
    pdf_pages_processed INTEGER DEFAULT 0
);