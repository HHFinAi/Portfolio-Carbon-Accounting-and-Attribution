# Portfolio interpretation

## Decision context
What emissions are financed by the scoped holdings, how complete is the data, and why did the measured inventory change?

## Assignment
Explain measurement changes before recommending portfolio work. A lower financed inventory is not independently evidence of additionality or lower climate risk. State turnover, transaction costs, tracking error, exposure changes and adverse-selection tradeoffs.

## Required output sections
- `real_economy_vs_portfolio`: substantive analysis linked to claim IDs.
- `engagement_priorities`: substantive analysis linked to claim IDs.
- `constraints_and_turnover`: substantive analysis linked to claim IDs.
- `disclosure_boundary`: substantive analysis linked to claim IDs.

## Evidence and methodology
Use PCAF-2025 with edition, applicability, date and limitations. Source references are in `references/standards.json` from the repository root.

## Return contract
Return the structured artifact in `schemas/artifact.schema.json`; copy run_id, input_digest, stage_id and revision from the current packet. Never recycle IDs from a demo. Source uncertainty is not resolved by lowering confidence alone: preserve a gap or issue.

## Domain boundary
Executable accounting is limited to long-only listed-company equity and corporate-debt EVIC inputs, not all PCAF asset classes. No short-netting, derivatives, sovereign GDP denominator, nature credits, or avoided-emissions offsets. Methodology changes and scope restatements require manual reconciliation.
