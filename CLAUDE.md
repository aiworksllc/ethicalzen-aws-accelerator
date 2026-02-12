# Claude Code Workflow Guidelines

## Default Goal: Super Moderator

Claude Code operates as the **Super Moderator** for the AI development team:

1. **Orchestrator** — Dispatch work to Sage, Marcus, Devon, and other agents via `/ai-team`
2. **Code Reviewer** — Review every PR/output from each agent against acceptance criteria
3. **Developer of Last Resort** — If an agent's output doesn't meet the bar, step in and fix it directly
4. **Quality Gate** — No story gets marked "Done" until verified it passes tests and meets acceptance criteria

---

## AI Team Delegation Rule (MANDATORY)

**All implementation, deployment, testing, and infrastructure work MUST be delegated to the AI development team via `/ai-team`.** Claude Code acts as the **coordinator/orchestrator** only - not the implementer. When agents fail to deliver, Claude Code steps in as developer of last resort.

### Rules:
1. **DEFAULT: Delegate to /ai-team** - Any task involving code changes, deployments, testing, or infrastructure must be assigned to the appropriate agent(s)
2. **Claude Code's role** - Coordinate, plan, present results, answer questions, communicate with the user, code review agent output, and fix as developer of last resort
3. **Never touch code directly** unless the user explicitly says "you do it" or "do it yourself" OR an agent's output fails review and needs correction
4. **Agent assignment guide:**

| Work Type | Assign To |
|-----------|-----------|
| Backend code, APIs, database | **Marcus** (Platform Core) |
| Go gateway, proxy, performance | **Velocity** (Gateway Engineer) |
| Infrastructure, CI/CD, deployment, git ops | **Devon** (DevOps) |
| Testing, QA, validation | **Laura** (QA Lead) |
| Feature planning, task breakdown | **Nova** (Product Lead) |
| LangGraph agents, guardrail design | **Alex** (AI Agent Specialist) |
| ML guardrails, embeddings | **Sage** (Smart Guardrail Engineer) |
| Frontend, UI, dashboard | **Pixel** (Frontend) |

### How to delegate:
```bash
# Single agent
/ai-team assign marcus "Add health check endpoint"

# Multiple agents in parallel
/ai-team parallel devon,laura "Deploy to UAT and run smoke tests"
```

### Exceptions (Claude Code can act directly):
- User explicitly asks Claude Code to do it
- Pure research/exploration (reading files, searching code, answering questions)
- Planning and coordination
- Explaining code or architecture
- Writing documentation when asked

---

## Mandatory Development Approach

Always follow this structured workflow for all tasks:

### 1. Plan Phase
- Before any implementation, create a detailed plan
- Break down the task into discrete, actionable steps
- Identify files that need to be modified or created
- Document dependencies between steps
- Use `TodoWrite` to track all planned items

### 2. Expert Plan Review Phase
- Adopt an **Expert Plan Reviewer** persona
- Critically evaluate the plan for:
  - Completeness: Are all edge cases covered?
  - Correctness: Is the technical approach sound?
  - Security: Are there any OWASP vulnerabilities introduced?
  - Performance: Are there any obvious bottlenecks?
  - Maintainability: Is the solution overly complex?
  - Test coverage: Is the testing strategy adequate?
- Document any gaps, risks, or improvements needed

### 3. Incorporate Feedback Phase
- Address all concerns raised during review
- Update the plan with improvements
- Re-validate the updated plan if significant changes were made
- Get explicit approval before proceeding to implementation

### 4. Implement Per Plan Phase
- Follow the approved plan step-by-step
- Mark todos as `in_progress` when starting each step
- Mark todos as `completed` only when fully done
- Do not deviate from the plan without re-planning
- Keep changes minimal and focused

### 5. Test All Changes Phase
- **No facades or mocks unless absolutely necessary**
- Run actual tests against real implementations
- Verify all modified functionality works end-to-end
- Test edge cases and error scenarios
- Run linting and type checking if applicable
- Validate no regressions were introduced

### 6. Iterate Until Goal Achieved
- If tests fail, fix issues and re-test
- If new requirements emerge, go back to Plan phase
- Continue until all acceptance criteria are met
- Do not mark task complete until fully verified

---

## Key Principles

- **No shortcuts**: Every step matters
- **No assumptions**: Verify before acting
- **No facades**: Test real implementations
- **No skipping**: Follow the workflow in order
- **No silent failures**: Report and fix all issues

## Anti-Patterns to Avoid

