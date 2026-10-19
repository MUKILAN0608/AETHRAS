# Phase 3.5 ? Cloudflare Clef-Flash fast decisions

Clef-Flash is the only supported decision provider. The deterministic Phase 2/3
demo remains available with the provider disabled, which is the default. There is
no alternate hosted-provider fallback. Offline tests and the local Godot/Go/Python
flow passed; authenticated Cloudflare inference and a reviewed A/B benchmark are
not verified. No accuracy, latency, cost or gameplay improvement is claimed.

## Inspection and implementation plan

Reviewed ARCHITECTURE.md, PHASE2_WORLD_ENGINE.md, PHASE3_PROMPT_ENGINE.md and ROADMAP.md;
Python endpoints/schemas/compiler/critic/validator/configuration/research logs/tests;
Go interpret/execute handlers, world rules, action mapping and proposal storage;
Godot project.godot, scenes/main.tscn, node paths, signals, main.gd, semantic_world.gd
and game_config.gd; dependencies, environment templates and startup scripts.

The Windows user profile resolved to C:/Users/Mukil. Recursively inspected
C:/Users/Mukil/.agents/skills and its skill entrypoints/directories: no installed
Godot skill was found, so none could be read. Existing Godot conventions were used;
no skill file was modified, deleted or relocated, and no missing instructions were
invented. The initial .NET profile lookup returned empty under the sandbox; the
actual USERPROFILE environment value supplied the resolved path.

Plan followed: replace the prior adapter in the existing provider boundary; verify
Cloudflare schemas; establish explicit root dotenv loading; preserve critic and Go
execution safeguards; add correlated outcome logging and bounded UI error handling;
verify mocked provider behavior, Go authority and the live local Godot HTTP flow.
Compatibility changes: old provider settings are rejected/unused; configuration now
comes from root .env; the active log path is ai/app/logs/experiments.jsonl. No
parallel prompt pipeline or future Phase 4+ modules were added.

## Exact verified hosted contract

Official sources checked during implementation:
- https://developers.cloudflare.com/workers-ai/models/clef-flash/
- https://developers.cloudflare.com/workers-ai/models/clef-flash/schema-input.json
- https://developers.cloudflare.com/workers-ai/models/clef-flash/schema-output.json
- https://developers.cloudflare.com/workers-ai/get-started/rest-api/

POST https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/@cf/cloudflare/clef-flash
with Authorization: Bearer <CLOUDFLARE_AUTH_TOKEN> and application/json.
The endpoint model is @cf/cloudflare/clef-flash. The request BODY model is clef-flash:

```json
{
  "model": "clef-flash",
  "state": {"prompt": "...", "candidates": []},
  "questions": {
    "review": {"type": "noul", "instructions": "Does this proposal need additional review?"}
  }
}
```

The REST envelope is {success, errors, messages, result}. The model output is
inside result, never the outer response: {model, answers, usage}. A successful
HTTP response still fails closed when success is false, errors is nonempty,
result is missing, or schema validation fails. Raw error bodies/messages are not
returned to players or logged. cf-ray is an allowlisted diagnostic identifier;
local request_id exists even when no provider identifier is returned.

Choice answers require type, choice, probabilities and confidence. Score answers
require type, weighted score, legend, probabilities and confidence. Noul requires
type and noul (a yes probability). Usage requires integer input_tokens and
output_tokens; neither is invented, and output_tokens is not assumed to be zero.
The parser rejects non-finite/out-of-range values, unexpected question IDs/types,
unknown candidate selections, non-maximal selections, inconsistent distributions,
altered legends and inconsistent weighted scores. Confidence is not game legality.

The official input schema permits 1?64 questions, choice sets with 2?255 options,
and score rubrics with 2?10 levels. We batch three questions for the existing one
proposal: impact, review routing and future simulation routing. If a future producer
supplies multiple real candidates, selection uses their identifiers plus
none_of_the_above; at most 254 candidates are accepted. No candidates are invented.
Impact levels: 0 local/reversible; 1 substantial tactical impact; 2 widespread,
destructive or persistent effect. The weighted score can be between levels.

