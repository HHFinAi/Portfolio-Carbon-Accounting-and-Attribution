# Methodology and model boundaries

Executable accounting is limited to long-only listed-company equity and corporate-debt EVIC inputs, not all PCAF asset classes. No short-netting, derivatives, sovereign GDP denominator, nature credits, or avoided-emissions offsets. Methodology changes and scope restatements require manual reconciliation.

## Analytical outputs
- Separate Scope 1+2 and Scope 3 financed inventories
- Full-denominator observed contribution and covered-only WACI
- Coverage and exposure-weighted data quality
- Reconciled holdings/emissions/EVIC change bridge

## Calculation library
The implementation is in `sf_agent/analytics.py`; generic helpers are in `sf_agent/maths.py`. Every exposed operation has argument-unit and result-unit metadata and is callable with `python -m sf_agent calc`. Arguments are not sourced automatically. See the operation inventory below, the worked example and domain regression tests.

### Financed emissions: implemented boundary
Supported calculation scope is positive long exposure to **listed-company equity and corporate bonds**, using EVIC. Listed equity financed amount is market value; corporate-bond financed amount is the book value defined by the selected PCAF method. Market value is recorded separately for WACI. PCAF third edition, printed pp. 41–42, identifies these numerator conventions. Unlisted companies, sovereigns, project finance, mortgages, derivatives, shorts and negative/zero EVIC need separate methods and are not silently processed.

All holdings must use a common currency and consistent source boundaries. Duplicate instrument IDs, conflicting issuer metrics, inconsistent amount bases and aggregate issuer financed amounts greater than EVIC are rejected. The EVIC denominator is supplied; the helper does not construct it from raw accounts. Zero or unknown denominators are unassessed, never divided through. M&A, restatements, timing and FX require explicit review.

`financed_emissions` = financed amount / EVIC × issuer emissions. Scope 1+2 and Scope 3 are reported separately, not added into an unexplained total. `carbon_inventory` reports observed contributions, coverage, unassessed exposure, independently covered data-quality scores and WACI. A null emission value is unknown; a verified numeric zero is a measured zero. Coverage uses the scoped financed amount; WACI uses market value and emissions per million units of issuer revenue. The WACI partial full-portfolio-denominator contribution and covered-only average are separately named. Out-of-scope NAV is reported as unmodelled, not automatically cash or zero-emission exposure. PCAF data quality 1–5 is supplied; the package does not assign it from reports or claim comprehensive PCAF conformance.

### Period attribution
`financed_emissions_bridge` uses exact three-factor Shapley decomposition of A×E/EVIC, averaging marginal changes across all six factor orderings. It separates financed-amount, reported-emissions and EVIC effects and reconciles to total change. It is a mathematical attribution convention, not a causal model. A corporate-bond financed-amount change can reflect accounting, amortization or trades; it is not automatically trading alone.

`portfolio_emissions_attribution` aggregates instruments to issuer, separates continuing issuers from entries/exits, adds explicit coverage-gain/loss and boundary-change effects, and reconciles the change in the **observed** inventory. It must not interpret an inventory decline caused by sales, missing data or EVIC increases as real-world decarbonisation. Currency changes, methodology changes and restatements are not automatically isolated; source comparability and any extra attribution need analyst review.

### Normalized holdings contract
Each record requires `id`, `issuer_id`, `asset_type` (`listed-equity`/`corporate-bond`), `issuer_is_listed: true`, `amount_basis` (`market_value`/`book_value`), `financed_amount`, `market_value`, `currency`, `boundary_id`, `financial_year`, `emissions_year`, and nullable `evic`, `revenue`, `scope12_tco2e`, `scope3_tco2e`, `quality_scope12`, `quality_scope3`. Per-row evidence maps remain a host/analyst responsibility; nested arrays are not automatically bound to source metrics by the generic scalar-provenance engine.


## Evidence status
Causal and legal interpretations remain human judgments. The software is not a complete implementation or certification of the referenced standards. Read the exact applicable original documents; the dated source register gives the verification scope. Proposed changes and future validation dates must not be applied retrospectively or represented as current law.
