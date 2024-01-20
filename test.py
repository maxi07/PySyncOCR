from src.helpers.ProcessItem import ItemType, ProcessItem
from src.webserver.db import update_scanneddata_database

item = ProcessItem("testing", ItemType.PDF)
item.pdf_pages = 3
item.db_id = 8
update_scanneddata_database(item.db_id, {"pdf_pages": item.pdf_pages})