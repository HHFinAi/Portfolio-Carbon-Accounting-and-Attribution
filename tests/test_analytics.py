"""Original HHFinAi domain arithmetic tests; all numbers are synthetic."""
import copy, math, random, unittest
from sf_agent.analytics import *
from sf_agent.validation import DataError

def holding(id='P1',issuer='I1',amount=10,market=None,evic=100,emissions=1000,scope3=2000,asset='listed-equity',revenue=1000000,boundary='b1'):
    return dict(id=id,issuer_id=issuer,asset_type=asset,issuer_is_listed=True,amount_basis='market_value' if asset=='listed-equity' else 'book_value',financed_amount=amount,market_value=amount if market is None else market,currency='USD',boundary_id=boundary,financial_year=2025,emissions_year=2025,evic=evic,revenue=revenue,scope12_tco2e=emissions,scope3_tco2e=scope3,quality_scope12=2,quality_scope3=4)
class Carbon(unittest.TestCase):
    def scope(self,result):return result['scopes']['scope12_tco2e']
    def test_financed_emissions(self):self.assertEqual(financed_emissions(10,100,1000),100)
    def test_zero_evic_rejected(self):
        with self.assertRaises(DataError):financed_emissions(10,0,1000)
    def test_negative_exposure_rejected(self):
        with self.assertRaises(DataError):financed_emissions(-1,100,1000)
    def test_scope_inventory_complete(self):self.assertEqual(self.scope(carbon_inventory([holding()],10))['complete_in_scope_financed_tco2e'],100)
    def test_scopes_not_netted(self):self.assertTrue(carbon_inventory([holding()],10)['scope12_plus_scope3_total_intentionally_not_reported'])
    def test_no_data_is_none_not_zero(self):
        r=self.scope(carbon_inventory([holding(emissions=None)],10));self.assertIsNone(r['observed_financed_tco2e']);self.assertEqual(r['fe_coverage_fraction'],0)
    def test_measured_zero_is_covered(self):
        r=self.scope(carbon_inventory([holding(emissions=0)],10));self.assertEqual(r['observed_financed_tco2e'],0);self.assertEqual(r['fe_coverage_fraction'],1)
    def test_missing_evic_unassessed(self):self.assertIsNone(self.scope(carbon_inventory([holding(evic=None)],10))['observed_financed_tco2e'])
    def test_partial_coverage_not_complete_inventory(self):
        r=self.scope(carbon_inventory([holding(),holding('P2','I2',10,emissions=None)],20));self.assertIsNone(r['complete_in_scope_financed_tco2e']);self.assertEqual(r['fe_coverage_fraction'],.5)
    def test_bond_book_value_numerator(self):self.assertEqual(self.scope(carbon_inventory([holding(asset='corporate-bond',amount=10,market=8)],8))['observed_financed_tco2e'],100)
    def test_waci_market_not_bond_book_weight(self):
        r=self.scope(carbon_inventory([holding(asset='corporate-bond',amount=10,market=8),holding('P2','I2',10,emissions=2000)],18));self.assertAlmostEqual(r['waci_covered_only'],(8*1000+10*2000)/18)
    def test_waci_nav_and_covered_denominators_separate(self):
        r=self.scope(carbon_inventory([holding()],20));self.assertEqual(r['waci_observed_contribution_full_portfolio_denominator'],500);self.assertEqual(r['waci_covered_only'],1000)
    def test_bond_wrong_basis_rejected(self):
        h=holding(asset='corporate-bond');h['amount_basis']='market_value'
        with self.assertRaises(DataError):carbon_inventory([h],10)
    def test_unlisted_rejected(self):
        h=holding();h['issuer_is_listed']=False
        with self.assertRaises(DataError):carbon_inventory([h],10)
    def test_unsupported_asset_rejected(self):
        h=holding();h['asset_type']='sovereign'
        with self.assertRaises(DataError):carbon_inventory([h],10)
    def test_duplicate_positions_rejected(self):
        with self.assertRaises(DataError):carbon_inventory([holding(),holding()],20)
    def test_same_issuer_aggregate(self):self.assertEqual(carbon_inventory([holding(),holding('P2',asset='corporate-bond')],20)['issuer_count'],1)
    def test_same_issuer_conflict_rejected(self):
        with self.assertRaises(DataError):carbon_inventory([holding(),holding('P2',emissions=900)],20)
    def test_mixed_currency_rejected(self):
        h=holding('P2','I2');h['currency']='EUR'
        with self.assertRaises(DataError):carbon_inventory([holding(),h],20)
    def test_quality_coverage_separate(self):
        h=holding();h['quality_scope12']=None;r=self.scope(carbon_inventory([h],10));self.assertEqual(r['fe_coverage_fraction'],1);self.assertIsNone(r['quality_exposure_weighted'])
    def test_invalid_quality(self):
        h=holding();h['quality_scope12']=6
        with self.assertRaises(DataError):carbon_inventory([h],10)
    def test_aggregate_attribution_over_one(self):
        with self.assertRaises(DataError):carbon_inventory([holding(amount=60),holding('P2',amount=60,asset='corporate-bond')],120)
    def test_shapley_only_emissions(self):
        r=financed_emissions_bridge(10,1000,100,10,800,100);self.assertAlmostEqual(r['reported_emissions_effect'],-20);self.assertAlmostEqual(r['financed_amount_effect'],0);self.assertAlmostEqual(r['evic_effect'],0)
    def test_shapley_valuation_can_reduce_inventory(self):
        r=financed_emissions_bridge(10,1000,100,10,1000,200);self.assertAlmostEqual(r['evic_effect'],-50);self.assertFalse(r['physical_decarbonisation_proven'])
    def test_random_shapley_reconciliation(self):
        g=random.Random(11)
        for i in range(100):
            r=financed_emissions_bridge(g.uniform(1,20),g.uniform(1,1000),g.uniform(50,200),g.uniform(1,20),g.uniform(1,1000),g.uniform(50,200));self.assertAlmostEqual(r['reconciliation_residual'],0,places=9)
    def test_attribution_sale_not_decarbonisation(self):
        r=portfolio_emissions_attribution([holding(),holding('P2','I2')],[holding()], 'scope12_tco2e');self.assertAlmostEqual(r['effects']['exits'],-100);self.assertAlmostEqual(r['reconciliation_residual'],0)
    def test_attribution_coverage_gain(self):
        r=portfolio_emissions_attribution([holding(emissions=None)],[holding()],'scope12_tco2e');self.assertEqual(r['effects']['coverage_gains'],100)
    def test_attribution_coverage_loss(self):
        r=portfolio_emissions_attribution([holding()],[holding(emissions=None)],'scope12_tco2e');self.assertEqual(r['effects']['coverage_losses'],-100)
    def test_boundary_change_not_emissions_effect(self):
        r=portfolio_emissions_attribution([holding()],[holding(emissions=900,boundary='restated')],'scope12_tco2e');self.assertEqual(r['effects']['boundary_changes'],-10);self.assertEqual(r['effects']['reported_emissions_effect'],0)
    def test_entries_accounted(self):
        r=portfolio_emissions_attribution([holding()],[holding(),holding('P2','I2')],'scope12_tco2e');self.assertEqual(r['effects']['entries'],100)
    def test_scope_must_be_explicit(self):
        with self.assertRaises(DataError):portfolio_emissions_attribution([holding()],[holding()],'combined')

if __name__=='__main__':unittest.main()
