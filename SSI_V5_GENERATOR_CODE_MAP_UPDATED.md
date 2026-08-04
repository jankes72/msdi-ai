# SSI_V5_GENERATOR_CODE_MAP.md

## Mapa Kodu Generatora SSI V5 - Konsolidacja czesc1-4.py

**Data:** 2026-08-03  
**Status:** ✅ **CZESC1.PY ZAKOŃCZONA** | ✅ **CZESC2.PY ZAKOŃCZONA**  
**Wersja:** 3.0  
**Cel:** Dokumentacja struktur kodu przed konsolidacja do SSI_V5_SPORTS_WORLD_MODEL_GENERATOR.py

---

## 🎯 **STATUS ANALIZY**
| Plik | Linie ogółem | Linie zanalizowane | % Analizy | Status |
|------|--------------|-------------------|-----------|--------|
| czesc1.py | 4,819+ | 1-4819+ | 100% | ✅ **ZAKOŃCZONA** |
| czesc2.py | 19,718 | 1-19718 | 100% | ✅ **ZAKOŃCZONA** |
| czesc3.py | ? | ? | 0% | ⏳ **OCZEKUJE** |
| czesc4.py | 23,386 | 1-1048 | ~4.5% | ⏳ **OCZEKUJE** |

---

## 🔚 **PODSUMOWANIE ARCHITEKTURY**

### **Odkryte Komponenty SSI V5:**
1. **WorldHierarchyManager** (czesc3.py:1082-1276) - Zarządza hierarchiczną pamięcią światów
2. **DynamicWeightsManager** (czesc3.py:1282-1367) - Dynamiczne wagi świata i klas
3. **CognitiveTeacher** (czesc3.py:1373+) - Model poznawczy, używa komponentów 1 i 2

### **Podział czesc3.py:**
- **Część 3A** (linie 1-979): Budowa sieci neuronowych na dane/kursy_przygotowane.csv
- **Część 3B** (linie 989+): System WORLD z WorldHierarchyManager, DynamicWeightsManager, CognitiveTeacher

### **Wejścia Wyjścia czesc3.py:**
- **Część 3A:** dane/kursy_przygotowane.csv + dane/mozg_kursy_przygotowane.csv -> modele_kursy_przygotowane/
- **Część 3B:** dane/dataBase_futbol_trend.csv + dane/kod_dataBase_futbol_trend.csv -> modele_dataBase_futbol_trend/

---

## ⚠️ **WAŻNE UWAGI O DUPLIKACJI KODU W CZESC2.PY**

### **📊 Statystyki Duplikacji**
| Metryka | Wartość | % Pliku |
|---------|---------|---------|
| **Liczba modeli obsługiwanych** | 4 | - |
| **Długość jednego bloku GŁÓWNA CZĘŚĆ** | ~1,166 linii | - |
| **Długość jednego LABORATORIUM V2** | ~1,037 linii | - |
| **Całkowita długość 4 bloków** | ~16,850 linii | 85.5% |
| **Linie unikalne** | ~2,868 linii | 14.5% |
| **Całkowita duplikacja** | **~14,850 linii** | **75%** |

### **🔍 Wzorzec Powtarzania w czesc2.py**
Plik **czesc2.py (19,718 linii)** składa się z **4 identycznych bloków** dla 4 modeli:
```
czesc2.py
├── [1-2208]       BLOK 1: siec_08_log_koniec
│   ├── [1-1170]     GŁÓWNA CZĘŚĆ (1/2 + 2/2)
│   └── [1172-2208]  LABORATORIUM V2 (Fragment 1/2 + 2/2)
│
├── [2276-4480]    BLOK 2: siec_09_ratio_start
│   ├── [2276-3442]  GŁÓWNA CZĘŚĆ (1/2 + 2/2)
│   └── [3443-4480]  LABORATORIUM V2 (Fragment 1/2 + 2/2)
│
├── [4547-6752]    BLOK 3: siec_10_ratio_koniec
│   ├── [4547-5712]  GŁÓWNA CZĘŚĆ (1/2 + 2/2)
│   └── [5713-6752]  LABORATORIUM V2 (Fragment 1/2 + 2/2)
│
└── [6818-19718]  BLOK 4: siec_11_statystyka
    ├── [6818-7983]  GŁÓWNA CZĘŚĆ (1/2 + 2/2)
    └── [7984-19718] LABORATORIUM V2 (Fragment 1/2 + 2/2)
```

