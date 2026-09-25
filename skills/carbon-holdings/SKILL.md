---
name: carbon-holdings
description: Holdings, denominators and scope for institutional sustainable-finance research; return evidence-linked findings, assumptions, gaps and reviewable outputs.
license: MIT
metadata:
  author: HHFinAi
  version: "0.2.0"
---
# Holdings, denominators and scope

Read `../../AGENTS.md` and `../../prompts/stages/holdings.md` relative to this skill directory. Obtain the current stage packet using the repository CLI. Do not create or claim unavailable source access.

## Task
Reconcile accounting perimeter, position IDs and issuer IDs. Aggregate positions in one issuer before attribution; reconcile joint equity/debt holdings. Inputs must use a common currency and scale. Exclude unsupported instruments explicitly, with the excluded portfolio value reported, not hidden.

## Deliverable
Return the fields in `../../schemas/artifact.schema.json`; use the current run ID and input digest. Required sections: position_reconciliation, entity_mapping, asset_class_boundary, currency_and_period. Include source IDs, scope, periods, methods and material gaps. Call only allowlisted calculations with explicit provenance; missing evidence means NEEDS_DATA, not invented values.

## Limit
Executable accounting is limited to long-only listed-company equity and corporate-debt EVIC inputs, not all PCAF asset classes. No short-netting, derivatives, sovereign GDP denominator, nature credits, or avoided-emissions offsets. Methodology changes and scope restatements require manual reconciliation.
