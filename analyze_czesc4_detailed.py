import re

with open('D:/sts/aplikacjaTyperBetAi/czesc4.py', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')

# Find block starts - where we see the pattern at the beginning of a file section
block_starts = []
for i, line in enumerate(lines):
    if line.strip().startswith('# ===') and 'GENERATOR' in line:
        block_starts.append(i+1)
    elif i == 0 and line.strip().startswith('# ==='):
        block_starts.append(i+1)
    elif line.strip() == '# =====================================================':
        # Check if next line is GENERATOR title
        if i+1 < len(lines) and 'GENERATOR' in lines[i+1]:
            block_starts.append(i+1)

# Also find where LABORATORIUM starts
lab_starts = []
for i, line in enumerate(lines):
    if 'LABORATORIUM' in line and 'FRAGMENT' in line:
        lab_starts.append(i+1)

print("Block starts (GENERATOR):")
for start in block_starts:
    print(f"Line {start}: {lines[start-1].strip()}")

print(f"\nLABORATORIUM starts:")
for start in lab_starts:
    print(f"Line {start}: {lines[start-1].strip()}")

# Let's find the major sections by looking for the main titles
major_sections = []
for i, line in enumerate(lines):
    if 'GENERATOR ANALIZY TREND' in line or 'LABORATORIUM V2' in line:
        major_sections.append((i+1, line.strip()))

print(f"\nMajor sections:")
for line_num, section in major_sections:
    print(f"Line {line_num}: {section}")

# Count how many times each model catalog appears
model_catalogs = re.findall(r'KATALOG_MODELU = r"([^"]+)"', content)
from collections import Counter
catalog_counts = Counter(model_catalogs)

print(f"\nModel catalog usage counts:")
for catalog, count in sorted(catalog_counts.items(), key=lambda x: x[1], reverse=True):
    print(f"{count}x: {catalog}")
