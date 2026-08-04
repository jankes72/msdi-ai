# SSI V5 - CZESC4 HOOK MAP

## Przeglad Architektur

`czesc4.py` jest **czwarta i ostatnia czescia** jednolitego generatora SSI V5. Zawiera **10 zagniezdzonych systemow** რ preto jest **powtorzeniem wzorca** z czesci 1-3, ale z rozszerszona analityka i laboratorium wiedzy.

---

## Potwierdzone Ekosystemy

### 1. DWA GLOWNE EKOSYSTEMY MODELI

| Ekosystem | Model Directory | Data Files | Status |
|----------|----------------|------------|--------|
| **dataBase_futbol_trend** | `modele_dataBase_futbol_trend\` | `dataBase_futbol_trend.csv`, `kod_dataBase_futbol_trend.csv` | **POTWIERDZONY** |
| **kursy_przygotowane** | `modele_kursy_przygotowane\` | `kursy_przygotowane.csv`, `mozg_kursy_przygotowane.csv` | **POTWIERDZONY** |

> **WAZNE**: Nie znaleziono referencji do `dataBase_futbol_popularne_trend` ani `kursy_popularne_przygotowane`. 
> **Do audytu**: Czy popularne mecze sa filtrem na danych wejsciowych, czy oddzielnym systemem.

---

## Struktura Czesc4.py

### Podzial na Sekcje (10 zagniezdzonych blokow)

```
CZESC4.PY (23,386 linii)
├── Blok 1: GENERATOR ANALIZY TRENDOW + PAMIEC OBSERWACJI CZESC 1/2 (linie 1-1169)
│   ├── KONFIGURACJA (modele_dataBase_futbol_trend\siec_08_log_koniec)
│   ├── WCZYTANIE METADANYCH MODELU
│   ├── WCZYTANIE KLAS
│   ├── WCZYTANIE AKTUALNEJ PREDYKCJI (dataBase_futbol_trend.csv)
│   ├── WCZYTANIE HISTORII Z WYNIKAMI (kod_dataBase_futbol_trend.csv)
│   ├── WCZYTANIE MODELU (model.h5)
│   ├── PREDYKCJA HISTORII
│   ├── PREDYKCJA AKTUALNYCH MECZOW
│   ├── WCZYTANIE PAMIECI (pamiec_obserwacji.json)
│   ├── WCZYTANIE OCENY (ocena.json)
│   ├── ANALIZA HISTORII Z WYNIKAMI
│   │   └── Aktualizacja pamieci meczow z wynikami
│   ├── AKTUALNE MECZE BEZ WYNIKU
│   │   └── Generowanie nowych predykcji
│   ├── AKTUALIZACJA OCENY MODELU
│   ├── ZAPIS PAMIECI (pamiec_obserwacji.json)
│   ├── ZAPIS OCENY (ocena.json)
│   └── ZAPIS AKTUALNEJ PREDYKCJI (predykcja_grupy.csv)
│
├── Blok 2: LABORATORIUM V2 - ANALIZA PAMIECI (linie 1171-2270)
│   ├── KONFIGURACJA (modele_dataBase_futbol_trend)
│   ├── WCZYTANIE KLAS
│   ├── WCZYTANIE HISTORII Z WYNIKAMI (predykcja_z_wynikiem.csv)
│   ├── WCZYTANIE AKTUALNYCH PREDYKCJI (predykcja_grupy.csv)
│   ├── WCZYTANIE OCENY MODELU
│   ├── WCZYTANIE PAMIECI OBSERWACJI
│   ├── ANALIZA KLAS (skutecznosc per klasa)
│   ├── ANALIZA PEWNOSCI DYNAMICZNA (10 koszykow)
│   ├── ANALIZA PEWNOSCI DLA KAZDEJ KLASY
│   ├── ANALIZA ODCHYLEN (co siec typowala vs co wyszlo)
│   ├── ANALIZA PAMIECI OBSERWACJI
│   ├── ANALIZA AKTUALNYCH PREDYKCJI
│   ├── KOLEKTOR WIEDZY (aggregation)
│   └── ZAPIS JSON (6 plikow: analiza_klas.json, analiza_pewnosci.json, itd.)
│
├── Blok 3: GENERATOR ANALIZY TRENDOW CZESC 1/2 - siec_09_ratio_start (linie 2275-3386)
│   └── **IDENTYCZNA STRUKTURA** do Bloku 1, ale inny model
│
├── Blok 4: LABORATORIUM V2 - siec_09_ratio_start (linie 3387-4489)
│   └── **IDENTYCZNA STRUKTURA** do Bloku 2, ale inny model
│
├── Blok 5: GENERATOR ANALIZY TRENDOW CZESC 1/2 - siec_10_ratio_koniec (linie 4490-5657)
│   └── **IDENTYCZNA STRUKTURA** do Bloku 1
│
├── Blok 6: LABORATORIUM V2 - siec_10_ratio_koniec (linie 5658-6760)
│   └── **IDENTYCZNA STRUKTURA** do Bloku 2
│
├── Blok 7: GENERATOR ANALIZY TRENDOW CZESC 1/2 - siec_11_statystyka (linie 6761-7928)
│   └── **IDENTYCZNA STRUKTURA** do Bloku 1
│
├── Blok 8: LABORATORIUM V2 - siec_11_statystyka (linie 7929-9031)
│   └── **IDENTYCZNA STRUKTURA** do Bloku 2
│
├── Blok 9: GENERATOR ANALIZY TRENDOW + PAMIEC - kursy_przygotowane (linie 9032-17048)
│   ├── siec_01_start_kursow (linie 9140-10229)
│   ├── LABORATORIUM V2 - siec_01_start_kursow (linie 10230-11332)
│   ├── siec_02_koniec_kursow (linie 11333-12502)
│   ├── LABORATORIUM V2 - siec_02_koniec_kursow (linie 12503-13605)
│   ├── siec_03_zmiana_kursow (linie 13606-14775)
│   └── LABORATORIUM V2 - siec_03_zmiana_kursow (linie 14776-15878)
│
├── Blok 10: GENERATOR ANALIZY TRENDOW - dataBase_futbol_trend final (linie 17049-20420)
│   ├── dataBase_futbol_trend (linie 18228-19317)
│   └── LABORATORIUM V2 - dataBase_futbol_trend (linie 19318-20420)
│
├── Blok 11: GENERATOR ANALIZY TRENDOW - kursy_przygotowane final (linie 20421-21588)
│   ├── kursy_przygotowane (linie 20499-21588)
│   └── LABORATORIUM V2 - kursy_przygotowane
│
└── Blok 12: MemoryEngine - Backup System (linie 22746-23386)
    ├── ROOTS: [modele_dataBase_futbol_trend, modele_kursy_przygotowane]
    ├── BACKUP_DIR: memory_backup
    └── Funkcje: create_backup(), restore_backup()
