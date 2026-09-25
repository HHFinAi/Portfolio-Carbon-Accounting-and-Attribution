---
name: carbon-emissions
description: Emissions and quality controls for institutional sustainable-finance research; return evidence-linked findings, assumptions, gaps and reviewable outputs.
license: MIT
metadata:
  author: HHFinAi
  version: "0.2.0"
---
# Emissions and quality controls

Read `../../AGENTS.md` and `../../prompts/stages/emissions.md` relative to this skill directory. Obtain the current stage packet using the repository CLI. Do not create or claim unavailable source access.

## Task
Separate Scope 1+2 from Scope 3; record Scope 2 method, reporting year, restatement version and category coverage. Missing emissions are null, not zero. Record data-quality scores as method-dependent inputs rather than infer them from vendor name.

## Deliverable
Return the fields in `../../schemas/artifact.schema.json`; use the current run ID and input digest. Required sections: scope12_vs_scope3, evic_revenue_sources, missing_data, restatements. Include source IDs, scope, periods, methods and material gaps. Call only allowlisted calculations with explicit provenance; missing evidence means NEEDS_DATA, not invented values.

## Limit
Executable accounting is limited to long-only listed-company equity and corporate-debt EVIC inputs, not all PCAF asset classes. No short-netting, derivatives, sovereign GDP denominator, nature credits, or avoided-emissions offsets. Methodology changes and scope restatements require manual reconciliation.
