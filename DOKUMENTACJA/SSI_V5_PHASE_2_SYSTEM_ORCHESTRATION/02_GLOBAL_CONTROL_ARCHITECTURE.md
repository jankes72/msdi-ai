# SSI V5 PHASE 2: GLOBAL CONTROL ARCHITECTURE

**Sprint:** 12+ (Phase 2 Foundation)
**Data:** 2026-08-01
**Wersja:** 1.0.0
**Status:** Completed
**Autor:** Glowny Architekt SSI V5

---

## 1. DIAGRAM ARCHITEKTURY KONTROLI

**Glowny diagram kontroli systemu SSI V5:**

```
                    ┌─────────────────────────────────────┐
                    │      SYSTEM ORCHESTRATION ENGINE      │
                    │  (Nadrzedna Warstwa Sterowania)        │
                    └─────────────────┬───────────────────┘
                                  |
          ┌───────────────────────┼───────────────────────┐
          |                       |                       |
          v                       v                       v
┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
│  TEACHER ENGINE  │   │   AGENT SYSTEM   │   │  DECISION LAYER  │
│   (15 Modeli)    │   │   (6 Agentów)    │   │  (Wybór Finalny) │
└────────┬────────┘   └────────┬────────┘   └────────┬────────┘
         |                       |                       |
         └───────────────┬───────┴───────┬───────────┘
                         |               |
                         v               v
              ┌─────────────────────────────────┐
              │       MEMORY LAYER               │
              │   (World Memory + Agent Memory)  │
              └─────────────────────────────────┘
                         |
                         v
              ┌─────────────────────────────────┐
              │       FUTURE DOMAIN MODULES      │
              │   (Football, Crypto, Financial,   │
              │    Energy, custom domains)        │
              └─────────────────────────────────┘
```

---

## 2. HIERARCHIA STEROWANIA

```
LEVEL 0: System Orchestration Engine
    │
    ├── LEVEL 1: Module Registry
    │       ├── Teacher Engine
    │       ├── Agent System
    │       ├── Decision Layer
    │       └── Memory Layer
    │
    ├── LEVEL 2: Lifecycle Manager
    │       ├── Model Lifecycle Controller
    │       └── Module Lifecycle Controller
    │
    ├── LEVEL 3: Data Flow Controller
    │       ├── Prediction Window Manager
    │       └── System Risk Engine
    │
    └── LEVEL 4: Monitoring & Automation
            ├── Health Monitoring Engine
            └── Automation Controller
```

---

## 3. ZALEZNOSCI MIEDZYWARSTWOWE

```
System Orchestration Engine
    ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
    │  CONTROL     │ │  MONITOR     │ │  AUTOMATE    │
    │  (start/stop)│ │  (observe)   │ │  (schedule)  │
    └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
           │                │                │
           ▼                ▼                ▼
Teacher Engine ──▶ Agent System ──▶ Decision Layer
    │                  │                  │
    ▼                  ▼                  ▼
    Models             Agents            Decisions
```

---

## 4. CONTROL FLOW DETAILS

**KOMUNIKACJA W SYSTEMIE:**

```
System Orchestration Engine
    │
    ├── CONTROL (start/stop/restart)
    │   │
    │   ├── Module Registry → Rejestracja modulow
    │   ├── Lifecycle Manager → Zarzadzanie cyklem zycia
    │   └── Automation Controller → Automatyzacja
    │
    ├── MONITOR (observe/collect metrics)
    │   │
    │   ├── Health Monitoring Engine → Zbieranie metryk
    │   ├── System Risk Engine → Ocena ryzyka
    │   └── Data Flow Controller → Kontrola przeplywu
    │
    └── COORDINATE (synchronizacja)
        │
        ├── Prediction Window Manager → Okna predykcji
        ├── Model Lifecycle Controller → Modele ML
        └── Plugin Architecture → Rozszerzenia
```

---

## 5. INTEGRATION POINTS

**PUNKTY INTEGRACJI:**

```
┌─────────────────────────────────────────────────────────────┐
│                    SYSTEM ORCHESTRATION ENGINE                 │
├─────────────────┬─────────────────┬─────────────────┬───────┤
│  Module Registry │ Lifecycle Manager│ Data Flow Ctrl  │ Risk │
│  (Rejestr)       │ (Cykl zycia)     │ (Przeplyw)      │Engine│
└─────────┬────────┴─────────┬────────┴─────────┬─────┬─┘
          │                  │                 │          │
          ▼                  ▼                 ▼          ▼
┌─────────────────┐ ┌─────────────┐ ┌───────────┐ ┌─────────┐
│ TEACHER ENGINE  │ │ AGENT SYSTEM │ │ MEMORY    │ │ DATA    │
│ (15 Modeli)      │ │ (6 Agentów)  │ │ LAYER     │ │ LAYER   │
└─────────────────┘ └─────────────┘ └───────────┘ └─────────┘
```

---

## SUMMARY

This document provides detailed architectural diagrams and control flow information for the System Orchestration Engine.

**Next Document:** See [03_CORE_COMPONENTS.md](./03_CORE_COMPONENTS.md) for detailed component specifications.

---

**Document Status:** Ready for Review  
**Version:** 1.0.0  
**Date:** 2026-08-01