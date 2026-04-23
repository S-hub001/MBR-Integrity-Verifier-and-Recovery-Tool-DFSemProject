import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import hashlib
from core.disk_reader import read_mbr_from_image
from core.mbr_parser import extract_boot_code

image_path = "images\\mbr_test.vhd"

# STEP 1: read MBR
mbr = read_mbr_from_image(image_path)

# STEP 2: boot code hash (440 bytes)
boot_code = extract_boot_code(mbr)
boot_hash = hashlib.sha256(boot_code).hexdigest()

print("BOOT CODE HASH:")
print(boot_hash)

# STEP 3: partition table hash (64 bytes)
partition_table = mbr[446:510]
pt_hash = hashlib.sha256(partition_table).hexdigest()

print("\nPARTITION TABLE HASH:")
print(pt_hash)