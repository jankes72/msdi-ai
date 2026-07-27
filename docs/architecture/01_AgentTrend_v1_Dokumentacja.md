PLATFORMA_AI/

│
├── README.md                         # główna dokumentacja projektu
├── CHANGELOG.md                      # historia zmian wersji
├── requirements.txt                  # biblioteki Python
├── .gitignore                        # pliki pomijane przez Git
│
│
├── dokumentacja/
│   │
│   ├── architektura.md               # opis całej platformy
│   ├── agent_trend_1.md              # opis pierwszego agenta
│   ├── struktura_danych.md            # opis CSV i pól
│   ├── strategie.md                  # opis strategii agentów
│   ├── uczenie_agentow.md            # opis mechanizmu uczenia
│   └── historia_wersji.md             # zmiany projektu
│
│
├── dane/
│   │
│   ├── dataBase_futbol_trend.csv
│   ├── analiza_poisson_dixon.csv
│   ├── analiza_korelacji_cech.csv
│   ├── syntetyczne_trendy_historyczne.csv
│   ├── ranking_cech.csv
│   └── random_forest_waznosc_cech.csv
│
│
├── agenci/
│   │
│   └── agent_trend_1/
│       │
│       ├── pamiec/
│       │   ├── strategie.json
│       │   ├── historia_strategii.csv
│       │   ├── wagi_zaufania.json
│       │   └── bankroll.json
│       │
│       ├── wyniki/
│       │   ├── predykcje.csv
│       │   ├── kupony.csv
│       │   └── raport.csv
│       │
│       └── konfiguracja.json
│
│
├── silnik_agentow/
│   │
│   ├── agent_trend.py                # główna klasa agenta
│   ├── loader_danych.py
│   ├── analiza_trendow.py
│   ├── generator_strategii.py
│   ├── symulator_kuponow.py
│   ├── uczenie_agenta.py
│   └── pamiec_agenta.py
│
│
├── platforma/
│   │
│   ├── demon_manager.py              # przyszłe sterowanie
│   ├── kontroler.py
│   └── harmonogram.py
│
│
├── modele/
│   └── zapisane_modele/
│
│
└── testy/
    ├── test_danych.py
    ├── test_agenta.py
    └── test_strategii.py
Jak to działa:

silnik_agentow/

tutaj jest kod całego mechanizmu
nie zmienia się przy tworzeniu kolejnych agentów

agenci/

tutaj są "mózgi" poszczególnych agentów
każdy ma własną pamięć

Przykład później:

agenci/

agent_trend_1/
agent_trend_2/
agent_trend_3/
agent_historyczny_1/
agent_poisson_1/

ale wszystkie korzystają z tego samego silnika.

Do GitHuba później można wrzucić:

kod ✅
dokumentację ✅
przykładowe dane testowe ✅

a wykluczyć:

pełną pamięć agentów
wyniki uczenia
bankroll
duże CSV