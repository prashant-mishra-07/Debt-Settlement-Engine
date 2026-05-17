# Optimized Debt-Settlement Engine (Cash Flow Minimizer)
## Project Architecture and Implementation Plan

---

## 1. System Overview

The Debt-Settlement Engine is a high-performance system designed to minimize cash flow transactions among groups of people using graph-based optimization algorithms. The system employs a hybrid architecture combining Python (FastAPI) for API layer, C++ for core algorithmic processing, and MongoDB for data persistence.

### 1.1 Core Objectives
- **Minimize Transaction Count**: Reduce the number of individual payments needed to settle all debts
- **Optimize Cash Flow**: Use graph theory and network flow algorithms to find optimal settlement paths
- **High Performance**: Leverage C++ for computationally intensive optimization tasks
- **Scalable API**: FastAPI-based RESTful interface for data ingestion and serving
- **Persistent Storage**: MongoDB for transaction ledgers and optimization results

---

## 2. System Architecture

### 2.1 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client Applications                      │
│                    (Web, Mobile, CLI, etc.)                     │
└──────────────────────────────┬──────────────────────────────────┘
                               │ HTTP/REST
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Backend API Layer (Python)                  │
│                         ┌───────────────┐                        │
│                         │   FastAPI     │                        │
│                         │   Server      │                        │
│                         └───────┬───────┘                        │
│                                 │                                │
│         ┌───────────────────────┼───────────────────────┐       │
│         ▼                       ▼                       ▼       │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐    │
│  │  Validation  │      │  Business    │      │  Response    │    │
│  │   Layer      │      │    Logic     │      │  Formatting  │    │
│  └──────────────┘      └──────┬───────┘      └──────────────┘    │
│                                │                                 │
└────────────────────────────────┼─────────────────────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
                    ▼                         ▼
┌───────────────────────────┐   ┌───────────────────────────┐
│   Database Layer (MongoDB) │   │  Core Engine (C++)        │
│  ┌───────────────────────┐ │   │  ┌─────────────────────┐  │
│  │  Transaction Ledger   │ │   │  │  Graph Builder      │  │
│  │  Group Metadata       │ │   │  │  Network Flow Algo  │  │
│  │  Optimization Cache   │ │   │  │  Greedy Optimizer   │  │
│  └───────────────────────┘ │   │  └─────────────────────┘  │
└───────────────────────────┘   └───────────────────────────┘
```

### 2.2 Component Responsibilities

#### Backend API Layer (Python/FastAPI)
- **Data Ingestion**: Accept transaction data via REST endpoints
- **Validation**: Validate input data structures and constraints
- **Orchestration**: Coordinate between database and C++ engine
- **Response Formatting**: Structure API responses with proper JSON schema
- **Error Handling**: Manage exceptions and provide meaningful error messages

#### Core Algorithmic Engine (C++)
- **Graph Construction**: Build directed graphs from transaction data
- **Net Balance Calculation**: Compute net balances for each participant
- **Optimization Algorithm**: Apply greedy/network flow algorithms to minimize transactions
- **Result Generation**: Produce optimized transaction set with minimal paths
- **Performance**: Leverage C++ speed for large-scale optimization

#### Database Layer (MongoDB)
- **Transaction Storage**: Persist raw transaction data
- **Group Management**: Store group metadata and participant information
- **Optimization Cache**: Cache optimization results for quick retrieval
- **Audit Trail**: Maintain history of all optimizations

---

## 3. Data Flow Schema

### 3.1 Data Flow Sequence

```
1. Client → API: POST /api/v1/groups
   Input: Group ID + List of Transactions
   
2. API → Database: Store group and transactions
   Action: Insert into MongoDB 'groups' collection
   
3. Client → API: POST /api/v1/optimize
   Input: Group ID
   
4. API → Database: Retrieve group data
   Action: Query MongoDB for transactions
   
5. API → C++ Engine: Execute optimization
   Action: Serialize data → Write temp file → Execute binary → Parse output
   
6. C++ Engine → API: Return optimized transactions
   Output: Minimized transaction set + metrics
   
7. API → Database: Cache optimization results
   Action: Update group document with optimization data
   
8. API → Client: Return optimization result
   Output: JSON with optimized transactions and reduction metrics
