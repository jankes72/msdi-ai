import re

with open('D:/sts/aplikacjaTyperBetAi/czesc4.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find all model catalog patterns
model_catalogs = re.findall(r'KATALOG_MODELU = r"([^"]+)"', content)
print('Model catalogs found:')
for i, catalog in enumerate(set(model_catalogs), 1):
    print(f'{i}. {catalog}')

print(f'\nTotal unique model catalogs: {len(set(model_catalogs))}')

# Find all main section titles
lines = content.split('\n')
main_sections = []
for i, line in enumerate(lines):
    if line.strip().startswith('# ===') and '===' in line:
        main_sections.append((i+1, line.strip()))

print(f'\nMain sections found: {len(main_sections)}')
for line_num, section in main_sections[:10]:
    print(f'{line_num}: {section}')