The service sends text/structured state only. No images/video or future multimodal
modules are implemented. State contains the original prompt, normalized intent,
extracted references, relationships and constraints, critic findings, relevant world
facts/environment/turn, validation result and existing candidates. Arbitrary context,
credentials and unbounded history are excluded. Local state budget is 24 KB; the
streamed response limit is 256 KB. This is a conservative byte heuristic rather
than exact model token accounting. Over-budget state requires review instead of
being silently truncated locally. The hosted service can truncate long state;
future production evaluation should add exact token budgeting.

## Provider boundary, policy and authority

The stable interface is evaluate_decision(state, candidate_actions, settings),
returning DecisionResult. provider.py defines the protocol/registry;
cloudflare_clef_client.py owns Cloudflare transport/envelope handling;
questions.py owns rubrics; decision_router.py owns local policy. Only
cloudflare_clef_flash is registered. No excluded provider implementation remains.

The original Normalize ? Intent ? Entities ? Strategy ? Compile ? Critic ? Validate
pipeline remains responsible for language. Invalid/ambiguous proposals skip
inference. An evaluated response cannot upgrade the critic or change action contents.

Initial uncalibrated gates: confidence below 0.7 requires review; a choice lead
<=0.1 requires review; review noul >=0.5 requires review. Simulation noul >=0.5 only
recommends future simulation. With one candidate, confidence is impact-assessment
confidence, not candidate selection confidence. None-of-the-above requires review.

Failures (timeout, connection failure, authentication/authorization errors, rate
limits, malformed/envelope errors or invalid selection) mark fallback and require
review. VALID becomes AMBIGUOUS, so Go does not issue an execution token. Disabled
mode preserves the existing deterministic proposal path. No hosted provider is
silently substituted, and failure never means permission to execute.

The total deadline defaults to 3 seconds, configurable up to 10. Connection timeout
is at most 1 second within that deadline. Retries default to 0, maximum 2. Only
429/502/503/504 may retry with bounded exponential backoff, jitter and Retry-After
(seconds or HTTP date), all within the same deadline. 401/403 and permanent failures
are not retried. Uncertain network delivery/timeouts are never retried automatically.
Redirects are disabled. HTTPX is an existing dependency; no SDK was invented.

Go stores approved proposals with actor/prompt and a full-world digest; tokens
expire in five minutes and are single-use. At execute, Go uses the stored action,
rejects stale/replayed/edited-context tokens, rechecks targets/permissions/numeric
limits/rules against the current world, and revalidates in Manager.ApplyAction before
mutation. Exact entity IDs resolve to exact targets; unsupported multi-target
proposals are rejected under the single-target Phase 2 action contract. The demo
serializes world requests to keep validation/execution atomic. Authenticated
multi-match/distributed permissions and persistent idempotency remain future work.

## Trace and Godot behavior

The default prompt The ocean rises and consumes the fortress travels through
Godot's asynchronous HTTPRequest to Go interpret. Go supplies authoritative world
context; Python compiles RAISE_WATER with intensity 0.87 and resolved entities,
then runs critic/validation and optional bounded decisions. Only approved VALID
proposals receive proposal_id. After player review, Go maps RAISE_WATER to FLOOD,
updates water/affected entity state/events/history, and Godot renders that result.

Existing node paths, controls, signals and scene layout remain. Execute requires a
VALID proposal and token. HTTPRequest has a 20-second client deadline (Go's Python
request has a 15-second deadline), so network work stays asynchronous. Errors clear
stale pending proposals, restore controls and explain stale/rejected/time-out
conditions. An existing tick completion bug was fixed so environment advancement
releases the busy state. Null action/strategy metadata is handled safely.
GODOT_GAME_SERVER_URL may override the backend URL through the Godot process
environment; it is only a Go server URL, never a provider credential.