```

---

## Zaleznosci Miedzy Czesciami

### Dane Wejsciowe z Czesc1
- **modele .h5**: Wczytywane z `KATALOG_MODELU/model.h5`
- **metadata.json**: Zawiera `cechy` i `nazwa` modelu
- **klasy.json**: Mapowanie ID klasy na wyniki

### Dane Wejsciowe z Czesc2
- **dataBase_futbol_trend.csv**: Aktualne dane do predykcji
- **kod_dataBase_futbol_trend.csv**: Historia meczow z wynikami
- **kursy_przygotowane.csv**: Aktualne dane kursow
- **mozg_kursy_przygotowane.csv**: Historia kursow z wynikami

### Dane Wejsciowe z Czesc3
- **PAMIEC_MODEL_POZNAWCZY.json**: **NIE ZNALEZIONO** referencji w czesc4.py
- **WIEDZA_DLA_MODELU_DOCELOWEGO.json**: **NIE ZNALEZIONO** referencji w czesc4.py
- **kolektor_wiedzy.json**: **GENEROWANY** w Bloku 2,4,6,8,10,11 (Laboratorium V2)

> **UWAGA**: Czesc4 **NIE KORZYSTA** z plikow generowanych przez Czesc3 (rdzen poznawczy). 
> Mozliwe, ze Czesc3 jest **oddzielnym potokiem wiedzy**, a Czesc4 to **potok operacyjny**.

---

## punkty Wejścia (START)

### Glowne Punkty Startu

| Lp. | Lokalizacja | Model | Opis |
|-----|-------------|-------|------|
| 1 | Linie 1-20 | - | Importy i funkcje pomocnicze |
| 2 | **Linie 21-73** | **GENERATOR 1/2** | KONFIGURACJA: siec_08_log_koniec (dataBase_futbol_trend) |
| 3 | Linie 79-96 | **GENERATOR 1/2** | WCZYTANIE METADANYCH MODELU |
| 4 | Linie 108-125 | **GENERATOR 1/2** | WCZYTANIE KLAS |
| 5 | Linie 141-153 | **GENERATOR 1/2** | WCZYTANIE AKTUALNEJ PREDYKCJI |
| 6 | Linie 258-272 | **GENERATOR 1/2** | WCZYTANIE HISTORII Z WYNIKAMI |
| 7 | Linie 305-319 | **GENERATOR 1/2** | WCZYTANIE MODELU |
| 8 | **Linie 326-350** | **GENERATOR 1/2** | **PREDYKCJA HISTORII (START ANALIZY)** |
| 9 | **Linie 357-384** | **GENERATOR 1/2** | **PREDYKCJA AKTUALNYCH MECZOW** |
| 10 | **Linie 1171-1183** | **LABORATORIUM V2** | KONFIGURACJA (dataBase_futbol_trend) |
| 11 | **Linie 2275-2291** | **GENERATOR 2/2** | KONFIGURACJA: siec_09_ratio_start |
| 12 | **Linie 9140-9154** | **GENERATOR KURSY** | KONFIGURACJA: siec_01_start_kursow (kursy_przygotowane) |
| 13 | **Linie 22746-22767** | **MemoryEngine** | System backupu pamieci |

---

## Punkty Wyjścia (STOP)

### Glowne Punkty Konca

| Lp. | Lokalizacja | Plik Wyjsciowy | Opis |
|-----|-------------|----------------|------|
| 1 | **Linie 922-979** | `pamiec_obserwacji.json` | Zapis pamieci obserwacji |
| 2 | **Linie 954-979** | `ocena.json` | Zapis oceny modelu |
| 3 | **Linie 988-1016** | `predykcja_grupy.csv` | Zapis aktualnej predykcji |
| 4 | **Linie 1025-1103** | `predykcja_z_wynikiem.csv` | Zapis historii z wynikami |
| 5 | **Linie 1111-1137** | - | **ZAKONCZENIE Bloku 1 (linia 1115)** |
| 6 | **Linie 2135-2206** | 6x JSON files | Zapis analiz Laboratorium V2 |
| 7 | **Linie 2211-2268** | - | **ZAKONCZENIE Bloku 2 (linia 2218)** |
| 8 | Linie 3386 | - | ZAKONCZENIE Bloku 3 |
| 9 | Linie 4489 | - | ZAKONCZENIE Bloku 4 |
| 10 | Linie 5657 | - | ZAKONCZENIE Bloku 5 |
| 11 | Linie 6760 | - | ZAKONCZENIE Bloku 6 |
| 12 | Linie 7928 | - | ZAKONCZENIE Bloku 7 |
| 13 | Linie 9031 | - | ZAKONCZENIE Bloku 8 |
| 14 | Linie 10229 | - | ZAKONCZENIE Bloku 9 (kursy_przygotowane) |
| 15 | Linie 11332 | - | ZAKONCZENIE Bloku 10 |
| 16 | Linie 12502 | - | ZAKONCZENIE Bloku 11 |
| 17 | Linie 13605 | - | ZAKONCZENIE Bloku 12 |
| 18 | Linie 14775 | - | ZAKONCZENIE Bloku 13 |
| 19 | Linie 15878 | - | ZAKONCZENIE Bloku 14 |
| 20 | Linie 17048 | - | ZAKONCZENIE Bloku 15 |
| 21 | Linie 18151 | - | ZAKONCZENIE Bloku 16 |
| 22 | Linie 19317 | - | ZAKONCZENIE Bloku 17 |
| 23 | Linie 20420 | - | ZAKONCZENIE Bloku 18 |
| 24 | Linie 21588 | - | ZAKONCZENIE Bloku 19 |
| 25 | **Linie 22691** | - | **ZAKONCZENIE Bloku 20 (Laboratorium V2 finalne)** |

---

## Kolejnosc Wykonania

```
1. GENERATOR ANALIZY TRENDOW + PAMIEC OBSERWACJI (siec_08_log_koniec)
   ├─ Wczytanie modelu, klas, predykcji, historii
   ├─ Predykcja historii i aktualnych meczow
   ├─ Aktualizacja pamieci i oceny
   └─ Zapis: pamiec_obserwacji.json, ocena.json, predykcja_grupy.csv, predykcja_z_wynikiem.csv