```

### 3.2 Data Structures

#### Input Transaction Schema
```json
{
  "from_user": "string (payer)",
  "to_user": "string (payee)",
  "amount": "float (positive)"
}
```

#### Group Request Schema
```json
{
  "group_id": "string (unique identifier)",
  "transactions": [
    {
      "from_user": "alice",
      "to_user": "bob",
      "amount": 100.0
    },
    {
      "from_user": "bob",
      "to_user": "charlie",
      "amount": 50.0
    }
  ]
}
```

#### Optimization Result Schema
```json
{
  "group_id": "string",
  "original_transactions": [
    {
      "from_user": "string",
      "to_user": "string",
      "amount": "float"
    }
  ],
  "optimized_transactions": [
    {
      "from_user": "string",
      "to_user": "string",
      "amount": "float"
    }
  ],
  "reduction_percentage": "float (0-100)",
  "total_original_amount": "float",
  "total_optimized_amount": "float"
}
```

#### MongoDB Document Schema
```json
{
  "_id": "ObjectId",
  "group_id": "string",
  "transactions": [
    {
      "from_user": "string",
      "to_user": "string",
      "amount": "float"
    }
  ],
  "status": "active|optimized",
  "optimization_result": {
    "optimized_transactions": [...],
    "reduction_percentage": "float",
    "total_original_amount": "float",
    "total_optimized_amount": "float",
    "timestamp": "ISODate"
  },
  "created_at": "ISODate",
  "updated_at": "ISODate"
}
```

---

## 4. API Endpoints Specification

### 4.1 Endpoints Overview

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| GET | `/health` | Health check | None | `{"status": "healthy"}` |
| POST | `/api/v1/groups` | Create new debt group | `GroupRequest` | Group creation confirmation |
| GET | `/api/v1/groups/{group_id}` | Retrieve group data | None | Group document with transactions |
| POST | `/api/v1/optimize` | Optimize cash flow | `OptimizationRequest` | `OptimizationResult` |
| DELETE | `/api/v1/groups/{group_id}` | Delete group | None | Deletion confirmation |

### 4.2 Endpoint Details

#### POST /api/v1/groups
**Purpose**: Create a new debt group with initial transactions

**Request**:
```json
{
  "group_id": "group_123",
  "transactions": [
    {"from_user": "alice", "to_user": "bob", "amount": 100.0},
    {"from_user": "bob", "to_user": "charlie", "amount": 50.0}
  ]
}
```

**Response**:
```json
{
  "message": "Group created successfully",
  "group_id": "group_123",
  "transaction_count": 2
}
```

#### POST /api/v1/optimize
**Purpose**: Execute cash flow optimization for a group

**Request**:
```json
{
  "group_id": "group_123"
}
```

**Response**:
```json
{
  "group_id": "group_123",
  "original_transactions": [
    {"from_user": "alice", "to_user": "bob", "amount": 100.0},
    {"from_user": "bob", "to_user": "charlie", "amount": 50.0}
  ],
  "optimized_transactions": [
    {"from_user": "alice", "to_user": "charlie", "amount": 50.0}
  ],
  "reduction_percentage": 50.0,
  "total_original_amount": 150.0,
  "total_optimized_amount": 50.0
}
```

---

## 5. Python-C++ Interface Design

### 5.1 Communication Protocol

The Python backend communicates with the C++ engine through:

1. **File-based IPC**: JSON files for input/output
2. **Subprocess Execution**: Python calls C++ binary via subprocess module
3. **JSON Serialization**: Structured data exchange format

### 5.2 Interface Flow

```
Python Layer:
1. Serialize transaction data to JSON
2. Write to temporary input file: /tmp/input_<timestamp>.json
3. Execute: ./debt_optimizer /tmp/input_<timestamp>.json
4. Read output from: /tmp/output_<timestamp>.json
5. Parse JSON response
6. Return to API layer
7. Clean up temporary files

