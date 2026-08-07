SSI_SELF_DEVELOPMENT_ENGINE
Opis:

Ten dokument opisuje system zarządzania modelami AI wykorzystywanymi w SSI_SELF_DEVELOPMENT_ENGINE.

Model Manager odpowiada za kontrolę modeli językowych, ich uruchamianie, wybór odpowiedniego modelu do zadania oraz zarządzanie zasobami sprzętowymi.

Jest warstwą pomiędzy systemem SSI a lokalnym środowiskiem modeli (np. Ollama).

Zakres dokumentu:
1. Rola Model Manager

Opisuje:

zarządzanie modelami AI,
wybór modelu do konkretnego zadania,
kontrolę aktywnego modelu,
komunikację z Ollama,
monitorowanie wykorzystania zasobów.
2. Miejsce w architekturze

Schemat:

SSI DIRECTOR

        ↓

MODEL MANAGER

        ↓

OLLAMA ENGINE

        ↓

LOCAL AI MODEL

        ↓

RESULT
3. Obsługa modeli

Dokument opisuje:

listę dostępnych modeli,
konfigurację modeli,
role modeli.

Przykład:

Qwen2.5 7B
↓
Programista

Qwen2.5-Coder 7B
↓
Kodowanie

Model mniejszy
↓
Walidacja / klasyfikacja
4. Model Role Assignment

Każdy model może posiadać określoną rolę:

Programmer Model
Director Model
Validation Model
Documentation Model
Analysis Model
5. System uruchamiania modeli

Opisuje:

start modelu,
przekazanie kontekstu,
wykonanie zadania,
odbiór odpowiedzi,
zapis wyniku.
6. Kontrola zasobów

Bardzo ważne dla obecnego sprzętu.

Model Manager kontroluje:

RAM,
VRAM,
czas działania,
liczbę aktywnych modeli.

Zasada:

1 ciężki model aktywny w jednym czasie

żeby uniknąć przeciążenia komputera.

7. Integracja z pamięcią

Przed uruchomieniem model otrzymuje:

prompt systemowy,
aktualne zadanie,
pamięć krótkotrwałą,
pamięć długotrwałą,
historię podobnych operacji.
8. Historia modeli

Zapisywane są:

jaki model wykonał zadanie,
czas wykonania,
wynik,
błędy,
skuteczność.
9. Rozwój przyszły

Obecnie:

Ollama
+
JSON CONFIG
+
LOCAL MODELS

Docelowo:

MODEL MANAGER

+

MULTI MODEL ROUTING

+

SERVER GPU

+

AUTOMATIC MODEL SELECTION