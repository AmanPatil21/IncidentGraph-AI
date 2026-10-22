# Runbook RB-ETL-008: Missing upstream partition

Owner: Platform Operations
Service: analytics-etl
Trigger: UPSTREAM_DEPENDENCY_FAILED

## Diagnostic checklist
1. Confirm incident time window, affected service and error code.
2. Inspect service logs and compare the last known healthy deployment.
3. Check upstream/downstream job dependencies.
4. Correlate metrics with configuration and deployment history.

## Recommended response
Restore missing partition; validate dependency chain; rerun ETL after approval.

## Safety and escalation
Never perform production rollback, financial replay, credential changes, or external side effects without an authorized operator's approval. Escalate unresolved incidents to the service owner.

## Related incident
INC-008
