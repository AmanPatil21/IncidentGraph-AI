# Runbook RB-SCHEMA-004: Schema compatibility mismatch

Owner: Platform Operations
Service: reconciliation
Trigger: SCHEMA_MISMATCH

## Diagnostic checklist
1. Confirm incident time window, affected service and error code.
2. Inspect service logs and compare the last known healthy deployment.
3. Check upstream/downstream job dependencies.
4. Correlate metrics with configuration and deployment history.

## Recommended response
Review schema contract; deploy backward-compatible mapping; rerun validation.

## Safety and escalation
Never perform production rollback, financial replay, credential changes, or external side effects without an authorized operator's approval. Escalate unresolved incidents to the service owner.

## Related incident
INC-004
