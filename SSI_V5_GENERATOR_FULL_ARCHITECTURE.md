# SSI V5 - GENERATOR TREND ANALYSIS - FULL ARCHITECTURE MAP

## Dokumentacja Architektury Systemu

**Data:** 2026-08-03  
**Status:** ZATWIERDZONA PO AUDYCIE CZESCI 1-4  
**Wersja:** 1.0 - Pełna mapa przed implementacją hooków

---

## 1. PRZEGLAD ARCHITEKTURY

### 1.1 Podział Systemu

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SSI V5 GENERATOR TREND ANALYSIS                       │
│                                                                          │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐  │
│  │    CZESC 1       │    │    CZESC 2      │    │    CZESC 3      │  │
│  │  Budowa Modeli   │───▶│  Predykcja &    │───▶│  Rdzen Poznawczy │  │
│  │  & Trening       │    │  Analiza Podst. │    │  (Teacher Engine)│  │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘  │
│                                                          │               │
│                                                          ▼               │
│                                                ┌─────────────────┐    │
│                                                │    CZESC 4      │    │
│                                                │  Analiza Oper.  │    │
│                                                │  & Laboratorium  │    │
│                                                └─────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.2 Dwa Główne Ekosystemy

| Ekosystem | Model Directory | Modele | Odpowiedzialnosc |
|----------|----------------|--------|-----------------|
| **Ekosystem A** | `modele_dataBase_futbol_trend\` | siec_08_log_koniec, siec_09_ratio_start, siec_10_ratio_koniec, siec_11_statystyka | Analiza trendow, zmiany kursow, zachowania przedmeczowe, predykcja na podstawie cech historycznych |
| **Ekosystem B** | `modele_kursy_przygotowane\` | siec_01_start_kursow, siec_02_koniec_kursow, siec_03_zmiana_kursow, siec_04_procent_kursow | Obserwacja ruchu kursow, analiza dynamiki, wykrywanie zmian |

---

## 2. SZCZEGOLOWA ARCHITEKTURA POSZCZEGOLNYCH CZESCI

---

### 2.1 CZESC 1 - BUDOWA MODELI & TRENING

**Plik:** `czesc1.py` (333,707 linii)

#### 2.1.1 Odpowiedzialnosc
- Budowanie struktur modeli sieci neuronowych
- Trening modeli na danych historycznych
- Generowanie plików `.h5` (modele Keras)
- Tworzenie metadanych modeli
- Definicja cech i klas

#### 2.1.2 Dane Wejsciowe
- `dane\dataBase_futbol_trend.csv` - dane trendów futbolowych
- `dane\kod_dataBase_futbol_trend.csv` - zakodowane dane z rezultatami
- `dane\kursy_przygotowane.csv` - dane kursów
- `dane\mozg_kursy_przygotowane.csv` - zakodowane dane kursów z rezultatami

#### 2.1.3 Dane Wyjsciowe
- `modele_dataBase_futbol_trend\<nazwa_sieci>\model.h5` - wytrenowane modele
- `modele_dataBase_futbol_trend\<nazwa_sieci>\metadata.json` - metadane modelu
- `modele_dataBase_futbol_trend\<nazwa_sieci>\klasy.json` - mapowanie klas
- `modele_kursy_przygotowane\<nazwa_sieci>\model.h5` - wytrenowane modele kursów
- `modele_kursy_przygotowane\<nazwa_sieci>\metadata.json` - metadane
- `modele_kursy_przygotowane\<nazwa_sieci>\klasy.json` - mapowanie klas

#### 2.1.4 Kluczowe Punkty START/STOP

| Typ | Lokalizacja | Opis |
|-----|-------------|------|
| **START** | Poczatek pliku | Definicja funkcji pomocniczych (normalize, bezpieczny_log, oblicz_cechy_*) |
| START | ~Linie 1000+ | Budowa modeli dla dataBase_futbol_trend |
| START | ~Linie 10000+ | Budowa modeli dla kursy_przygotowane |
| STOP | Koniec pliku | Zapis ostatniego modelu |

#### 2.1.5 Zidentyfikowane Modele (sieci)
- **Ekosystem A:** siec_08_log_koniec, siec_09_ratio_start, siec_10_ratio_koniec, siec_11_statystyka
- **Ekosystem B:** siec_01_start_kursow, siec_02_koniec_kursow, siec_03_zmiana_kursow, siec_04_procent_kursow

---

### 2.2 CZESC 2 - PREDYKCJA & ANALIZA PODSTAWOWA

**Plik:** `czesc2.py` (242,969 linii)

#### 2.2.1 Odpowiedzialnosc
- Ładowanie wytrenowanych modeli z Czesci 1
- Generowanie predykcji na nowych danych
- Przetwarzanie i analiza wyników predykcji
- Przygotowanie danych dla Czesci 3 i 4

#### 2.2.2 Dane Wejsciowe (z Czesci 1)
- Modele `.h5` z katalogów modeli
- Pliki `metadata.json`
- Pliki `klasy.json`
- Aktualne dane: `dataBase_futbol_trend.csv`, `kursy_przygotowane.csv`

#### 2.2.3 Dane Wyjsciowe
- Przetworzone predykcje (DataFrame)
- Analizy statystyczne predykcji
- Dane wejsciowe dla Czesci 3 (rd zen poznawczy)
- Dane wejsciowe dla Czesci 4 (analiza operacyjna)

#### 2.2.4 Kluczowe Funkcjonalnosci
- Ładowanie modeli Keras
- Predykcja na danych testowych
- Walidacja i normalizacja danych
- Agregacja wyników

---

### 2.3 CZESC 3 - RDZEN POZNAWCZY (Teacher Engine)

**Plik:** `czesc3.py` (271,976 linii)

#### 2.3.1 Odpowiedzialnosc
- **WorldHierarchyManager** - Zarządzanie hierarchią wiedzy
- **DynamicWeightsManager** - Dynamiczne wagowanie cech
- **CognitiveTeacher** - Nauczanie modelu na podstawie doświadczeń
- Generowanie zaawansowanej wiedzy dla modelu docelowego

#### 2.3.2 Dane Wejsciowe (z Czesci 2)
- Predykcje z modeli
- Historia meczów z wynikami
- Bledy predykcji

#### 2.3.3 Dane Wyjsciowe
| Plik | Opis | Uzycie |
|------|------|--------|
| `PAMIEC_MODEL_POZNAWCZY.json` | Pamięć poznawcza modelu | **NIE UZYWANY** w Czesc4 - do integracji |
| `WIEDZA_DLA_MODELU_DOCELOWEGO.json` | Wiedza dla modelu docelowego | **NIE UZYWANY** w Czesc4 - do integracji |
| `kolektor_wiedzy.json` | Zbiorcza wiedza poznawcza | **NIE UZYWANY** w Czesc4 - do integracji |

#### 2.3.4 Kluczowe Komponenty

```
CognitiveTeacher
├── WorldHierarchyManager
│   ├── Hierarchia wiedzy domenowej
│   ├── Klasyfikacja wydarzen
│   └── Powiazania miedzy encjami
│
├── DynamicWeightsManager
│   ├── Dynamiczna adaptacja wag cech
│   ├── Mechanizmy uczenia się
│   └── Optymalizacja parametrów
│
└── MemorySystem
    ├── Pamięć krótkotrwała
    ├── Pamięć długotrwała
    └── Mechanizmy zapisu/odczytu
