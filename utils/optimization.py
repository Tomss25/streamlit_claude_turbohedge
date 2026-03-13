"""
Optimization module for Turbo Short hedge strategy
Find optimal Strike and Maturity for target hedge ratio
"""

import numpy as np
from typing import Dict, List, Tuple
import pandas as pd
from scipy.optimize import minimize


class StrategyOptimizer:
    """Optimizer for Turbo hedge strategy parameters"""
    
    def __init__(self, base_params: Dict):
        """
        Initialize optimizer
        
        Args:
            base_params: Base parameters (will be varied during optimization)
        """
        self.base_params = base_params.copy()
    
    def evaluate_strategy(self, strike: float, giorni: int, 
                         target_scenario: float = None) -> Dict:
        """
        Evaluate strategy for given Strike and Maturity
        
        Args:
            strike: Strike level to test
            giorni: Days to maturity
            target_scenario: Target index value (uses base if None)
        
        Returns:
            Dictionary with evaluation metrics
        """
        from utils.calculations import TurboCalculator
        
        # Update parameters
        params = self.base_params.copy()
        params['strike'] = strike
        params['giorni'] = giorni
        
        if target_scenario is not None:
            params['valore_ipotetico_indice'] = target_scenario
        
        # Calculate results
        calc = TurboCalculator(params)
        results = calc.calculate_hedge_results()
        
        return results
    
    def optimize_for_hedge_ratio(self, target_hedge_ratio: float = 0.95,
                                 strike_range: Tuple[float, float] = None,
                                 giorni_range: Tuple[int, int] = (30, 180),
                                 target_scenario: float = None) -> Dict:
        """
        Find optimal Strike and Maturity for target hedge ratio
        
        Args:
            target_hedge_ratio: Target hedge effectiveness (0-1)
            strike_range: Range of strikes to search (auto if None)
            giorni_range: Range of maturities to search
            target_scenario: Target index scenario
        
        Returns:
            Dictionary with optimal parameters and results
        """
        spot = self.base_params['valore_iniziale_indice']
        
        if strike_range is None:
            # Auto-determine reasonable range (5-20% above spot)
            strike_range = (spot * 1.05, spot * 1.20)
        
        def objective(x):
            """Objective function to minimize"""
            strike, giorni_float = x
            giorni = int(giorni_float)
            
            results = self.evaluate_strategy(strike, giorni, target_scenario)
            hedge_ratio = results['hedge_ratio']
            
            # Penalize deviation from target and high capital usage
            deviation = abs(hedge_ratio - target_hedge_ratio)
            capital_penalty = results['capitale_investito_pct'] / 100 * 0.1  # 10% weight on capital
            
            return deviation + capital_penalty
        
        # Initial guess
        x0 = [(strike_range[0] + strike_range[1]) / 2, 
              (giorni_range[0] + giorni_range[1]) / 2]
        
        # Bounds
        bounds = [strike_range, giorni_range]
        
        # Optimize
        result = minimize(objective, x0, method='L-BFGS-B', bounds=bounds)
        
        optimal_strike = result.x[0]
        optimal_giorni = int(result.x[1])
        
        # Evaluate optimal solution
        optimal_results = self.evaluate_strategy(optimal_strike, optimal_giorni, target_scenario)
        
        return {
            'optimal_strike': optimal_strike,
            'optimal_giorni': optimal_giorni,
            'results': optimal_results,
            'optimization_success': result.success,
        }
    
    def grid_search_parameters(self, strike_points: int = 10,
                              giorni_points: int = 6,
                              strike_range: Tuple[float, float] = None,
                              giorni_range: Tuple[int, int] = (30, 180),
                              target_scenario: float = None) -> pd.DataFrame:
        """
        Perform grid search over Strike and Maturity space
        
        Args:
            strike_points: Number of strike levels to test
            giorni_points: Number of maturities to test
            strike_range: Range of strikes (auto if None)
            giorni_range: Range of maturities
            target_scenario: Target index scenario
        
        Returns:
            DataFrame with results for all combinations
        """
        spot = self.base_params['valore_iniziale_indice']
        
        if strike_range is None:
            strike_range = (spot * 1.05, spot * 1.20)
        
        # Create grid
        strikes = np.linspace(strike_range[0], strike_range[1], strike_points)
        giorni_array = np.linspace(giorni_range[0], giorni_range[1], giorni_points, dtype=int)
        
        results_list = []
        
        for strike in strikes:
            for giorni in giorni_array:
                results = self.evaluate_strategy(strike, giorni, target_scenario)
                
                # Check if knocked out in scenario
                barrier = results['barrier_future']
                scenario_spot = target_scenario if target_scenario else self.base_params['valore_ipotetico_indice']
                is_knocked_out = scenario_spot >= barrier
                
                results_list.append({
                    'Strike': strike,
                    'Giorni': giorni,
                    'Leva': results['leverage'],
                    'N. Turbo': results['n_turbo'],
                    'Capitale %': results['capitale_investito_pct'],
                    'Barriera': barrier,
                    'Dist. Barriera %': results['distanza_barriera_pct'],
                    'Hedge Ratio': results['hedge_ratio'],
                    'Performance %': results['performance_totale'] * 100,
                    'Knocked Out': is_knocked_out,
                })
        
        return pd.DataFrame(results_list)
    
    def find_best_tradeoff(self, target_scenario: float = None,
                          max_capital_pct: float = 20,
                          min_hedge_ratio: float = 0.90) -> Dict:
        """
        Find best tradeoff between capital usage and hedge effectiveness
        
        Args:
            target_scenario: Target index scenario
            max_capital_pct: Maximum capital to invest (% of portfolio)
            min_hedge_ratio: Minimum acceptable hedge ratio
        
        Returns:
            Dictionary with recommended parameters
        """
        # Perform grid search
        grid_results = self.grid_search_parameters(
            strike_points=15,
            giorni_points=8,
            target_scenario=target_scenario
        )
        
        # Filter by constraints
        valid = grid_results[
            (grid_results['Capitale %'] <= max_capital_pct) &
            (grid_results['Hedge Ratio'] >= min_hedge_ratio) &
            (grid_results['Knocked Out'] == False)
        ]
        
        if len(valid) == 0:
            return {
                'success': False,
                'message': 'Nessuna soluzione trovata con i vincoli specificati'
            }
        
        # Score each option (minimize capital, maximize hedge ratio)
        valid['Score'] = (1 - valid['Capitale %'] / 100) * 0.5 + valid['Hedge Ratio'] * 0.5
        
        # Get best option
        best_idx = valid['Score'].idxmax()
        best = valid.loc[best_idx]
        
        # Evaluate full results for best option
        full_results = self.evaluate_strategy(best['Strike'], best['Giorni'], target_scenario)
        
        return {
            'success': True,
            'recommended_strike': best['Strike'],
            'recommended_giorni': int(best['Giorni']),
            'capitale_pct': best['Capitale %'],
            'hedge_ratio': best['Hedge Ratio'],
            'leverage': best['Leva'],
            'distanza_barriera_pct': best['Dist. Barriera %'],
            'performance_pct': best['Performance %'],
            'full_results': full_results,
        }


