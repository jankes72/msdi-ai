#!/usr/bin/env python3
"""Skrypt do naprawy pyproject.toml - zamiana package_data na sekcję."""

with open('D:/sts/aplikacjaTyperBetAi/pyproject.toml', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Znajdź i zastąp sekcję package_data i exclude_package_data
new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    
    # Znajdź linię z package_data = {
    if line.strip().startswith('package_data = {'):
        # Zastąp na [tool.setuptools.package-data]
        new_lines.append('[tool.setuptools.package-data]\n')
        i += 1
        # Przetwarzaj zawartość
        while i < len(lines) and not line.strip().startswith('}'):
            line = lines[i]
            if '"SSI"' in line:
                new_lines.append('SSI = ["py.typed"]\n')
            i += 1
        # Pomijaj zamykający }
        if i < len(lines) and lines[i].strip() == '}':
            i += 1
    # Znajdź linię z exclude_package_data = {
    elif line.strip().startswith('exclude-package_data = {'):
        # Zastąp na [tool.setuptools.exclude-package-data]
        new_lines.append('[tool.setuptools.exclude-package-data]\n')
        i += 1
        # Przetwarzaj zawartość
        while i < len(lines) and not line.strip().startswith('}'):
            line = lines[i]
            new_lines.append(line)
            i += 1
        # Pomijaj zamykający }
        if i < len(lines) and lines[i].strip() == '}':
            i += 1
    else:
        new_lines.append(line)
        i += 1

with open('D:/sts/aplikacjaTyperBetAi/pyproject.toml', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print('Zaktualizowano pyproject.toml')