2. LABORATORIUM V2 (siec_08_log_koniec)
   ├─ Analiza klas, pewnosci, odchylen
   ├─ Kolektor wiedzy
   └─ Zapis: 6x JSON (analiza_klas.json, analiza_pewnosci.json, itd.)

3. GENERATOR ANALIZY TRENDOW (siec_09_ratio_start)
   └─ Powtorzenie krokow 1-2 dla innego modelu

4. LABORATORIUM V2 (siec_09_ratio_start)
   └─ Powtorzenie analizy

5. GENERATOR ANALIZY TRENDOW (siec_10_ratio_koniec)
   └─ Powtorzenie

6. LABORATORIUM V2 (siec_10_ratio_koniec)
   └─ Powtorzenie

7. GENERATOR ANALIZY TRENDOW (siec_11_statystyka)
   └─ Powtorzenie

8. LABORATORIUM V2 (siec_11_statystyka)
   └─ Powtorzenie

9. GENERATOR ANALIZY TRENDOW (kursy_przygotowane - 4 modele)
   ├─ siec_01_start_kursow
   ├─ siec_02_koniec_kursow
   ├─ siec_03_zmiana_kursow
   └─ siec_04_procent_kursow
   each with LABORATORIUM V2

10. MemoryEngine
    └─ Backup system for memory files
