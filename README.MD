MBR Integrity Verifier and Recovery Tool
========================================

A Python-based digital forensics utility for reading, verifying, parsing, and recoveringMaster Boot Record (MBR) and GPT data from forensic disk images and live physical disks.

---

1\. 🔍Tool Overview
----------------------

This tool provides raw sector-level access to disk structures critical in forensicinvestigations — including the Master Boot Record (MBR), Primary GPT Header, and Backup GPT Header.

The system is modular:
\
**Disk Reader Module** handles low-level disk access.
\
**MBR & GPT Parser Module** extracts structured forensic information from raw bytes.
\
**Integrity & Recovery Module** verifies and restores modified boot structures.
\
**GUI & Reporting Module** provides visualization and report generation.
    

The disk reading module (core/disk\_reader.py) forms the foundation of the system. It reads 512-byte sectors from:
 - Forensic images (.dd, .img, split .001–.00N)
 - Live physical disks (Windows \\\\.\\PhysicalDriveN)
    

Split forensic image formats are automatically detected and reassembled in memory. All functions strictly follow a forensic rule: 
> No modification, no printing, only raw byte extraction.
The modification is just simulated for demonstration purposes.

---

2\. ⚙️Installation Instructions
-----------------------------

**Step 1 — Install Python 3.10 or higher**

