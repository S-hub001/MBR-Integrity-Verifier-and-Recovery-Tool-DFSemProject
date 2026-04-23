import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

from core.disk_reader import (
    read_mbr_from_image,
    read_gpt_header_from_image,
    read_mbr_from_live,
    read_gpt_header_from_live
)
from core.recovery import (
    recover_mbr,
    recover_mbr_partition_table,
    recover_gpt_partition_table_from_backup
)

from core.mbr_parser import extract_boot_code, extract_partition_table_raw, parse_partition_table
from core.gpt_parser import parse_gpt_header
from core.integrity_checker import check_mbr_integrity, check_gpt_integrity
from Report.report_generator import generate_pdf_report


class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("MBR Integrity Forensic Dashboard")
        self.root.geometry("950x600")
        self.root.configure(bg="#0f172a")  # dark navy background

        self.image_path = None
        self.mode = "image"
        self.last_results = {}

        # ─────────────────────────────
        # TOP TITLE
        # ─────────────────────────────
        title = tk.Label(
            root,
            text="FORENSIC MBR & GPT INTEGRITY DASHBOARD",
            font=("Arial", 16, "bold"),
            fg="white",
            bg="#0f172a"
        )
        title.pack(pady=10)

        # ─────────────────────────────
        # MAIN FRAME
        # ─────────────────────────────
        main_frame = tk.Frame(root, bg="#0f172a")
        main_frame.pack(fill="both", expand=True)

        # LEFT PANEL (CONTROLS)
        self.left = tk.Frame(main_frame, bg="#111827", width=250)
        self.left.pack(side="left", fill="y", padx=10, pady=10)

        # RIGHT PANEL (OUTPUT)
        self.right = tk.Frame(main_frame, bg="#1f2937")
        self.right.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # ─────────────────────────────
        # BUTTON STYLE
        # ─────────────────────────────
        def btn(text, cmd):
            return tk.Button(
                self.left,
                text=text,
                command=cmd,
                width=25,
                bg="#2563eb",
                fg="white",
                font=("Arial", 10, "bold"),
                relief="flat"
            )

        btn("Load Image", self.load_image).pack(pady=5)
        btn("Select Live Disk", self.select_live_disk).pack(pady=5)
        btn("Verify MBR", self.verify_mbr).pack(pady=5)
        btn("Verify GPT", self.verify_gpt).pack(pady=5)
        btn("Corrupt MBR", self.corrupt_mbr).pack(pady=5)
        btn("Corrupt MBR PT", self.corrupt_mbr_partition).pack(pady=5)
        btn("Corrupt GPT PT", self.corrupt_gpt).pack(pady=5)
        btn("Recover MBR Boot Code", self.recover_mbr).pack(pady=5)
        btn("Recover MBR Partition Table", self.recover_mbr_partition).pack(pady=5)
        btn("Recover GPT Partition Table", self.recover_gpt_partition_table_from_backup).pack(pady=5)
        btn("Generate Report", self.generate_report).pack(pady=5)
        # ─────────────────────────────
        # OUTPUT BOX (RIGHT PANEL)
        # ─────────────────────────────
        self.output = tk.Text(
            self.right,
            bg="#0b1220",
            fg="#00ff99",
            font=("Consolas", 11),
            wrap="word"
        )
        self.output.pack(fill="both", expand=True)

        # ─────────────────────────────
        # STATUS BAR
        # ─────────────────────────────
        self.status = tk.Label(
            root,
            text="STATUS: READY",
            bg="#111827",
            fg="white",
            font=("Arial", 10)
        )
        self.status.pack(fill="x")

    # ─────────────────────────────
    # UTILITY
    # ─────────────────────────────
    def log(self, text):
        self.output.insert(tk.END, text + "\n")
        self.output.see(tk.END)

    def set_status(self, text):
        self.status.config(text=f"STATUS: {text}")

    # ─────────────────────────────
    # LOAD IMAGE
    # ─────────────────────────────
    def load_image(self):
        path = filedialog.askopenfilename()
        if path:
            self.image_path = path
            self.mode = "image"
            self.set_status("IMAGE LOADED")
            self.log(f"[+] Loaded: {path}")

    # ─────────────────────────────
    # LIVE DISK
    # ─────────────────────────────
    def select_live_disk(self):
        self.image_path = 0
        self.mode = "live"
        self.set_status("LIVE DISK SELECTED")
        self.log("[+] Live Disk: PhysicalDrive0")

    # ─────────────────────────────
    # MBR CHECK
    # ─────────────────────────────
    def verify_mbr(self):
        try:
            self.set_status("ANALYZING MBR")

            if self.mode == "image":
                mbr = read_mbr_from_image(self.image_path)
            else:
                mbr = read_mbr_from_live(self.image_path)

            boot = extract_boot_code(mbr)
            pt = parse_partition_table(mbr)
            pt_raw = extract_partition_table_raw(mbr)

            result = check_mbr_integrity({
                "boot_code": boot,
                "partition_table": pt_raw
            })

            partitions = parse_partition_table(mbr)
            result["partitions"] = partitions

            self.last_results["MBR"] = result

            color = "🟢" if result["status"] == "OK" else "🔴"

            self.log(f"\n{color} MBR STATUS: {result['status']}")

            self.log(f"Boot Hash: {result['boot_hash']}")
            self.log(f"Partition Table Hash: {result['partition_table_hash']}")
            self.log(f"Boot OK: {result['boot_match']}")
            self.log(f"Partition Table OK: {result['partition_table_match']}")

            self.set_status("MBR CHECK COMPLETE")

        except Exception as e:
            self.set_status("ERROR")
            messagebox.showerror("Error", str(e))

    # ─────────────────────────────
    # GPT CHECK
    # ─────────────────────────────
    def verify_gpt(self):
        try:
            self.set_status("ANALYZING GPT")

            if self.mode == "image":
                gpt = read_gpt_header_from_image(self.image_path)
            else:
                gpt = read_gpt_header_from_live(self.image_path)

            gpt_dict = parse_gpt_header(gpt)
            result = check_gpt_integrity(gpt_dict)

            self.last_results["GPT"] = result

            color = "🟢" if result["status"] == "OK" else "🔴"

            self.log(f"\n{color} GPT STATUS: {result['status']}")
            self.log(f"Signature OK: {result['signature_valid']}")
            self.log(f"Structure OK: {result['structure_valid']}")

            self.set_status("GPT CHECK COMPLETE")

        except Exception as e:
            self.set_status("ERROR")
            messagebox.showerror("Error", str(e))

    # ─────────────────────────────
    # CORRUPTION SIMULATION
    # ─────────────────────────────
    def corrupt_mbr(self):
        if self.mode != "image":
            messagebox.showerror("Error", "Only for image mode")
            return

        with open(self.image_path, "r+b") as f:
            f.seek(0)
            f.write(b"\x00")

        self.set_status("MBR CORRUPTED")
        self.log("[!] MBR corrupted (simulation)")

    # corrupt MBR Partition Table (simulate)
    def corrupt_mbr_partition(self):
        if self.mode != "image":
            messagebox.showerror("Error", "Only for image mode")
            return

        with open(self.image_path, "r+b") as f:
            f.seek(446)  # partition table offset
            f.write(b"\x00" * 64)

        self.set_status("MBR PARTITION TABLE CORRUPTED")
        self.log("[!] MBR partition table corrupted (simulation)")

    # Corrupt GPT Partition Table (simulate)
    def corrupt_gpt(self):
        if self.mode != "image":
            messagebox.showerror("Error", "Only for image mode")
            return

        with open(self.image_path, "r+b") as f:
            f.seek(512 * 2)  # GPT partition entries start at LBA 2
            f.write(b"\x00" * 512)  # corrupt first 512 bytes of partition entries

        self.set_status("GPT PARTITION TABLE CORRUPTED")
        self.log("[!] GPT partition table corrupted (simulation)")

    # ─────────────────────────────
    # RECOVERY
    # ─────────────────────────────
    def recover_mbr(self):
        clean = filedialog.askopenfilename(title="Select CLEAN MBR")
        if clean:
            result = recover_mbr(self.image_path, clean)
            self.log("\n[RECOVERY] " + result["message"])
            self.set_status("RECOVERY DONE")

    # ─────────────────────────────
    # REPORT
    # ─────────────────────────────
    def generate_report(self):
        if not self.last_results:
            messagebox.showerror("Error", "Run checks first")
            return

        mbr_status = self.last_results.get("MBR", {}).get("status", "")
        gpt_status = self.last_results.get("GPT", {}).get("status", "")

        if mbr_status == "OK" and gpt_status == "OK":
            status = "SAFE"
        elif mbr_status == "CORRUPTED" or gpt_status == "CORRUPTED":
            status = "RISK"
        else:
            status = "UNKNOWN"

        filename = generate_pdf_report(self.last_results)

        self.set_status("REPORT GENERATED")
        self.log(f"[+] PDF Report Created: {filename}")

    # ─────────────────────────────
    # RECOVERY METHODS
    # ─────────────────────────────
    def recover_mbr_partition(self):
        clean = filedialog.askopenfilename(title="Select CLEAN IMAGE")
        if clean:
            result = recover_mbr_partition_table(self.image_path, clean)
            self.log("\n[RECOVERY] " + result["message"])
            self.set_status("MBR PARTITION TABLE RECOVERED")

    def recover_gpt_partition_table_from_backup(self):
        try:
            result = recover_gpt_partition_table_from_backup(self.image_path)
            self.log("\n[RECOVERY] " + result["message"])
            self.set_status("GPT PARTITION RECOVERED")
        except Exception as e:
            messagebox.showerror("Error", str(e))