```

---

## Pliki Generowane przez Czesc4

### Pliki JSON
- `pamiec_obserwacji.json` - Historia obserwacji meczow
- `ocena.json` - Ocena modelu (skutecznosc, trafienia)
- `analiza_klas.json` - Analiza skutecznosci per klasa
- `analiza_pewnosci.json` - Analiza skutecznosci w 10 koszykach pewnosci
- `analiza_pewnosci_klasy.json` - Analiza pewnosci dla kazdej klasy
- `analiza_odchylen.json` - Analiza odchylen predykcji
- `analiza_pamieci.json` - Statystyki pamieci obserwacji
- `kolektor_wiedzy.json` - **AGREGACJA** wszystkich analiz

### Pliki CSV
- `predykcja_grupy.csv` - Aktualne predykcje
- `predykcja_z_wynikiem.csv` - Historia predykcji z wynikami
- `analiza_przyszlych_predykcji.csv` - Analiza przyszlych predykcji z wiedza historyczna

---

## Mechanizmy Kontroli (Istniejące)

### 1. Sprawdzanie Istnienia Plików
```python
if os.path.exists(PLIK_PAMIEC):
    with open(PLIK_PAMIEC) as f:
        pamiec_obserwacji = json.load(f)
else:
    pamiec_obserwacji = {}
```

### 2. Walidacja Cech Modelu
```python
for cecha in CECHY:
    if cecha not in INDEX_MAP:
        raise Exception(f"Brak cechy modelu: {cecha}")
```

### 3. Obsluga Bledow Predykcji
```python
if trafienie:
    analiza[pred_wynik]["trafienia"] += 1
else:
    if real_wynik not in analiza[pred_wynik]["bledy"]:
        analiza[pred_wynik]["bledy"][real_wynik] = 0
    analiza[pred_wynik]["bledy"][real_wynik] += 1
