# Inventory and period attribution

## Decision context
What emissions are financed by the scoped holdings, how complete is the data, and why did the measured inventory change?

## Assignment
Compute listed-corporate attribution only on valid positive EVIC. Show holdings, issuer emissions and EVIC contributions using an exact three-factor Shapley bridge. Separate entries, exits and coverage changes. Do not call portfolio reweighting or denominator appreciation real-economy decarbonisation.

## Required output sections
- `financed_inventory`: substantive analysis linked to claim IDs.
- `waci_and_coverage`: substantive analysis linked to claim IDs.
- `factor_bridge`: substantive analysis linked to claim IDs.
- `methodology_limitations`: substantive analysis linked to claim IDs.

## Evidence and methodology
Use PCAF-2025 with edition, applicability, date and limitations. Source references are in `references/standards.json` from the repository root.

## Return contract
Return the structured artifact in `schemas/artifact.schema.json`; copy run_id, input_digest, stage_id and revision from the current packet. Never recycle IDs from a demo. Source uncertainty is not resolved by lowering confidence alone: preserve a gap or issue.

## Domain boundary
Executable accounting is limited to long-only listed-company equity and corporate-debt EVIC inputs, not all PCAF asset classes. No short-netting, derivatives, sovereign GDP denominator, nature credits, or avoided-emissions offsets. Methodology changes and scope restatements require manual reconciliation.

A domain calculation must pass recomputation. The minimal runnable illustration is `financed_emissions`; other needed specialist models must remain explicitly external and independently reviewed.
