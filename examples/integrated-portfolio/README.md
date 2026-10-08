# Five issuers: carbon accounting → site evidence → stewardship

**Research status: NEEDS_DATA. Information cutoff: 8 October 2026.** Start with the [investment committee memo](MEMO.md), then inspect the [inputs](inputs.json), [source ledger](sources.json), [results](results.json) and [proposed handoffs](handoffs.json).

This case combines real public issuer disclosures with a **hypothetical USD 10 million portfolio**. The weights are illustrative, not Ed's holdings, a client portfolio or a trading recommendation. Both snapshots use the same illustrative NAV; the weight changes do not represent observed trades or returns.

| Issuer | FY2023 / FY2024 period ends | 2023 weight | 2024 weight | EVIC status |
|---|---|---:|---:|---|
| Microsoft | 30 June / 30 June | 30% | 25% | Unverified; excluded from financed totals |
| Amazon | 31 December / 31 December | 25% | 20% | Unverified; excluded from financed totals |
| Meta | 31 December / 31 December | 20% | 25% | Constructed from dated filing components |
| Cisco | 29 July / 27 July | 15% | 15% | Unverified; excluded from financed totals |
| IBM | 31 December / 31 December | 10% | 15% | Unverified; excluded from financed totals |

Portfolio snapshots are dated **31 December 2023 and 31 December 2024**. Emissions and revenue match each issuer's fiscal year and year-end. This is a retrospective disclosure-vintage comparison retrieved in 2026, including later restatements, rather than a historical information-set backtest. Acquisition boundaries still require review for Microsoft and Cisco.

## Reproduce

From the repository root, using Python 3.10 or newer:

```sh
python3 examples/integrated-portfolio/model.py --check
python3 -m unittest discover -s tests -p 'test_integrated_portfolio.py' -v
python3 examples/integrated-portfolio/model.py
```

`--check` recomputes and compares committed results and hashes without writing files. The final command prints the full result to stdout. No credentials, market feed or model API is needed. Standard-library code calls the existing `sf_agent.analytics` inventory and financed-emissions attribution functions; the example adds exact six-permutation Shapley attribution for WACI.

## Definitions and coverage

For each separately reported scope, financed emissions are `illustrative holding value / EVIC × issuer emissions`. WACI is `sum(portfolio market-value weight × issuer emissions / revenue in USD millions)`. Scope 1 plus market-based Scope 2 and Scope 3 remain separate; offsets and removal credits are not subtracted. All monetary inputs are USD. Currency translation already embedded in global reported revenue stays within the revenue denominator effect; it is not separately identified.

Meta EVIC uses year-end outstanding Class A plus Class B shares at the disclosed Class A closing price, plus total liabilities. Class B has the disclosed conversion and economic rights; applying the Class A price is an explicit valuation convention. Rounded share counts make the result approximate. Preferred and minority equity are not separately presented in the reviewed balance sheet; modeled absence is an inference awaiting independent review. Under the cited PCAF definition, total liabilities include interest-bearing and non-interest-bearing liabilities; debt and leases are not added again, and cash is not deducted. See the ledger's filing and PCAF locators.

| Metric | 2023 | 2024 | Meaning |
|---|---:|---:|---|
| Scope 1+2 WACI | 9.129864 | 6.909311 | tCO2e per USD million revenue; 100% disclosed-data coverage |
| Scope 3 observed contribution on full NAV | 122.974547 | 98.716543 | 90% / 85% coverage; heterogeneous issuer methods |
| Scope 1+2 observed financed emissions | 0.102976 t | 0.077398 t | Meta only; 20% / 25% financed-exposure coverage |
| Complete portfolio financed emissions | Unassessed | Unassessed | Four unverified EVIC denominators |

Missing IBM Scope 3 remains `null`. Scope 3 covered-only intensity is also shown in the results, with a different denominator; it is not substituted for the full-NAV statistic. Meta changes its Scope 3 reporting criteria between years, so its observed delta is placed in a boundary/methodology bucket. A smaller reported intensity is not evidence of physical decarbonisation or investment alpha. Quality scores remain unassigned rather than inferred from publication of a report.

## Evidence and handoffs

The ledger records primary publisher URLs, table locators, unit conversions, limits and unsuccessful EVIC retrieval attempts. It records session AI review, not independent human assurance. [provenance.json](provenance.json) hashes the exact authored inputs, ledger, calculation code, results and handoff packet. It does **not** claim hashes of the original publisher PDFs, formal recordkeeping certification or independent source entailment verification.

Meta's disclosed Mesa, Arizona site withdrawal anchors the nature/resilience work. No precise site coordinates, basin hazard intersection or monetary benefit is invented. The [nature repository handoff](https://github.com/hhfinai/Nature-and-Biodiversity-Investment-Agent/tree/main/examples/integrated-portfolio) describes the remaining spatial and financial evidence. The [stewardship repository handoff](https://github.com/hhfinai/Stewardship-and-Controversy-Assessment/tree/main/examples/integrated-portfolio) points to dated proposed milestones. No communication has been sent. Material gaps remain open, accountable human review is unrecorded, and research approval has not been granted.
