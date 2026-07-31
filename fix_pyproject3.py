#!/usr/bin/env python3
"""Skrypt do naprawy pyproject.toml - zamiana myślników na podkreślniki."""

with open('D:/sts/aplikacjaTyperBetAi/pyproject.toml', 'r', encoding='utf-8') as f:
    content = f.read()

# Zastąp klucze z myślnikami na wersje z podkreślnikami
content = content.replace('package-dir =', 'package_dir =')
content = content.replace('include-package-data =', 'include_package_data =')
content = content.replace('package-data =', 'package_data =')
content = content.replace('exclude-package-data =', 'exclude_package_data =')

with open('D:/sts/aplikacjaTyperBetAi/pyproject.toml', 'w', encoding='utf-8') as f:
    f.write(content)

print('Zaktualizowano pyproject.toml')
