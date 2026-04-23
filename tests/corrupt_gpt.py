# corrupt_gpt.py
# Simulates GPT partition table corruption

file_path = "images/gpt_test.vhd"  

with open(file_path, "r+b") as f:
    f.seek(1024)  # GPT partition area start (approx LBA 2)
    f.write(b"\x00" * 64)

print("GPT partition table corrupted (64 bytes modified)")