```

#### 2.3.5 **WAZNE: Odkrycie Architekturalne**
Czesc3 generuje **oddzielny potok wiedzy poznawczej**, który **nie jest obecnie wykorzystywany** przez Czesc4.  
**To nie jest błąd** - to zaplanowana architektura, która wymaga przyszłej integracji.

---

### 2.4 CZESC 4 - ANALIZA OPERACYJNA & LABORATORIUM V2

**Plik:** `czesc4.py` (233,86 linii)

#### 2.4.1 Odpowiedzialnosc
- Operacyjna analiza predykcji
- Zarządzanie pamięcią obserwacji
- Generowanie wiedzy dla agentów (Laboratorium V2)
- System backupu pamięci (MemoryEngine)

#### 2.4.2 Dane Wejsciowe (z Czesci 1 i 2)
| Zrodlo | Plik | Opis |
|--------|------|------|
| Czesc1 | `modele_*/model.h5` | Modele do predykcji |
| Czesc1 | `modele_*/metadata.json` | Metadane modeli |
| Czesc1 | `modele_*/klasy.json` | Mapowanie klas |
| Czesc2 | `dataBase_futbol_trend.csv` | Aktualne dane do predykcji |
| Czesc2 | `kod_dataBase_futbol_trend.csv` | Historia meczów z wynikami |
| Czesc2 | `kursy_przygotowane.csv` | Aktualne dane kursów |
| Czesc2 | `mozg_kursy_przygotowane.csv` | Historia kursów z wynikami |

#### 2.4.3 Dane Wyjsciowe

**Pliki JSON:**
- `pamiec_obserwacji.json` - Historia obserwacji meczów
- `ocena.json` - Ocena modelu (skutecznosc, trafienia)
- `analiza_klas.json` - Analiza skutecznosci per klasa
- `analiza_pewnosci.json` - Analiza skutecznosci w 10 koszykach pewnosci
- `analiza_pewnosci_klasy.json` - Analiza pewnosci dla kazdej klasy
- `analiza_odchylen.json` - Analiza odchylen predykcji
- `analiza_pamieci.json` - Statystyki pamieci obserwacji
- `kolektor_wiedzy.json` - **AGREGACJA** wszystkich analiz

**Pliki CSV:**
- `predykcja_grupy.csv` - Aktualne predykcje
- `predykcja_z_wynikiem.csv` - Historia predykcji z wynikami
- `analiza_przyszlych_predykcji.csv` - Analiza przyszlych predykcji z wiedza historyczna

#### 2.4.4 Struktura Wewnetrzna

```
CZESC4.PY (23,386 linii)
├── Blok 1: GENERATOR ANALIZY TRENDOW + PAMIEC (siec_08_log_koniec)
│   ├── Konfiguracja
│   ├── Wczytanie modelu, klas, danych
│   ├── Predykcja historii i aktualnych meczów
│   ├── Aktualizacja pamięci i oceny
│   └── Zapis wyników
│
├── Blok 2: LABORATORIUM V2 (siec_08_log_koniec)
│   ├── Analiza klas
│   ├── Analiza pewnosci
│   ├── Analiza odchyleń
│   └── Kolektor wiedzy
│
├── Blok 3-4: Powtórzenie dla siec_09_ratio_start
├── Blok 5-6: Powtórzenie dla siec_10_ratio_koniec
├── Blok 7-8: Powtórzenie dla siec_11_statystyka
│
├── Blok 9-16: Powtórzenie dla Ekosystemu B (kursy_przygotowane)
│   ├── siec_01_start_kursow + Laboratorium
│   ├── siec_02_koniec_kursow + Laboratorium
│   ├── siec_03_zmiana_kursow + Laboratorium
│   └── siec_04_procent_kursow + Laboratorium
│
└── Blok 17-20: Ostatnie powtórzenia i MemoryEngine
    ├── dataBase_futbol_trend final
    ├── kursy_przygotowane final
    └── MemoryEngine (backup system)
