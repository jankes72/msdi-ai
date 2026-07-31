#!/usr/bin/env python3
"""Skrypt do naprawy pyproject.toml - zamiana kluczy z myślnikami na wersje w cudzysłowie."""

with open('D:/sts/aplikacjaTyperBetAi/pyproject.toml', 'r', encoding='utf-8') as f:
    content = f.read()

# Zastąp klucze z myślnikami na wersje w cudzysłowie
replacements = [
    ('package-dir =', '"package-dir" ='),
    ('include-package-data =', '"include-package-data" ='),
    ('package-data =', '"package-data" ='),
    ('exclude-package-data =', '"exclude-package-data" ='),
]

for old, new in replacements:
    content = content.replace(old, new)

with open('D:/sts/aplikacjaTyperBetAi/pyproject.toml', 'w', encoding='utf-8') as f:
    f.write(content)

print('Zaktualizowano pyproject.toml')
