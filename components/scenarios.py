"""
Scenario analysis component
"""

import pandas as pd
import numpy as np
from typing import Dict
from utils.calculations import TurboCalculator


def generate_scenario_table(calculator: TurboCalculator, 
                           scenario_range: tuple = (-30, 30),
                           n_scenarios: int = 13) -> pd.DataFrame:
    """
    Generate scenario analysis table
    
    Args:
        calculator: TurboCalculator instance
        scenario_range: Range of index variations in %
        n_scenarios: Number of scenarios to generate
    
    Returns:
        DataFrame with scenario results
    """
    spot_initial = calculator.valore_iniziale_indice
    
    # Generate index variation scenarios
    variations = np.linspace(scenario_range[0], scenario_range[1], n_scenarios)
    
    results = []
    
    for var_pct in variations:
        # Calculate new spot
        new_spot = spot_initial * (1 + var_pct / 100)
        
        # Update calculator with new scenario
        calculator.valore_ipotetico_indice = new_spot
        
        # Calculate results
        hedge_results = calculator.calculate_hedge_results()
        
        # Check knock-out
        is_knocked_out = new_spot >= hedge_results['barrier_future']
        
        results.append({
            'Variazione Indice %': var_pct,
            'Livello Indice': new_spot,
            'Valore Portafoglio': hedge_results['valore_portafoglio_futuro'],
            'Performance Portafoglio %': hedge_results['performance_portafoglio'] * 100,
            'Valore Turbo': hedge_results['valore_turbo_futuro_gross'],
            'Performance Turbo %': hedge_results['performance_turbo'] * 100,
            'Valore Totale': hedge_results['valore_totale_futuro'],
            'Performance Totale %': hedge_results['performance_totale'] * 100,
            'P&L Netto': hedge_results['pl_netto'],
            'Hedge Ratio': hedge_results['hedge_ratio'],
            'Knocked Out': '❌' if is_knocked_out else '✓',
        })
    
    df = pd.DataFrame(results)
    
    # Format numbers
    df['Livello Indice'] = df['Livello Indice'].apply(lambda x: f'{x:,.2f}')
    df['Valore Portafoglio'] = df['Valore Portafoglio'].apply(lambda x: f'€{x:,.0f}')
    df['Valore Turbo'] = df['Valore Turbo'].apply(lambda x: f'€{x:,.0f}')
    df['Valore Totale'] = df['Valore Totale'].apply(lambda x: f'€{x:,.0f}')
    df['P&L Netto'] = df['P&L Netto'].apply(lambda x: f'€{x:,.0f}')
    
    # Format percentages
    for col in ['Variazione Indice %', 'Performance Portafoglio %', 
                'Performance Turbo %', 'Performance Totale %']:
        df[col] = df[col].apply(lambda x: f'{x:.2f}%')
    
    df['Hedge Ratio'] = df['Hedge Ratio'].apply(lambda x: f'{x:.2%}')
    
    return df


def generate_scenario_summary(calculator: TurboCalculator) -> Dict:
    """
    Generate summary statistics for key scenarios
    
    Args:
        calculator: TurboCalculator instance
    
    Returns:
        Dictionary with summary statistics
    """
    spot_initial = calculator.valore_iniziale_indice
    
    # Key scenarios to test
    scenarios = {
        'Crash Severo (-30%)': -30,
        'Ribasso Forte (-20%)': -20,
        'Ribasso Moderato (-10%)': -10,
        'Scenario Base': (calculator.valore_ipotetico_indice / spot_initial - 1) * 100,
        'Stabile (0%)': 0,
        'Rialzo Moderato (+5%)': 5,
        'Rialzo Forte (+10%)': 10,
        'Vicino Barriera': None,  # Will calculate
    }
    
    # Calculate barrier and distance
    barrier = calculator.calculate_barrier()
    barrier_scenario_pct = (barrier / spot_initial - 1) * 100
    scenarios['Vicino Barriera'] = barrier_scenario_pct - 0.5  # Just below barrier
    
    summary = {}
    
    for scenario_name, var_pct in scenarios.items():
        new_spot = spot_initial * (1 + var_pct / 100)
        calculator.valore_ipotetico_indice = new_spot
        
        results = calculator.calculate_hedge_results()
        
        is_knocked_out = new_spot >= results['barrier_future']
        
        summary[scenario_name] = {
            'variazione_pct': var_pct,
            'livello_indice': new_spot,
            'performance_portafoglio': results['performance_portafoglio'] * 100,
            'performance_totale': results['performance_totale'] * 100,
            'pl_netto': results['pl_netto'],
            'hedge_ratio': results['hedge_ratio'],
            'knocked_out': is_knocked_out,
        }
    
    return summary


def create_comparison_matrix(base_params: Dict, 
                             strategies: list) -> pd.DataFrame:
    """
    Create comparison matrix for different strategies
    
    Args:
        base_params: Base parameters dictionary
        strategies: List of strategy configurations
    
    Returns:
        DataFrame with strategy comparisons
    """
    from utils.optimization import compare_strategies
    
    return compare_strategies(base_params, strategies)


def create_stress_test_table(calculator: TurboCalculator) -> pd.DataFrame:
    """
    Create stress test scenarios table
    
    Args:
        calculator: TurboCalculator instance
    
    Returns:
        DataFrame with stress test results
    """
    spot_initial = calculator.valore_iniziale_indice
    
    stress_scenarios = [
        {
            'name': 'Flash Crash',
            'variation': -25,
            'description': 'Caduta improvvisa del 25%'
        },
        {
            'name': 'Mercato Orso',
            'variation': -35,
            'description': 'Bear market severo'
        },
        {
            'name': 'Correzione Normale',
            'variation': -10,
            'description': 'Correzione tecnica standard'
        },
        {
            'name': 'Rally Prima della Barriera',
            'variation': (calculator.calculate_barrier() / spot_initial - 1) * 100 - 0.5,
            'description': 'Ultimo momento prima del knock-out'
        },
        {
            'name': 'Scenario Black Swan',
            'variation': -40,
            'description': 'Evento estremo improbabile'
        },
    ]
    
    results = []
    
    for scenario in stress_scenarios:
        new_spot = spot_initial * (1 + scenario['variation'] / 100)
        calculator.valore_ipotetico_indice = new_spot
        
        hedge_results = calculator.calculate_hedge_results()
        
        is_knocked_out = new_spot >= hedge_results['barrier_future']
        
        # Calculate protection effectiveness
        if hedge_results['pl_portafoglio'] < 0:
            protection_pct = min(100, abs(hedge_results['pl_turbo'] / hedge_results['pl_portafoglio']) * 100)
        else:
            protection_pct = 0
        
        results.append({
            'Scenario': scenario['name'],
            'Descrizione': scenario['description'],
            'Var. Indice': f"{scenario['variation']:.1f}%",
            'Perdita Ptf': f"€{hedge_results['pl_portafoglio']:,.0f}",
            'Guadagno Turbo': f"€{hedge_results['pl_turbo']:,.0f}",
            'P&L Netto': f"€{hedge_results['pl_netto']:,.0f}",
            'Protezione': f"{protection_pct:.1f}%",
            'Status': '❌ K.O.' if is_knocked_out else '✓ Attivo',
        })
    
    return pd.DataFrame(results)
