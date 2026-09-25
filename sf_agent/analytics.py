"""Long-only listed-corporate carbon accounting; other PCAF asset classes are excluded.

PCAF Part A 2025, printed pp.41-42: equity outstanding at market value,
corporate bonds at book value; listed-company denominator is EVIC.
WACI instead uses portfolio MARKET-value weights. No implicit unit conversion.
"""
from __future__ import annotations
import copy
from itertools import permutations
from .maths import COMMON_OPERATIONS, checked, number, operation, positive, require
from .validation import mapping, sequence, text

@operation({'outstanding_amount':'$money','evic':'$money','emissions_tco2e':'tCO2e'},'tCO2e')
def financed_emissions(outstanding_amount: float,evic: float,emissions_tco2e: float) -> float:
    amount=checked(outstanding_amount,'outstanding_amount',0);denom=positive(evic,'evic');e=checked(emissions_tco2e,'emissions_tco2e',0)
    require(amount<=denom+1e-9,'attribution exceeds 100%; reconcile amount, denominator and periods')
    return amount/denom*e

def _optional_nonnegative(row: dict,field: str) -> float | None:
    value=row.get(field)
    return None if value is None else checked(value,field,0)

def _holdings(holdings: list[dict]) -> tuple[dict,list[dict]]:
    sequence(holdings,'holdings',True);require(len(holdings)<=10000,'too many holdings for local helper')
    ids=set();issuers={};currencies=set()
    metrics=('evic','scope12_tco2e','scope3_tco2e','revenue','quality_scope12','quality_scope3','boundary_id','financial_year','emissions_year')
    for item in holdings:
        row=copy.deepcopy(mapping(item,'holding'));pid=text(row.get('id'),'position id');require(pid not in ids,'duplicate position id');ids.add(pid)
        iid=text(row.get('issuer_id'),'issuer_id');asset=row.get('asset_type')
        require(asset in {'listed-equity','corporate-bond'},'unsupported asset: use asset-class-specific accounting')
        require(row.get('issuer_is_listed') is True,'EVIC helper requires a listed issuer')
        expected='market_value' if asset=='listed-equity' else 'book_value'
        require(row.get('amount_basis')==expected,'equity uses market value; corporate bonds use book value for financed emissions')
        row['financed_amount']=checked(row.get('financed_amount'),'financed_amount',0)
        row['market_value']=checked(row.get('market_value'),'market_value',0)
        if asset=='listed-equity':require(abs(row['financed_amount']-row['market_value'])<=max(1e-8,row['market_value']*1e-9),'equity financed amount and market value differ')
        currency=text(row.get('currency'),'currency');require(len(currency)==3 and currency.isupper(),'normalize to one ISO-style currency code');currencies.add(currency)
        text(row.get('boundary_id'),'boundary_id')
        for key in ('financial_year','emissions_year'):require(type(row.get(key)) is int and 1900<=row[key]<=2200,'invalid year')
        for key in ('evic','revenue','scope12_tco2e','scope3_tco2e'):row[key]=_optional_nonnegative(row,key)
        # Zero EVIC/revenue are not usable, but remain explicit unassessed data.
        for key in ('quality_scope12','quality_scope3'):
            v=row.get(key)
            require(v is None or (type(v) is int and 1<=v<=5),'quality scores must be integer 1..5 or null')
            row[key]=v
        if iid in issuers:
            prior=issuers[iid]
            require(all(prior.get(k)==row.get(k) for k in metrics),'conflicting issuer data across positions; reconcile before aggregating')
            prior['financed_amount']+=row['financed_amount'];prior['market_value']+=row['market_value'];prior['position_ids'].append(pid)
        else:
            issuers[iid]=row;issuers[iid]['position_ids']=[pid]
    require(len(currencies)==1,'mixed currencies must be converted explicitly before accounting')
    for row in issuers.values():
        if row['evic'] is not None and row['evic']>0:require(row['financed_amount']<=row['evic']+1e-9,'aggregate issuer attribution exceeds 100%')
    return issuers,list(issuers.values())

def _fe(row: dict,scope: str) -> float | None:
    e=row.get(scope);evic=row.get('evic')
    return row['financed_amount']/evic*e if e is not None and evic is not None and evic>0 else None

