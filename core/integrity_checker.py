"""
core/integrity_checker.py
=========================
Member 3: Integrity Verification Logic (MBR + GPT)
"""

import hashlib
from core.gpt_parser import parse_gpt_header
SECTOR_SIZE = 512

# hash calulated through the gernate_hash.py script on a known clean MBR image (mbr_test.vhd) - this is our "golden hash" for integrity checks
KNOWN_MBR_HASH = "59019b8b59cffb325855cdc7716d38f8ce2112b9b027f2f8516992e2e686525b"
KNOWN_MBR_PARTITION_TABLE_HASH = "9964173eba57c6cdf76a14843d7d8c197c66de18d3921a09751a5bddc19b3625"

# ─────────────────────────────────────────────
# MBR INTEGRITY CHECK
# ─────────────────────────────────────────────
def check_mbr_integrity(mbr_dict: dict) -> dict:
    """
    Checks both:
    1. Boot code integrity (440 bytes)
    2. Partition table integrity (64 bytes)
    """

    boot_code = mbr_dict["boot_code"]
    partition_table = mbr_dict["partition_table"]

    # ────────────────
    # HASH BOOT CODE
    # ────────────────
    boot_hash = hashlib.sha256(boot_code).hexdigest()
    boot_ok = (boot_hash == KNOWN_MBR_HASH)

    # ────────────────
    # HASH PARTITION TABLE
    # ────────────────
    pt_hash = hashlib.sha256(partition_table).hexdigest()
    pt_ok = (pt_hash == KNOWN_MBR_PARTITION_TABLE_HASH)

    # ────────────────
    # FINAL STATUS
    # ────────────────
    if boot_ok and pt_ok:
        status = "OK"
    else:
        status = "CORRUPTED"

    return {
        "type": "MBR",

        "status": status,

        "boot_hash": boot_hash,
        "boot_match": boot_ok,

        "partition_table_hash": pt_hash,
        "partition_table_match": pt_ok,

        "expected_boot_hash": KNOWN_MBR_HASH,
        "expected_partition_table_hash": KNOWN_MBR_PARTITION_TABLE_HASH
    }


# ─────────────────────────────────────────────
# GPT INTEGRITY CHECK
# ─────────────────────────────────────────────
def check_gpt_integrity(gpt_dict: dict) -> dict:
    """
    Simple GPT integrity verification:
    1. Check signature
    2. Check basic consistency
    """

    signature_ok = (gpt_dict.get("signature") == "EFI PART")

    # basic sanity checks
    backup_lba = gpt_dict.get("backup_lba", 0)
    current_lba = gpt_dict.get("current_lba", 0)

    structure_ok = backup_lba > 0 and current_lba >= 1

    if signature_ok and structure_ok:
        status = "OK"
    else:
        status = "CORRUPTED"

    return {
        "type": "GPT",
        "status": status,
        "signature_valid": signature_ok,
        "structure_valid": structure_ok
    }


# ─────────────────────────────────────────────
# COMBINED SYSTEM CHECK (FOR GUI)
# ─────────────────────────────────────────────
def full_integrity_report(mbr_dict: dict, gpt_dict: dict) -> dict:
    """
    Returns unified report for dashboard/demo.
    """

    mbr_result = check_mbr_integrity(mbr_dict)
    gpt_result = check_gpt_integrity(gpt_dict)

    return {
        "MBR": mbr_result,
        "GPT": gpt_result,
        "system_status": "SAFE"
        if mbr_result["status"] == "OK" and gpt_result["status"] == "OK"
        else "COMPROMISED"
    }