C++ Layer:
1. Read input JSON file path from command line argument
2. Parse JSON into C++ data structures
3. Build graph representation
4. Execute optimization algorithm
5. Serialize optimized transactions to JSON
6. Write to output file
7. Exit with success code
```

### 5.3 C++ Input/Output Format

#### C++ Input JSON
```json
{
  "transactions": [
    {
      "from_user": "alice",
      "to_user": "bob",
      "amount": 100.0
    }
  ]
}
```

#### C++ Output JSON
```json
{
  "optimized_transactions": [
    {
      "from_user": "alice",
      "to_user": "charlie",
      "amount": 50.0
    }
  ],
  "reduction_percentage": 50.0,
  "total_original_amount": 150.0,
  "total_optimized_amount": 50.0,
  "status": "success"
}
```

### 5.4 Error Handling

- **Python Layer**: Catch subprocess exceptions, check return codes, validate JSON output
- **C++ Layer**: Validate input JSON, handle graph construction errors, return error status in JSON
- **Fallback**: If C++ engine fails, return original transactions with error message

---

## 6. Algorithm Design (High-Level)

### 6.1 Problem Statement

Given a set of transactions among N participants, find the minimal set of transactions that settles all debts with the same net balances.

### 6.2 Algorithm Approach

#### Phase 1: Net Balance Calculation
- For each participant, calculate net balance (total owed - total to receive)
- Participants with positive net balance are debtors
- Participants with negative net balance are creditors

#### Phase 2: Graph Construction
- Construct directed graph where nodes are participants
- Edges represent potential payment paths
- Edge weights represent transaction amounts

#### Phase 3: Greedy Optimization
- Match largest debtor with largest creditor
- Settle maximum possible amount between them
- Update balances and repeat
- Continue until all balances are zero

#### Phase 4: Transaction Minimization
- Identify chains of payments that can be consolidated
- Merge intermediate transactions where possible
- Ensure final transaction count is minimized

### 6.3 Time Complexity
- Net Balance Calculation: O(T) where T = number of transactions
- Graph Construction: O(N + T) where N = number of participants
- Greedy Optimization: O(N log N) with priority queue
- Overall: O(T + N log N)

---

## 7. Database Schema Design

### 7.1 Collections

#### groups
```javascript
{
  _id: ObjectId,
  group_id: String (unique, indexed),
  transactions: [
    {
      from_user: String,
      to_user: String,
      amount: Double
    }
  ],
  status: String ("active" | "optimized"),
  optimization_result: {
    optimized_transactions: [...],
    reduction_percentage: Double,
    total_original_amount: Double,
    total_optimized_amount: Double,
    timestamp: Date
  },
  created_at: Date,
  updated_at: Date
}
```

#### audit_log (optional, for Phase 3)
```javascript
{
  _id: ObjectId,
  group_id: String,
  action: String ("create" | "optimize" | "delete"),
  timestamp: Date,
  details: Object
}
```

### 7.2 Indexes
- `group_id`: Unique index for fast lookups
- `status`: Index for filtering by optimization status
- `created_at`: Index for time-based queries

---

## 8. Implementation Phases

### Phase 1: Foundation (Current)
- ✅ Project structure setup
- ✅ Configuration files
- ✅ Database connection utility
- ✅ FastAPI stub with endpoints
- ✅ CMakeLists.txt configuration

### Phase 2: Core Algorithm Implementation
- Implement C++ graph builder
- Implement net balance calculator
- Implement greedy optimization algorithm
- Implement JSON parser for C++
- Integrate Python-C++ interface
- Add error handling and validation

### Phase 3: API Enhancement
- Complete FastAPI endpoint implementations
- Add request/response validation
- Implement caching layer
- Add rate limiting
- Add authentication/authorization (optional)

### Phase 4: Testing & Optimization
- Unit tests for C++ algorithms
- Integration tests for API endpoints
- Performance benchmarking
- Algorithm optimization
- Load testing

### Phase 5: Deployment
- Docker containerization
- CI/CD pipeline setup
- Monitoring and logging
- Documentation completion
- Production deployment

---

## 9. Technology Stack Details

### 9.1 Backend (Python)
- **FastAPI**: Modern, fast web framework for building APIs
- **Pydantic**: Data validation using Python type annotations
- **Uvicorn**: ASGI server for FastAPI
- **PyMongo**: MongoDB driver for Python
- **Motor**: Async MongoDB driver (optional for async operations)

### 9.2 Core Engine (C++)
- **C++17**: Modern C++ standard
- **CMake**: Cross-platform build system
- **nlohmann/json**: JSON library for C++ (to be added)
- **STL**: Standard Template Library for data structures

### 9.3 Database
- **MongoDB**: NoSQL document database
- **Schema flexibility**: Accommodates varying transaction structures
- **Horizontal scaling**: Supports large-scale deployments

### 9.4 Development Tools
- **Git**: Version control
- **pytest**: Python testing framework
- **Google Test**: C++ testing framework (to be added)
- **Docker**: Containerization (Phase 5)

---

## 10. Security Considerations

### 10.1 Input Validation
- Validate all user inputs at API layer
- Sanitize data before C++ engine processing
- Limit transaction amounts to prevent overflow

### 10.2 Database Security
- Use environment variables for connection strings
- Implement connection pooling
- Add authentication for MongoDB (production)

### 10.3 API Security
- Implement rate limiting (Phase 3)
- Add CORS configuration
- Consider API key authentication (Phase 3)

---

## 11. Performance Targets

### 11.1 Response Time Targets
- Group creation: < 100ms
- Optimization (small groups < 10 users): < 500ms
- Optimization (medium groups 10-100 users): < 2s
- Optimization (large groups 100-1000 users): < 10s

### 11.2 Scalability Targets
- Support up to 10,000 concurrent groups
- Handle up to 100,000 transactions per group
- Process optimization requests with < 1s latency for 90% of requests

---

## 12. Next Steps

After completing Phase 1 (Foundation), the immediate next steps are:

1. **C++ Core Engine Development**
   - Implement graph data structures
   - Implement net balance calculation
   - Implement greedy optimization algorithm
   - Add JSON parsing capabilities

2. **Python-C++ Integration**
   - Complete subprocess interface
   - Add temporary file management
   - Implement error handling
   - Add timeout mechanisms

3. **API Implementation**
   - Complete all endpoint implementations
   - Add comprehensive validation
   - Implement error responses
   - Add logging

4. **Testing**
   - Write unit tests for C++ algorithms
   - Write integration tests for API
   - Test with sample transaction data
   - Validate optimization correctness

---

## 13. Example Use Case

### Scenario
Four friends (Alice, Bob, Charlie, Dave) have the following transactions:
- Alice owes Bob $100
- Bob owes Charlie $50
- Charlie owes Dave $75
- Dave owes Alice $25

### Current State
- Total transactions: 4
- Total amount: $250

### After Optimization
- Calculate net balances:
  - Alice: -100 + 25 = -75 (owes $75)
  - Bob: +100 - 50 = +50 (is owed $50)
  - Charlie: +50 - 75 = -25 (owes $25)
  - Dave: +75 - 25 = +50 (is owed $50)

- Optimized transactions:
  - Alice pays Bob $50
  - Alice pays Dave $25
  - Charlie pays Dave $25

- Result: 3 transactions (25% reduction)
- Total amount: $100 (60% reduction in cash flow)

---

## 14. Project Directory Structure

```
debt-settlement-engine/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── requirements.txt        # Python dependencies
│   └── (future: routers, models, services)
├── core_engine/
│   ├── CMakeLists.txt          # C++ build configuration
│   ├── src/                    # C++ source files
│   │   ├── main.cpp
│   │   ├── graph_builder.cpp
│   │   ├── optimizer.cpp
│   │   └── json_parser.cpp
│   ├── include/                # C++ header files
│   │   ├── graph_builder.h
│   │   ├── optimizer.h
│   │   ├── json_parser.h
│   │   └── types.h
│   └── build/                  # Build output directory
├── database/
│   ├── db_connection.py        # MongoDB connection utility
│   └── (future: models, repositories)
├── config/
│   └── .env.example            # Environment variables template
├── PROJECT_PLAN.md             # This file
└── (future: tests, docs, docker)
```

---

## 15. Conclusion

This project plan provides a comprehensive roadmap for building an optimized debt-settlement engine with a hybrid Python-C++ architecture. The system is designed for high performance, scalability, and maintainability. The phased approach ensures systematic development with clear milestones and deliverables.

The next phase (Phase 2) will focus on implementing the core C++ optimization algorithm and integrating it with the Python backend, followed by comprehensive testing and API enhancement.