```

#### 2.4.5 **WAZNE: Odkrycie Architekturalne**
Czesc4 **NIE KORZYSTA** z plików generowanych przez Czesc3.  
Obie czesci (3 i 4) dzialaja jako **oddzielne swiaty**:
- Czesc3: Potok poznawczy (Teacher Engine → Pamięć poznawcza)
- Czesc4: Potok operacyjny (Generator → Laboratorium V2 → Kolektor wiedzy)

---

## 3. PRZEPLYW DANYCH MIEDZY CZESCIAMI

```
┌─────────────────────────────────────────────────────────────────────┐
│                           PRZEPLYW DANYCH SSI V5                         │
└─────────────────────────────────────────────────────────────────────┘

     ┌──────────────┐         ┌──────────────┐         ┌──────────────┐
     │  CZESC 1     │         │  CZESC 2     │         │  CZESC 3     │
     │  Budowa      │────────▶│  Predykcja & │────────▶│  Rdzen        │
     │  Modeli      │  .h5    │  Analiza     │  df     │  Poznawczy   │
     │              │  .json  │  Podstawowa  │         │  (Teacher    │
     └──────────────┘         └──────────────┘         │   Engine)    │
           │                         │                    └──────┬──────┘
           │                         │                           │
           │                         ▼                           ▼
           │               ┌─────────────────────────────────────┐
           │               │                                      │
           └──────────────▶  CZESC 4                              │
                          │  Analiza Operacyjna &               │
                          │  Laboratorium V2                     │
                          │                                      │
                          └─────────────────────────────────────┘
                                    │
                                    ▼
                          ┌─────────────────────────────────────┐
                          │         tölt: Brak Integracji           │
                          │   Miedzy Czesc3 a Czesc4               │
                          └─────────────────────────────────────┘