### **📌 Lista Modeli Obsługiwanych przez czesc2.py**
| Lp. | Model | GŁÓWNA CZĘŚĆ | LABORATORIUM V2 | Zakres linii | Długość |
|-----|-----------|------------------|---------------------|------------------|-------------|
| 1 | **siec_08_log_koniec** | 1-1170 | 1172-2208 | 1-2208 | 2208 linii |
| 2 | **siec_09_ratio_start** | 2276-3442 | 3443-4480 | 2276-4480 | 2205 linii |
| 3 | **siec_10_ratio_koniec** | 4547-5712 | 5713-6752 | 4547-6752 | 2206 linii |
| 4 | **siec_11_statystyka** | 6818-7983 | 7984-19718 | 6818-19718 | **12,901 linii** |

---

## 📁 **LEGENDA**

| Kolumna | Opis |
|--------|------|
| **Sekcja** | Logiczna część kodu |
| **Źródło** | Plik źródłowy (czesc1-4.py) |
| **Linie** | Zakres linii w pliku źródłowym |
| **Funkcje/Klasy** | Główne elementy kodu |
| **Wejście** | Dane wejściowe |
| **Wyjście** | Dane wyjściowe |
| **Użytkownicy** | Kto korzysta z tych danych |
| **Zależności** | Zależności od innych sekcji |
| **Duplikat** | Czy sekcja jest powtórzeniem (✅/❌) |

---

## 🔹 **CZESC1.PY - ANALIZA**

---

### **SEKCJA 1.A: Globalne Struktury SSI V5**
| Sekcja | 1.A | Źródło | czesc1.py | Linie | 1-228 |
|---|---|---|---|---|---|
| **Funkcje/Klasy** | SSI_STAGE_STATUS, SSI_AGENT_INPUT, SSI_AGENT_OUTPUT, SSI_EVENTS, update_stage_status, register_agent_input, export_agent_output, SSI_EVENT, SSI_START_NETWORK_BUILD, SSI_START_TRAINING, SSI_END_TRAINING, SSI_OUTPUT_READY, SSI_NETWORK_FINISH, SSI_MAIN_LOOP_START, SSI_MAIN_LOOP_END |
| **Wejście** | - | **Wyjście** | SSI_STAGE_STATUS, SSI_AGENT_INPUT, SSI_AGENT_OUTPUT, SSI_EVENTS |
| **Użytkownicy** | Cały system SSI V5 | **Zależności** | - |
| **Duplikat** | ❌ |

**Opis:**
Globalne struktury dla agentów SSI V5:
- `SSI_STAGE_STATUS` (dict): Rejestr statusu procesu
- `SSI_AGENT_INPUT` (dict): Punkty wejścia dla agentów
- `SSI_AGENT_OUTPUT` (dict): Punkty wyjścia dla agentów
- `SSI_EVENTS` (list): Lista zdarzeń systemowych

Funkcje zarządzania stanem:
- `update_stage_status(stage, status, timestamp)`
- `register_agent_input(data_type, data)`
- `export_agent_output(data_type, data)`

Hooki zdarzeń (Event Logging):
- `SSI_EVENT(event, network, stage, status, data)`
- `SSI_START_NETWORK_BUILD(network, features)`
- `SSI_START_TRAINING(network, X_train_shape, y_train_shape, X_val_shape, epochs, batch_size)`
- `SSI_END_TRAINING(network, accuracy, loss, val_accuracy, val_loss, duration)`
- `SSI_OUTPUT_READY(network, catalog, file_list, model_accuracy)`
- `SSI_NETWORK_FINISH(network)`
- `SSI_MAIN_LOOP_START(total_networks)`
- `SSI_MAIN_LOOP_END(completed_networks, skipped_networks)`

**Zależności:**
- Importy: csv, math, statistics, os, sys, time, datetime
- CSV config: csv.field_size_limit(sys.maxsize)