## Root environment loading and security

A local root .env was created/reconciled without displaying its values. Existing
unrelated values/comments and credential values are preserved. .gitignore excludes
.env, credential files and generated logs; .env.example contains only safe defaults.
Python Settings explicitly resolves Path(__file__).resolve().parents[2] / '.env',
so changing working directory does not select a different configuration file.
Pydantic Settings gives deployment environment variables precedence over dotenv.
No dependency was added: pydantic-settings and python-dotenv were already present.

Required account ID/token are validated only when enabled. Account IDs must be
32 hexadecimal characters. Tokens use SecretStr, and validation errors hide input
values. Configured health is a boolean; neither account ID nor token is exposed.
HTTPS base URL must have no embedded credentials/query/fragment. The model setting
is restricted to the verified endpoint model. No credentials are placed in Godot,
its exports, game settings, HTTP payloads or research records.

## Windows PowerShell setup and launch

From C:/Users/Mukil/Propmt, run in separate terminals:

The existing full ML setup script targets Python 3.11 (py -3.11), with Go and
Godot on PATH. Its fallback to another Python version does not guarantee the old
PyTorch pins are compatible; the full dependency installation was not rerun here.

```powershell
# Terminal 1: setup once if needed, then start AI
.\scripts\setup-ai.ps1
.\scripts\start-ai.ps1
# Terminal 2
.\scripts\start-game-server.ps1
# Terminal 3
.\scripts\launch-godot.ps1
```

The offline demo needs no Cloudflare account: Generate World ? Interpret Prompt ?
Review ? Execute. The startup script restores the caller's working directory.
For Cloudflare, edit ROOT .env locally (never commit it):

```dotenv
AETHRAS_DECISION_ENABLED=true
AETHRAS_DECISION_PROVIDER=cloudflare_clef_flash
AETHRAS_DECISION_TIMEOUT_SECONDS=3
AETHRAS_DECISION_MAX_RETRIES=0
CLOUDFLARE_ACCOUNT_ID=<your-32-hex-account-id>
CLOUDFLARE_AUTH_TOKEN=<your-workers-ai-token>
CLOUDFLARE_CLEF_MODEL=@cf/cloudflare/clef-flash
CLOUDFLARE_CLEF_API_BASE_URL=https://api.cloudflare.com/client/v4
```

Alternatively supply values through the AI process environment, which overrides
.env. Obtain the account ID and a Workers AI API token from Cloudflare's dashboard;
follow the official REST setup guide for permissions. Restart AI after edits.
GET http://localhost:8000/api/v1/prompt/health reports provider/model and safe
configured/enabled state. It does not make a remote health request or prove token
validity, account access or hosted model availability.

## Offline and explicit live tests

```powershell
cd ai
.\.venv\Scripts\python.exe -m pytest tests -q
cd ..\server\game-server
go test ./...
cd ..\..
godot --headless --path game/godot --editor --quit
godot --headless --path game/godot --quit-after 2
ai/.venv/Scripts/python.exe scripts/smoke-phase35.py --godot
```

The last script builds a temporary Go executable and starts isolated local AI/Go
services on ephemeral ports with the decision provider explicitly DISABLED. It
verifies real HTTP world execution, replay/critic rejection, then runs the actual
Godot main scene through generate, interpretation, review, execute, tick, invalid
proposal and HTTP-error recovery. A second test-only AI app uses a delayed
MockTransport to trigger the provider deadline: Godot continues processing frames,
restores its controls and keeps Execute disabled. These synthetic provider records
use a temporary log directory. The harness always stops its services and never
calls Cloudflare. Normal Python tests mock all provider HTTP and isolate research logs.

An optional LIVE smoke test is billable and requires explicit opt-in plus valid
credentials in root .env or the environment:

