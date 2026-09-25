# Emissions and quality controls

## Decision context
What emissions are financed by the scoped holdings, how complete is the data, and why did the measured inventory change?

## Assignment
Separate Scope 1+2 from Scope 3; record Scope 2 method, reporting year, restatement version and category coverage. Missing emissions are null, not zero. Record data-quality scores as method-dependent inputs rather than infer them from vendor name.

## Required output sections
- `scope12_vs_scope3`: substantive analysis linked to claim IDs.
- `evic_revenue_sources`: substantive analysis linked to claim IDs.
- `missing_data`: substantive analysis linked to claim IDs.
- `restatements`: substantive analysis linked to claim IDs.

## Evidence and methodology
Use PCAF-2025 with edition, applicability, date and limitations. Source references are in `references/standards.json` from the repository root.

## Return contract
Return the structured artifact in `schemas/artifact.schema.json`; copy run_id, input_digest, stage_id and revision from the current packet. Never recycle IDs from a demo. Source uncertainty is not resolved by lowering confidence alone: preserve a gap or issue.

## Domain boundary
Executable accounting is limited to long-only listed-company equity and corporate-debt EVIC inputs, not all PCAF asset classes. No short-netting, derivatives, sovereign GDP denominator, nature credits, or avoided-emissions offsets. Methodology changes and scope restatements require manual reconciliation.