@operation({'holdings':'normalized_holding_records','portfolio_market_value':'$money'},'carbon_inventory')
def carbon_inventory(holdings: list[dict],portfolio_market_value: float) -> dict:
    _,rows=_holdings(holdings);nav=positive(portfolio_market_value,'portfolio_market_value')
    total_market=sum(r['market_value'] for r in rows);total_financed=sum(r['financed_amount'] for r in rows)
    require(total_market<=nav+max(1e-8,nav*1e-9),'holdings market value exceeds supplied portfolio value')
    require(total_financed>0,'positive in-scope financed exposure required')
    output={'currency':rows[0]['currency'],'in_scope_financed_amount':total_financed,'in_scope_market_value':total_market,
            'portfolio_market_value':nav,'unmodelled_market_value':max(0,nav-total_market),'scopes':{},'issuer_count':len(rows),
            'scope12_plus_scope3_total_intentionally_not_reported':True}
    for scope,quality in [('scope12_tco2e','quality_scope12'),('scope3_tco2e','quality_scope3')]:
        covered=[r for r in rows if _fe(r,scope) is not None and r['financed_amount']>0]
        exposure=sum(r['financed_amount'] for r in covered)
        fe=sum(_fe(r,scope) for r in covered) if covered else None
        wr=[r for r in rows if r[scope] is not None and r['revenue'] is not None and r['revenue']>0 and r['market_value']>0]
        wm=sum(r['market_value'] for r in wr)
        # Unit: tCO2e per MILLION currency revenue. All input money is unscaled currency units.
        weighted=sum(r['market_value']/nav*r[scope]/(r['revenue']/1_000_000) for r in wr) if wr else None
        quality_rows=[r for r in covered if r[quality] is not None];qe=sum(r['financed_amount'] for r in quality_rows)
        output['scopes'][scope]={'observed_financed_tco2e':fe,'fe_coverage_fraction':exposure/total_financed,
            'unassessed_financed_amount':total_financed-exposure,
            'complete_in_scope_financed_tco2e':fe if abs(exposure-total_financed)<max(1e-8,total_financed*1e-9) else None,
            'waci_observed_contribution_full_portfolio_denominator':weighted,
            'waci_covered_only':weighted*nav/wm if wm and weighted is not None else None,
            'waci_market_coverage_of_in_scope':wm/total_market if total_market else None,
            'waci_units':'tCO2e per million '+rows[0]['currency']+' revenue',
            'quality_exposure_weighted':sum(r['financed_amount']*r[quality] for r in quality_rows)/qe if qe else None,
            'quality_score_coverage_of_financed_exposure':qe/total_financed}
    return output

@operation({'amount0':'$money','emissions0':'tCO2e','evic0':'$money','amount1':'$money','emissions1':'tCO2e','evic1':'$money'},'financed_emissions_bridge')
def financed_emissions_bridge(amount0: float,emissions0: float,evic0: float,amount1: float,emissions1: float,evic1: float) -> dict:
    start=[checked(amount0,'amount0',0),checked(emissions0,'emissions0',0),positive(evic0,'evic0')]
    end=[checked(amount1,'amount1',0),checked(emissions1,'emissions1',0),positive(evic1,'evic1')]
    # Intermediate Shapley combinations are hypothetical; endpoint ratios must be valid.
    require(start[0]<=start[2] and end[0]<=end[2],'endpoint attribution exceeds 100%')
    def value(v):return v[0]*v[1]/v[2]
    contrib=[0.0,0.0,0.0]
    for order in permutations(range(3)):
        current=list(start)
        for i in order:
            before=value(current);current[i]=end[i];contrib[i]+=(value(current)-before)/6
    delta=value(end)-value(start)
    return {'start_observed_fe':value(start),'end_observed_fe':value(end),'delta':delta,
            'financed_amount_effect':contrib[0],'reported_emissions_effect':contrib[1],'evic_effect':contrib[2],
            'reconciliation_residual':delta-sum(contrib),'physical_decarbonisation_proven':False}

@operation({'previous_holdings':'normalized_holding_records','current_holdings':'normalized_holding_records','scope':'scope_name'},'portfolio_emissions_attribution')
def portfolio_emissions_attribution(previous_holdings: list[dict],current_holdings: list[dict],scope: str) -> dict:
    require(scope in {'scope12_tco2e','scope3_tco2e'},'scope must be separately selected')
    old,oldrows=_holdings(previous_holdings);new,newrows=_holdings(current_holdings)
    require(oldrows[0]['currency']==newrows[0]['currency'],'period currencies differ')
    totals={k:0.0 for k in ('financed_amount_effect','reported_emissions_effect','evic_effect','entries','exits','coverage_gains','coverage_losses','boundary_changes')}
    details=[]
    for iid in sorted(old.keys()|new.keys()):
        o=old.get(iid);n=new.get(iid);f0=_fe(o,scope) if o else None;f1=_fe(n,scope) if n else None
        # Zero here means contribution to the OBSERVED inventory, never zero issuer emissions.
        start=f0 if f0 is not None else 0;end=f1 if f1 is not None else 0;delta=end-start
        if o is None:bucket='entries'
        elif n is None:bucket='exits'
        elif f0 is None and f1 is not None:bucket='coverage_gains'
        elif f0 is not None and f1 is None:bucket='coverage_losses'
        elif f0 is None and f1 is None:bucket='unassessed_both_periods'
        elif o['boundary_id']!=n['boundary_id']:bucket='boundary_changes'
        else:
            bridge=financed_emissions_bridge(o['financed_amount'],o[scope],o['evic'],n['financed_amount'],n[scope],n['evic'])
            for key in ('financed_amount_effect','reported_emissions_effect','evic_effect'):totals[key]+=bridge[key]
            details.append({'issuer_id':iid,'bucket':'comparable_reported_boundary','bridge':bridge});continue
        if bucket in totals:totals[bucket]+=delta
        details.append({'issuer_id':iid,'bucket':bucket,'observed_inventory_delta':delta})
    start=sum(_fe(r,scope) for r in oldrows if _fe(r,scope) is not None)
    end=sum(_fe(r,scope) for r in newrows if _fe(r,scope) is not None)
    return {'scope':scope,'start_observed_inventory':start,'end_observed_inventory':end,'delta':end-start,
            'effects':totals,'reconciliation_residual':end-start-sum(totals.values()),'issuer_details':details,
            'restatements_fx_and_physical_changes_not_separately_identified':True}
OPERATIONS=dict(COMMON_OPERATIONS)
OPERATIONS.update({f.__name__:f for f in (financed_emissions,carbon_inventory,financed_emissions_bridge,portfolio_emissions_attribution)})
