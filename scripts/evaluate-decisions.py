"""Paired A/B study against TWO isolated Go servers; B may incur API charges.

Usage: python scripts/evaluate-decisions.py --baseline http://localhost:8080
       --treatment http://localhost:8081 --output docs/research/exports/paired.json
Each Go server must point to a separate AI process with the corresponding setting.
"""
import argparse
import json
import statistics
import time
from pathlib import Path

import httpx

CASES = [
    ("The ocean rises and consumes the fortress.", "RAISE_WATER", "VALID"),
    ("The forest catches fire.", "START_FIRE", "VALID"),
    ("The invisible moon destroys the ancient city.", "DESTROY_ENTITY", "INVALID"),
    ("The fortress remembers the last attack.", "MEMORY_ADD", "AMBIGUOUS"),
]


def study(base, expected_enabled, repeats, price, transport=None):
    records = []
    with httpx.Client(base_url=base, timeout=20, transport=transport) as client:
        for repeat in range(repeats):
            for prompt, reference_action, reference_status in CASES:
                seed = 42 + repeat
                world = client.post("/api/world/generate", json={"scenario_id": "scenario_1", "scenario": "A fortress stands between a living forest and a restless ocean.", "seed": seed})
                world.raise_for_status()
                started = time.perf_counter()
                interpreted = client.post("/api/prompt/interpret", json={"prompt": prompt})
                interpreted.raise_for_status()
                data = interpreted.json()
                elapsed = (time.perf_counter() - started) * 1000
                decision = data.get("decision") or {}
                if (decision.get("status") != "disabled") != expected_enabled:
                    raise RuntimeError("Server decision configuration does not match study arm")
                if decision.get("provider") != "cloudflare_clef_flash":
                    raise RuntimeError("Study arm is not configured for Clef-Flash")
                action = data.get("action") or {}
                execution_status = None
                if data.get("proposal_id"):
                    execution_status = client.post("/api/prompt/execute", json={"prompt": prompt, "actor": "human", "proposal_id": data["proposal_id"]}).status_code
                records.append({"seed": seed, "prompt": prompt, "reference_action": reference_action,
                                "reference_status": reference_status, "action": action,
                                "status": data.get("status"), "decision": decision,
                                "latency_ms": elapsed, "go_execution_status": execution_status})
    latencies = sorted(row["latency_ms"] for row in records)
    executions = [row["go_execution_status"] for row in records if row["go_execution_status"] is not None]
    tokens = sum(row["decision"].get("usage", {}).get("input_tokens", 0) for row in records)
    invoked = [row for row in records if row["decision"].get("invoked")]
    selections = [row for row in invoked if len(row["decision"].get("candidate_ids", [])) > 1]
    metered = [row for row in invoked if row["decision"].get("billed_credits") is not None]
    credits = sum(row["decision"]["billed_credits"] for row in metered)
    metrics = {"cases": len(records), "action_agreement": statistics.mean(row["action"].get("action_type") == row["reference_action"] for row in records),
               "status_agreement": statistics.mean(row["status"] == row["reference_status"] for row in records),
               "schema_valid_rate": statistics.mean(bool(row["action"].get("action_id")) and bool(row["action"].get("action_type")) for row in records),
               "go_validation_pass_rate": statistics.mean(code == 200 for code in executions) if executions else None,
               "go_execution_attempts": len(executions),
               "latency_p50_ms": statistics.median(latencies), "latency_p95_ms": latencies[max(0, int(len(latencies)*0.95 + 0.999)-1)],
               "fallback_rate": statistics.mean(row["decision"].get("fallback", False) for row in records),
               "provider_failure_rate": statistics.mean(row["decision"].get("invoked", False) and row["decision"].get("fallback", False) for row in records),
               "input_tokens": tokens, "estimated_cost": tokens * price / 1000000 if price is not None else None,
               "invalid_selection_rate": statistics.mean(row["decision"].get("reason") == "invalid_choice" for row in selections) if selections else None,
               "selection_requests": len(selections),
               "actual_billed_credits_reported": credits if metered else None,
               "metered_requests": len(metered), "unmetered_requests": len(invoked) - len(metered),
               "candidate_selection_accuracy": None,
               "limitations": "One real candidate per prompt; selection metrics are unavailable. Reference labels require human review. Schema metric checks required fields only. Go pass rate covers eligible executions only. Estimated token cost is not billed usage; actual credits are reported separately, with missing metering never assumed zero."}
    return {"metrics": metrics, "records": records}


def assert_paired_candidates(baseline, treatment):
    if len(baseline["records"]) != len(treatment["records"]):
        raise RuntimeError("Study arms have different case counts")
    for first, second in zip(baseline["records"], treatment["records"]):
        # IDs are generated UUIDs; all executable candidate contents must match.
        def canonical(record):
            return {key: value for key, value in record["action"].items() if key != "action_id"}
        if (first["seed"], first["prompt"]) != (second["seed"], second["prompt"]) or canonical(first) != canonical(second):
            raise RuntimeError("Study arms did not produce the same seeded candidate action")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", required=True)
    parser.add_argument("--treatment", required=True)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--input-price-per-million", type=float)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.repeats < 1 or args.baseline == args.treatment:
        parser.error("Use positive repeats and two isolated servers")
    report = {"baseline": study(args.baseline, False, args.repeats, args.input_price_per_million),
              "cloudflare_clef_flash": study(args.treatment, True, args.repeats, args.input_price_per_million)}
    assert_paired_candidates(report["baseline"], report["cloudflare_clef_flash"])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