Download from [https://www.python.org/downloads/](https://www.python.org/downloads/) and enable “Add to PATH”.

Verify:
```   
python --version   
```

**Step 2 — Project Structure**
```
   DFProject/  
   ├── core/  
   │   ├── disk_reader.py  
   │   ├── mbr_parser.py  
   │   ├── gpt_parser.py
   │   ├── integrity_checker.py
   │   ├── recovery.py
   |   └── log.py
   ├── generated_reports/
   │   ├── .... (all reports created - stored here)
   ├── GUI/
   │   └── main_window.py
   ├── images/  
   │   ├── clean_mbr.vhd  # for recovery purposes
   │   ├── mbr_test.vhd  
   │   ├── gpt_test.vhd  
   │   └── README_IMAGES.txt 
   ├── logs/
   |   └── log.txt
   ├── tests/  
   │   ├── test_disk_reader.py  
   |   ├── ......py's
   │   └── test_run_parser.py  
   └── main.py  
```

**Step 3 — Load forensic images or VHD disks**
**IMP**: Place all .001 image segments or mounted VHD disk files inside images/, and make sure to keep a clean backup of mbr_test.vhd (naming convention accordingly) for backup purposes of MBR boot code and MBR partition table.

**Step 4 — External libraries required**
```
1. reportlab (for PDF report generation)
```
Rest all are Python's standard libraries.

---

3\. ⚠️Dependencies and Prerequisites
----------------------------------
No external dependencies are required. It relies entirely on the following
Python standard library modules which come pre-installed with Python:
- `os` — file path resolution and size calculation
- `sys` — platform detection for live disk access
- `glob` — segment file discovery
- `struct` — reserved for binary parsing extensions
- `ReportLab` — used for report generation

**Requirements:**
 - Python 3.10+
 - Windows (for live disk access)
 - Administrator privileges (for PhysicalDrive access only)
    
---

4\. 🛠️Execution Steps
-------------------
## **Running the test suite (recommended first step):**

```python
      cd <folder_name>
      python tests/test_disk_reader.py
```

This will run six tests covering segment detection, MBR reading, GPT header reading,
backup GPT reading, live disk access, and error handling. All results are printed
with PASS/FAIL indicators.

 - **Using the module in code:**

```python
      from core.disk_reader import read_mbr_from_image

      mbr = read_mbr_from_image("images/<image_file_name.***>")
      # mbr is exactly 512 raw bytes
```

 - **Live disk access on Windows (must run PowerShell as Administrator):**

```python
      from core.disk_reader import read_mbr_from_live

      mbr = read_mbr_from_live(drive_number=0)
      # 0 = PhysicalDrive0, 1 = PhysicalDrive1, and so on
```

 - **Getting image metadata:**

```python
      from core.disk_reader import get_image_info

      info = get_image_info("images/clean_mbr.001")
      # Returns total size, sector count, segment list, and split flag
```

## **Run full integration test:**
```   
      python tests/test_run_parser.py   
```

 - **Read MBR:**
```python
      from core.disk_reader 
      import read_mbr_from_imagembr = read_mbr_from_image("images/mbr_test.vhd")   
```

 - **Parse MBR:**
```python
      from core.mbr_parser 
      import parse_partition_tablepartitions = parse_partition_table(mbr)   
```

 - **Parse GPT:**
```python
      from core.gpt_parser 
      import parse_gpt_headergpt_info = parse_gpt_header(gpt_bytes)   
```

## ***>>> 🚧 Finally Running the Tool : :***
In terminal, run
```python
       python main.py
```
inside the main folder. This file has capability to call the GUI/main_window.py which further calls other required functions from core/'s components.

---

5\. 🖥️Platform Compatibility
--------------------------

### Windows 10 / 11

✔ Full support\
✔ Live disk reading supported (PhysicalDrive)\
✔ VHD and forensic images supported

### Linux / macOS

✔ Forensic images supported\
✔ VHD must be mounted manually\
❌ Live disk reading module disabled

---
6\. ✨Features
-----------------
🔹 **Raw Sector-Level Disk Access**\
Reads 512-byte sectors directly from forensic images (.dd, .img, .vhd, split .001–.00N) and live physical disks (Windows PhysicalDrive). Ensures strict raw byte acquisition without modification.

🔹 **MBR Structure Parsing**\
Extracts and structures the 440-byte boot code, disk signature, 4 partition entries (16 bytes each), and validates boot signature (0x55AA).

🔹 **GPT Header Parsing**\
Parses primary GPT header fields including signature ("EFI PART"), revision, header size, CRC32 field, current/backup LBAs, and partition entry metadata.

🔹 **Partition Table Parsing (MBR & GPT)**\
Decodes partition entries into structured forensic dictionaries including type, start LBA, size, GUIDs, and partition names.

🔹 **SHA-256 Integrity Verification**\
Generates and compares cryptographic hashes for:
 - MBR boot code
 - MBR partition table
 - GPT partition entry array\
Detects unauthorized modification or corruption.

🔹 **GPT Primary vs Backup Validation**\
Compares primary GPT partition table with backup GPT partition table to detect tampering or structural inconsistencies.

🔹 **Corruption Simulation Module**\
Allows controlled corruption of:
 - MBR boot code
 - MBR partition table
 - GPT partition table\
Used for forensic testing and demonstration purposes.

🔹 **MBR Recovery**\
Using a clean reference image, restores corrupted:
 - Boot code (440 bytes)
 - Partition table (64 bytes)

🔹 **GPT Partition Table Recovery**\
Recovers corrupted primary GPT partition table directly from the backup GPT partition table stored at the end of the disk.

🔹 **GUI-Based Forensic Dashboard**\
Interactive Tkinter-based interface for loading images, running integrity checks, performing recovery, and visualizing forensic results.

🔹 **Automated PDF Report Generation**\
Generates structured forensic reports including integrity status, hashes, partition details, and final system verdict.

🔹 **Persistent Logging System**\
All dashboard actions and integrity results are saved to a log file for forensic traceability and audit documentation.

---
7\. 🆘Troubleshooting
-----------------------

**`FileNotFoundError` when running the test**
The image path in `tests/test_disk_reader.py` is set to `images/clean_mbr.001`.
Make sure your segment files are inside a folder named `images/` at the project root
and that the file is named exactly `clean_mbr.001`.

**`ValueError: only got N bytes`**
One or more image segments are missing or corrupted. Confirm that all 18 segments
are present in the `images/` folder and that none of them are 0 bytes in size.
Re-export the image from FTK Imager if segments are damaged.

**`PermissionError: Access denied to \\.\PhysicalDrive0`**
The script is not running with Administrator privileges. Close PowerShell, right-click
it, select "Run as administrator", navigate back to the project folder, and re-run
the test.

**`FileNotFoundError` on `\\.\PhysicalDrive0`**
The drive index may be wrong. Open Disk Management (`diskmgmt.msc`) to confirm which
physical drive number corresponds to the disk you want to read, then pass that number
to `read_mbr_from_live()`.

**`OSError: only supported on Windows`**
You called `read_mbr_from_live()` on Linux or macOS. Use `read_mbr_from_image()`
with the raw device path instead, as described in the Platform Compatibility section.

**Segments not being detected automatically**
The auto-detection looks for files sharing the same base name with purely numeric
extensions (`.001`, `.002`, etc.). If your files use a different naming convention,
rename them to follow this pattern or pass each path manually.

---

8\. 🤝Team Members
-----------------------
***1. Syeda Shanzay Shah 23I-2016\
2. Sarita Sangrez 23I-2088\
3. Rumaisah Haroon 23I-2106\
4. Fatima Naeem 23I-2046***
