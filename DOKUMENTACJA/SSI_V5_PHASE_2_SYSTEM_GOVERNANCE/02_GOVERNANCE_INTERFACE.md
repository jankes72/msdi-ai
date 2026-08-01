# SSI V5 Phase 2 — Governance Interface

## 02. Governance Interface Specification

**Wersja:** 1.0.0  
**Data:** 2026-08-01  
**Status:** ✅ COMPLETED  
**Poziom:** Technical Specification  
**Domena:** System Governance → Operator Communication

---

## 📋 Spis Treści

1. [Overview](#1-overview)
2. [Architecture](#2-architecture)
3. [Governance API](#3-governance-api)
4. [Command Input Interface](#4-command-input-interface)
5. [JSON Format Specifications](#5-json-format-specifications)
6. [Input Validation](#6-input-validation)
7. [Response Statuses](#7-response-statuses)
8. [Error Handling](#8-error-handling)
9. [Communication with System Orchestration](#9-communication-with-system-orchestration)
10. [Komponenty — Szczegóły Techniczne](#10-komponenty--szczegóły-techniczne)

---

## 1. Overview

### 1.1 DESCRIPTION

**Governance Interface** jest głównym punktem wejścia dla komunikacji między **SYSTEM OWNER** (operatorem) a **System Governance**. Stanowi warstwę abstrakcji, która umożliwia operatorowi wydawanie poleceń administracyjnych w sposób strukturyzowany, bezpieczeczny i audytowalny.

Interfejs jest **multi-protocol**, obsługując różne metody wprowadzania poleceń:
- **CLI** (Command Line Interface)
- **REST API** (HTTP/HTTPS)
- **gRPC** (High-performance RPC)
- **WebSocket** (Real-time bidirectional)
- **Direct SDK** (Programmatic access)

### 1.2 RESPONSIBILITIES

- **Authentication**: Weryfikacja tożsamości operatora
- **Command Parsing**: Przetwarzanie różnorodnych formatów wejściowych
- **Input Validation**: Walidacja struktury i treści poleceń
- **Session Management**: Zarządzanie aktywnymi sesjami poleceń
- **Response Formatting**: Standaryzacja odpowiedzi dla klienta
- **Audit Logging**: Rejestrowanie wszystkich interakcji

### 1.3 Place in SSI V5 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     SYSTEM GOVERNANCE LAYER                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌───────────────────────┐                                       │
│  │  GOVERNANCE           │                                       │
│  │  INTERFACE            │  ◄── GŁÓWNY PUNKT WEJŚCIA             │
│  └──────────┬──────────────┘                                       │
│             │                                                        │
│             ├─── CLI Interface (Terminal)                           │
│             ├─── REST API (HTTP/HTTPS)                              │
│             ├─── gRPC Service (Binary Protocol)                    │
│             ├─── WebSocket (Real-time)                              │
│             └─── Direct SDK (Programmatic)                          │
│             │                                                        │
│             ▼                                                        │
│  ┌─────────────────────────────┐                                  │
│  │   COMMAND PROCESSOR          │  ◄── Przetwarzanie poleceń      │
│  └─────────────────────────────┘                                  │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 1.4 Key Principles

✅ **Single Entry Point**: Wszystkie polecenia operatora przechodzą przez Governance Interface  
✅ **Protocol Agnostic**: Obsługa wielu protokołów komunikacyjnych  
✅ **Backward Compatible**: Wsparcie dla starszych wersji API  
✅ **Audit Trail**: Żadne polecenie nie jest przegapione w logach  
✅ **Security First**: Wszystkie połączenia są szyfrowane i autoryzowane  

---

## 2. Architecture

### 2.1 Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    GOVERNANCE INTERFACE                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────┐  │
│  │  AUTHENTICATION  │    │   REQUEST        │    │  SESSION    │  │
│  │  MANAGER         │    │   ROUTER         │    │  MANAGER    │  │
│  └──────────┬──────┘    └──────────┬──────┘    └───────┬─────┘  │
│             │                      │                 │        │
│             ▼                      ▼                 ▼        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    COMMAND PARSER                          │   │
│  │  (JSON/XML/Plain Text → Command Object)                   │   │
│  └─────────────────────────────┬───────────────────────────┘   │
│                                    │                             │
│                                    ▼                             │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                 VALIDATION LAYER                           │   │
│  │  (Schema, Business Logic, Permission Pre-Check)           │   │
│  └─────────────────────────────┬───────────────────────────┘   │
│                                    │                             │
│                                    ▼                             │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                 RESPONSE FORMATTER                         │   │
│  │  (Command Object → Standardized Response)                 │   │
│  └───────────────────────────────────────────────────────────┘   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Data Flow

```
Operator Input (CLI/API/SDK)
       │
       ▼
┌─────────────────┐
│  Protocol        │ ◄── HTTP/gRPC/WS/CLI
│  Adapter         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Authentication  │ ◄── JWT/API Key/Certificate
│  & Authorization │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Request        │ ◄── Routing based on type
│  Router         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Command        │ ◄── Parse & validate
│  Parser         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Validation     │ ◄── Schema + business rules
│  Layer          │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Session        │ ◄── Create managed session
│  Manager        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Response       │ ◄── Format standardized output
│  Formatter      │
└────────┬────────┘
         │
         ▼
   Command Processor
```

---

## 3. Governance API

### 3.1 API Overview

| Aspect | Description |
|--------|-------------|
| **Base URL** | `https://governance.ssi-v5.internal/api/v1` |
| **Content-Type** | `application/json` (primary), `application/x-www-form-urlencoded` (legacy) |
| **Authentication** | Bearer Token (JWT), API Key, Mutual TLS |
| **Rate Limiting** | 100 requests/minute (default), configurable per role |
| **CORS** | Disabled for internal use, configurable for external |
| **Versioning** | URL path (`/v1/`), Header (`Accept: application/vnd.ssi.v1+json`) |

### 3.2 Endpoints

#### Command Submission

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|----------------|
| POST | `/commands` | Submit new command | ✅ |
| POST | `/commands/batch` | Submit multiple commands | ✅ |
| GET | `/commands/{id}` | Get command status | ✅ |
| GET | `/commands` | List recent commands | ✅ |
| DELETE | `/commands/{id}` | Cancel pending command | ✅ |

#### Session Management

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|----------------|
| POST | `/sessions` | Create new session | ✅ |
| GET | `/sessions/{id}` | Get session details | ✅ |
| DELETE | `/sessions/{id}` | Terminate session | ✅ |
| GET | `/sessions` | List active sessions | ✅ |

#### System Information

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|----------------|
| GET | `/status` | System status | ✅ |
| GET | `/capabilities` | Available command types | ✅ |
| GET | `/health` | Health check | ❌ (optional) |

### 3.3 gRPC Service Definition

```protobuf
service GovernanceInterface {
  // Submit a single command
  rpc SubmitCommand (CommandRequest) returns (CommandResponse);
  
  // Submit multiple commands in batch
  rpc SubmitCommandBatch (CommandBatchRequest) returns (CommandBatchResponse);
  
  // Get command execution status
  rpc GetCommandStatus (CommandStatusRequest) returns (CommandStatusResponse);
  
  // Create a new session
  rpc CreateSession (SessionRequest) returns (SessionResponse);
  
  // Stream command results (WebSocket alternative)
  rpc StreamCommands (stream CommandRequest) returns (stream CommandResponse);
}

message CommandRequest {
  string command_id = 1;
  string session_id = 2;
  string operator_id = 3;
  string command_type = 4;
  map<string, string> parameters = 5;
  map<string, string> metadata = 6;
  string signature = 7;
  int64 timestamp = 8;
}

message CommandResponse {
  string command_id = 1;
  string status = 2; // PENDING, PROCESSING, COMPLETED, FAILED
  string result = 3;
  repeated string errors = 4;
  repeated string warnings = 5;
  int64 processing_time_ms = 6;
  string session_id = 7;
}
```

---

## 4. Command Input Interface

### 4.1 Input Methods

#### CLI Interface

```bash
# Submit command via CLI
ssi-governance submit --command CREATE_MODULE \
  --param module_name=CryptoAnalyzer \
  --param module_type=ANALYSIS \
  --param description="Krypto market analysis module" \
  --priority HIGH \
  --format json

# Check command status
ssi-governance status CMD_2026_08_01_0001

# List recent commands
ssi-governance list --limit 10 --filter "CREATE_MODULE"

# Interactive mode
ssi-governance interactive
```

#### REST API Example

```bash
# Submit command
curl -X POST \
  https://governance.ssi-v5.internal/api/v1/commands \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "X-Operator-ID: SYSTEM_OWNER_01" \
  -d '{
    "command_type": "CREATE_MODULE",
    "parameters": {
      "module_name": "Cryptocurrency市场Analyzer",
      "module_type": "ANALYSIS",
      "description": "Module for cryptocurrency market analysis"
    },
    "priority": "HIGH",
    "metadata": {
      "source": "rest_api",
      "client_version": "1.0.0"
    }
  }'

# Check status
curl -X GET \
  https://governance.ssi-v5.internal/api/v1/commands/CMD_2026_08_01_0001 \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

#### SDK Example (Python)

```python
from ssi_v5.governance import GovernanceClient

# Initialize client
client = GovernanceClient(
    base_url="https://governance.ssi-v5.internal",
    api_key="YOUR_API_KEY",
    operator_id="SYSTEM_OWNER_01"
)

# Submit command
response = client.submit_command(
    command_type="CREATE_MODULE",
    parameters={
        "module_name": "CryptoAnalyzer",
        "module_type": "ANALYSIS",
        "description": "Cryptocurrency analysis module"
    },
    priority="HIGH"
)

print(f"Command ID: {response.command_id}")
print(f"Status: {response.status}")

# Check status
status = client.get_command_status(response.command_id)
print(f"Execution: {status.execution_percentage}%")
```

---

## 5. JSON Format Specifications

### 5.1 Command Request Structure

```json
{
  "header": {
    "command_id": "CMD_2026_08_01_0001",
    "session_id": "SESS_2026_08_01_ABC123",
    "operator_id": "SYSTEM_OWNER_01",
    "timestamp": "2026-08-01T10:00:00.000Z",
    "version": "1.0",
    "signature": "SHA256_HMAC_HEX_STRING"
  },
  "body": {
    "command_type": "CREATE_MODULE",
    "parameters": {
      "module_name": "CryptocurrencyMarketAnalyzer",
      "module_type": "ANALYSIS",
      "description": "Module for analyzing cryptocurrency markets",
      "priority": "HIGH",
      "assignee": "AI_LAB_COMPUTER_01"
    },
    "metadata": {
      "source": "rest_api",
      "ip_address": "192.168.1.100",
      "user_agent": "SSI-Governance-Client/1.0.0",
      "correlation_id": "CORR_123456789"
    }
  }
}
```

### 5.2 Field Specifications

| Field | Type | Required | Description | Format/Example |
|-------|------|----------|-------------|----------------|
| `header.command_id` | string | ❌ | Unique command identifier | UUID or sequential ID |
| `header.session_id` | string | ❌ | Session identifier | `SESS_YYYY_MM_DD_XXX` |
| `header.operator_id` | string | ✅ | Operator identifier | `SYSTEM_OWNER_01` |
| `header.timestamp` | string | ✅ | Command timestamp | ISO 8601 UTC |
| `header.version` | string | ✅ | API version | `1.0`, `1.1` |
| `header.signature` | string | ✅ | Request signature | HMAC-SHA256 hex |
| `body.command_type` | string | ✅ | Command type | `CREATE_MODULE`, `START_PROCESS` |
| `body.parameters` | object | ✅ | Command-specific parameters | JSON object |
| `body.metadata` | object | ❌ | Additional metadata | Key-value pairs |

### 5.3 Command Type Schemas

#### CREATE_MODULE Command Schema

```json
{
  "type": "object",
  "required": ["module_name", "module_type"],
  "properties": {
    "module_name": {
      "type": "string",
      "minLength": 3,
      "maxLength": 64,
      "pattern": "^[a-zA-Z][a-zA-Z0-9_]*$"
    },
    "module_type": {
      "type": "string",
      "enum": ["ANALYSIS", "PROCESSOR", "STORAGE", "INTERFACE", "UTILITY"]
    },
    "description": {
      "type": "string",
      "maxLength": 512
    },
    "priority": {
      "type": "string",
      "enum": ["LOW", "NORMAL", "HIGH", "CRITICAL"],
      "default": "NORMAL"
    },
    "assignee": {
      "type": "string",
      "pattern": "^[A-Z][A-Z0-9_]*$"
    },
    "data_sources": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "dependencies": {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  }
}
```

#### START_PROCESS Command Schema

```json
{
  "type": "object",
  "required": ["process_name"],
  "properties": {
    "process_name": {
      "type": "string",
      "minLength": 3,
      "maxLength": 64
    },
    "process_id": {
      "type": "string",
      "pattern": "^PROC_[A-Z0-9_]+$"
    },
    "parameters": {
      "type": "object",
      "additionalProperties": true
    },
    "scheduled_time": {
      "type": "string",
      "format": "date-time"
    },
    "timeout_seconds": {
      "type": "integer",
      "minimum": 1,
      "maximum": 86400
    }
  }
}
```

---

## 6. Input Validation

### 6.1 Validation Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                    VALIDATION PIPELINE                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────────┐    ┌─────────────────────┐             │
│  │   SYNTACTIC         │    │   STRUCTURAL        │             │
│  │   VALIDATION        │───▶│   VALIDATION         │             │
│  │  (JSON Schema)      │    │  (Required Fields)    │             │
│  └─────────────────────┘    └──────────┬──────────┘             │
│                                              │                     │
│                                              ▼                     │
│  ┌─────────────────────┐    ┌─────────────────────┐             │
│  │   SEMANTIC          │    │   BUSINESS LOGIC    │             │
│  │   VALIDATION        │───▶│   VALIDATION         │             │
│  │  (Type Checking)    │    │  (Domain Rules)      │             │
│  └─────────────────────┘    └──────────┬──────────┘             │
│                                              │                     │
│                                              ▼                     │
│  ┌─────────────────────┐    ┌─────────────────────┐             │
│  │   PERMISSION         │    │   CONTEXTUAL        │             │
│  │   VALIDATION         │───▶│   VALIDATION         │             │
│  │  (Role Checking)     │    │  (State Dependency)  │             │
│  └─────────────────────┘    └─────────────────────┘             │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 6.2 Validation Rules

#### Syntactic Validation
- ✅ Valid JSON format
- ✅ Correct data types (string, number, boolean, array, object)
- ✅ No trailing commas
- ✅ Valid Unicode characters

#### Structural Validation
- ✅ All required fields present
- ✅ No unknown fields (strict mode)
- ✅ Correct field order (if applicable)
- ✅ Nested object validation

#### Semantic Validation
- ✅ Module names match pattern `^[a-zA-Z][a-zA-Z0-9_]*$`
- ✅ Process IDs match pattern `^PROC_[A-Z0-9_]+$`
- ✅ Timestamps in ISO 8601 UTC format
- ✅ Priority values from allowed enum

#### Business Logic Validation
- ✅ Module name is unique in registry
- ✅ Process is not already running
- ✅ Required dependencies are available
- ✅ Sufficient resources for requested operation

#### Permission Validation
- ✅ Operator has required role
- ✅ Operator has permission for command type
- ✅ IP address is whitelisted (if applicable)
- ✅ Rate limit not exceeded

### 6.3 Validation Error Codes

| Code | Description | HTTP Status | Example |
|------|-------------|--------------|---------|
| `GOV_001` | Invalid JSON format | 400 | Malformed JSON |
| `GOV_002` | Missing required field | 400 | Missing `command_type` |
| `GOV_003` | Invalid field value | 400 | Invalid `priority` value |
| `GOV_004` | Module name already exists | 409 | Duplicate module |
| `GOV_005` | Insufficient permissions | 403 | Operator cannot DELETE |
| `GOV_006` | Rate limit exceeded | 429 | Too many requests |
| `GOV_007` | Invalid signature | 401 | Tampered request |
| `GOV_008` | Session expired | 401 | Session timeout |
| `GOV_009` | Command not found | 404 | Unknown command ID |
| `GOV_010` | System unavailable | 503 | Maintenance mode |

---

## 7. Response Statuses

### 7.1 Status Flow

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   RECEIVED   │────▶│  VALIDATED   │────▶│   QUEUED    │
└──────────────┘     └──────────────┘     └──────────────┘
         │                        │                    │
         │                        ▼                    ▼
         │               ┌──────────────┐     ┌──────────────┐
         │               │  PROCESSING  │     │   REJECTED   │
         │               └──────────────┘     └──────────────┘
         │                        │                    │
         │                        ▼                    │
         │               ┌──────────────┐             │
         │               │  COMPLETED   │◀────────────┘
         │               └──────────────┘
         │                        │
         │                        ▼
         │               ┌──────────────┐
         └──────────────▶│    FAILED    │
                         └──────────────┘
```

### 7.2 Status Definitions

| Status | Code | Description | Final State | Next Possible States |
|--------|------|-------------|--------------|---------------------|
| RECEIVED | 100 | Command received, awaiting parsing | ❌ | VALIDATED, REJECTED |
| VALIDATED | 200 | Command parsed and validated | ❌ | QUEUED, REJECTED |
| QUEUED | 300 | Command in queue, awaiting execution | ❌ | PROCESSING, REJECTED |
| PROCESSING | 400 | Command being executed | ❌ | COMPLETED, FAILED |
| COMPLETED | 500 | Command executed successfully | ✅ | - |
| FAILED | 600 | Command execution failed | ✅ | - |
| REJECTED | 700 | Command rejected (validation/permission) | ✅ | - |
| CANCELLED | 800 | Command cancelled by operator | ✅ | - |

### 7.3 Response Structure

#### Success Response

```json
{
  "header": {
    "command_id": "CMD_2026_08_01_0001",
    "session_id": "SESS_2026_08_01_ABC123",
    "status": "QUEUED",
    "status_code": 300,
    "timestamp": "2026-08-01T10:00:05.123Z",
    "processing_time_ms": 1234
  },
  "body": {
    "result": {
      "queue_position": 1,
      "estimated_start_time": "2026-08-01T10:00:10Z"
    },
    "task_id": "TASK_2026_08_01_0001",
    "orchestration_token": "ORCH_TOKEN_ABC123"
  },
  "metadata": {
    "validation_token": "VAL_TOKEN_XYZ789",
    "operator_id": "SYSTEM_OWNER_01",
    "command_type": "CREATE_MODULE"
  }
}
```

#### Error Response

```json
{
  "header": {
    "command_id": "CMD_2026_08_01_0001",
    "session_id": "SESS_2026_08_01_ABC123",
    "status": "REJECTED",
    "status_code": 700,
    "timestamp": "2026-08-01T10:00:05.456Z",
    "processing_time_ms": 456
  },
  "error": {
    "code": "GOV_005",
    "message": "Insufficient permissions for command type DELETE_MODULE",
    "severity": "HIGH",
    "details": {
      "required_role": "SYSTEM_OWNER",
      "operator_role": "ANALYST",
      "command_type": "DELETE_MODULE"
    }
  },
  "suggestions": [
    "Upgrade operator permissions",
    "Contact system administrator",
    "Use a different command type"
  ]
}
```

---

## 8. Error Handling

### 8.1 Error Classification

| Category | Severity | Retryable | Example |
|----------|----------|-----------|---------|
| **Validation** | LOW | ✅ | Missing required field |
| **Authentication** | HIGH | ❌ | Invalid credentials |
| **Authorization** | HIGH | ❌ | Insufficient permissions |
| **Business Logic** | MEDIUM | ❌ | Duplicate module name |
| **System** | HIGH | ✅ | Service unavailable |
| **Rate Limit** | MEDIUM | ✅ | Too many requests |

### 8.2 Error Handling Strategy

```
Operator Request
       │
       ▼
┌─────────────────┐
│  Try Policy      │ ◄── Immediate retry for transient errors
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Error          │
│  Classification │ ◄── Categorize error type
└────────┬────────┘
         │
    ┌────┴────┬─────────────────┐
    │         │                 │
    ▼         ▼                 ▼
┌────────┐ ┌──────────┐ ┌─────────────────┐
│ Retry  │ │ Reject   │ │ Escalate        │
│ (Auto) │ │ (Permanent)│ │ (Manual Review) │
└────────┘ └──────────┘ └─────────────────┘
```

### 8.3 Retry Policy

| Error Code | Max Retries | Backoff Strategy | Max Delay |
|------------|--------------|-------------------|------------|
| GOV_001 | 3 | Exponential (1s, 2s, 4s) | 8s |
| GOV_006 | 5 | Linear (1s increments) | 5s |
| GOV_010 | 10 | Exponential (1s base) | 30s |

### 8.4 Error Logging

All errors are logged with:
- Timestamp (microsecond precision)
- Error code and message
- Command details (sanitized)
- Operator information
- System state snapshot
- Stack trace (for internal errors)

---

## 9. Communication with System Orchestration

### 9.1 Integration Points

```
┌─────────────────────────┐     ┌─────────────────────────┐
│   GOVERNANCE INTERFACE   │     │   SYSTEM ORCHESTRATION   │
├─────────────────────────┤     ├─────────────────────────┤
│                             │     │                             │
│  ┌─────────────────────┐  │     │  ┌─────────────────────┐  │
│  │  Command Processor   │◀├─────▶│  Task Receiver        │  │
│  │  (Validated Commands)│  │     │  (New Tasks)           │  │
│  └─────────────────────┘  │     └─────────────────────┘  │
│                             │     │                             │
│  ┌─────────────────────┐  │     │  ┌─────────────────────┐  │
│  │  Status Monitor      │◀├─────▶│  Status Reporter      │  │
│  │  (Task Updates)      │  │     │  (Execution Status)    │  │
│  └─────────────────────┘  │     └─────────────────────┘  │
│                             │     │                             │
│  ┌─────────────────────┐  │     │  ┌─────────────────────┐  │
│  │  Result Handler      │◀├─────▶│  Result Dispatcher     │  │
│  │  (Final Results)     │  │     │  (Completed Tasks)     │  │
│  └─────────────────────┘  │     └─────────────────────┘  │
│                             │     │                             │
└─────────────────────────┘     └─────────────────────────┘
```

### 9.2 Communication Protocol

| Aspect | Value |
|--------|-------|
| **Transport** | gRPC (primary), REST (fallback) |
| **Serialization** | Protocol Buffers, JSON |
| **Authentication** | Mutual TLS, API Key |
| **Timeout** | 30s (default), configurable |
| **Retry** | 3 attempts with exponential backoff |
| **Compression** | gzip, deflate |

### 9.3 Message Flow

```
Governance Interface → System Orchestration

Request:
{
  "message_type": "NEW_TASK",
  "task_id": "TASK_2026_08_01_0001",
  "command_id": "CMD_2026_08_01_0001",
  "operator_id": "SYSTEM_OWNER_01",
  "command_type": "CREATE_MODULE",
  "priority": "HIGH",
  "parameters": {...},
  "validation_token": "VAL_TOKEN_XYZ789",
  "timestamp": "2026-08-01T10:00:05.123Z"
}

System Orchestration → Governance Interface

Response:
{
  "message_type": "TASK_ACCEPTED",
  "task_id": "TASK_2026_08_01_0001",
  "status": "QUEUED",
  "queue_position": 1,
  "estimated_start": "2026-08-01T10:00:10Z",
  "orchestration_token": "ORCH_TOKEN_ABC123"
}

Status Update:
{
  "message_type": "TASK_STATUS",
  "task_id": "TASK_2026_08_01_0001",
  "status": "PROCESSING",
  "progress_percentage": 45,
  "current_step": "AI_LABORATORY",
  "timestamp": "2026-08-01T10:05:00.000Z"
}

Result:
{
  "message_type": "TASK_COMPLETED",
  "task_id": "TASK_2026_08_01_0001",
  "status": "COMPLETED",
  "result": {
    "module_id": "MOD_CRYPTO_001",
    "creation_status": "DEPLOYED",
    "validation_score": 0.98
  },
  "execution_time_ms": 5000,
  "timestamp": "2026-08-01T10:05:05.000Z"
}
```

### 9.4 Synchronization

- **Heartbeat**: Every 30 seconds to maintain connection
- **Acknowledgment**: Every message requires ACK
- **Sequence Numbers**: All messages have unique sequence IDs
- **Checksum**: Message integrity verification

---

## 10. Komponenty — Szczegóły Techniczne

### 10.1 Authentication Manager

**DESCRIPTION:**
Zarządza autentykacją i autoryzacją operatorów.

**RESPONSIBILITIES:**
- Operator authentication (JWT, API Key, Certificate)
- Token validation and refresh
- IP whitelist management
- Rate limiting enforcement

**INPUT:**
- Authentication credentials (token, key, certificate)
- Request metadata (IP, User-Agent)

**PROCESS:**
1. Extract credentials from request
2. Validate credentials against operator database
3. Check IP against whitelist
4. Verify rate limit not exceeded
5. Generate session token

**OUTPUT:**
- Authentication result (SUCCESS/FAILURE)
- Operator ID and role
- Session token

**MEMORY USED:**
- Operator Database
- IP Whitelist
- Rate Limit Counters

**MEMORY UPDATED:**
- Active Sessions
- Authentication Logs

**COMMUNICATION:**
- Operator Database (read/write)
- IP Whitelist Service (read)
- Rate Limiter (read/write)

**ERROR HANDLING:**
- Invalid credentials → `GOV_007` (401)
- IP not whitelisted → `GOV_007` (401)
- Rate limit exceeded → `GOV_006` (429)
- Expired token → `GOV_008` (401)

**PERFORMANCE:**
- Authentication time: < 50ms
- Concurrent sessions: 10,000+
- Memory per session: ~1KB

**FUTURE EXTENSIONS:**
- Biometric authentication
- Hardware token support
- Multi-factor authentication (MFA)

---

### 10.2 Request Router

**DESCRIPTION:**
Route'uje żądania do odpowiednich handlerów na podstawie typu polecenia.

**RESPONSIBILITIES:**
- Command type detection
- Handler selection
- Request forwarding
- Load balancing (for multiple handlers)

**INPUT:**
- Validated request
- Command type

**PROCESS:**
1. Parse command type from request
2. Lookup handler in registry
3. Forward request to handler
4. Track request progress

**OUTPUT:**
- Handler response
- Routing metadata

**MEMORY USED:**
- Handler Registry
- Routing Table

**MEMORY UPDATED:**
- Routing Statistics

**COMMUNICATION:**
- Command Parser (unidirectional)
- Handlers (bidirectional)

**ERROR HANDLING:**
- Unknown command type → `GOV_002` (400)
- No handler available → `GOV_010` (503)

**PERFORMANCE:**
- Routing time: < 10ms
- Throughput: 1000 requests/second

---

### 10.3 Command Parser

**DESCRIPTION:**
Parsuje i waliduje polecenia z różnych formatów do jednu struktury.

**RESPONSIBILITIES:**
- JSON/XML/plain text parsing
- Schema validation
- Command object creation
- Format normalization

**INPUT:**
- Raw request body
- Content-Type header

**PROCESS:**
1. Detect input format
2. Parse according to format
3. Validate against schema
4. Create command object
5. Normalize fields

**OUTPUT:**
- Command Object
- Parsing errors (if any)

**MEMORY USED:**
- Command Schemas
- Format Definitions

**MEMORY UPDATED:**
- Parsing Logs

**ERROR HANDLING:**
- Invalid JSON → `GOV_001` (400)
- Schema violation → `GOV_002` (400)
- Unknown format → `GOV_001` (415)

**PERFORMANCE:**
- Parsing time: < 20ms per command
- Supported formats: JSON, XML, YAML, Plain Text

---

### 10.4 Validation Layer

**DESCRIPTION:**
Wykonuje wielowarstwową walidację poleceń.

**RESPONSIBILITIES:**
- Syntactic validation
- Structural validation
- Semantic validation
- Business logic validation
- Permission validation

**INPUT:**
- Command Object
- Operator ID
- System State

**PROCESS:**
1. Run all validation layers
2. Collect all errors
3. Determine overall status
4. Generate validation token (if successful)

**OUTPUT:**
- Validation Result
- List of errors/warnings
- Validation Token (if successful)

**MEMORY USED:**
- Validation Rules
- System State
- Permission Matrix

**ERROR HANDLING:**
- Any validation failure → Appropriate error code

**PERFORMANCE:**
- Validation time: < 100ms per command
- Rule cache: In-memory for performance

---

### 10.5 Session Manager

**DESCRIPTION:**
Zarządza sesjami operatorów.

**RESPONSIBILITIES:**
- Session creation and termination
- Session state tracking
- Session cleanup
- Session history

**INPUT:**
- Authentication result
- Command requests

**PROCESS:**
1. Create session on first command
2. Track session activity
3. Cleanup expired sessions
4. Log session history

**OUTPUT:**
- Session ID
- Session state

**MEMORY USED:**
- Active Sessions
- Session History

**MEMORY UPDATED:**
- Session Logs

**ERROR HANDLING:**
- Session expired → `GOV_008` (401)
- Session conflict → `GOV_009` (409)

**PERFORMANCE:**
- Session creation: < 10ms
- Concurrent sessions: 10,000+

---

### 10.6 Response Formatter

**DESCRIPTION:**
Formatuje odpowiedzi do standardowego formatu.

**RESPONSIBILITIES:**
- Response structure creation
- Status code mapping
- Error formatting
- Metadata inclusion

**INPUT:**
- Handler result
- Processing time
- Errors/warnings

**PROCESS:**
1. Create response structure
2. Map internal status to HTTP status
3. Format errors/warnings
4. Add metadata

**OUTPUT:**
- Formatted Response

**MEMORY USED:**
- Response Templates
- Status Code Mapping

**ERROR HANDLING:**
- Internal formatting errors are logged but not returned

**PERFORMANCE:**
- Formatting time: < 5ms

---

## 📝 Podsumowanie

**Governance Interface** stanowi krytyczny komponent **System Governance**, zapewniający:

✅ **Uniwersalny interfejs** dla wielorakich metod wprowadzania poleceń  
✅ **Kompleksową walidację** wejściową (syntaktyczna, strukturana, semantyczna, biznesowa, uprawnień)  
✅ **Standaryzowane formaty** JSON dla poleceń i odpowiedzi  
✅ **Obsługę błędów** z klasyfikacją, retry policy i loggingiem  
✅ **Integrację z System Orchestration** za pomocą gRPC/REST  
✅ **Wysoką wydajność** (< 100ms na polecenie, 100+ poleceń/sekundę)  

Architektura jest **w pełni kompatybilna** z zasadami SSI V5:
- **Separation of Concerns**: Oddzielona warstwa interfejsu od przetwarzania
- **Niezmienność**: Żadne dane źródłowe nie są modyfikowane
- **Bezpieczeństwo**: Wszystkie operacje są autoryzowane i audytowane
- **Skalowalność**: Obsługa wielkich wolumenów poleceń

---

## 🎯 Next Steps

1. **Implementacja Command Processor** (03_COMMAND_PROCESSOR.md)
2. **Definicja Permission Model** (04_PERMISSION_MODEL.md)
3. **Projekt Command Memory** (05_COMMAND_MEMORY.md)
4. **Bezpieczeństwo i Audyt** (06_SECURITY_AND_AUDIT.md)
5. **Przewodnik Integracji** (07_INTEGRATION_GUIDE.md)

---

**Generated by Mistral Vibe.**  
**Co-Authored-By: Mistral Vibe <vibe@mistral.ai>**  
**Version: 1.0.0 | Date: 2026-08-01**