- Jumping straight to implementation without planning
- Skipping the expert review phase
- Writing stub/mock implementations to pass tests
- Marking tasks complete before full verification
- Ignoring edge cases or error handling
- Over-engineering beyond what was requested

---

# Project Context: EthicalZen.ai

## Overview

**EthicalZen.ai** is an enterprise-grade AI Safety Governance Platform. It's a polyglot monorepo combining:
- Multi-tenant SaaS platform with centralized governance
- Microservices with API gateway pattern
- Agent-based AI systems for guardrail design and automation
- Blockchain-integrated contract management
- Cloud-native deployment architecture

**Mission**: Build AI Safety Guardrails in Minutes (FEMA-powered auto-configuration)

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│  CUSTOMER FRONTEND (Browser)                                │
│  - HTML/CSS/JavaScript Dashboard                            │
│  - Real-time monitoring & guardrail builder UI              │
└──────────────────┬──────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────┐
│  BACKEND API LAYER (Node.js/Express) - Port 4000            │
│  - Multi-tenant management                                  │
│  - Contract generation & lifecycle                          │
│  - AI service registration                                  │
│  - Database: MySQL/PostgreSQL + Redis cache                 │
└──────────────────┬──────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────┐
│  ACVPS GATEWAY (Go) - Port 8443                             │
│  - Transparent HTTP proxy                                   │
│  - Contract-driven validation                               │
│  - PII redaction, grounding checks, injection detection     │
│  - <5ms overhead, 10,000 req/s per instance                │
└──────────────────┬──────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────┐
│  CUSTOMER'S AI SERVICES                                     │
│  - OpenAI, Anthropic, Groq (LLM providers)                 │
│  - Custom microservices                                     │
│  - Any REST/HTTP API                                        │
└─────────────────────────────────────────────────────────────┘
```

---

## Directory Structure

```
aipromptandseccheck/
├── CORE INFRASTRUCTURE
│   ├── acvps-gateway/              # Go - HTTP API governance layer
│   ├── portal/                     # Node.js + HTML - Admin SaaS platform
│   │   ├── backend/                # Express.js API server
│   │   └── frontend/               # Static HTML dashboard
│   ├── sdk/                        # TypeScript - Client SDK
│   ├── metrics-service/            # Node.js - Observability
│   └── orchestrator/               # Node.js - Service orchestration
│
├── AI AGENTS & INTELLIGENCE
│   ├── alex-agent/                 # Python/FastAPI - Guardrail design assistant
│   ├── laura-agent/                # Python - Test automation & QA
│   ├── dc-control-plane/           # Python - Contract control plane
│   └── spectral_guardrail/         # Python - ML-based guardrail engine
│
├── GUARDRAIL & RULES ENGINE
│   ├── guardrails/                 # JSON contracts library
│   ├── guardrail-generator-sdk/    # Web-based guardrail builder
│   └── dlm-guardrails/             # Dynamic guardrail management
│
├── EXAMPLES & ACCELERATORS
│   ├── demo/                       # JavaScript demo scripts
│   ├── examples/                   # Industry examples (healthcare, finance, legal)
│   └── accelerators/               # Performance optimization demos
│
├── DEPLOYMENT & INFRASTRUCTURE
│   ├── deploy/                     # GCP deployment scripts
│   ├── infrastructure/             # Kubernetes configs
│   └── docker-compose.yml          # Local development
│
└── DEVELOPMENT & TESTING
    ├── tests/                      # E2E & integration tests
    ├── scripts/                    # Automation scripts
    └── docs/                       # Technical documentation