def compare_strategies(base_params: Dict, strategies: List[Dict]) -> pd.DataFrame:
    """
    Compare multiple strategy configurations
    
    Args:
        base_params: Base parameters
        strategies: List of strategy configurations with 'strike' and 'giorni'
    
    Returns:
        DataFrame comparing all strategies
    """
    from utils.calculations import TurboCalculator
    
    results_list = []
    
    for i, strategy in enumerate(strategies):
        params = base_params.copy()
        params.update(strategy)
        
        calc = TurboCalculator(params)
        results = calc.calculate_hedge_results()
        
        results_list.append({
            'Strategia': strategy.get('name', f'Strategia {i+1}'),
            'Strike': strategy['strike'],
            'Giorni': strategy['giorni'],
            'Leva': results['leverage'],
            'Capitale €': results['capitale_turbo'],
            'Capitale %': results['capitale_investito_pct'],
            'Hedge Ratio': results['hedge_ratio'],
            'Dist. Barriera %': results['distanza_barriera_pct'],
            'Performance Ptf %': results['performance_portafoglio'] * 100,
            'Performance Tot %': results['performance_totale'] * 100,
            'P&L Netto €': results['pl_netto'],
        })
    
    return pd.DataFrame(results_list)


def sensitivity_to_spot(base_params: Dict, spot_range: Tuple[float, float],
                       n_points: int = 20) -> pd.DataFrame:
    """
    Calculate sensitivity of hedge to different spot levels
    
    Args:
        base_params: Base parameters
        spot_range: Range of spot prices to test
        n_points: Number of points
    
    Returns:
        DataFrame with sensitivity results
    """
    from utils.calculations import TurboCalculator
    
    spot_values = np.linspace(spot_range[0], spot_range[1], n_points)
    
    results_list = []
    
    for spot in spot_values:
        params = base_params.copy()
        params['valore_ipotetico_indice'] = spot
        
        calc = TurboCalculator(params)
        results = calc.calculate_hedge_results()
        
        variazione_pct = (spot / base_params['valore_iniziale_indice'] - 1) * 100
        
        results_list.append({
            'Spot': spot,
            'Variazione %': variazione_pct,
            'Valore Ptf': results['valore_portafoglio_futuro'],
            'Valore Turbo': results['valore_turbo_futuro_gross'],
            'Valore Totale': results['valore_totale_futuro'],
            'Performance Tot %': results['performance_totale'] * 100,
            'Hedge Ratio': results['hedge_ratio'],
            'Knocked Out': spot >= results['barrier_future'],
        })
    
    return pd.DataFrame(results_list)
