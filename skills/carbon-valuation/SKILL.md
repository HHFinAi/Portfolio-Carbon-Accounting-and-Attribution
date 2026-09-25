---
name: carbon-valuation
description: Inventory and period attribution for institutional sustainable-finance research; return evidence-linked findings, assumptions, gaps and reviewable outputs.
license: MIT
metadata:
  author: HHFinAi
  version: "0.2.0"
---
# Inventory and period attribution

Read `../../AGENTS.md` and `../../prompts/stages/valuation.md` relative to this skill directory. Obtain the current stage packet using the repository CLI. Do not create or claim unavailable source access.

## Task
Compute listed-corporate attribution only on valid positive EVIC. Show holdings, issuer emissions and EVIC contributions using an exact three-factor Shapley bridge. Separate entries, exits and coverage changes. Do not call portfolio reweighting or denominator appreciation real-economy decarbonisation.

## Deliverable
Return the fields in `../../schemas/artifact.schema.json`; use the current run ID and input digest. Required sections: financed_inventory, waci_and_coverage, factor_bridge, methodology_limitations. Include source IDs, scope, periods, methods and material gaps. Call only allowlisted calculations with explicit provenance; missing evidence means NEEDS_DATA, not invented values.

## Limit
Executable accounting is limited to long-only listed-company equity and corporate-debt EVIC inputs, not all PCAF asset classes. No short-netting, derivatives, sovereign GDP denominator, nature credits, or avoided-emissions offsets. Methodology changes and scope restatements require manual reconciliation.