```

### 4. System Backupu (MemoryEngine)
- Tworzy kopie zapasowe plikow JSON
- Moze восстанавливать dane z backupu
- Obsluguje obie bazy modeli

---

## Potencjalne Miejsca dla Agentow SSI

### 1. Punkty Decyzyjne (HOOK_START)

| Lokalizacja | Typ Hooka | Opis |
|-------------|-----------|------|
| **Linie 326-350** | `HOOK_PREDICTION_START` | Przed predykcja historii - moze modyfikowac dane wejsciowe |
| **Linie 357-384** | `HOOK_PREDICTION_CURRENT` | Przed predykcja aktualnych meczow |
| **Linie 541-724** | `HOOK_OBSERVATION_UPDATE` | Przy aktualizacji pamieci meczow z wynikami |
| **Linie 736-790** | `HOOK_NEW_PREDICTION` | Przy generowaniu nowych predykcji bez wynikow |
| **Linie 813-913** | `HOOK_EVALUATION_UPDATE` | Przy aktualizacji oceny modelu |

### 2. Punkty Monitorujące (HOOK_MONITOR)

| Lokalizacja | Typ Hooka | Opis |
|-------------|-----------|------|
| **Linie 624-686** | `HOOK_MEMORY_CHANGE` | Monitorowanie zmian w pamieci meczu (zmiana predykcji/pewnosci) |
| **Linie 922-979** | `HOOK_SAVE_MEMORY` | Przed zapisaniem pamieci |
| **Linie 954-979** | `HOOK_SAVE_EVALUATION` | Przed zapisaniem oceny |

### 3. Punkty Analityczne (HOOK_ANALYSIS)

| Lokalizacja | Typ Hooka | Opis |
|-------------|-----------|------|
| **Linie 1413-1538** | `HOOK_CLASS_ANALYSIS` | Analiza klas - moze dodawac wlasne metryki |
| **Linie 1543-1621** | `HOOK_CONFIDENCE_ANALYSIS` | Analiza pewnosci - moze modyfikowac koszyki |
| **Linie 1626-1742** | `HOOK_CLASS_CONFIDENCE` | Analiza pewnosci per klasa |
| **Linie 1755-1835** | `HOOK_DEVIATION_ANALYSIS` | Analiza odchylen predykcji |
| **Linie 1841-1887** | `HOOK_MEMORY_STATS` | Analiza statystyk pamieci |

### 4. Punkty Agregacji Wiedzy (HOOK_KNOWLEDGE)

| Lokalizacja | Typ Hooka | Opis |
|-------------|-----------|------|
| **Linie 2072-2129** | `HOOK_KNOWLEDGE_COLLECTION` | Przed utworzeniem kolektora wiedzy - moze dodawac wlasne analityki |
| **Linie 2134-2206** | `HOOK_KNOWLEDGE_SAVE` | Przed zapisaniem plikow JSON |

### 5. Punkty Integracji z Czesc3 (HOOK_INTEGRATION)

> **UWAGA**: Obecnie **BRAK** integracji z Czesc3 (rdzen poznawczy). 
> **Potencjalne miejsca**:
> - Przed predykcja (linie 326-350) - wczytanie PAMIEC_MODEL_POZNAWCZY.json
> - Przed analiza klas (linie 1413) - wczytanie WIEDZA_DLA_MODELU_DOCELOWEGO.json
> - Przed agregacja wiedzy (linie 2072) - polaczenie z kolektor_wiedzy.json z Czesc3

---

## Podsumowanie Architektury

### Co jest Potwierdzone
1. ✅ Czesc4 **NIE JEST** osobnym systemem - to kontynuacja generatora
2. ✅ Obsluguje **DWA EKOSYSTEMY**: dataBase_futbol_trend i kursy_przygotowane
3. ✅ **NIE ZNALEZIONO** referencji do wersji popularnych (dataBase_futbol_popularne_trend, kursy_popularne_przygotowane)
4. ✅ Generuje **pamiec obserwacji** (pamiec_obserwacji.json)
5. ✅ Generuje **dane dla agentow** (kolektor_wiedzy.json, analiza_przyszlych_predykcji.csv)
6. ✅ Ma **wlasne punkty START/STOP** (20 zagniezdzonych blokow)
7. ✅ Ma **istniejące mechanizmy kontroli** (sprawdzanie plikow, walidacja cech, backup)

### Co Wymaga Audytu
1. ❓ Czy popularne mecze sa filtrem na danych wejsciowych, czy oddzielnym systemem
2. ❓ Integracja z Czesc3 (rdzen poznawczy) - obecnie **BRAK** referencji
3. ❓ Czy kolektor_wiedzy.json z Czesc4 powinien byc polaczony zWIEDZA_DLA_MODELU_DOCELOWEGO.json z Czesc3

### Rekomendacje dla Hookow
1. **Nie dodawac hookow** az wszystkie 4 mapy (czesc1-4) beda zatwierdzone
2. **Hooki powinny byc** na poziomie calego generatora, nie poszczegolnych blokow
3. **Priorytetowe miejsca**:
   - Przed predykcja (linie 326-350)
   - Przed analiza (linie 1413)
   - Przed agregacja wiedzy (linie 2072)
   - Przed zapisaniem pamieci (linie 922)

---

## Coalogicznosc z Innymi Czesciami

| Element | Czesc1 | Czesc2 | Czesc3 | Czesc4 |
|---------|--------|--------|--------|--------|
| Budowanie modeli | ✅ | ❌ | ❌ | ❌ |
| Tبريng modeli | ✅ | ❌ | ❌ | ❌ |
| Generowanie .h5 | ✅ | ❌ | ❌ | ❌ |
| Ladowanie modeli | ❌ | ✅ | ✅ | ✅ |
| Predykcje | ❌ | ✅ | ❌ | ✅ |
| Rdzen Poznawczy | ❌ | ❌ | ✅ | ❌ |
| Pamiec Obserwacji | ❌ | ❌ | ❌ | ✅ |
| Laboratorium | ❌ | ❌ | ❌ | ✅ |
| Kolektor Wiedzy | ❌ | ❌ | ✅ | ✅ |

---

## Wniosek

`czesc4.py` to **finalny etap** potoku SSI V5, odpowiedzialny za:
1. **Operacyjna analize** predykcji na podstawie modeli z Czesc1
2. **Zarządanie pamięcią** obserwacji i ocen
3. **Generowanie wiedzy** dla agentów (Laboratorium V2)
4. **Backup** systemu pamieci

**Brak integracji z Czesc3 (rdzen poznawczy) wskazuje na potrzebę polaczenia obu potokow w przyszlosci.**

---

*Raport wygenerowany na podstawie analizy czesc4.py (23,386 linii)*
*Data: 2026-08-03*