```

### 3.1 Szczegółowy Przepływ

#### 3.1.1 Czesc1 → Czesc2
```
Czesc1 Output:
├── modele_dataBase_futbol_trend\<siec>\model.h5
├── modele_dataBase_futbol_trend\<siec>\metadata.json
├── modele_dataBase_futbol_trend\<siec>\klasy.json
├── modele_kursy_przygotowane\<siec>\model.h5
├── modele_kursy_przygotowane\<siec>\metadata.json
└── modele_kursy_przygotowane\<siec>\klasy.json

Czesc2 Input:
├── (wszystkie powyższe)
└── dane\*.csv (aktualne dane do predykcji)
```

#### 3.1.2 Czesc2 → Czesc3
```
Czesc2 Output:
├── Predykcje (DataFrame)
├── Historia meczów z wynikami
└── Bledy predykcji

Czesc3 Input:
└── (dane do uczenia się i generowania wiedzy poznawczej)
```

#### 3.1.3 Czesc2 → Czesc4
```
Czesc2 Output:
├── Predykcje (DataFrame)
└── Historia meczów/kursów z wynikami

Czesc4 Input:
├── (predykcje i historia)
└── modele z Czesc1 (do ładowania)
```

#### 3.1.4 Czesc3 → (Brak Polaczenia)
```
Czesc3 Output:
├── PAMIEC_MODEL_POZNAWCZY.json
├── WIEDZA_DLA_MODELU_DOCELOWEGO.json
└── kolektor_wiedzy.json

⚠️  NIE SĄ UZYWANE PRZEZ CZESC4!
    → Potrzeba przyszłej integracji
```

---

## 4. ZALEZNOSCI MIEDZY CZESCIAMI

### 4.1 Macierz Zaleznosci

| Zalezy od \ Zaleznosc | Czesc1 | Czesc2 | Czesc3 | Czesc4 |
|------------------------|--------|--------|--------|--------|
| **Czesc1** | - | ✅ | ❌ | ❌ |
| **Czesc2** | ✅ | - | ✅ | ✅ |
| **Czesc3** | ❌ | ✅ | - | ❌ |
| **Czesc4** | ✅ | ✅ | ❌ | - |

### 4.2 Objasnienie Zaleznosci

- **Czesc1 → Czesc2**: Czesc2 używa modeli wygenerowanych przez Czesc1
- **Czesc1 → Czesc4**: Czesc4 ładuje modele z Czesc1
- **Czesc2 → Czesc3**: Czesc3 używa danych predykcyjnych z Czesc2
- **Czesc2 → Czesc4**: Czesc4 używa danych predykcyjnych z Czesc2
- **Czesc3 → Czesc4**: ❌ **BRAK ZALEZNOSCI** (do naprawy w przyszłości)

---

## 5. POPULARNE MECZE - PRZYSZLY AUDYT

### 5.1 Hipoteza Architekturalna

```
Data Flow Hypothesis:

┌─────────────────┐     ┌──────────────────────────┐
│  dataBase_       │     │                          │
│  futbol_trend    │────▶│      FILTR                │
└─────────────────┘     │    POPULARNOSCI           │
                       └──────────┬──────────┘
                                  │
                                  ▼
                       ┌─────────────────┐
                       │  dataBase_       │
                       │  futbol_         │
                       │  popularne_     │
                       │  trend          │
                       └─────────────────┘

                       Ten sam silnik!
                       Inne dane wejsciowe!

┌─────────────────┐     ┌──────────────────────────┐
│  kursy_          │     │                          │
│  przygotowane    │────▶│      FILTR                │
└─────────────────┘     │    POPULARNOSCI           │
                       └──────────┬──────────┘
                                  │
                                  ▼
                       ┌─────────────────┐
                       │  kursy_          │
                       │  popularne_      │
                       │  przygotowane   │
                       └─────────────────┘
