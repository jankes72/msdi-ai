#!/usr/bin/env python3
"""Skrypt do naprawy pyproject.toml - usunięcie cudzysłowia z kluczy."""

with open('D:/sts/aplikacjaTyperBetAi/pyproject.toml', 'r', encoding='utf-8') as f:
    content = f.read()

# Usun cudzysłów z kluczy
content = content.replace('"package-dir"', 'package-dir')
content = content.replace('"include-package-data"', 'include-package-data')
content = content.replace('"package-data"', 'package-data')
content = content.replace('"exclude-package-data"', 'exclude-package-data')

with open('D:/sts/aplikacjaTyperBetAi/pyproject.toml', 'w', encoding='utf-8') as f:
    f.write(content)

print('Zaktualizowano pyproject.toml')