```

---

## Key Components

### 1. Portal Backend (Node.js/Express)

**Location**: `portal/backend/`
**Entry Point**: `server.js`
**Port**: 4000

**Responsibilities**:
- Multi-tenant SaaS management
- Authentication (JWT + API keys)
- Deterministic Contract (DC) generation
- Smart Guardrail (SG) design system
- Guardrail CRUD operations
- Certificate issuance

**Key Routes**:
| Route | Purpose |
|-------|---------|
| `/api/auth`, `/api/auth-v2` | Authentication (login, register, JWT) |
| `/api/guardrails` | Guardrail CRUD operations |
| `/api/dc/contracts` | Deterministic Contract management |
| `/api/sg/*` | Smart Guardrail design, evaluate, deploy |
| `/api/usecases` | Use case registration |
| `/api/admin-v2` | Admin operations |

**Key Files**:
- `server.js` - Main Express app
- `routes/auth.js`, `routes/auth-v2.js` - Authentication
- `routes/guardrails.js` - Guardrail endpoints
- `routes/contracts.js` - Contract management
- `src/smart-guardrail/` - SG design system (TypeScript)
- `services/GuardrailMatcher.js` - Domain + Theme matching
- `db/connection.js` - Database pool management

**Database Tables**:
- `users` - User accounts with tenant association
- `tenants` - Multi-tenant configuration
- `contracts` - Deterministic Contracts
- `guardrail_registry` - Tenant guardrails
- `smart_guardrails` - SG v3 guardrails
- `certificates` - Issued certificates

---

### 2. ACVPS Gateway (Go)

**Location**: `acvps-gateway/`
**Entry Point**: `cmd/gateway/main.go`
**Port**: 8443 (HTTPS), 9090 (metrics)

**Responsibilities**:
- Universal API governance proxy
- Contract-driven validation
- PII detection and redaction
- Grounding confidence checks
- Smart guardrail evaluation
- Prompt injection detection

**Key Files**:
- `cmd/gateway/main.go` - Entry point
- `internal/api/handler.go` - REST endpoints
- `internal/api/sse_handler.go` - SSE streaming
- `internal/proxy/handler.go` - HTTP reverse proxy
- `pkg/gateway/boot.go` - Contract loading
- `pkg/txrepo/txrepo.go` - Guardrail registry
- `smart-guardrail-engine/` - TypeScript ML sidecar

**Key Endpoints**:
| Endpoint | Purpose |
|----------|---------|
| `GET /health` | Health check |
| `POST /api/proxy` | Transparent proxy (production) |
| `POST /api/guardrails/evaluate` | Direct guardrail evaluation |
| `POST /api/contracts` | Register contracts |
| `POST /api/stream/sse` | SSE streaming validation |

**Performance Targets**:
- Throughput: 10,000 req/s per instance
- Latency (p50): 2ms (cache hit)
- Cache hit rate: 99%

---

### 3. Alex Agent (Python/LangGraph)

**Location**: `alex-agent/`
**Entry Point**: `service.py`
**Port**: 8001

**Responsibilities**:
- Conversational guardrail design assistant
- Discovers existing guardrails from GuardrailHub
- Failure Mode Analysis (FMA) for security gaps
- Builds custom Smart Guardrails
- Deploys guardrails and issues certificates

**Key Files**:
- `service.py` - FastAPI service wrapper
- `src/agent.py` - Main `GuardrailDesigner` class
- `src/graph_v2.py` - LangGraph definition
- `src/nodes_v2.py` - 8 focused action nodes
- `src/state.py` - State definitions
- `src/contextual_memory.py` - Priority-based memory
- `src/api_client.py` - Backend API client

**V2 Node Architecture** (8 nodes):
1. `state_planner_node` - LLM-powered probabilistic routing
2. `clarify_node` - Ask clarifying questions
3. `fma_analysis_node` - Failure Mode Analysis
4. `explain_node` - Context-aware explanations
5. `custom_guardrail_node` - Custom guardrail requirements
6. `build_custom_guardrail_node` - Create Smart Guardrails
7. `integration_code_node` - Generate SDK code
8. `deploy_decision_node` - Deploy and issue certificate

---

### 4. Smart Guardrail System

**Backend Location**: `portal/backend/src/smart-guardrail/`
**Gateway Sidecar**: `acvps-gateway/smart-guardrail-engine/`

**Components**:
1. **Designer** (`designer.ts`) - Natural language → guardrail config
2. **Embeddings** (`embeddings.ts`) - Sentence transformers (all-MiniLM-L6-v2)
3. **Classifier** (`classifier.ts`) - Decision boundary classification
4. **Semantic Evaluator** (`semantic-evaluator.ts`) - LLM-based evaluation
5. **Calibrator** (`calibrator.ts`) - Threshold calibration

**Workflow**:
```
Natural Language → Designer → Embeddings → Classifier → Evaluation → Published Guardrail
```

---

### 5. Testing Infrastructure

**Location**: `tests/`

**Key Test Files**:
- `e2e-full-flow.js` - Complete user workflow
- `alex-contract-e2e.js` - Alex agent tests
- `contract/service-contracts.test.js` - API contract validation
- `sdk-all-modes-e2e.js` - SDK testing
- `test-tenant-guardrail-flow.js` - Multi-tenant validation

**Contract Schemas** (from `service-contracts.test.js`):
- `guardrailEvaluateRequest/Response` - Guardrail evaluation
- `contractCreateRequest/Response` - Contract creation
- `alexChatRequest/Response` - Alex Agent chat
- `errorResponse` - Standard error format

---

## Technology Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Node.js 18+, Express 4.x |
| **Gateway** | Go 1.24, gorilla/mux |
| **Agents** | Python 3.10+, FastAPI, LangGraph |
| **Frontend** | HTML/CSS/JavaScript |
| **Database** | PostgreSQL, MySQL, Redis |
| **ML/AI** | OpenAI, Groq, Transformers.js |
| **Blockchain** | Ethereum/Arbitrum, ethers.js |
| **Observability** | Prometheus, OpenTelemetry |
| **Deployment** | Docker, Google Cloud Run, Kubernetes |

---

## Common Patterns

### Authentication
- **API Key**: `X-API-Key` header for service-to-service
- **JWT**: Bearer token for user sessions
- **Tenant ID**: `X-Tenant-ID` header for multi-tenancy

### Contract ID Format
- Pattern: `dc_<tenant>_<uuid>` (e.g., `dc_demo_abc123`)
- Always prefixed with `dc_`

### Guardrail ID Format
- Base: `<guardrail_name>` (e.g., `pii_blocker`)
- Tenant-specific: `<tenant>:<guardrail_name>` (e.g., `demo:pii_blocker`)

### Error Response Format
```json
{
  "error": "Error message",
  "code": "ERROR_CODE",
  "details": {}
}
```

---

## Development Commands

```bash
# Start all services locally
docker-compose up -d

# Backend only
cd portal/backend && npm start

# Gateway only
cd acvps-gateway && go run cmd/gateway/main.go

# Alex Agent only
cd alex-agent && python service.py

# Run tests
cd tests && npm test

# Run specific test
node tests/e2e-full-flow.js
```

---

## Key Configuration Files

| File | Purpose |
|------|---------|
| `docker-compose.yml` | Local development orchestration |
| `portal/backend/.env` | Backend environment variables |
| `acvps-gateway/config.yaml` | Gateway configuration |
| `alex-agent/pyproject.toml` | Python dependencies |
| `portal/backend/init-mysql.sql` | Database schema |

---

## Important Considerations

### Security
- Never commit `.env` files or API keys
- Validate all user input at API boundaries
- Use parameterized queries for database operations
- OWASP Top 10 awareness required

### Multi-Tenancy
- Always scope queries by `tenant_id`
- Validate tenant access on every request
- Use tenant-specific caching keys

### Testing
- Contract tests validate API schemas
- E2E tests cover full user workflows
- Unit tests for business logic
- No mocks/facades for integration tests

---

## AI Development Team

EthicalZen has an AI development team with 8 specialized agents. Each agent runs in its **own independent Claude context** with persona-specific skills.

### Team Orchestrator

Located at: `/Users/srinivasvaravooru/workspace/ethicalzen-ai-team/orchestrator/`

**Commands:**
```bash
cd /Users/srinivasvaravooru/workspace/ethicalzen-ai-team/orchestrator

# Assign task to agent
node src/cli.js assign <agent> "<task>"

# Run multiple agents in parallel
node src/cli.js parallel marcus,laura "<task>"

# Check team status
node src/cli.js status

# Reset agent session
node src/cli.js reset <agent>
```

### Available Agents

| Agent | Role | Expertise |
|-------|------|-----------|
| `nova` | Product Lead | Feature planning, task assignment |
| `marcus` | Platform Core | Backend, APIs, database, multi-tenancy |
| `velocity` | Gateway Engineer | Go gateway, proxy, performance |
| `devon` | DevOps | Infrastructure, CI/CD, deployment |
| `alex` | AI Agent Specialist | LangGraph, guardrail design |
| `laura` | QA Lead | Testing, quality assurance |
| `sage` | Smart Guardrail Engineer | ML guardrails, embeddings |
| `pixel` | Frontend | UI, dashboard, UX |

### Context System

| Path | Purpose |
|------|---------|
| `ethicalzen-ai-team/context/shared/sprint.md` | Current sprint goals |
| `ethicalzen-ai-team/context/shared/patterns.md` | Code patterns |
| `ethicalzen-ai-team/context/agents/<name>/working.md` | Agent's work status |
| `ethicalzen-ai-team/<agent>/skill.md` | Agent's skill profile |

### Communication

Agents communicate via Slack MCP:
- Channel: `#all-ethicalzenai`
- Each agent posts updates after completing work
- Use `mcp__slack__slack_post_message` with `agent_name` parameter
