import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime


# ─────────────────────────────
# PARTITION TYPE MAP (GLOBAL)
# ─────────────────────────────
MBR_TYPE_MAP = {
    "0x07": "NTFS",
    "07": "NTFS",
    0x07: "NTFS",

    "0x0C": "FAT32",
    "0C": "FAT32",
    0x0C: "FAT32",

    "0x83": "Linux",
    "83": "Linux",

    "0x00": "EMPTY"
}


def draw_box(c, x, y, width, height):
    c.setStrokeColorRGB(0.2, 0.2, 0.2)
    c.rect(x, y, width, height)


def get_next_report_filename(folder="generated_reports"):
    if not os.path.exists(folder):
        os.makedirs(folder)

    i = 1
    while True:
        filename = os.path.join(folder, f"forensic_report_{i}.pdf")
        if not os.path.exists(filename):
            return filename
        i += 1


def generate_pdf_report(results):
    filename = get_next_report_filename()
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter

    def header(title):
        c.setFillColorRGB(0.12, 0.12, 0.12)
        c.rect(0, height - 60, width, 60, fill=1)

        c.setFillColorRGB(1, 1, 1)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(40, height - 35, title)

    def footer(page_num):
        c.setFillColorRGB(0.5, 0.5, 0.5)
        c.setFont("Helvetica", 9)
        c.drawString(40, 30, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        c.drawRightString(width - 40, 30, f"Page {page_num}")

    def section_title(text, y):
        c.setFillColorRGB(0.2, 0.2, 0.2)
        c.rect(40, y - 5, width - 80, 20, fill=1)

        c.setFillColorRGB(1, 1, 1)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, y, text)

    def box(x, y, w, h):
        c.setStrokeColorRGB(0.7, 0.7, 0.7)
        c.rect(x, y, w, h)

    page = 1

    # ─────────────────────────────
    # COVER PAGE
    # ─────────────────────────────
    header("MBR FORENSIC ANALYSIS REPORT")

    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width / 2, 650, "MBR & GPT INTEGRITY REPORT")

    c.setFont("Helvetica", 12)
    c.drawCentredString(width / 2, 620, "Digital Forensics Analysis System")

    c.setFont("Helvetica", 10)
    c.drawCentredString(width / 2, 590, f"Report ID: {os.path.basename(filename)}")

    c.showPage()
    page += 1

    # ─────────────────────────────
    # MBR SECTION
    # ─────────────────────────────
    header("MBR ANALYSIS")

    mbr = results.get("MBR", {})
    status = mbr.get("status", "N/A")
    status_color = (0, 0.6, 0) if status == "OK" else (0.8, 0, 0)

    section_title("MBR Integrity Results", 700)
    draw_box(c, 40, 420, 520, 300)

    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica", 11)

    c.drawString(60, 660, "Status:")
    c.setFillColorRGB(*status_color)
    c.drawString(120, 660, status)

    c.setFillColorRGB(0, 0, 0)
    c.drawString(60, 635, f"Hash: {mbr.get('current_hash', 'N/A')}")
    c.drawString(60, 610, f"Expected: {mbr.get('expected_hash', 'N/A')}")

    c.drawString(60, 585, "Partitions:")

    y = 565
    for i, p in enumerate(mbr.get("partitions", [])):

        raw_type = p.get("type", "UNKNOWN")

        # ── FIX: Proper mapping ──
        p_type = MBR_TYPE_MAP.get(
            raw_type,
            MBR_TYPE_MAP.get(str(raw_type).upper(), "UNKNOWN")
        )

        start = p.get("start_lba", "N/A")
        size = p.get("size", "N/A")

        c.drawString(80, y, f"{i+1}) {p_type} | Start: {start} | Size: {size}")
        y -= 18

    c.showPage()
    page += 1

    # ─────────────────────────────
    # GPT SECTION
    # ─────────────────────────────
    header("GPT ANALYSIS")

    gpt = results.get("GPT", {})
    gpt_status = gpt.get("status", "N/A")
    gpt_color = (0, 0.6, 0) if gpt_status == "OK" else (0.8, 0, 0)

    section_title("GPT Integrity Results", 700)
    box(40, 540, width - 80, 140)

    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica", 11)

    c.drawString(60, 660, "Status:")
    c.setFillColorRGB(*gpt_color)
    c.drawString(120, 660, gpt_status)

    c.setFillColorRGB(0, 0, 0)
    c.drawString(60, 635, f"Signature Valid: {gpt.get('signature_valid', 'N/A')}")
    c.drawString(60, 610, f"Structure Valid: {gpt.get('structure_valid', 'N/A')}")

    c.showPage()
    page += 1

    # ─────────────────────────────
    # FINAL SUMMARY
    # ─────────────────────────────
    header("FINAL SUMMARY")

    system_status = results.get("system_status", "UNKNOWN")
    final_color = (0, 0.5, 0) if system_status == "SAFE" else (0.8, 0, 0)

    section_title("System Integrity Verdict", 700)
    box(40, 520, width - 80, 180)

    c.setFont("Helvetica-Bold", 14)
    c.setFillColorRGB(*final_color)
    c.drawString(60, 640, f"SYSTEM STATUS: {system_status}")

    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica", 11)

    c.drawString(60, 610, "MBR and GPT structures analyzed using forensic validation.")
    c.drawString(60, 590, "Results reflect boot-level integrity condition.")

    footer(page)
    c.save()

    return filename