```

### 5.2 Do Sprawdzenia w Przyszlym Audycie

1. Czy istnieja pliki:
   - `dataBase_futbol_popularne_trend.csv`
   - `kod_dataBase_futbol_popularne_trend.csv`
   - `kursy_popularne_przygotowane.csv`
   - `mozg_kursy_popularne_przygotowane.csv`

2. Czy istnieja modele:
   - `modele_dataBase_futbol_popularne_trend\`
   - `modele_kursy_popularne_przygotowane\`

3. Czy jest to:
   - Ten sam generator + inny filtr danych wejściowych
   - Czy oddzielny system z wlasna logika

---

## 6. PUNKTY PRZYSZLYCH HOOKOW (PRZYGOTOWANIE)

### 6.1 Ogólna Filozofia

Hooki powinny byc dodawane **na poziomie calego generatora**, nie poszczegolnych czesci.  
Kazdy hook powinien miec:
- **Unikalna nazwe** (prefiks SSI_)
- **Dokumentacje** celu
- **Lokalizacje** w kodzie
- **Format danych** wejścia/wyjścia

### 6.2 Proponowane Typy Hooków

#### 6.2.1 Hooki Start/Stop
| Hook | Lokalizacja | Opis |
|------|-------------|------|
| `SSI_START_CZESC1` | Poczatek czesc1.py | Start budowy modeli |
| `SSI_STOP_CZESC1` | Koniec czesc1.py | Koniec budowy modeli |
| `SSI_START_CZESC2` | Poczatek czesc2.py | Start predykcji |
| `SSI_STOP_CZESC2` | Koniec czesc2.py | Koniec predykcji |
| `SSI_START_CZESC3` | Poczatek czesc3.py | Start rdzenia poznawczego |
| `SSI_STOP_CZESC3` | Koniec czesc3.py | Koniec rdzenia poznawczego |
| `SSI_START_CZESC4` | Poczatek czesc4.py | Start analizy operacyjnej |
| `SSI_STOP_CZESC4` | Koniec czesc4.py | Koniec analizy operacyjnej |

#### 6.2.2 Hooki Integracyjne (Miedzy Czesciami)
| Hook | Lokalizacja | Opis |
|------|-------------|------|
| `SSI_HOOK_C1_TO_C2` | Koniec Czesc1 / Poczatek Czesc2 | Przekazanie modeli |
| `SSI_HOOK_C2_TO_C3` | Koniec Czesc2 / Poczatek Czesc3 | Przekazanie predykcji |
| `SSI_HOOK_C2_TO_C4` | Koniec Czesc2 / Poczatek Czesc4 | Przekazanie predykcji |
| `SSI_HOOK_C3_TO_C4` | **BRAK** - Do dodania | Integracja wiedzy poznawczej |

#### 6.2.3 Hooki Analityczne (Czesc4)
| Hook | Lokalizacja | Opis |
|------|-------------|------|
| `SSI_HOOK_PREDICTION_START` | Czesc4, Linie ~326-350 | Przed predykcja historii |
| `SSI_HOOK_PREDICTION_CURRENT` | Czesc4, Linie ~357-384 | Przed predykcja aktualnych meczów |
| `SSI_HOOK_MEMORY_UPDATE` | Czesc4, Linie ~541-724 | Aktualizacja pamięci obserwacji |
| `SSI_HOOK_CLASS_ANALYSIS` | Czesc4, Linie ~1413-1538 | Analiza klas |
| `SSI_HOOK_CONFIDENCE_ANALYSIS` | Czesc4, Linie ~1543-1621 | Analiza pewności |
| `SSI_HOOK_KNOWLEDGE_COLLECTION` | Czesc4, Linie ~2072-2129 | Agregacja wiedzy |

#### 6.2.4 Hooki dla Agentów
| Hook | Opis | Format Wejścia | Format Wyjścia |
|------|------|----------------|-----------------|
| `SSI_AGENT_INPUT` | Wejście agenta | `AGENT_REQUEST` | - |
| `SSI_AGENT_OUTPUT` | Wyjście agenta | - | `AGENT_RESPONSE` |

### 6.3 Przykladowy Format AGENT_REQUEST

```json
{
  "agent_id": "AGENT_001",
  "model": "siec_03_zmiana_kursow",
  "akcja": "analiza",
  "ekosystem": "kursy_przygotowane",
  "zakres": "ostatnie_30_dni",
  "parametry": {
    "pewnosc_min": 0.7,
    "klasa": "wszystkie",
    "typ_analizy": "full"
  }
}
```

### 6.4 Przykladowy Format AGENT_RESPONSE

```json
{
  "agent_id": "AGENT_001",
  "request_id": "req_12345",
  "timestamp": "2026-08-03 14:30:00",
  "status": "success",
  "wynik": {
    "predykcja": {
      "id_meczu": "MECZ_001",
      "wynik": "1",
      "pewnosc": 0.85
    },
    "reguly": [
      {
        "typ": "trend",
        "wartosc": "rosnacy",
        "waga": 0.6
      },
      {
        "typ": "pewnosc",
        "wartosc": "wysoka",
        "waga": 0.4
      }
    ],
    "pamiec": {
      "ilosc_obserwacji": 100,
      "skutecznosc": 0.75
    },
    "analiza": {
      "klasa": "1",
      "skutecznosc_klasy": 0.80,
      "odchylenie": "normalne"
    }
  }
}
```

---

## 7. PODSUMOWANIE I REKOMENDACJE

### 7.1 Potwierdzone Fakty

✅ **Dwa ekosystemy modeli** potwierdzone i działające
✅ **Przepływ danych** między Czesciami 1→2→3 i 1→2→4 potwierdzony
✅ **Czesc3 i Czesc4** to oddzielne swiaty (nie blad, ale zaplanowana architektura)
✅ **Hooki** zidentyfikowane, ale nie zaimplementowane
✅ **Popularne mecze** - hipoteza: ten sam silnik + inny filtr

### 7.2 Do Zrobienia (Kolejnosc)

#### ETAP A - Zamkniecie Dokumentacji ✅ (TRWA)
- [x] SSI_V5_CZESC1_HOOK_MAP.md
- [x] SSI_V5_CZESC2_HOOK_MAP.md
- [x] SSI_V5_CZESC3_HOOK_MAP.md
- [x] SSI_V5_CZESC4_HOOK_MAP.md
- [x] **SSI_V5_GENERATOR_FULL_ARCHITECTURE.md** ← **TEN DOKUMENT**

#### ETAP B - Projekt Hooków (NASTEPNY)
- [ ] SSI_V5_HOOK_ARCHITECTURE.md (projekt wszystkich hooków)
- [ ] Decyzja o lokalizacjach hooków
- [ ] Formaty danych wejścia/wyjścia
- [ ] Mechanizmy kontroli i bezpieczeństwa

#### ETAP C - Integracja (PRZYSZLA)
- [ ] Połaczenie Czesci 3 i 4 (most miedzy wiedza poznawcza a operacyjna)
- [ ] Implementacja hooków w kodzie
- [ ] Testy integracyjne
- [ ] Refaktoryzacja (usuniecie duplikacji kodu)

#### ETAP D - Audyt Popularnych Meczów (PRZYSZLY)
- [ ] Sprawdzenie czy istnieja pliki popularne_*
- [ ] Decyzja: filtr vs. oddzielny system
- [ ] Ewentualna integracja

### 7.3 Krytyczne Uwagi

1. **Brak Integracji Czesci 3 i 4**: Obie czesci generuja wiedze, ale nie dziela sie nia.  
   → **Priorytet**: Zaprojektowac warstwe integracyjna

2. **Duplikacja Kodu w Czesc4**: 10 identycznych bloków (Generator + Laboratorium).  
   → **Rekomendacja**: Refaktoryzacja w przyszłej wersji

3. **Popularne Mecze**: Nie potwierdzone.  
   → **Rekomendacja**: Oddzielny audyt

4. **Hooki**: Nie dodawac do kodu az wszystkie mapy BedA zatwierdzone.  
   → **Rekomendacja**: Najpierw jeden wspolny projekt

---

## 8. HISTORIA DOKUMENTU

| Data | Wersja | Autor | Opis |
|------|--------|-------|------|
| 2026-08-03 | 1.0 | Mistral Vibe | Pełna mapa architektury po audycie Czesci 1-4 |

---

**Status:** Oczekuje na zatwierdzenie i decyzje o kolejnym etapie (ETAP B - Projekt Hooków)
