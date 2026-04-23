from core.disk_reader import read_mbr_from_image
from core.mbr_parser import extract_boot_code
from core.mbr_parser import extract_partition_table_raw
from core.disk_reader import read_gpt_header_from_image
from core.gpt_parser import parse_gpt_header

def recover_mbr(image_path: str, clean_image_path: str) -> dict:
    """
    Restores MBR boot code from clean image into corrupted image.
    """

    # 1. read clean boot code
    clean_mbr = read_mbr_from_image(clean_image_path)
    clean_boot_code = extract_boot_code(clean_mbr)

    # 2. overwrite corrupted image
    with open(image_path, "r+b") as f:
        f.seek(0)  # start of disk (LBA 0)
        f.write(clean_boot_code)  # restore first 440 bytes

    return {
        "status": "RECOVERED",
        "message": "MBR boot code restored successfully"
    }


def recover_mbr_partition_table(image_path: str, clean_image_path: str) -> dict:
    """
    Restores 64-byte MBR partition table from clean image.
    """

    # read clean MBR
    clean_mbr = read_mbr_from_image(clean_image_path)
    clean_partition_table = extract_partition_table_raw(clean_mbr)

    # overwrite corrupted partition table
    with open(image_path, "r+b") as f:
        f.seek(446)  # partition table offset
        f.write(clean_partition_table)

    return {
        "status": "RECOVERED",
        "message": "MBR partition table restored successfully"
    }


def recover_gpt_partition_table(image_path: str, clean_image_path: str) -> dict:
    """
    Restores GPT partition entry array from clean image.
    """

    # 1. Read clean GPT header
    clean_header_bytes = read_gpt_header_from_image(clean_image_path)
    clean_header = parse_gpt_header(clean_header_bytes)

    entries_lba = clean_header["partition_entries_lba"]
    num_entries = clean_header["num_partition_entries"]
    entry_size = clean_header["size_of_partition_entry"]

    total_size = num_entries * entry_size
    offset = entries_lba * 512

    # 2. Read clean partition entries
    with open(clean_image_path, "rb") as f:
        f.seek(offset)
        clean_entries = f.read(total_size)

    # 3. Overwrite corrupted image
    with open(image_path, "r+b") as f:
        f.seek(offset)
        f.write(clean_entries)

    return {
        "status": "RECOVERED",
        "message": "GPT partition table restored successfully"
    }

SECTOR_SIZE = 512

def recover_gpt_partition_table_from_backup(image_path: str) -> dict:
    """
    Recover PRIMARY GPT partition table using BACKUP GPT partition table.
    """

    with open(image_path, "r+b") as f:

        # 1. Read PRIMARY GPT header (LBA 1)
        f.seek(SECTOR_SIZE)
        primary_header_bytes = f.read(SECTOR_SIZE)
        primary = parse_gpt_header(primary_header_bytes)

        # 2. Read BACKUP GPT header
        backup_lba = primary["backup_lba"]
        f.seek(backup_lba * SECTOR_SIZE)
        backup_header_bytes = f.read(SECTOR_SIZE)
        backup = parse_gpt_header(backup_header_bytes)

        # 3. Compute partition table size
        num_entries = backup["num_partition_entries"]
        entry_size = backup["size_of_partition_entry"]

        total_size = num_entries * entry_size

        # 4. Read backup partition array
        backup_entries_offset = backup["partition_entries_lba"] * SECTOR_SIZE
        f.seek(backup_entries_offset)
        backup_table = f.read(total_size)

        # 5. Write into PRIMARY partition table location
        primary_entries_offset = primary["partition_entries_lba"] * SECTOR_SIZE
        f.seek(primary_entries_offset)
        f.write(backup_table)

    return {
        "status": "RECOVERED",
        "message": "GPT partition table restored from backup successfully"
    }