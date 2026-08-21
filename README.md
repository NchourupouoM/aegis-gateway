# Aegis-LLM : Enterprise AI Safety Firewall & Smart Multi-LLM Gateway

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Package Manager](https://img.shields.io/badge/uv-Astral-blueviolet.svg?logo=astral&logoColor=white)](https://github.com/astral-sh/uv)
[![Security](https://img.shields.io/badge/OWASP-LLM_Top_10_Protected-red.svg?logo=owasp&logoColor=white)](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
[![Database](https://img.shields.io/badge/SQLAlchemy_2.0-Async_aiosqlite-red.svg?logo=sqlite&logoColor=white)](https://www.sqlalchemy.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An enterprise-grade, high-availability security proxy and FinOps routing gateway sitting between client applications and large language model providers (**OpenAI & Google Gemini**).

---

## The Enterprise Problem (Why Enterprises Need This)

In enterprise production environments, directly connecting client applications to a single upstream LLM API introduces three critical vulnerabilities:

1. **Single Point of Failure (SPOF)**: Upstream HTTP 429 rate limits, quota exhaustion, or vendor service degradations bring entire business operations to a halt.
2. **Cost Inefficiency & Budget Leaks**: Routing simple tasks (e.g., summaries, text translations, JSON extraction) to premium models like GPT-4o costs **15x to 25x more** than necessary.
3. **Data Privacy & Jailbreak Vulnerabilities (OWASP LLM01 & LLM02)**: Direct connections risk exposing Personally Identifiable Information (PII) to third-party model providers (GDPR/HIPAA violations) and leave systems vulnerable to prompt injection attacks.

---

## 🏛️ System Architecture

Aegis-LLM implements a non-blocking, multi-layered pipeline ensuring strict security boundaries, intelligent load-dispatching, and zero-downtime failover:

```
[ Client / Frontend Application ]
               │
               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      AEGIS AI GATEWAY & FIREWALL                        │
│                                                                         │
│  1. Ingress Security Firewall (Presidio PII Masking + OWASP LLM01 Scan) │
│  2. Smart FinOps Router (Complexity Classifier + Token Counter)        │
│  3. Resilient Dispatcher (Circuit Breaker + Instant Auto-Fallback)     │
│  4. Egress Guardrails (Surgical PII Restoration + Secret Leak Filter)   │
│  5. Async FinOps Ledger & Telemetry (SQLAlchemy 2.0 + SQLite)           │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                 ┌───────────────────┴───────────────────┐
                 │ (If Fast / Bulk)                      │ (If High Reasoning)
                 ▼                                       ▼
    [ Google Gemini 2.0/2.5 Flash ]             [ OpenAI GPT-4o ]
```

---

<!-- ========================================================================= -->
<!-- 📸 PLACEHOLDER: ARCHITECTURE DIAGRAM -->
<!-- Export your Excalidraw diagram as a clean PNG/SVG and save it in docs/ -->
<!-- ========================================================================= -->
<p align="center">
  <img src="docs/architecture.png" alt="Aegis-LLM Architecture Diagram" width="850">
</p>
<p align="center"><em>Figure 1: Full-duplex Security, Smart Routing, and Auto-Fallback Flow.</em></p>

---

## 🚀 Key Architectural Capabilities

### 1. Ingress Security Firewall (OWASP LLM01 & PII Protection)
- **Reversible PII Pseudonymization**: Automatically detects and replaces sensitive entities (Credit Cards verified via ISO/IEC 7812 Luhn algorithm, Emails, Phone Numbers, Names, IP addresses) with deterministic placeholders (`<PERSON_1>`, `<CREDIT_CARD_1>`) powered by **Microsoft Presidio**.
- **Jailbreak & Prompt Injection Defense**: Intercepts direct prompt overrides, DAN (Do Anything Now) personas, system prompt exfiltration attempts, and special delimiter manipulations (`<|im_start|>`) before any tokens reach upstream APIs.

### 2. Smart FinOps & Complexity Router
- **Semantic Complexity Classifier**: Evaluates reasoning depth, structural markers, and context length to dynamically dispatch queries:
  - **Fast / Economical Tier** $\rightarrow$ **Google Gemini 2.0 / 2.5 Flash** ($0.10 / 1M input tokens).
  - **Deep Reasoning Tier** $\rightarrow$ **OpenAI GPT-4o** ($2.50 / 1M input tokens).
- **Exact Real-Time FinOps Ledger**: Computes dollar costs per transaction and measures **net dollars saved ($)** against a 100% GPT-4o baseline.

### 3. High Availability & Circuit Breaker (Zero-Downtime)
- **Circuit Breaker Pattern**: Maintains `CLOSED`, `OPEN`, and `HALF_OPEN` state machines for each provider. If a provider encounters consecutive failures, calls fail fast to avoid latency build-up.
- **Transparent Auto-Fallback**: Automatically and seamlessly re-routes queries from OpenAI to Google Gemini upon encountering HTTP 429, 500, 503, or connection timeouts.

### 4. Egress Guardrails & De-anonymization (OWASP LLM02)
- **Surgical PII Restoration**: Safely re-substitutes original sensitive data into the response returned to the authorized user, ensuring the external LLM never observed raw PII.
- **Secret & Key Leak Prevention**: Scans generated outputs for leaked API keys (`sk-...`), Bearer tokens, or database connection strings.

### 5. Built-in Observability & Studio Playground
- Live Single Page Application (SPA) with **Real-Time "X-Ray" Pipeline Inspection**, Red-Teaming attack sandbox, and FinOps telemetry dashboard.

---

## 📸 Production Interface & Visual Proof

### 1. Ingress Firewall Intercepting Prompt Injections (OWASP LLM01)
The firewall inspects and stops jailbreak attempts with a **`403 Forbidden`** status before any upstream API call is executed:

<!-- ========================================================================= -->
<!-- 📸 PLACEHOLDER: INGRESS JAILBREAK BLOCKED SCREENSHOT -->
<!-- Insert your screenshot showing the red "BLOCKED BY INGRESS FIREWALL" banner -->
<!-- ========================================================================= -->
<p align="center">
  <img src="docs/screenshots/jailbreak_blocked.png" alt="Ingress Firewall Blocking Jailbreak" width="850">
</p>
<p align="center"><em>Figure 2: Real-time Jailbreak and System Override interception.</em></p>

---

### 2. Surgical PII Anonymization & JSON Restoration
Raw credit cards and customer names are stripped before transit and restored into valid JSON outputs on egress:

<!-- ========================================================================= -->
<!-- 📸 PLACEHOLDER: PII MASKING & RESTORATION SCREENSHOT -->
<!-- Insert your screenshot showing the JSON receipt with "PII Restored (2)" badge -->
<!-- ========================================================================= -->
<p align="center">
  <img src="docs/screenshots/pii_restoration_json.png" alt="Reversible PII Masking and Restoration" width="850">
</p>
<p align="center"><em>Figure 3: Reversible PII token substitution and zero-leakage egress restoration.</em></p>

---

### 3. Live FinOps & Observability Dashboard
Aggregated analytics tracking total cost, baseline avoidance, latency, and blocked threats:

<!-- ========================================================================= -->
<!-- 📸 PLACEHOLDER: FINOPS DASHBOARD SCREENSHOT -->
<!-- Insert your screenshot of the "/v1/analytics/dashboard" or "FinOps & Analytics" tab -->
<!-- ========================================================================= -->
<p align="center">
  <img src="docs/screenshots/finops_dashboard.png" alt="FinOps and Analytics Dashboard" width="850">
</p>
<p align="center"><em>Figure 4: Real-time FinOps ledger, latency metrics, and savings breakdown.</em></p>

---

## 📊 FinOps Cost Optimization Matrix

| Scenario / Task Type | Default Route (Without Gateway) | Aegis Smart Route | Cost Reduction (%) |
| :--- | :--- | :--- | :--- |
| **Simple Summarization & QA** | GPT-4o ($2.50 / $10.00 per 1M) | Gemini 2.0 Flash ($0.10 / $0.40 per 1M) | **-96.0%** 🟢 |
| **Translation & Classification** | GPT-4o ($2.50 / $10.00 per 1M) | GPT-4o-mini ($0.15 / $0.60 per 1M) | **-94.0%** 🟢 |
| **High Context Bulk Analysis (50k tokens)** | GPT-4o ($0.125 / req) | Gemini 2.0 Flash ($0.005 / req) | **-96.0%** 🟢 |
| **Deep Reasoning / Math Proofs** | GPT-4o ($2.50 / $10.00 per 1M) | GPT-4o ($2.50 / $10.00 per 1M) | **Optimized for Accuracy** |
| **Provider Downtime (HTTP 429/500)** | Application Crash (100% loss) | Transparent Failover to Gemini | **100% Availability** 🛡️ |

---

## 📂 Clean Architecture Directory Structure

```text
aegis-gateway/
├── docs/                               # Architecture diagrams & screenshots
├── scripts/
│   └── seed_and_benchmark.py           # Automated red-teaming traffic generator
├── src/
│   └── aegis_gateway/
│       ├── main.py                     # FastAPI application factory & lifespan
│       ├── api/                        # HTTP Endpoints & Routers
│       │   └── v1/
│       │       ├── chat.py             # Main proxy (/v1/chat/completions)
│       │       ├── analytics.py        # FinOps metrics (/v1/analytics/summary)
│       │       ├── health.py           # Healthcheck probe (/v1/health)
│       │       └── ui.py               # Embedded Aegis Studio SPA UI (/)
│       ├── core/                       # Settings, Config & Logging
│       │   ├── config.py               # Pydantic v2 BaseSettings
│       │   └── logger.py               # Structured Loguru logging
│       ├── domain/                     # Domain DTOs, Schemas & Models
│       │   └── models.py
│       ├── firewall/                   # Ingress Security Layer
│       │   ├── pii_anonymizer.py       # Presidio reversible pseudonymization
│       │   ├── prompt_injection_scanner.py # Heuristic OWASP LLM01 detector
│       │   └── ingress_pipeline.py     # Ingress orchestrator
│       ├── router/                     # Smart Routing & FinOps Layer
│       │   ├── pricing.py              # Real-time token pricing catalog
│       │   ├── token_counter.py        # Tiktoken tokenizer engine
│       │   ├── complexity_analyzer.py  # Intent & reasoning depth classifier
│       │   └── smart_router.py         # Dynamic routing orchestrator
│       ├── providers/                  # Resilient LLM Execution Layer
│       │   ├── base.py                 # Abstract BaseLLMProvider interface
│       │   ├── openai_provider.py      # Async OpenAI SDK adapter
│       │   ├── gemini_provider.py      # Async Google GenAI SDK adapter
│       │   ├── circuit_breaker.py      # Fault tolerance & state machine
│       │   └── dispatcher.py           # Multi-provider resilient dispatcher
│       ├── egress/                     # Egress Guardrails Layer
│       │   ├── demasker.py             # Safe PII restoration engine
│       │   ├── output_moderator.py     # Secret & credential leak scanner
│       │   └── pipeline.py             # Egress validation orchestrator
│       └── observability/              # Asynchronous Persistence Layer
│           ├── database.py             # SQLAlchemy 2.0 async engine & session
│           ├── models.py               # TransactionAuditLog ORM table
│           └── service.py              # FinOps analytical calculations
├── tests/                              # Automated Pytest Suite (14+ tests)
│   ├── conftest.py
│   ├── test_health.py
│   ├── test_ingress_firewall.py
│   ├── test_smart_router.py
│   ├── test_resilient_dispatcher.py
│   ├── test_egress_pipeline.py
│   └── test_end_to_end_gateway.py
├── pyproject.toml
└── uv.lock
```

---

## ⚡ Quickstart & Installation

### Prerequisites
- **Python 3.12+**
- **uv** (Astral's fast Python package manager):
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

### 1. Clone & Install Dependencies
```bash
git clone https://github.com/<your-username>/aegis-llm-gateway.git
cd aegis-llm-gateway

# Synchronize virtual environment with lockfile
uv sync
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env` and configure your API keys:
```bash
cp .env.example .env
```

Edit `.env`:
```ini
APP_NAME=Aegis-LLM-Gateway
APP_ENV=development
DEBUG=True

# Upstream LLM Provider API Keys
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=AIzaSy...

# Security Flags
ENABLE_PII_MASKING=True
ENABLE_JAILBREAK_DETECTION=True

# Database Configuration
DATABASE_URL=sqlite+aiosqlite:///./aegis_gateway.db
```

### 3. Run Automated Tests
Execute the complete test suite across all 5 architectural layers:
```bash
uv run pytest -v
```

### 4. Start the Application
Launch the server with Uvicorn:
```bash
uv run uvicorn aegis_gateway.main:app --reload --port 8000
```

- **Interactive Studio UI**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Swagger REST API Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **FinOps Telemetry Dashboard**: [http://127.0.0.1:8000/v1/analytics/dashboard](http://127.0.0.1:8000/v1/analytics/dashboard)

### 5. Run Adversarial Red-Teaming & Benchmark Simulation
Populate your database with realistic mixed traffic (Jailbreaks, PII queries, Deep reasoning, and Failovers):
```bash
uv run python scripts/seed_and_benchmark.py
```

---

## 🛡️ OWASP Top 10 for LLM Compliance Matrix

| OWASP Vulnerability | Threat Description | Aegis-LLM Defense Mechanism |
| :--- | :--- | :--- |
| **LLM01: Prompt Injection** | Adversarial jailbreaks and instruction overrides. | `PromptInjectionScanner` inspects syntax, control delimiters, and heuristic jailbreak signatures before dispatch. |
| **LLM02: Sensitive Information Disclosure** | Leaking PII or proprietary secrets in prompts or outputs. | `PIIAnonymizer` masks PII upstream with reversible tokens; `OutputModerator` blocks output leaks (`sk-...`, Bearer tokens). |
| **LLM04: Model Denial of Service** | Resource exhaustion and single-provider rate limits. | `SmartRouter` distributes load; `CircuitBreaker` and `ResilientDispatcher` provide zero-downtime auto-failovers. |
| **LLM06: Excessive Agency & Uncontrolled Output** | Unchecked LLM generations reaching end-users. | `EgressPipeline` enforces strict content sanitization and schema validation before delivery. |

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author & Connect

Developed with passion by **Nchourupouo Mohamed** – AI Engineer.

- **LinkedIn**: [linkedin.com/in/your-profile](https://linkedin.com/in/your-profile)
- **GitHub**: [github.com/your-username](https://github.com/your-username)