```powershell
cd ai
$env:AETHRAS_DECISION_LIVE_TEST = 'true'
.\.venv\Scripts\python.exe -m pytest tests/test_decision_engine.py -k live_smoke -v
Remove-Item Env:AETHRAS_DECISION_LIVE_TEST
```

Ordinary tests skip this call. Merely setting a key does not enable a live test.
A live pass must verify the real envelope, answer/usage fields and local policy;
mock fixtures are never described as live results.

## Research stream and evaluation

All NEW Python pipeline/decision and Go execution records append to
ai/app/logs/experiments.jsonl. Historical records from the former ai/logs file were
copied once into this active stream; the old file is retained as a historical
archive and has no active writer. No past provider records were relabeled.
Decision events include local request ID, provider, decision-v3, configured/resolved
model, action/candidate IDs, match/turn, scores/probabilities/confidence, latency,
attempts, success/fallback/reason and critic findings. Go execution events join by
request/action ID and record authoritative validation outcome and final event IDs.
No raw provider error bodies, authorization headers or hidden reasoning are logged.
Original Phase 3 logs already contain prompts; use nonpersonal research data.

Go's default log path is resolved from the repository source location. A standalone
binary deployed away from this tree needs a shared-path deployment design; no claim
of distributed crash-safe logging is made. Local append failures are reported with
a safe generic diagnostic and never turn a rejected action into an accepted one.

The adapter records documented input/output token usage and an optional cf-ray.
There is no verified per-request Cloudflare billed-credit header in this contract;
billed_credits stays unknown, and dollar estimates are not actual billed usage.
Reconcile account billing separately before claiming a complete cost measurement.

For a reviewed study, prepare TWO isolated Go+AI stacks (baseline disabled,
treatment Clef enabled), then run:

```powershell
python scripts/evaluate-decisions.py --baseline http://localhost:8080 --treatment http://localhost:8081 --repeats 3 --output docs/research/exports/paired.json
```

Matching seeds/prompts and identical candidate contents (apart from generated IDs)
are enforced. Metrics include reference action/status agreement, required field
validity, eligible Go execution pass rate, latency p50/p95, invalid selections,
fallback/failure rate and token usage. Selection accuracy/rate is unavailable for
today's single-candidate pipeline; the four seed reference labels need human review
and expansion. No A/B results, threshold calibration or quality gain are claimed.

## Verification and remaining limitations

Python offline suite: 81 passed, 1 explicitly gated live test skipped. Go tests
passed for server and world packages. Godot headless import passed. The real local
Godot/Go/Python smoke passed all stated scenarios, including responsive frame
processing and blocked execution during a mocked provider timeout, with no hosted API call. The
local test runtime uses Python 3.14, FastAPI 0.135.3, httpx 0.28.1 and temporary
workspace dependencies (Pydantic 2.14.1, pydantic-settings 2.7.1, pytest 8.4.2,
pytest-asyncio 0.25.2). Existing asyncio-policy deprecation warnings remain.
The full older pinned ML environment was not reinstalled or verified.

Still pending: authenticated Cloudflare smoke, reviewed A/B evaluation, threshold
calibration, exact token budgeting, account billing reconciliation and graphical
human acceptance. PostgreSQL/Redis wiring, durable multi-match state, authenticated
multiplayer, live LLM parsing, world-model simulation and other excluded future
modules remain deferred. Offline success is not proof of hosted integration success.

Main changed/created files: ai/app/config.py, main.py, prompt_schemas.py,
prompt_engine/pipeline.py, research_logger.py; decision_engine/provider.py,
cloudflare_clef_client.py, decision_router.py, schemas.py and questions.py; Python
contract/config/evaluation tests; server/game-server/research.go, proposals.go,
prompt_handlers.go and their tests; game_config.gd, main.gd, semantic_world.gd and
tests/prompt_flow_test.gd and ai/tests/mocked_provider_app.py; scripts/start-ai.ps1, smoke-phase35.py and
evaluate-decisions.py; root .env (local), .env.example, .gitignore and these docs.
