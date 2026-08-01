# SSI V5 Phase 2 — Command Processor

## 03. Command Processor Specification

**Wersja:** 1.0.0  
**Data:** 2026-08-01  
**Status:** ✅ COMPLETED  
**Poziom:** Technical Specification  
**Domena:** System Governance → Command Processing Engine

---

## 📋 Spis Treści

1. [Overview](#1-overview)
2. [Architecture](#2-architecture)
3. [Command Lifecycle](#3-command-lifecycle)
4. [Command Reception](#4-command-reception)
5. [Command Classification](#5-command-classification)
6. [Validation Pipeline](#6-validation-pipeline)
7. [Priority System](#7-priority-system)
8. [Command Queue](#8-command-queue)
9. [Conflict Resolution](#9-conflict-resolution)
10. [Orchestration Handoff](#10-orchestration-handoff)
11. [Komponenty — Szczegóły Techniczne](#11-komponenty--szczegóły-techniczne)

---

## 1. Overview

### 1.1 DESCRIPTION

**Command Processor** jest centralnym silnikiemetwarzania poleceń w warstwie **System Governance**. Odpowiada za odbiór, klasyfikację, walidację, priorytetyzację i przekazywanie poleceń operatora do **System Orchestration Engine** w celu wykonania.

Jest **mózgiem** System Governance — koordynuje cały przepływ poleceń od momentu ich odebrania przez **Governance Interface** aż do przekazania do odpowiednich modułów wykonawczych.

### 1.2 RESPONSIBILITIES

- **Command Reception**: Odbiór poleceń z Governance Interface
- **Command Classification**: Kategoryzacja poleceń według typu i charakteru
- **Pre-Validation**: Wstępna walidacja poprawności poleceń
- **Priority Assignment**: Przypisywanie priorytetów na podstawie reguł biznesowych
- **Queue Management**: Zarządzanie kolejką poleceń z uwzględnieniem priorytetów
- **Conflict Detection**: Wykrywanie i rozwałanie konfliktów między poleceniami
- **Dependency Resolution**: Rozwiązywanie zależności między poleceniami
- **Orchestration Handoff**: Przekazywanie zwalidowanych poleceń do System Orchestration
- **State Tracking**: Śledzenie stanu poleceń w czasie rzeczywistym

### 1.3 Place in SSI V5 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      SYSTEM GOVERNANCE LAYER                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌───────────────────────┐                                       │
│  │  GOVERNANCE           │                                       │
│  │  INTERFACE            │  ◄── Odbiór poleceń                │
│  └──────────┬──────────────┘                                       │
│             │                                                        │
│             ▼                                                        │
│  ┌─────────────────────────────┐                                  │
│  │     COMMAND PROCESSOR       │  ◄── PRZETWARZANIE POLECEŃ      │
│  │  (Silnik przetwarzania)      │  ▬ Klasyfikacja, walidacja,    │
│  │                             │  ▬ priorytety, kolejka           │
│  └──────────┬──────────────────────┘                                  │
│             │                                                        │
│             ▼                                                        │
│  ┌─────────────────────────────┐                                  │
│  │   SYSTEM ORCHESTRATION       │  ◄── Wykonanie poleceń        │
│  │   ENGINE                    │                                  │
│  └─────────────────────────────┘                                  │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 1.4 Key Principles

✅ **Single Responsibility**: Każdy komponent ma ściśle zdefiniowane zadania  
✅ **Priority-Based**: Polecenia są przetwarzane według priorytetów  
✅ **Conflict-Aware**: Wykrywa i rozpravia konflikty między poleceniami  
✅ **Stateful**: Śledzi stan każdego polecenia od odebrania do wykonania  
✅ **Idempotent**: Powtarzane polecenia nie powodują nieoczekiwanych efektów  
✅ **Audit-Friendly**: Pełna historia przetwarzania dostępna dla audytu  

---

## 2. Architecture

### 2.1 Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      COMMAND PROCESSOR                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────┐  │
│  │  COMMAND        │    │  CLASSIFIER      │    │ PRIORITY     │  │
│  │  RECEIVER       │───▶│  & CATEGORIZER   │───▶│ ASSIGNER     │  │
│  │  (Input Handler) │    │  (Type Detection)│    │ (Rule Engine) │  │
│  └─────────────────┘    └─────────────────┘    └───────┬─────┘  │
│                                                        │            │
│                                                        ▼            │
│  ┌─────────────────┐    ┌─────────────────┐            │          │
│  │  VALIDATION      │    │  DEPENDENCY      │            │          │
│  │  ENGINE          │───▶│  RESOLVER        │            │          │
│  │  (Pre-Check)     │    │  (Graph Analysis)│            │          │
│  └─────────────────┘    └─────────────────┘            │          │
│                                                        │            │
│                                                        ▼            │
│  ┌─────────────────┐    ┌─────────────────┐                  │          │
│  │  CONFLICT        │    │  QUEUE           │                  │          │
│  │  DETECTOR        │───▶│  MANAGER         │◀─────────────────┘          │
│  │  (Analysis)      │    │  (Prioritized)   │                                  │
│  └─────────────────┘    └─────────────────┘                                  │
│                                                        │                             │
│                                                        ▼                             │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    STATE TRACKER                          │   │
│  │  (Real-time command state monitoring)                   │   │
│  └─────────────────────────────┬───────────────────────────┘   │
│                                    │                             │
│                                    ▼                             │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              ORCHESTRATION HANDOFF                         │   │
│  │  (Communication with System Orchestration Engine)         │   │
│  └───────────────────────────────────────────────────────────┘   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Data Flow

```
Governance Interface
         │
         ▼
┌─────────────────┐
│  Command        │ ◄── Raw command from operator
│  Receiver       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Classifier &   │ ◄── Determine command type & category
│  Categorizer    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Validation     │ ◄── Pre-validate command structure
│  Engine         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Priority       │ ◄── Assign priority based on rules
│  Assigner      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Dependency     │ ◄── Resolve command dependencies
│  Resolver       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Conflict       │ ◄── Detect & resolve conflicts
│  Detector       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Queue         │ ◄── Add to prioritized queue
│  Manager       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  State         │ ◄── Track command state
│  Tracker       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Orchestration │ ◄── Handoff to System Orchestration
│  Handoff       │
└─────────────────┘
```

---

## 3. Command Lifecycle

### 3.1 Lifecycle Diagram

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   RECEIVED   │────▶│ CLASSIFIED   │────▶│ VALIDATED    │
└──────────────┘     └──────────────┘     └──────────────┘
         │                        │                    │
         │                        ▼                    ▼
         │               ┌──────────────┐     ┌──────────────┐
         │               │ PRIORITIZED  │     │ DEPENDENCY   │
         │               │              │     │ RESOLVED     │
         │               └──────────────┘     └──────────────┘
         │                        │                    │
         │                        ▼                    │
         │               ┌──────────────┐            │
         │               │ CONFLICT     │            │
         │               │ CHECKED      │◀───────────┘
         │               └──────────────┘
         │                        │
         │                        ▼
         │               ┌──────────────┐
         │               │ QUEUED       │
         │               └──────────────┘
         │                        │
         │                        ▼
         │               ┌──────────────┐
         └──────────────▶│ HANDOFF      │
                         │ (to Orchestration)
                         └──────────────┘
```

### 3.2 State Transitions

| Current State | Next State | Condition | Action |
|---------------|------------|-----------|--------|
| RECEIVED | CLASSIFIED | Command parsed successfully | Classify command |
| CLASSIFIED | VALIDATED | Pre-validation passed | Validate structure |
| VALIDATED | PRIORITIZED | Priority rules applied | Assign priority |
| PRIORITIZED | DEPENDENCY_RESOLVED | Dependencies checked | Resolve dependencies |
| DEPENDENCY_RESOLVED | CONFLICT_CHECKED | Conflict analysis complete | Check conflicts |
| CONFLICT_CHECKED | QUEUED | No conflicts or conflicts resolved | Add to queue |
| QUEUED | HANDOFF | Command at queue head | Send to Orchestration |

### 3.3 State Definitions

| State | Description | Timestamp | Persistence |
|-------|-------------|-----------|-------------|
| RECEIVED | Command received from Governance Interface | Reception time | ✅ Temporary |
| CLASSIFIED | Command type and category determined | After classification | ✅ Temporary |
| VALIDATED | Pre-validation checks passed | After validation | ✅ Temporary |
| PRIORITIZED | Priority assigned based on rules | After priority assignment | ✅ Temporary |
| DEPENDENCY_RESOLVED | Dependencies analyzed and resolved | After dependency resolution | ✅ Persistent |
| CONFLICT_CHECKED | Conflict detection and resolution complete | After conflict check | ✅ Persistent |
| QUEUED | Command in execution queue | Queue entry time | ✅ Persistent |
| HANDOFF | Command sent to System Orchestration | Handoff time | ✅ Persistent |

---

## 4. Command Reception

### 4.1 DESCRIPTION

**Command Receiver** jest pierwszym komponentem Command Processor, odpowiedzialnym za odbieranie poleceń z **Governance Interface** i przygotowywanie ich do dalszego przetwarzania.

### 4.2 RESPONSIBILITIES

- Receive commands from multiple input channels
- Normalize command format
- Assign unique command identifiers
- Initialize command context
- Acknowledge receipt to sender

### 4.3 INPUT

- Raw command from Governance Interface (JSON format)
- Authentication context (operator ID, session ID)
- Source information (channel, IP address, user agent)

### 4.4 PROCESS

1. **Reception**: Receive command via message queue or direct call
2. **Format Normalization**: Convert to internal command object format
3. **ID Assignment**: Generate unique command ID if not provided
4. **Context Initialization**: Create command execution context
5. **Timestamping**: Record reception timestamp with microsecond precision
6. **Acknowledgment**: Send ACK to Governance Interface

### 4.5 OUTPUT

- Command Object (normalized structure)
- Command Context (execution metadata)
- Reception ACK

### 4.6 MEMORY USED

- Command Registry (for duplicate detection)
- Operator Database (for context lookup)
- System Clock (for timestamping)

### 4.7 MEMORY UPDATED

- Active Commands (temporary storage)
- Reception Logs

### 4.8 COMMUNICATION

- Governance Interface (bidirectional)
- Classifier (unidirectional)

### 4.9 ERROR HANDLING

- Invalid command format → Reject with `GOV_001`
- Duplicate command ID → Reject with `GOV_009`
- Authentication context missing → Reject with `GOV_007`

### 4.10 PERFORMANCE

- Reception time: < 5ms per command
- Concurrent capacity: 1000+ commands/second
- Queue buffer: 10,000 commands

### 4.11 FUTURE EXTENSIONS

- Batch command reception
- Streaming command support
- Command deduplication cache

---

## 5. Command Classification

### 5.1 DESCRIPTION

**Classifier & Categorizer** analizuje odebrane polecenia i przypisuje im odpowiednią kategorię, typ oraz metadane niezbędne do dalszego przetwarzania.

### 5.2 RESPONSIBILITIES

- Identify command type from command object
- Determine command category (SYSTEM, MODULE, PROCESS, etc.)
- Extract command-specific parameters
- Validate command type exists in registry
- Assign classification metadata

### 5.3 Classification Hierarchy

```
COMMAND_TYPES
├── SYSTEM_COMMANDS
│   ├── START_SYSTEM
│   ├── STOP_SYSTEM
│   ├── RESTART_SYSTEM
│   └── SYSTEM_BACKUP
│
├── MODULE_COMMANDS
│   ├── CREATE_MODULE
│   ├── UPDATE_MODULE
│   ├── DELETE_MODULE
│   ├── ENABLE_MODULE
│   └── DISABLE_MODULE
│
├── PROCESS_COMMANDS
│   ├── START_PROCESS
│   ├── STOP_PROCESS
│   ├── PAUSE_PROCESS
│   ├── RESUME_PROCESS
│   └── MONITOR_PROCESS
│
├── CONFIGURATION_COMMANDS
│   ├── CONFIGURATION_CHANGE
│   ├── LOAD_CONFIG
│   ├── SAVE_CONFIG
│   └── RESET_CONFIG
│
├── DEVELOPMENT_COMMANDS
│   ├── REQUEST_ANALYSIS
│   ├── CREATE_TEACHER_MODEL
│   ├── CREATE_AGENT
│   └── DEPLOY_TO_PRODUCTION
│
├── MONITORING_COMMANDS
│   ├── SYSTEM_HEALTH_CHECK
│   ├── PERFORMANCE_AUDIT
│   ├── DIAGNOSE_ISSUE
│   └── GENERATE_REPORT
│
└── EMERGENCY_COMMANDS
    ├── EMERGENCY_STOP
    ├── ROLLBACK
    └── SYSTEM_LOCK
```

### 5.4 Classification Process

```
Input: Command Object
       │
       ▼
┌─────────────────┐
│  Type Detection │ ◄── Extract command_type field
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Category       │ ◄── Map type to category
│  Mapping        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Validation     │ ◄── Check type exists in registry
│  (Type Check)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Parameter      │ ◄── Extract and validate parameters
│  Extraction     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Metadata       │ ◄── Assign classification metadata
│  Assignment     │
└─────────────────┘
```

### 5.5 INPUT

- Command Object from Command Receiver
- Command Type Registry

### 5.6 PROCESS

1. Extract `command_type` field from command object
2. Lookup command type in Command Type Registry
3. Determine command category based on type
4. Extract command-specific parameters using type schema
5. Validate required parameters are present
6. Assign classification metadata (category, type, timestamp)

### 5.7 OUTPUT

- Classified Command Object
- Classification Metadata

### 5.8 MEMORY USED

- Command Type Registry
- Parameter Schemas
- Classification Rules

### 5.9 MEMORY UPDATED

- Classification Statistics
- Command Type Usage Logs

### 5.10 COMMUNICATION

- Command Receiver (input)
- Validation Engine (output)

### 5.11 ERROR HANDLING

- Unknown command type → Reject with `GOV_002`
- Missing required parameters → Reject with `GOV_002`
- Invalid parameter format → Reject with `GOV_003`

### 5.12 PERFORMANCE

- Classification time: < 10ms per command
- Type registry size: < 1MB (100+ command types)

---

## 6. Validation Pipeline

### 6.1 DESCRIPTION

**Validation Engine** wykonuje wielowarstwową wstępną walidację poleceń przed ich priorytetyzacją. Celem jest jak najszybsze wykrycie błędów, które uniemożliwią wykonanie polecenia.

### 6.2 Validation Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                    VALIDATION PIPELINE                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────┐    ┌─────────────────┐                   │
│  │   SYNTACTIC      │    │   STRUCTURAL    │                   │
│  │   VALIDATION     │───▶│   VALIDATION     │                   │
│  │  (Format Check)  │    │  (Schema Check)  │                   │
│  └─────────────────┘    └─────────────────┘                   │
│                                                        │            │
│                                                        ▼            │
│  ┌─────────────────┐    ┌─────────────────┐                   │
│  │   TYPE-SPECIFIC  │    │   BUSINESS       │                   │
│  │   VALIDATION     │───▶│   RULES          │                   │
│  │  (Parameters)    │    │  VALIDATION      │                   │
│  └─────────────────┘    └─────────────────┘                   │
│                                                        │            │
│                                                        ▼            │
│  ┌─────────────────┐    ┌─────────────────┐                   │
│  │   PERMISSION     │    │   CONTEXTUAL     │                   │
│  │   PRE-CHECK      │───▶│   VALIDATION     │                   │
│  └─────────────────┘    └─────────────────┘                   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 6.3 Validation Rules by Layer

#### Syntactic Validation
- ✅ Valid JSON structure (if JSON input)
- ✅ All values have correct data types
- ✅ No syntax errors in command structure

#### Structural Validation
- ✅ All required fields present
- ✅ No unknown fields (strict mode)
- ✅ Correct nesting structure
- ✅ Field length within limits

#### Type-Specific Validation
- ✅ Module name matches pattern `^[a-zA-Z][a-zA-Z0-9_]*$`
- ✅ Process ID matches pattern `^PROC_[A-Z0-9_]+$`
- ✅ Priority is from allowed enum
- ✅ Timestamps in ISO 8601 UTC format

#### Business Rules Validation
- ✅ Module name is not reserved
- ✅ Process can be started (not already running)
- ✅ Required system state for command
- ✅ Resource requirements can be met

#### Permission Pre-Check
- ✅ Operator has valid session
- ✅ Operator role exists
- ✅ Basic permission check (detailed in Permission Model)

#### Contextual Validation
- ✅ System is not in maintenance mode
- ✅ No conflicting commands in progress
- ✅ Dependencies can be satisfied

### 6.4 INPUT

- Classified Command Object
- Operator Context
- System State Snapshot

### 6.5 PROCESS

1. Run syntactic validation
2. If failed, return error
3. Run structural validation
4. If failed, return error
5. Run type-specific validation
6. If failed, return error
7. Run business rules validation
8. If failed, return error
9. Run permission pre-check
10. If failed, return error
11. Run contextual validation
12. If passed, mark as VALIDATED

### 6.6 OUTPUT

- Validation Result (PASSED/FAILED)
- List of validation errors (if any)
- Validation Token (if passed)

### 6.7 MEMORY USED

- Validation Rules Database
- System State Cache
- Permission Matrix (partial)

### 6.8 MEMORY UPDATED

- Validation Logs
- Validation Statistics

### 6.9 COMMUNICATION

- Classifier (input)
- Priority Assigner (output if passed)

### 6.10 ERROR HANDLING

- Any validation failure → Return specific error code
- Critical failures → Log and alert
- Non-critical warnings → Collect and include in response

### 6.11 PERFORMANCE

- Total validation time: < 50ms per command
- Parallel validation: Available for batch commands

---

## 7. Priority System

### 7.1 DESCRIPTION

**Priority Assigner** przypisuje priorytety poleceniom na podstawie zdefiniowanych reguł biznesowych, co umożliwia optymalne zarządzanie kolejką wykonania.

### 7.2 Priority Levels

| Level | Code | Description | Default Timeout | Example Commands |
|-------|------|-------------|-----------------|------------------|
| CRITICAL | 0 | System-critical operations | Immediate | EMERGENCY_STOP, SYSTEM_LOCK |
| HIGH | 1 | High-impact operational changes | 1 minute | CREATE_MODULE (production), DEPLOY_TO_PRODUCTION |
| NORMAL | 2 | Standard operational commands | 5 minutes | START_PROCESS, CONFIGURATION_CHANGE |
| LOW | 3 | Low-impact or background tasks | 1 hour | SYSTEM_HEALTH_CHECK, GENERATE_REPORT |
| BACKGROUND | 4 | Non-blocking maintenance | 4 hours | System cleanup, optimization |

### 7.3 Priority Assignment Rules

```
Priority = MAX(
    BasePriority(command_type),
    OperatorOverride(operator_role),
    SystemStateAdjustment(current_state),
    DependencyPriority(dependencies),
    SLARequirements(service_level)
)
```

#### Base Priority by Command Type

| Command Type | Base Priority | Rationale |
|--------------|----------------|-----------|
| EMERGENCY_STOP | CRITICAL (0) | Immediate system protection |
| ROLLBACK | CRITICAL (0) | Revert potentially harmful changes |
| SYSTEM_LOCK | CRITICAL (0) | Prevent system access |
| DEPLOY_TO_PRODUCTION | HIGH (1) | Production impact |
| CREATE_MODULE | HIGH (1) | New functionality |
| DELETE_MODULE | HIGH (1) | Irreversible action |
| START_PROCESS | NORMAL (2) | Standard operation |
| STOP_PROCESS | NORMAL (2) | Standard operation |
| CONFIGURATION_CHANGE | NORMAL (2) | System configuration |
| REQUEST_ANALYSIS | NORMAL (2) | Development task |
| SYSTEM_BACKUP | LOW (3) | Scheduled maintenance |
| GENERATE_REPORT | LOW (3) | Non-critical information |
| SYSTEM_HEALTH_CHECK | BACKGROUND (4) | Routine monitoring |

#### Operator Role Override

| Operator Role | Priority Boost | Max Priority |
|---------------|----------------|--------------|
| SYSTEM_OWNER | +0 (no change) | CRITICAL |
| SYSTEM_ADMIN | +0 (no change) | HIGH |
| DEVELOPMENT_LEAD | +0 (no change) | HIGH |
| ANALYST | +1 (downgrade) | NORMAL |
| AUTOMATION_AGENT | +0 (no change) | NORMAL |

#### System State Adjustment

| System State | Priority Adjustment |
|--------------|---------------------|
| Normal Operation | +0 (no change) |
| High Load | +1 (upgrade for maintenance) |
| Maintenance Mode | +2 (upgrade for critical) |
| Emergency State | +0 (all commands CRITICAL) |

### 7.4 Priority Assignment Process

```
Input: Validated Command Object
       │
       ▼
┌─────────────────┐
│  Base Priority   │ ◄── Get base priority from command type
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Operator        │ ◄── Apply role-based adjustment
│  Adjustment      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  System State   │ ◄── Apply system state adjustment
│  Adjustment     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Dependency     │ ◄── Consider dependency priorities
│  Analysis       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Final Priority │ ◄── Calculate final priority
│  Determination   │
└─────────────────┘
```

### 7.5 INPUT

- Validated Command Object
- Operator Role
- Current System State
- Command Dependencies

### 7.6 PROCESS

1. Get base priority from command type registry
2. Apply operator role adjustment
3. Apply system state adjustment
4. Analyze dependency priorities
5. Consider SLA requirements
6. Calculate final priority as maximum of all factors
7. Cap at maximum allowed priority for operator role

### 7.7 OUTPUT

- Command Object with assigned priority
- Priority assignment rationale

### 7.8 MEMORY USED

- Priority Rules Database
- System State Cache
- Operator Roles Database

### 7.9 MEMORY UPDATED

- Priority Assignment Logs

### 7.10 COMMUNICATION

- Validation Engine (input)
- Dependency Resolver (output)

### 7.11 ERROR HANDLING

- Unknown command type → Use NORMAL priority
- Invalid operator role → Use NORMAL priority
- System state unavailable → Use NORMAL priority

### 7.12 PERFORMANCE

- Priority assignment time: < 5ms per command

---

## 8. Command Queue

### 8.1 DESCRIPTION

**Queue Manager** zarządza kolejką poleceń oczekujących na wykonanie, uwzględniając ich priorytety, zależności i potencjalne konflikty.

### 8.2 Queue Structure

Kolejka implementuje **Priority Queue** z następującymi cechami:
- Polecenia są sortowane według priorytetu (CRITICAL > HIGH > NORMAL > LOW > BACKGROUND)
- W ramach tego samego priorytetu: FIFO (First In, First Out)
- Polecenia z zależnościami są blokowane do momentu spełnienia zależności
- Polecenia w konflikcie są oznaczone i wymagają rozwiązania

```
┌─────────────────────────────────────────────────────────────────┐
│                      COMMAND QUEUE                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Priority Level 0 (CRITICAL):                                    │
│  ├── CMD_001 (EMERGENCY_STOP) - Ready                            │
│  └── CMD_002 (SYSTEM_LOCK) - Ready                              │
│                                                                   │
│  Priority Level 1 (HIGH):                                        │
│  ├── CMD_003 (CREATE_MODULE) - Ready                             │
│  ├── CMD_004 (DEPLOY_TO_PRODUCTION) - Waiting (dependency)         │
│  └── CMD_005 (UPDATE_MODULE) - Ready                             │
│                                                                   │
│  Priority Level 2 (NORMAL):                                      │
│  ├── CMD_006 (START_PROCESS) - Ready                             │
│  ├── CMD_007 (CONFIGURATION_CHANGE) - Ready                      │
│  └── CMD_008 (REQUEST_ANALYSIS) - Conflict (with CMD_006)         │
│                                                                   │
│  Priority Level 3 (LOW):                                          │
│  ├── CMD_009 (SYSTEM_BACKUP) - Scheduled (2026-08-01T12:00)      │
│  └── CMD_010 (GENERATE_REPORT) - Ready                            │
│                                                                   │
│  Priority Level 4 (BACKGROUND):                                   │
│  └── CMD_011 (SYSTEM_HEALTH_CHECK) - Ready                        │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 8.3 Queue Operations

#### Enqueue (Add to Queue)
```
Input: Prioritized Command Object
       │
       ▼
┌─────────────────┐
│  Check          │ ◄── Can command be queued?
│  Dependencies   │
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
│ Add to      │ │ Mark as     │
│ Queue       │ │ Waiting     │
└─────────────┘ └─────────────┘
```

#### Dequeue (Get Next Command)
```
┌─────────────────┐
│  Check Queue    │ ◄── Any commands?
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
│ Get Highest │ │ Return      │
│ Priority    │ │ EMPTY       │
│ Ready       │ │             │
│ Command     │ │             │
└─────────────┘ └─────────────┘
```

#### Requeue (Retry/Reschedule)
- Return command to queue with updated priority
- Used for transient failures or manual retries

### 8.4 Queue States

| State | Description | Transition |
|-------|-------------|------------|
| READY | Command ready for execution | Dequeued or Timeout |
| WAITING | Command waiting for dependencies | Enqueued when ready |
| CONFLICT | Command in conflict with others | Resolved → READY |
| BLOCKED | Command blocked by system state | Unblocked → READY |
| TIMEOUT | Command execution timed out | Requeued or Failed |

### 8.5 INPUT

- Prioritized Command Object
- Dependency Resolution Result
- Conflict Detection Result

### 8.6 PROCESS

**Enqueue:**
1. Check if command has unmet dependencies
2. If yes, mark as WAITING
3. If no, check for conflicts
4. If conflicts, mark as CONFLICT
5. If no conflicts, add to queue with priority
6. Update queue statistics

**Dequeue:**
1. Check queue for commands
2. Find highest priority READY command
3. Remove from queue
4. Return command for handoff

### 8.7 OUTPUT

- Queue position for newly added commands
- Next command for execution
- Queue statistics and metrics

### 8.8 MEMORY USED

- Command Queue (in-memory with persistence)
- Dependency Graph
- Conflict Matrix

### 8.9 MEMORY UPDATED

- Queue State
- Command Positions
- Queue Metrics

### 8.10 COMMUNICATION

- Dependency Resolver (input)
- Conflict Detector (input)
- Orchestration Handoff (output)

### 8.11 ERROR HANDLING

- Queue full → Reject with `GOV_011` (507 Insufficient Storage)
- Dependency loop detected → Reject with `GOV_012` (400 Bad Request)
- Command already in queue → Return existing position

### 8.12 PERFORMANCE

- Enqueue time: < 1ms per command
- Dequeue time: < 1ms per command
- Maximum queue size: 100,000 commands
- Memory per command: ~512 bytes

---

## 9. Conflict Resolution

### 9.1 DESCRIPTION

**Conflict Detector** identyfikuje potencjalne konflikty między poleceniami i zapewnia mechanizmy ich rozwiązywania.

### 9.2 Conflict Types

#### Resource Conflicts
- Two commands require the same exclusive resource
- Example: Two CREATE_MODULE commands for the same module name

#### State Conflicts
- Commands that cannot both succeed given current system state
- Example: START_PROCESS and STOP_PROCESS for the same process

#### Dependency Conflicts
- Circular dependencies between commands
- Example: Command A depends on Command B, which depends on Command A

#### Logical Conflicts
- Commands whose combined execution would violate business rules
- Example: ENABLE_MODULE and DISABLE_MODULE for the same module simultaneously

### 9.3 Conflict Matrix

```
┌─────────────────────────────────────────────────────────────────────┐
│ CONFLICT MATRIX                                                      │
├─────────────────────────────────────────────────────────────────────┤
│ Command A →         │ CREATE_ │ START_ │ STOP_  │ DELETE_│ UPDATE_│       │
│ Command B ↓         │ MODULE │ PROCESS│ PROCESS│ MODULE │ MODULE │       │
├────────────────────┼────────┼────────┼────────┼────────┼────────┤░      │
│ CREATE_MODULE       │   ❌   │   ✅   │   ✅   │   ❌   │   ⚠️   │       │
│ START_PROCESS       │   ✅   │   ❌   │   ❌   │   ✅   │   ✅   │       │
│ STOP_PROCESS        │   ✅   │   ❌   │   ❌   │   ✅   │   ✅   │       │
│ DELETE_MODULE       │   ❌   │   ✅   │   ✅   │   ❌   │   ❌   │       │
│ UPDATE_MODULE       │   ⚠️   │   ✅   │   ✅   │   ❌   │   ❌   │       │
└────────────────────┴────────┴────────┴────────┴────────┴─────┴───────┘

Legenda:
❌ = Hard Conflict (cannot both execute)
⚠️ = Soft Conflict (requires ordering)
✅ = No Conflict
```

### 9.4 Conflict Resolution Strategies

#### Priority-Based Resolution
- Higher priority command executes first
- Lower priority command is queued or rejected

#### Chronological Resolution
- First-received command executes first
- Later command is queued or rejected

#### Manual Resolution
- Operator must explicitly resolve conflict
- System provides conflict details and resolution options

#### Automatic Merge (where possible)
- Some commands can be merged (e.g., multiple CONFIGURATION_CHANGE)
- System automatically merges compatible commands

### 9.5 Conflict Detection Process

```
Input:classified and prioritized command
       │
       ▼
┌─────────────────┐
│  Static         │ ◄── Check predefined conflict matrix
│  Conflict Check │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Dynamic        │ ◄── Check current system state
│  Conflict Check │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Resource       │ ◄── Check resource availability
│  Conflict Check │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Conflict       │ ◄── If conflicts found
│  Resolution     │
└─────────────────┘
```

### 9.6 INPUT

- Prioritized Command Object
- Current Queue State
- System State Snapshot

### 9.7 PROCESS

1. Check static conflict matrix for command type pairs
2. Analyze dynamic system state for potential conflicts
3. Check resource availability and locks
4. If conflicts found:
   a. Identify conflict type
   b. Determine resolution strategy
   c. Apply resolution (queue, reject, or request manual)
5. If no conflicts, mark as CONFLICT_CHECKED

### 9.8 OUTPUT

- Conflict Detection Result
- Resolution Recommendation (if applicable)

### 9.9 MEMORY USED

- Conflict Matrix
- Resource Lock Registry
- System State Cache

### 9.10 MEMORY UPDATED

- Conflict Log
- Resolution History

### 9.11 COMMUNICATION

- Queue Manager (input)
- Orbchestration Handoff (output)

### 9.12 ERROR HANDLING

- Conflict resolution timeout → Escalate to operator
- Cannot resolve conflict → Reject with `GOV_013` (409 Conflict)

### 9.13 PERFORMANCE

- Conflict detection time: < 20ms per command

---

## 10. Orchestration Handoff

### 10.1 DESCRIPTION

**Orchestration Handoff** jest ostatnim etapem Command Processor, odpowiedzialnym za przekazywanie zwalidowanych, zaklasyfikowanych i spriorytetyzowanych poleceń do **System Orchestration Engine** w celu wykonania.

### 10.2 RESPONSIBILITIES

- Prepare command for Orchestration Engine
- Establish connection with Orchestration Engine
- Send command with all required context
- Receive and process acknowledgment
- Handle communication errors
- Track handoff status

### 10.3 Handoff Process

```
Input: Queued Command (next in line)
       │
       ▼
┌─────────────────┐
│  Prepare        │ ◄── Create task object for Orchestration
│  Task Object    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Establish     │ ◄── Connect to Orchestration Engine
│  Connection    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Send Command   │ ◄── Transmit command and context
│  & Context      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Wait for       │ ◄── Await acknowledgment
│  ACK           │
└────────┬────────┘
         │
    ┌────▼────┐
    │         │
    ▼         ▼
┌────────┐ ┌──────────┐
│ Success │ │ Failure  │
└────┬────┘ └────┬─────┘
     │            │
     ▼            ▼
┌─────────────┐ ┌─────────────┐
│ Mark as     │ │ Requeue or  │
│ HANDOFF     │ │ Reject      │
└─────────────┘ └─────────────┘
```

### 10.4 Task Object Structure

```json
{
  "task_id": "TASK_2026_08_01_0001",
  "command_id": "CMD_2026_08_01_0001",
  "session_id": "SESS_2026_08_01_ABC123",
  "operator_id": "SYSTEM_OWNER_01",
  "command_type": "CREATE_MODULE",
  "priority": "HIGH",
  "priority_code": 1,
  "parameters": {
    "module_name": "CryptocurrencyMarketAnalyzer",
    "module_type": "ANALYSIS",
    "description": "Module for cryptocurrency market analysis"
  },
  "validation_token": "VAL_TOKEN_XYZ789",
  "dependencies": [],
  "conflict_resolution": null,
  "timestamp": "2026-08-01T10:00:05.123Z",
  "hand-off_timestamp": "2026-08-01T10:05:00.000Z",
  "metadata": {
    "source": "governance_interface",
    "classification": {
      "category": "MODULE_COMMANDS",
      "type": "CREATE_MODULE"
    },
    "validation": {
      "syntactic": true,
      "structural": true,
      "semantic": true,
      "business": true,
      "permission": true,
      "contextual": true
    }
  }
}
```

### 10.5 INPUT

- Command Object from Queue Manager
- System Orchestration Endpoint Configuration

### 10.6 PROCESS

1. Create Task Object from Command Object
2. Establish secure connection to System Orchestration Engine
3. Send Task Object via gRPC/REST
4. Wait for acknowledgment (with timeout)
5. On success: Mark command as HANDOFF
6. On failure: Apply retry policy or reject

### 10.7 OUTPUT

- Handoff Confirmation
- Task ID from Orchestration Engine
- Orchestration Token

### 10.8 MEMORY USED

- Task Templates
- Connection Pool
- Orchestration Configuration

### 10.9 MEMORY UPDATED

- Handoff Logs
- Task Registry

### 10.10 COMMUNICATION

- System Orchestration Engine (bidirectional)
- Queue Manager (input)
- State Tracker (output)

### 10.11 ERROR HANDLING

- Connection failed → Retry with backoff
- Timeout → Requeue or escalate
- Orchestration rejected → Reject with reason
- Serialization error → Reject with `GOV_014` (500 Internal Error)

### 10.12 PERFORMANCE

- Handoff time: < 100ms per command
- Connection pool: 50 concurrent connections
- Retry policy: 3 attempts with exponential backoff

---

## 11. Komponenty — Szczegóły Techniczne

### 11.1 Command Receiver

**DESCRIPTION:**
Odbiera polecenia z Governance Interface i inicjuje ich przetwarzanie.

**INPUT:**
- Raw command from Governance Interface
- Authentication context

**PROCESS:**
1. Receive and parse command
2. Normalize format
3. Assign unique ID
4. Initialize context
5. Timestamp
6. Send ACK

**OUTPUT:**
- Command Object
- Command Context

**MEMORY USED:**
- Command Registry
- Operator Database

**MEMORY UPDATED:**
- Active Commands
- Reception Logs

**COMMUNICATION:**
- Governance Interface (bidirectional)
- Classifier (unidirectional)

**ERROR HANDLING:**
- Invalid format → `GOV_001`
- Duplicate ID → `GOV_009`
- Missing context → `GOV_007`

**PERFORMANCE:**
- Reception: < 5ms/command
- Throughput: 1000+/second

**FUTURE EXTENSIONS:**
- Batch reception
- Streaming support

---

### 11.2 Classifier & Categorizer

**DESCRIPTION:**
Klasyfikuje polecenia według typu i kategorii.

**INPUT:**
- Command Object
- Command Type Registry

**PROCESS:**
1. Extract command_type
2. Lookup in registry
3. Determine category
4. Extract parameters
5. Validate type
6. Assign metadata

**OUTPUT:**
- Classified Command Object
- Classification Metadata

**MEMORY USED:**
- Command Type Registry
- Parameter Schemas

**MEMORY UPDATED:**
- Classification Statistics

**ERROR HANDLING:**
- Unknown type → `GOV_002`
- Missing parameters → `GOV_002`

**PERFORMANCE:**
- Classification: < 10ms/command

---

### 11.3 Validation Engine

**DESCRIPTION:**
Wykonuje wielowarstwową walidację poleceń.

**INPUT:**
- Classified Command Object
- System State

**PROCESS:**
1. Run all 6 validation layers
2. Collect errors
3. Determine status
4. Generate token if passed

**OUTPUT:**
- Validation Result
- Errors/Warnings
- Validation Token

**MEMORY USED:**
- Validation Rules
- System State Cache

**ERROR HANDLING:**
- Any failure → Appropriate error code

**PERFORMANCE:**
- Validation: < 50ms/command

---

### 11.4 Priority Assigner

**DESCRIPTION:**
Przypisuje priorytety poleceniom.

**INPUT:**
- Validated Command Object
- Operator Role
- System State

**PROCESS:**
1. Get base priority
2. Apply role adjustment
3. Apply state adjustment
4. Analyze dependencies
5. Calculate final priority

**OUTPUT:**
- Command with Priority
- Assignment Rationale

**MEMORY USED:**
- Priority Rules
- System State Cache

**PERFORMANCE:**
- Assignment: < 5ms/command

---

### 11.5 Dependency Resolver

**DESCRIPTION:**
Rozwiązuje zależności między poleceniami.

**INPUT:**
- Prioritized Command Object
- Dependency Graph

**PROCESS:**
1. Extract dependencies
2. Check availability
3. Build dependency graph
4. Detect cycles
5. Resolve order

**OUTPUT:**
- Resolved Dependencies
- Wait Conditions

**MEMORY USED:**
- Dependency Graph
- Resource State

**ERROR HANDLING:**
- Circular dependency → `GOV_012`
- Missing dependency → WAIT

**PERFORMANCE:**
- Resolution: < 15ms/command

---

### 11.6 Conflict Detector

**DESCRIPTION:**
Wykrywa i rozwiązuje konflikty między poleceniami.

**INPUT:**
- Prioritized Command Object
- Queue State
- System State

**PROCESS:**
1. Check conflict matrix
2. Analyze system state
3. Check resource locks
4. Resolve conflicts

**OUTPUT:**
- Conflict Detection Result
- Resolution Recommendation

**MEMORY USED:**
- Conflict Matrix
- Resource Locks

**ERROR HANDLING:**
- Unresolvable conflict → `GOV_013`

**PERFORMANCE:**
- Detection: < 20ms/command

---

### 11.7 Queue Manager

**DESCRIPTION:**
Zarządza kolejką poleceń.

**INPUT:**
- Prioritized Command Object
- Dependency Result
- Conflict Result

**PROCESS:**
1. Check dependencies
2. Check conflicts
3. Add to queue
4. Track position

**OUTPUT:**
- Queue Position
- Next Command
- Queue Metrics

**MEMORY USED:**
- Command Queue
- Dependency Graph
- Conflict Matrix

**ERROR HANDLING:**
- Queue full → `GOV_011`
- Dependency loop → `GOV_012`

**PERFORMANCE:**
- Enqueue/Dequeue: < 1ms/command
- Max size: 100,000 commands

---

### 11.8 State Tracker

**DESCRIPTION:**
Śledzi stan poleceń w czasie rzeczywistym.

**INPUT:**
- Command Events
- State Transitions

**PROCESS:**
1. Record state changes
2. Update timestamps
3. Maintain history
4. Generate metrics

**OUTPUT:**
- Current State
- State History
- Metrics

**MEMORY USED:**
- Command States
- State History

**PERFORMANCE:**
- Update: < 1ms/change

---

### 11.9 Orchestration Handoff

**DESCRIPTION:**
Przekazuje polecenia do System Orchestration.

**INPUT:**
- Queued Command Object
- Orchestration Config

**PROCESS:**
1. Create Task Object
2. Establish connection
3. Send command
4. Wait for ACK

**OUTPUT:**
- Handoff Confirmation
- Task ID

**COMMUNICATION:**
- System Orchestration Engine

**ERROR HANDLING:**
- Connection failure → Retry
- Timeout → Requeue

**PERFORMANCE:**
- Handoff: < 100ms/command

---

## 📝 Podsumowanie

**Command Processor** jest centralnym komponentem **System Governance**, zapewniając:

✅ **Kompleksowe przetwarzanie poleceń** od odbioru do przekazania do wykonania  
✅ **Inteligentną klasyfikację** i walidację poleceń  
✅ **System priorytetów** z wieloma czynnikami wpływającymi na kolejność  
✅ **Zarządzanie kolejką** z uwzględnieniem priorytetów, zależności i konfliktów  
✅ **Wykrywanie i rozważanie konfliktów** między poleceniami  
✅ **Bezproblemową integrację** z System Orchestration Engine  
✅ **Pełne śledzenie stanu** poleceń w czasie rzeczywistym  

Architektura jest **w pełni kompatybilna** z zasadami SSI V5:
- **Separation of Concerns**: Każdy komponent ma ściśle zdefiniowane zadania
- **Niezmienność**: Polecenia nie modyfikują danych źródłowych
- **Bezpieczeństwo**: Wszystkie operacje są walidowane i autoryzowane
- **Skalowalność**: Obsługa wielkich wolumenów poleceń
- ** niezbędna**: Pełna historia przetwarzania dostępna dla audytu

---

## 🎯 Next Steps

1. **Definicja Permission Model** (04_PERMISSION_MODEL.md)
2. **Projekt Command Memory** (05_COMMAND_MEMORY.md)
3. **Bezpieczeństwo i Audyt** (06_SECURITY_AND_AUDIT.md)
4. **Przewodnik Integracji** (07_INTEGRATION_GUIDE.md)

---

**Generated by Mistral Vibe.**  
**Co-Authored-By: Mistral Vibe <vibe@mistral.ai>**  
**Version: 1.0.0 | Date: 2026-08-01**
