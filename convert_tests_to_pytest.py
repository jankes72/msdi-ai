#!/usr/bin/env python3
"""
Masowy konwerter testów unittest na pytest
Szybka konwersja dla Sprint 8
"""

import re
from pathlib import Path

def convert_file(file_path):
    """Skonwertuj pojedynczy plik testowy"""
    print(f"Konwertuje: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        
        # 1. Usun import unittest
        content = re.sub(r'^import unittest\n', '', content, flags=re.MULTILINE)
        content = re.sub(r'^from unittest import .+?\n', '', content, flags=re.MULTILINE)
        
        # 2. Zamien unittest.TestCase
        content = re.sub(r'class (\w+)\(unittest\.TestCase\):', r'class \1:', content)
        
        # 3. Zamien asercje
        simple_asserts = [
            (r'self\.assertEqual\(([^,]+),\s*([^)]+)\)', r'assert \1 == \2'),
            (r'self\.assertNotEqual\(([^,]+),\s*([^)]+)\)', r'assert \1 != \2'),
            (r'self\.assertTrue\(([^)]+)\)', r'assert \1'),
            (r'self\.assertFalse\(([^)]+)\)', r'assert not \1'),
            (r'self\.assertIn\(([^,]+),\s*([^)]+)\)', r'assert \1 in \2'),
            (r'self\.assertNotIn\(([^,]+),\s*([^)]+)\)', r'assert \1 not in \2'),
            (r'self\.assertIs\(([^,]+),\s*([^)]+)\)', r'assert \1 is \2'),
            (r'self\.assertIsNot\(([^,]+),\s*([^)]+)\)', r'assert \1 is not \2'),
            (r'self\.assertIsNone\(([^)]+)\)', r'assert \1 is None'),
            (r'self\.assertIsNotNone\(([^)]+)\)', r'assert \1 is not None'),
            (r'self\.assertGreater\(([^,]+),\s*([^)]+)\)', r'assert \1 > \2'),
            (r'self\.assertLess\(([^,]+),\s*([^)]+)\)', r'assert \1 < \2'),
            (r'self\.fail\(([^)]+)\)', r'assert False, \1'),
        ]
        
        for pattern, replacement in simple_asserts:
            content = re.sub(pattern, replacement, content)
        
        # 4. Usun if __name__ == __main__ blok
        content = re.sub(r'\nif __name__\s*==\s*["\']__main__["\']:\s*\n(?:\s+.+\n)*.*?unittest\.main\(\)', '', content, flags=re.DOTALL)
        content = re.sub(r'\nif __name__\s*==\s*["\']__main__["\']:\s*\n(?:\s+.+\n)+', '\n', content, flags=re.DOTALL)
        
        # 5. Dodaj import pytest
        if 'import pytest' not in content:
            lines = content.split('\n')
            insert_pos = 0
            for i, line in enumerate(lines):
                stripped = line.strip()
                if stripped and (stripped.startswith('import ') or stripped.startswith('from ') or stripped.startswith('"""')):
                    if stripped.startswith('import ') and 'unittest' not in stripped:
                        insert_pos = i
                        break
                    elif stripped.startswith('"""'):
                        # Find the end of docstring and insert after it
                        for j in range(i, len(lines)):
                            if '"""' in lines[j] and j > i:
                                insert_pos = j + 1
                                break
                        break
            
            if insert_pos > 0:
                lines.insert(insert_pos, 'import pytest')
                content = '\n'.join(lines)
            else:
                content = 'import pytest\n\n' + content
        
        # Zapisz zmiany
        if content != original:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  [OK] Zmieniony")
            return True
        else:
            print(f"  [SKIP] Brak zmian")
            return False
            
    except Exception as e:
        print(f"  [ERROR] Blad: {e}")
        return False


# Lista plików testowych do konwersji
test_files = [
    "tests/integration/test_vertical_flow.py",
    "tests/integration/test_agent_concurrency.py",
    "SSI/tests/test_vertical_flow.py",
    "SSI/tests/test_paths.py",
    "SSI/tests/test_observability.py", 
    "SSI/tests/test_contracts.py",
    "SSI/tests/test_agent_concurrency.py",
    "SSI/v3/tests/test_world_integration.py",
    "SSI/v3/tests/test_v3_to_v4_bridge.py",
    "SSI/v3/tests/test_v3_integration.py",
    "SSI/v3/tests/test_memory_sync.py",
    "SSI/v3/tests/test_imports.py",
]

project_root = Path("D:/sts/aplikacjaTyperBetAi")

converted = 0
skipped = 0

for test_file in test_files:
    full_path = project_root / test_file
    if full_path.exists():
        if convert_file(full_path):
            converted += 1
        else:
            skipped += 1
    else:
        print(f"⚠️  Plik nie istnieje: {full_path}")
        skipped += 1

print(f"\n{'='*60}")
print(f"PODSUMOWANIE:")
print(f"{'='*60}")
print(f"Skonwertowane: {converted} pliki")
print(f"Pominięte: {skipped} pliki")