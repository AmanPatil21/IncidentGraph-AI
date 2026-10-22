# Runbook RB-LOCK-010: Database deadlocks

Owner: Platform Operations
Service: ledger-api
Trigger: DB_DEADLOCK

## Diagnostic checklist
1. Confirm incident time window, affected service and error code.
2. Inspect service logs and compare the last known healthy deployment.
3. Check upstream/downstream job dependencies.
4. Correlate metrics with configuration and deployment history.

## Recommended response
Review transaction ordering; add bounded retry; test locking change.

## Safety and escalation
Never perform production rollback, financial replay, credential changes, or external side effects without an authorized operator's approval. Escalate unresolved incidents to the service owner.

## Related incident
INC-010
