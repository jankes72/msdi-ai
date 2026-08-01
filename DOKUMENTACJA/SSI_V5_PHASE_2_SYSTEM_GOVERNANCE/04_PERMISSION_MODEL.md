# SSI V5 Phase 2 — Permission Model

## 04. Permission Model Specification

**Wersja:** 1.0.0  
**Data:** 2026-08-01  
**Status:** ✅ COMPLETED  
**Poziom:** Technical Specification  
**Domena:** System Governance → Access Control & Authorization

---

## 📋 Spis Treści

1. [Overview](#1-overview)
2. [Role Definitions](#2-role-definitions)
3. [Permission Matrix](#3-permission-matrix)
4. [Permission Types](#4-permission-types)
5. [Access Control Lists](#5-access-control-lists)
6. [Permission Inheritance](#6-permission-inheritance)
7. [Permission Evaluation](#7-permission-evaluation)
8. [Permission Overrides](#8-permission-overrides)
9. [Temporary Permissions](#9-temporary-permissions)
10. [Komponenty — Szczegóły Techniczne](#10-komponenty--szczegóły-techniczne)

---

## 1. Overview

### 1.1 DESCRIPTION

**Permission Model**定义了 system uprawnień i kontroli dostępu w warstwie **System Governance**. Określa **kto** (Role), **co** (Operacje), **na czym** (Zasoby) może wykonywać w systemie SSI V5.

Model opiera się na **Role-Based Access Control (RBAC)** z elementami **Attribute-Based Access Control (ABAC)**, umożliwiając elastyczne i precyzyjne zarządzanie uprawnieniami.

### 1.2 RESPONSIBILITIES

- **Access Control**: Kontrola dostępu do poleceń i zasobów
- **Authorization**: Autoryzacja operacji podejmowanych przez operatorów
- **Permission Validation**: Walidacja uprawnień przed wykonaniem poleceń
- **Audit Trail**: Rejestrowanie wszystkich działań związanych z uprawnieniami
- **Escalation**: Mechanizmy eskalacji dla operacji wymagających podwyższonych uprawnień

### 1.3 Place in SSI V5 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     SYSTEM GOVERNANCE LAYER                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌───────────────────────┐                                       │
│  │   PERMISSION           │                                       │
│  │   MODEL                │  ◄── Kontrola dostępu               │
│  │  (Access Control)      │  ▬ Definicje ról, uprawnień         │
│  └──────────┬──────────────┘                                       │
│             │                                                        │
│             ├─── Role Definitions                                  │
│             ├─── Permission Matrix                                  │
│             ├─── Access Control Lists                               │
│             ├─── Inheritance Rules                                   │
│             └─── Evaluation Engine                                  │
│             │                                                        │
│             ▼                                                        │
│  ┌─────────────────────────────┐                                  │
│  │   COMMAND PROCESSOR          │  ◄── Walidacja uprawnień       │
│  └─────────────────────────────┘                                  │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 1.4 Key Principles

✅ **Principle of Least Privilege**: Każda rola ma jedynie niezbędne uprawnienia  
✅ **Separation of Duties**: Krytyczne operacje wymagają współdziałania wielu ról  
✅ **Explicit Authorization**: Dostęp jest jawne udzielany, nie domyślny  
✅ **Auditability**: Wszystkie decyzje autoryzacyjne są rejestrowane  
✅ **Flexibility**: Możliwe dostosowanie uprawnień do specyficznych potrzeb  
✅ **Security First**: Bezpieczeństwo ma pierwszy priorytet  

---

## 2. Role Definitions

### 2.1 Role Hierarchy

```
┌─────────────────────────────────────────────────────────────────┐
│                    ROLE HIERARCHY                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  SYSTEM_OWNER (Level 0)                                            │
│  │                                                                │
│  ├─── SYSTEM_ADMIN (Level 1)                                       │
│  │     │                                                           │
│  │     ├─── DEVELOPMENT_LEAD (Level 2)                            │
│  │     │     │                                                     │
│  │     │     └─── DEVELOPER (Level 3)                             │
│  │     │                                                           │
│  │     └─── OPERATIONS_LEAD (Level 2)                             │
│  │           │                                                     │
│  │           └─── OPERATOR (Level 3)                               │
│  │                                                               │
│  └─── ANALYST (Level 1)                                           │
│        │                                                           │
│        └─── REPORT_ANALYST (Level 2)                              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

Special Roles (Non-hierarchical):
├─ AUTOMATION_AGENT (System service account)
├─ AI_LABORATORY (Development system)
└─ AUDITOR (Read-only, full visibility)
```

### 2.2 Role Specifications

#### SYSTEM_OWNER

**DESCRIPTION:**
Główny operator systemu z pełnią uprawnień. Odpowiada za strategiczne zarządzanie całym systemem SSI V5.

**RESPONSIBILITIES:**
- Pełna kontrola nad systemem
- Zarządzanie rolami i uprawnieniami innych operatorów
- Autoryzacja krytycznych operacji
- Konfiguracja polityk bezpieczeństwa
- Awaryjne operacje systemowe

**CHARACTERISTICS:**
- Poziom dostępu: **Unrestricted**
- Dziedziczenie: **Źródło** (nie dziedziczy po innych)
- Liczba: **Ograniczona** (1-3 osoby)
- Autoryzacja: **Multi-factor** (MFA wymagana)

**ALLOWED OPERATIONS:**
- Wszystkie typy poleceń
- Pełny dostęp do wszystkich zasobów
- Konfiguracja systemu
- Zarządzanie użytkownikami i rolami

#### SYSTEM_ADMIN

**DESCRIPTION:**
Administrator systemu z rozległymi uprawnieniami administracyjnymi, ale bez możliwości wykonywania krytycznych operacji systemowych.

**RESPONSIBILITIES:**
- Zarządzanie konfiguracją systemu
- Monitorowanie stanu systemu
- Rozwiązywanie problemów operacyjnych
- Wsparcie dla użytkowników

**CHARACTERISTICS:**
- Poziom dostępu: **High**
- Dziedziczenie: Dziedziczy z SYSTEM_OWNER (ograniczone)
- Liczba: **Ograniczona** (5-10 osób)
- Autoryzacja: **Standard** (MFA zalecana)

**ALLOWED OPERATIONS:**
- Polecenia systemowe (z wyjątkiem EMERGENCY_STOP, SYSTEM_LOCK)
- Zarządzanie konfiguracją
- Monitoring i diagnoza
- Zarządzanie modułami (CREATE, UPDATE, DISABLE)

**RESTRICTIONS:**
- ❌ Nie może wykonywać: DELETE_MODULE, DEPLOY_TO_PRODUCTION
- ❌ Nie może modyfikować: Permission Model, Security Policies

#### DEVELOPMENT_LEAD

**DESCRIPTION:**
Kierownik zespołu developerskiego odpowiedzialny za rozwój nowych modułów i funkcjonalności systemu.

**RESPONSIBILITIES:**
- Koordynacja prac rozwojowych
- Tworzenie nowych modułów analitycznych
- Integracja z AI Laboratory
- Zarządzanie cyklem życia rozwoju oprogramowania

**CHARACTERISTICS:**
- Poziom dostępu: **Medium-High**
- Dziedziczenie: Dziedziczy z SYSTEM_ADMIN
- Liczba: **Ograniczona** (2-5 osób)
- Autoryzacja: **Standard**

**ALLOWED OPERATIONS:**
- Tworzenie i modyfikacja modułów
- Request Analysis
- Create Teacher Model / Agent
- Testowanie i walidacja

**RESTRICTIONS:**
- ❌ Nie może: Wdrażać do produkcji bez zatwierdzenia
- ❌ Nie może: Wykonuje poleceń systemowych
- ❌ Ograniczone: Tylko moduły w obszarze rozwoju

#### DEVELOPER

**DESCRIPTION:**
Deweloper pracujący pod nadzorem DEVELOPMENT_LEAD, odpowiedzialny za implementację nowych funkcjonalności.

**RESPONSIBILITIES:**
- Implementacja modułów według specyfikacji
- Testowanie jednostkowe i integracyjne
- Dokumentacja techniczna
- Współpraca z AI Laboratory

**CHARACTERISTICS:**
- Poziom dostępu: **Medium**
- Dziedziczenie: Dziedziczy z DEVELOPMENT_LEAD
- Liczba: **Nieograniczona**
- Autoryzacja: **Standard**

**ALLOWED OPERATIONS:**
- Rozwój modułów w sandbox
- Testowanie w środowisku developerskim
- Współpraca z AI Laboratory

**RESTRICTIONS:**
- ❌ Nie może: Tworzyć moduły produkcji
- ❌ Nie może: Wykonywać poleceń systemowych
- ❌ Ograniczone: Tylko do przypisanych zadań

#### OPERATIONS_LEAD

**DESCRIPTION:**
Kierownik operacji odpowiedzialny za codzienne funkcjonowanie systemu i zarządzanie procesami.

**RESPONSIBILITIES:**
- Monitorowanie procesów systemowych
- Zarządzanie harmonogramem zadań
- Optymalizacja wydajności
- Rozwiązywanie bieżących problemów

**CHARACTERISTICS:**
- Poziom dostępu: **Medium-High**
- Dziedziczenie: Dziedziczy z SYSTEM_ADMIN
- Liczba: **Ograniczona** (2-5 osób)
- Autoryzacja: **Standard**

**ALLOWED OPERATIONS:**
- START_PROCESS, STOP_PROCESS, PAUSE_PROCESS, RESUME_PROCESS
- MONITOR_PROCESS, SYSTEM_HEALTH_CHECK
- CONFIGURATION_CHANGE (ograniczone)

**RESTRICTIONS:**
- ❌ Nie może: Tworzyć lub usuwać moduły
- ❌ Nie może: Wykonywać poleceń krytycznych

#### OPERATOR

**DESCRIPTION:**
Operator systemu odpowiedzialny za standardowe operacje i monitorowanie.

**RESPONSIBILITIES:**
- Monitorowanie stanu systemu
- Wykonywanie rutynowych operacji
- Raportowanie problemów
- Współpraca z OPERATIONS_LEAD

**CHARACTERISTICS:**
- Poziom dostępu: **Medium**
- Dziedziczenie: Dziedziczy z OPERATIONS_LEAD
- Liczba: **Nieograniczona**
- Autoryzacja: **Standard**

**ALLOWED OPERATIONS:**
- START_PROCESS, STOP_PROCESS (zaaprobowane)
- SYSTEM_HEALTH_CHECK, GENERATE_REPORT
- Read-only dostęp do konfiguracji

**RESTRICTIONS:**
- ❌ Nie może: Modyfikować konfigurację
- ❌ Nie może: Tworzyć lub usuwać moduły
- ❌ Ograniczone: Tylko zatwierdzone procesy

#### ANALYST

**DESCRIPTION:**
Analityk systemu odpowiedzialny za analizę danych, generowanie raportów i optymalizację procesów decyzyjnych.

**RESPONSIBILITIES:**
- Generowanie raportów i analiz
- Optymalizacja parametrów systemowych
- Współpraca z Teacher Engine i Agent System
- ocena wyników systemu

**CHARACTERISTICS:**
- Poziom dostępu: **Medium-Low**
- Dziedziczenie: Dziedziczy z SYSTEM_OWNER (ograniczone)
- Liczba: **Nieograniczona**
- Autoryzacja: **Standard**

**ALLOWED OPERATIONS:**
- GENERATE_REPORT
- REQUEST_ANALYSIS
- Read-only dostęp do danych
- Analiza wyników

**RESTRICTIONS:**
- ❌ Nie może: Modyfikować system
- ❌ Nie może: Wykonywać poleceń administracyjnych
- ❌ Ograniczone: Tylko do analizy i raportowania

#### REPORT_ANALYST

**DESCRIPTION:**
Specjalista od generowania i analizy raportów, z dostępem jedynie do danych i narzędzi analitycznych.

**CHARACTERISTICS:**
- Poziom dostępu: **Low**
- Dziedziczenie: Dziedziczy z ANALYST
- Autoryzacja: **Standard**

**ALLOWED OPERATIONS:**
- GENERATE_REPORT
- Read-only dostęp do historycznych danych

**RESTRICTIONS:**
- ❌ Nie może: Wykonywać żadnych poleceń modyfikujących

#### AUTOMATION_AGENT

**DESCRIPTION:**
Konto usługi systemowej używane przez procesy automatyzacji do wykonywania zdefiniowanych zadań.

**CHARACTERISTICS:**
- Poziom dostępu: **Limited** (tylko zdefiniowane operacje)
- Dziedziczenie: **Brak** (specjalna rola)
- Autoryzacja: **Certificate-based**

**ALLOWED OPERATIONS:**
- Wykonanie zdefiniowanych zadań automatycznych
- System health checks
- Backup operations (scheduled)

**RESTRICTIONS:**
- ❌ Tylko operacje jawnie przypisane do roli
- ❌ Nie może inicjować nowych zadań

#### AI_LABORATORY

**DESCRIPTION:**
System rozwijający nowe moduły i funkcjonalności, działający jako odrębna jednostka.

**CHARACTERISTICS:**
- Poziom dostępu: **Development-only**
- Dziedziczenie: **Brak** (specjalna rola)
- Autoryzacja: **System token**

**ALLOWED OPERATIONS:**
- Tworzenie nowych modułów w rozwoju
- Testowanie i walidacja
- Współpraca z DEVELOPMENT_LEAD

**RESTRICTIONS:**
- ❌ Nie może wdrażać do produkcji
- ❌ Ograniczone do rozwoju

#### AUDITOR

**DESCRIPTION:**
Rola z pełnym dostępem do odczytu, przeznaczona wyłącznie do audytu i monitorowania systemu.

**CHARACTERISTICS:**
- Poziom dostępu: **Read-only, Full visibility**
- Dziedziczenie: **Brak** (specjalna rola)
- Autoryzacja: **MFA + IP Whitelist**

**ALLOWED OPERATIONS:**
- Read-only dostęp do wszystkich danych
- Generowanie raportów audytowych
- Analiza logów systemowych

**RESTRICTIONS:**
- ❌ Nie może wykonywać ŻADNYCH poleceń modyfikujących
- ❌ Tylko odczyt

---

## 3. Permission Matrix

### 3.1 Full Permission Matrix

```
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                            PERMISSION MATRIX                                         │
├─────────────────┬───────┬────────┬────────┬────────┬────────┬────────┬────────┬────────┤
│ Role             │ READ  │ WRITE  │ EXECUTE│ MODIFY │ DEPLOY │ ROLLBK │ CREATE │ DELETE │
├─────────────────┼───────┼────────┼────────┼────────┼────────┼────────┼────────┼────────┤
│ SYSTEM_OWNER     │   ✅   │   ✅   │   ✅   │   ✅   │   ✅   │   ✅   │   ✅   │   ✅   │
│ SYSTEM_ADMIN     │   ✅   │   ✅   │   ✅   │   ✅   │   ⚠️   │   ✅   │   ✅   │   ⚠️   │
│ DEVELOPMENT_LEAD │   ✅   │   ✅   │   ✅   │   ✅   │   ⚠️   │   ❌   │   ✅   │   ⚠️   │
│ DEVELOPER       │   ✅   │   ✅   │   ⚠️   │   ❌   │   ❌   │   ❌   │   ⚠️   │   ❌   │
│ OPERATIONS_LEAD  │   ✅   │   ⚠️   │   ✅   │   ⚠️   │   ❌   │   ⚠️   │   ❌   │   ❌   │
│ OPERATOR        │   ✅   │   ❌   │   ⚠️   │   ❌   │   ❌   │   ❌   │   ❌   │   ❌   │
│ ANALYST         │   ✅   │   ❌   │   ❌   │   ❌   │   ❌   │   ❌   │   ❌   │   ❌   │
│ REPORT_ANALYST  │   ✅   │   ❌   │   ❌   │   ❌   │   ❌   │   ❌   │   ❌   │   ❌   │
│ AUTOMATION_AGENT│   ✅   │   ❌   │   ✅   │   ❌   │   ❌   │   ❌   │   ❌   │   ❌   │
│ AI_LABORATORY    │   ✅   │   ✅   │   ✅   │   ✅   │   ❌   │   ❌   │   ✅   │   ❌   │
│ AUDITOR         │   ✅   │   ❌   │   ❌   │   ❌   │   ❌   │   ❌   │   ❌   │   ❌   │
└─────────────────┴───────┴────────┴────────┴────────┴────────┴────────┴────────┴────────┘

Legenda:
✅ = Pełne uprawnienia
⚠️ = Ograniczone uprawnienia (wymaga dodatkowej autoryzacji lub limitowane)
❌ = Brak uprawnień
```

### 3.2 Permission Matrix by Command Type

```
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                 PERMISSION MATRIX — COMMAND TYPE VIEW                              │
├─────────────────┬─────────────────┬───────────────────────────────────────────────────┤
│ Command Type     │     Roles        │               Notes                          │
├─────────────────┼─────────────────┼───────────────────────────────────────────────────┤
│ EMERGENCY_STOP   │ SYSTEM_OWNER    │ ✅ Full access                                │
│                 │ SYSTEM_ADMIN     │ ❌ Restricted                                  │
│                 │ DEVELOPMENT_LEAD│ ❌ Restricted                                  │
├─────────────────┼─────────────────┼───────────────────────────────────────────────────┤
│ SYSTEM_LOCK     │ SYSTEM_OWNER    │ ✅ Full access                                │
│                 │ SYSTEM_ADMIN     │ ❌ Restricted                                  │
│                 │ Others           │ ❌ Restricted                                  │
├─────────────────┼─────────────────┼───────────────────────────────────────────────────┤
│ ROLLBACK        │ SYSTEM_OWNER    │ ✅ Full access                                │
│                 │ SYSTEM_ADMIN     │ ✅ With approval                               │
│                 │ DEVELOPMENT_LEAD│ ⚠️  Limited (own modules)                      │
├─────────────────┼─────────────────┼───────────────────────────────────────────────────┤
│ CREATE_MODULE   │ SYSTEM_OWNER    │ ✅ Full access                                │
│                 │ SYSTEM_ADMIN     │ ✅ Full access                                │
│                 │ DEVELOPMENT_LEAD│ ✅ Full access                                │
│                 │ DEVELOPER       │ ⚠️  Sandbox only                               │
├─────────────────┼─────────────────┼───────────────────────────────────────────────────┤
│ DELETE_MODULE   │ SYSTEM_OWNER    │ ✅ Full access                                │
│                 │ SYSTEM_ADMIN     │ ⚠️  With approval                               │
│                 │ Others           │ ❌ Restricted                                  │
├─────────────────┼─────────────────┼───────────────────────────────────────────────────┤
│ DEPLOY_TO_PRODUCTION │ SYSTEM_OWNER │ ✅ Full access                                │
│                 │ DEVELOPMENT_LEAD│ ⚠️  With SYSTEM_OWNER approval                  │
│                 │ Others           │ ❌ Restricted                                  │
├─────────────────┼─────────────────┼───────────────────────────────────────────────────┤
│ START_PROCESS   │ SYSTEM_OWNER    │ ✅ Full access                                │
│                 │ SYSTEM_ADMIN     │ ✅ Full access                                │
│                 │ OPERATIONS_LEAD  │ ✅ Full access                                │
│                 │ OPERATOR        │ ⚠️  Approved processes only                    │
├─────────────────┼─────────────────┼───────────────────────────────────────────────────┤
│ STOP_PROCESS    │ SYSTEM_OWNER    │ ✅ Full access                                │
│                 │ SYSTEM_ADMIN     │ ✅ Full access                                │
│                 │ OPERATIONS_LEAD  │ ✅ Full access                                │
│                 │ OPERATOR        │ ⚠️  Approved processes only                    │
├─────────────────┼─────────────────┼───────────────────────────────────────────────────┤
│ CONFIGURATION_  │ SYSTEM_OWNER    │ ✅ Full access                                │
│ CHANGE          │ SYSTEM_ADMIN     │ ✅ Limited scope                              │
│                 │ Others           │ ❌ Restricted                                  │
├─────────────────┼─────────────────┼───────────────────────────────────────────────────┤
│ REQUEST_ANALYSIS│ SYSTEM_OWNER    │ ✅ Full access                                │
│                 │ DEVELOPMENT_LEAD│ ✅ Full access                                │
│                 │ ANALYST         │ ✅ Full access                                │
│                 │ REPORT_ANALYST  │ ⚠️  Read-only analysis                         │
└─────────────────┴─────────────────┴───────────────────────────────────────────────────┘
```

### 3.3 Permission Matrix by Resource Type

```
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                 PERMISSION MATRIX — RESOURCE TYPE VIEW                             │
├─────────────────┬────────────────────────────────────────────────────────────────────────┤
│ Resource Type    │                          Permissions                                  │
├─────────────────┼────────────────────────────────────────────────────────────────────────┤
│ SYSTEM_CONFIG    │ READ: All Roles | WRITE: SYSTEM_OWNER, SYSTEM_ADMIN           │
│                 │ MODIFY: SYSTEM_OWNER only                                        │
├─────────────────┼────────────────────────────────────────────────────────────────────────┤
│ MODULE_REGISTRY  │ READ: All Roles | WRITE: SYSTEM_OWNER, SYSTEM_ADMIN, DEV_LEAD   │
│                 │ CREATE/DELETE: SYSTEM_OWNER, SYSTEM_ADMIN (approved)             │
├─────────────────┼────────────────────────────────────────────────────────────────────────┤
│ PROCESS_MANAGER  │ READ: All Roles | CONTROL: SYSTEM_OWNER, SYSTEM_ADMIN, OPER_LEAD│
│                 │ LIMITED: OPERATOR (approved processes)                            │
├─────────────────┼────────────────────────────────────────────────────────────────────────┤
│ COMMAND_HISTORY  │ READ: SYSTEM_OWNER, SYSTEM_ADMIN, AUDITOR                        │
│                 │ LIMITED: Others (own commands only)                               │
├─────────────────┼────────────────────────────────────────────────────────────────────────┤
│ AI_LABORATORY   │ READ/WRITE: SYSTEM_OWNER, DEVELOPMENT_LEAD, DEVELOPER, AI_LAB     │
│                 │ EXECUTE: SYSTEM_OWNER, AI_LAB                                     │
├─────────────────┼────────────────────────────────────────────────────────────────────────┤
│ DATA_STORE      │ READ: All Roles with clearance | WRITE: Restricted                   │
│                 │ SYSTEM_DATA: No direct access (via API only)                    │
└─────────────────┴────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Permission Types

### 4.1 Permission Type Definitions

| Permission Type | Code | Description | Scope |
|----------------|------|-------------|-------|
| **READ** | R | Odczyt danych lub konfiguracji | All resources |
| **WRITE** | W | Modyfikacja danych | Non-protected resources |
| **EXECUTE** | X | Wykonanie poleceń | Commands, processes |
| **MODIFY** | M | Zmiana konfiguracji systemowej | System settings |
| **DEPLOY** | D | Wdrożenie do produkcji | Production environment |
| **ROLLBACK** | B | Cofnięcie zmian | All changes |
| **CREATE** | C | Tworzenie nowych elementów | Modules, processes |
| **DELETE** | L | Usuwanie elementów | Modules, data |
| **ADMIN** | A | Zarządzanie systemem | Users, roles, policies |

### 4.2 Permission Type Matrix

```
┌─────────────────┬────────┬────────┬────────┬────────┬────────┬────────┤
│ Permission      │ Command │ System │ Module │ Process│ Data  │ Users │
├─────────────────┼────────┼────────┼────────┼────────┼────────┼────────┤
│ READ (R)        │   ❌   │   ✅   │   ✅   │   ✅   │   ✅   │   ✅   │
│ WRITE (W)       │   ❌   │   ⚠️   │   ✅   │   ❌   │   ⚠️   │   ❌   │
│ EXECUTE (X)     │   ✅   │   ✅   │   ❌   │   ✅   │   ❌   │   ❌   │
│ MODIFY (M)      │   ❌   │   ✅   │   ⚠️   │   ❌   │   ❌   │   ❌   │
│ DEPLOY (D)      │   ❌   │   ❌   │   ✅   │   ❌   │   ❌   │   ❌   │
│ ROLLBACK (B)    │   ❌   │   ✅   │   ✅   │   ✅   │   ⚠️   │   ❌   │
│ CREATE (C)      │   ❌   │   ❌   │   ✅   │   ✅   │   ❌   │   ✅   │
│ DELETE (L)      │   ❌   │   ❌   │   ✅   │   ❌   │   ✅   │   ✅   │
│ ADMIN (A)       │   ❌   │   ✅   │   ❌   │   ❌   │   ❌   │   ✅   │
└─────────────────┴────────┴────────┴────────┴────────┴────────┴────────┘
```

---

## 5. Access Control Lists

### 5.1 ACL Structure

Każdy zasób w systemie ma przyporządkowaną **Access Control List (ACL)**, która definiuje, które role mają jakie uprawnienia względem tego zasobu.

```json
{
  "resource_id": "MODULE_CRYPTO_ANALYZER",
  "resource_type": "MODULE",
  "acl": {
    "SYSTEM_OWNER": ["READ", "WRITE", "EXECUTE", "MODIFY", "DELETE"],
    "SYSTEM_ADMIN": ["READ", "WRITE", "EXECUTE", "MODIFY"],
    "DEVELOPMENT_LEAD": ["READ", "WRITE", "EXECUTE"],
    "DEVELOPER": ["READ", "EXECUTE"],
    "OPERATIONS_LEAD": ["READ", "EXECUTE"],
    "OPERATOR": ["READ", "EXECUTE"],
    "ANALYST": ["READ"],
    "REPORT_ANALYST": ["READ"],
    "AUTOMATION_AGENT": [],
    "AI_LABORATORY": ["READ", "WRITE"],
    "AUDITOR": ["READ"]
  },
  "default_permission": "DENY",
  "inheritance_enabled": true,
  "audit_required": true
}
```

### 5.2 ACL Templates

#### System Configuration ACL
```json
{
  "resource_type": "SYSTEM_CONFIG",
  "template_name": "system_config_acl",
  "acl": {
    "SYSTEM_OWNER": ["READ", "WRITE", "MODIFY"],
    "SYSTEM_ADMIN": ["READ", "WRITE"],
    "AUDITOR": ["READ"],
    "DEFAULT": ["READ"]
  }
}
```

#### Module ACL
```json
{
  "resource_type": "MODULE",
  "template_name": "module_acl",
  "acl": {
    "SYSTEM_OWNER": ["READ", "WRITE", "EXECUTE", "MODIFY", "DELETE"],
    "SYSTEM_ADMIN": ["READ", "WRITE", "EXECUTE", "MODIFY"],
    "DEVELOPMENT_LEAD": ["READ", "WRITE", "EXECUTE"],
    "DEVELOPER": ["READ", "EXECUTE"],
    "AUDITOR": ["READ"],
    "DEFAULT": ["READ"]
  }
}
```

#### Process ACL
```json
{
  "resource_type": "PROCESS",
  "template_name": "process_acl",
  "acl": {
    "SYSTEM_OWNER": ["READ", "EXECUTE", "MODIFY"],
    "SYSTEM_ADMIN": ["READ", "EXECUTE", "MODIFY"],
    "OPERATIONS_LEAD": ["READ", "EXECUTE"],
    "OPERATOR": ["READ", "EXECUTE"],
    "AUDITOR": ["READ"],
    "DEFAULT": ["READ"]
  }
}
```

#### Data Store ACL
```json
{
  "resource_type": "DATA_STORE",
  "template_name": "data_store_acl",
  "acl": {
    "SYSTEM_OWNER": ["READ", "WRITE"],
    "SYSTEM_ADMIN": ["READ", "WRITE"],
    "ANALYST": ["READ"],
    "REPORT_ANALYST": ["READ"],
    "AUDITOR": ["READ"],
    "DEFAULT": []
  }
}
```

### 5.3 ACL Evaluation

Proces oceny ACL:

```
Request: (Role, Permission, Resource)
       │
       ▼
┌─────────────────┐
│  Check ACL      │ ◄── Lookup ACL for resource
│  for Resource    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Check         │ ◄── Does role have permission?
│  Permission    │
└────────┬────────┘
         │
    ┌────▼────┐
    │         │
    ▼         ▼
┌────────┐ ┌──────────┐
│ Yes     │ │ No       │
└────┬────┘ └────┬─────┘
     │            │
     ▼            ▼
┌─────────────┐ ┌─────────────┐
│ GRANT      │ │ DENY       │
│ ACCESS     │ │ ACCESS     │
└─────────────┘ └─────────────┘
```

---

## 6. Permission Inheritance

### 6.1 Inheritance Rules

#### Role Hierarchy Inheritance

Role dziedziczą uprawnienia od ról wyższych w hierarchii:

```
SYSTEM_OWNER
    │
    └── SYSTEM_ADMIN (dziedziczy wszystkie uprawnienia SYSTEM_OWNER)
          │
          ├─── DEVELOPMENT_LEAD (dziedziczy od SYSTEM_ADMIN)
          │       │
          │       └── DEVELOPER (dziedziczy od DEVELOPMENT_LEAD)
          │
          └── OPERATIONS_LEAD (dziedziczy od SYSTEM_ADMIN)
                  │
                  └── OPERATOR (dziedziczy od OPERATIONS_LEAD)

ANALYST (dziedziczy selektywnie od SYSTEM_OWNER)
    │
    └── REPORT_ANALYST (dziedziczy od ANALYST)
```

**Zasada:** Role dziedziczą **wszystkie uprawnienia** od swoich przodków, chyba że:
1. Uprawnienie jest jawnie odebrane w definicji roli
2. Uprawnienie jest ograniczone przez systemowe polityki bezpieczeństwa

#### Permission Type Inheritance

Niektóre uprawnienia implikują inne:

```
MODIFY → WRITE → READ
DEPLOY → EXECUTE → READ
ADMIN → ALL PERMISSIONS (for governed scope)
```

**Zasada:** Jeśli rola ma uprawnienie MODIFY, automatycznie ma WRITE i READ.

### 6.2 Inheritance Examples

#### Example 1: SYSTEM_ADMIN

```
Role: SYSTEM_ADMIN
Inherits from: SYSTEM_OWNER

Effective Permissions:
├── From SYSTEM_OWNER: ALL PERMISSIONS
├── Explicit restrictions:
│   ├── DEPLOY: Requires approval
│   └── DELETE: Requires approval
└── Result: Full access with approval requirements
```

#### Example 2: DEVELOPER

```
Role: DEVELOPER
Inherits from: DEVELOPMENT_LEAD → SYSTEM_ADMIN → SYSTEM_OWNER

Effective Permissions:
├── From SYSTEM_OWNER: ALL PERMISSIONS
├── From SYSTEM_ADMIN: All (inherited)
├── From DEVELOPMENT_LEAD: All (inherited)
├── Explicit restrictions:
│   ├── DEPLOY: ❌ Denied
│   ├── SYSTEM_COMMANDS: ❌ Denied
│   └── WRITE: Limited to sandbox only
└── Result: Development environment access only
```

#### Example 3: OPERATOR

```
Role: OPERATOR
Inherits from: OPERATIONS_LEAD → SYSTEM_ADMIN → SYSTEM_OWNER

Effective Permissions:
├── From SYSTEM_OWNER: ALL PERMISSIONS
├── From SYSTEM_ADMIN: All (inherited)
├── From OPERATIONS_LEAD: All (inherited)
├── Explicit restrictions:
│   ├── MODIFY: ❌ Denied
│   ├── CREATE: ❌ Denied
│   ├── DELETE: ❌ Denied
│   └── EXECUTE: Limited to approved processes
└── Result: Process control only
```

### 6.3 Inheritance Calculation

Algorithm for calculating effective permissions:

```
function calculate_effective_permissions(role, resource):
    permissions = set()
    
    # Get direct permissions
    permissions.add_all(ACL[resource].get(role, []))
    
    # Get inherited permissions from parent roles
    parent = role.parent
    while parent is not null:
        permissions.add_all(ACL[resource].get(parent, []))
        parent = parent.parent
    
    # Apply inheritance rules
    if "MODIFY" in permissions:
        permissions.add("WRITE")
        permissions.add("READ")
    if "DEPLOY" in permissions:
        permissions.add("EXECUTE")
        permissions.add("READ")
    if "ADMIN" in permissions:
        permissions.add_all("ALL")
    
    # Apply explicit denials
    for denial in role.explicit_denials:
        permissions.remove(denial)
    
    # Apply resource-specific restrictions
    permissions = permissions.intersection(resource.allowed_permissions)
    
    return permissions
```

---

## 7. Permission Evaluation

### 7.1 Evaluation Process

Proces oceny uprawnień dla danego żądania:

```
Request: (Operator, Command, Resource, Action)
       │
       ▼
┌─────────────────┐
│  Step 1:       │ ◄── Extract operator role
│  Get Role      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Step 2:       │ ◄── Get resource ACL
│  Get ACL       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Step 3:       │ ◄── Calculate effective permissions
│  Calculate     │
│  Permissions   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Step 4:       │ ◄── Check if action is allowed
│  Check         │
│  Permission    │
└────────┬────────┘
         │
    ┌────▼────┐
    │         │
    ▼         ▼
┌────────┐ ┌──────────┐
│ YES     │ │ NO       │
└────┬────┘ └────┬─────┘
     │            │
     ▼            ▼
┌─────────────┐ ┌─────────────┐
│ GRANT      │ │ DENY       │
│ ACCESS     │ │ ACCESS     │
└─────────────┘ └─────────────┘
         │            │
         │            ▼
         │     ┌─────────────────┐
         │     │  RETURN ERROR    │
         │     │  (403 Forbidden) │
         │     └─────────────────┘
         │
         ▼
┌─────────────────┐
│  Step 5:       │ ◄── Check for additional constraints
│  Additional    │
│  Constraints   │
└─────────────────┘
```

### 7.2 Evaluation Algorithm

```
function evaluate_permission(operator_id, command_type, resource_id, action):
    # Step 1: Get operator role
    operator = get_operator(operator_id)
    if operator is null:
        return DENIED (401 Unauthorized)
    
    role = operator.role
    
    # Step 2: Get resource ACL
    acl = get_acl(resource_id)
    if acl is null:
        acl = get_default_acl(resource_type)
    
    # Step 3: Calculate effective permissions
    effective_permissions = calculate_effective_permissions(role, acl)
    
    # Step 4: Check permission
    if action not in effective_permissions:
        return DENIED (403 Forbidden)
    
    # Step 5: Check additional constraints
    constraints = get_constraints(role, command_type, resource_id)
    
    for constraint in constraints:
        if not constraint.evaluate():
            return DENIED (403 Forbidden, constraint.message)
    
    # Step 6: Check approval requirements
    if requires_approval(role, command_type, resource_id):
        approval = await get_approval(operator_id, command_type, resource_id)
        if not approval.granted:
            return PENDING_APPROVAL (402 Payment Required)
    
    # Step 7: Log the access
    log_access(operator_id, command_type, resource_id, action, GRANTED)
    
    return GRANTED
```

### 7.3 Evaluation Context

Ocena uprawnień uwzględnia:

1. **Static Context**
   - Role definicje
   - ACL definicje
   - Hierarchia ról

2. **Dynamic Context**
   - Current system state
   - Time of day
   - Operator location (IP)
   - Session state

3. **Environmental Context**
   - Current load
   - Maintenance mode
   - Emergency state

---

## 8. Permission Overrides

### 8.1 Temporary Overrides

Czasowe nadpisanie uprawnień dla specyficznych potrzeb.

```json
{
  "override_id": "OVERRIDE_2026_08_01_001",
  "role": "DEVELOPER",
  "resource_id": "MODULE_CRYPTO_ANALYZER",
  "additional_permissions": ["DEPLOY"],
  "effective_from": "2026-08-01T00:00:00Z",
  "effective_until": "2026-08-08T23:59:59Z",
  "requested_by": "SYSTEM_OWNER_01",
  "approved_by": "SYSTEM_OWNER_02",
  "reason": "Emergency deployment for critical bug fix",
  "status": "ACTIVE",
  "audit_required": true
}
```

### 8.2 Break-Glass Overrides

Mechanizm awaryjnego nadania pełnych uprawnień w sytuacjach kryzysowych.

```json
{
  "override_id": "BREAK_GLASS_001",
  "role": "OPERATIONS_LEAD",
  "temporary_role": "SYSTEM_ADMIN",
  "effective_from": "2026-08-01T10:00:00Z",
  "effective_until": "2026-08-01T12:00:00Z",
  "initiated_by": "SYSTEM_OWNER_01",
  "justification": "Emergency situation - System Orchestration failure",
  "required_approvals": ["SYSTEM_OWNER_01", "SYSTEM_OWNER_02"],
  "collected_approvals": ["SYSTEM_OWNER_01"],
  "status": "PENDING_APPROVAL",
  "notification_sent": true,
  "audit_trail": []
}
```

**Break-Glass Procedure:**
1. Operator identyfikuje sytuację kryzysową
2. System tworzy żądanie break-glass
3. Wymagane aprobaty od określonej liczby SYSTEM_OWNER
4. Po zatwierdzeniu, operator otrzymuje tymczasowe uprawnienia
5. Wszystkie akcje są rejestrowane z najwyższym priorytetem audytu
6. Po upływie czasu, uprawnienia są automatycznie cofane

### 8.3 Role-Based Overrides

Trwałe nadpisania uprawnień dla określonych ról.

```json
{
  "override_id": "ROOT_OVERRIDE_001",
  "role": "ANALYST",
  "resource_pattern": "REPORT_*",
  "permission": "EXECUTE",
  "value": true,
  "created_by": "SYSTEM_OWNER_01",
  "created_at": "2026-01-01T00:00:00Z",
  "reason": "Analysts need to execute report generation commands",
  "expiration": null
}
```

---

## 9. Temporary Permissions

### 9.1 Time-Limited Permissions

Uprawnienia przyznawane na określony czas.

**Use Cases:**
- Tymczasowy dostęp dla konsultantów zewnętrznych
- Okresowe zadania wymagające podwyższonych uprawnień
- Testowanie nowych funkcjonalności

```json
{
  ".permission_id": "TEMP_PERM_2026_08_01_001",
  "operator_id": "CONTRACTOR_001",
  "role": "TEMPORARY_ANALYST",
  "permissions": ["READ", "EXECUTE"],
  "resources": ["MODULE_MARKET_ANALYSIS", "PROCESS_DAILY_REPORT"],
  "valid_from": "2026-08-01T09:00:00Z",
  "valid_until": "2026-08-15T17:00:00Z",
  "created_by": "SYSTEM_OWNER_01",
  "auto_revoke": true,
  "notification_before_expiry": "24h",
  "status": "ACTIVE"
}
```

### 9.2 Session-Based Permissions

Uprawnienia przyznawane na czas trwania sesji.

```json
{
  "session_id": "SESS_2026_08_01_XYZ123",
  "operator_id": "OPERATOR_01",
  "temporary_permissions": [
    {
      "permission": "WRITE",
      "resource": "TEMP_CONFIG_001",
      "reason": "Configuration adjustment for testing",
      "granted_by": "SYSTEM_ADMIN_01"
    }
  ],
  "elevated_role": "SYSTEM_ADMIN",
  "elevation_reason": "Troubleshooting session",
  "audit_required": true
}
```

### 9.3 Just-In-Time Permissions

Uprawnienia przyznawane na żądanie, na krótki okres czasu.

```
Request:
{
  "operator_id": "DEVELOPER_01",
  "requested_permission": "DEPLOY",
  "resource_id": "MODULE_CRYPTO_001",
  "duration_minutes": 30,
  "reason": "Hotfix deployment approval received"
}

Response:
{
  "request_id": "JIT_2026_08_01_001",
  "status": "APPROVED",
  "temporary_token": "JIT_TOKEN_ABC123",
  "valid_until": "2026-08-01T11:00:00Z",
  "permissions_granted": ["DEPLOY"],
  "resources": ["MODULE_CRYPTO_001"],
  "approvals_required": 1,
  "approvals_collected": 1
}
```

---

## 10. Komponenty — Szczegóły Techniczne

### 10.1 Role Manager

**DESCRIPTION:**
Zarządza definicjami ról, hierarchią i relacjami między rolami.

**RESPONSIBILITIES:**
- Role creation, modification, deletion
- Hierarchy management
- Role assignment to operators
- Role validation

**INPUT:**
- Role definition requests
- Operator assignments

**PROCESS:**
1. Validate role definition
2. Check hierarchy consistency
3. Store role in database
4. Update role cache
5. Propagate changes to dependent services

**OUTPUT:**
- Role definitions
- Hierarchy information

**MEMORY USED:**
- Role Database
- Hierarchy Graph

**MEMORY UPDATED:**
- Role Cache
- Operator-Role Mapping

**COMMUNICATION:**
- Permission Evaluator (data)
- Audit Logger (events)

**ERROR HANDLING:**
- Invalid role definition → Reject with GOV_201
- Circular hierarchy → Reject with GOV_202
- Duplicate role name → Reject with GOV_203

**PERFORMANCE:**
- Role lookup: < 1ms
- Hierarchy traversal: < 5ms
- Cache update: < 10ms

**FUTURE EXTENSIONS:**
- Role versioning
- Role templates
- Bulk role management

---

### 10.2 Permission Evaluator

**DESCRIPTION:**
Ocenia uprawnienia dla żądań operatorów.

**RESPONSIBILITIES:**
- Permission evaluation
- ACL checking
- Constraint validation
- Approval management

**INPUT:**
- Permission evaluation requests
- Operator context
- Command context

**PROCESS:**
1. Extract role from operator
2. Get ACL for resource
3. Calculate effective permissions
4. Check against requested action
5. Validate constraints
6. Check approvals if required

**OUTPUT:**
- Evaluation result (GRANTED/DENIED/PENDING)
- Reason for decision

**MEMORY USED:**
- Role Database
- ACL Database
- Constraint Registry

**MEMORY UPDATED:**
- Access Logs
- Evaluation Cache

**COMMUNICATION:**
- Command Processor (requests)
- Approval Manager (approval checks)
- Audit Logger (logging)

**ERROR HANDLING:**
- Invalid role → Deny with GOV_007
- Permission denied → Deny with GOV_005
- Approval required → Pending with GOV_204

**PERFORMANCE:**
- Evaluation time: < 10ms
- Cache hit rate: > 90%

---

### 10.3 ACL Manager

**DESCRIPTION:**
Zarządza Access Control Lists dla zasobów.

**RESPONSIBILITIES:**
- ACL creation and management
- Template application
- ACL inheritance
- ACL validation

**INPUT:**
- ACL modification requests
- Resource creation events

**PROCESS:**
1. Validate ACL structure
2. Apply appropriate template
3. Check inheritance rules
4. Store ACL
5. Update ACL cache

**OUTPUT:**
- ACL definitions
- Effective permissions

**MEMORY USED:**
- ACL Database
- ACL Templates

**MEMORY UPDATED:**
- ACL Cache

**COMMUNICATION:**
- Permission Evaluator (ACL data)
- Resource Manager (resource events)

**ERROR HANDLING:**
- Invalid ACL → Reject with GOV_205
- Conflicting ACL → Reject with GOV_206

**PERFORMANCE:**
- ACL lookup: < 2ms
- Cache update: < 5ms

---

### 10.4 Approval Manager

**DESCRIPTION:**
Zarządza mechanizmami aprobat dla operacji wymagających podwyższonych uprawnień.

**RESPONSIBILITIES:**
- Approval request management
- Approver assignment
- Approval tracking
- Automatic approvals (where configured)

**INPUT:**
- Approval requests
- Approval responses

**PROCESS:**
1. Create approval request
2. Assign to required approvers
3. Track responses
4. Notificate requester of result
5. Enforce approval policies

**OUTPUT:**
- Approval status
- Required approvers list

**MEMORY USED:**
- Approval Requests Database
- Approver List
- Approval Policies

**MEMORY UPDATED:**
- Approval Status
- Audit Trail

**COMMUNICATION:**
- Notification Service (notifications)
- Permission Evaluator (status)
- Audit Logger (logging)

**ERROR HANDLING:**
- Approval timeout → Deny with GOV_207
- Insufficient approvers → Deny with GOV_208

**PERFORMANCE:**
- Request processing: < 100ms
- Status update: < 10ms

---

### 10.5 Override Manager

**DESCRIPTION:**
Zarządza czasowymi i stałymi nadpisaniami uprawnień.

**RESPONSIBILITIES:**
- Override creation and management
- Expiration handling
- Override application
- Audit of overrides

**INPUT:**
- Override requests
- Expiration events

**PROCESS:**
1. Validate override request
2. Check authorization
3. Apply override
4. Schedule expiration
5. Log override

**OUTPUT:**
- Active overrides list
- Effective permissions with overrides

**MEMORY USED:**
- Override Database
- Override Policies

**MEMORY UPDATED:**
- Active Overrides Cache
- Override Audit Log

**COMMUNICATION:**
- Permission Evaluator (override data)
- Scheduler (expiration events)

**ERROR HANDLING:**
- Unauthorized override → Reject with GOV_209
- Conflicting overrides → Reject with GOV_210

**PERFORMANCE:**
- Override lookup: < 5ms
- Cache update: < 10ms

---

### 10.6 Constraint Engine

**DESCRIPTION:**
Ocenia dodatkowe ograniczenia (constraints) na uprawnienia.

**RESPONSIBILITIES:**
- Constraint evaluation
- Dynamic constraint application
- Constraint validation

**INPUT:**
- Constraint evaluation requests
- Context information

**PROCESS:**
1. Load applicable constraints
2. Evaluate each constraint
3. Collect results
4. Return overall constraint status

**OUTPUT:**
- Constraint evaluation results
- Blocking constraints list

**MEMORY USED:**
- Constraint Registry
- Constraint Rules

**PERFORMANCE:**
- Constraint evaluation: < 5ms

**FUTURE EXTENSIONS:**
- Custom constraint types
- Constraint templates
- Constraint chaining

---

## 📝 Podsumowanie

**Permission Model** stanowi fundament bezpieczeństwa i kontroli dostępu w **System Governance**, zapewniając:

✅ **Precyzyjną kontrolę dostępu** za pomocą RBAC z elementami ABAC  
✅ **Hierarchię ról** z dziedziczeniem uprawnień  
✅ **Macierz uprawnień** dla wszystkich typów poleceń i zasobów  
✅ **Access Control Lists** dla precyzyjnej kontroli na poziomie zasobów  
✅ **Mechanizmy nadpisywania** uprawnień (tymczasowe i stałe)  
✅ **System aprobat** dla operacji krytycznych  
✅ **Ograniczenia kontekstowe** (time, location, system state)  
✅ **Pełny audyt** wszystkich decyzji autoryzacyjnych  

Architektura jest **w pełni kompatybilna** z zasadami SSI V5:
- **Separation of Concerns**: Oddzielny model uprawnień od mechanizmu przetwarzania
- **Principle of Least Privilege**: Minimalne uprawnienia dla każdej roli
- **Bezpieczeństwo**: Wszystkie dostępy są autoryzowane i rejestrowane
- **Skalowalność**: Obsługa złożonych struktur uprawnień
- **Audytowalność**: Pełna historia decyzji dostępna dla audytu

---

## 🎯 Next Steps

1. **Projekt Command Memory** (05_COMMAND_MEMORY.md)
2. **Bezpieczeństwo i Audyt** (06_SECURITY_AND_AUDIT.md)
3. **Przewodnik Integracji** (07_INTEGRATION_GUIDE.md)

---

**Generated by Mistral Vibe.**  
**Co-Authored-By: Mistral Vibe <vibe@mistral.ai>**  
**Version: 1.0.0 | Date: 2026-08-01**
