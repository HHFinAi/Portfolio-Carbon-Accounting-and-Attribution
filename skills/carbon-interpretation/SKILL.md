---
name: carbon-interpretation
description: Portfolio interpretation for institutional sustainable-finance research; return evidence-linked findings, assumptions, gaps and reviewable outputs.
license: MIT
metadata:
  author: HHFinAi
  version: "0.2.0"
---
# Portfolio interpretation

Read `../../AGENTS.md` and `../../prompts/stages/interpretation.md` relative to this skill directory. Obtain the current stage packet using the repository CLI. Do not create or claim unavailable source access.

## Task
Explain measurement changes before recommending portfolio work. A lower financed inventory is not independently evidence of additionality or lower climate risk. State turnover, transaction costs, tracking error, exposure changes and adverse-selection tradeoffs.

## Deliverable
Return the fields in `../../schemas/artifact.schema.json`; use the current run ID and input digest. Required sections: real_economy_vs_portfolio, engagement_priorities, constraints_and_turnover, disclosure_boundary. Include source IDs, scope, periods, methods and material gaps. Call only allowlisted calculations with explicit provenance; missing evidence means NEEDS_DATA, not invented values.

## Limit
Executable accounting is limited to long-only listed-company equity and corporate-debt EVIC inputs, not all PCAF asset classes. No short-netting, derivatives, sovereign GDP denominator, nature credits, or avoided-emissions offsets. Methodology changes and scope restatements require manual reconciliation.
