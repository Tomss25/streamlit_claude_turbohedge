"""
Monte Carlo simulation for Turbo Short hedge portfolio
"""

import numpy as np
from typing import Dict, Tuple
import pandas as pd


class MonteCarloSimulator:
    """Monte Carlo simulation for portfolio outcomes"""
    
    def __init__(self, calculator, volatility: float, n_simulations: int = 10000):
        """
        Initialize Monte Carlo simulator
        
        Args:
            calculator: TurboCalculator instance
            volatility: Annualized volatility (e.g., 0.20 for 20%)
            n_simulations: Number of simulation paths
        """
        self.calculator = calculator
        self.volatility = volatility
        self.n_simulations = n_simulations
        
    def simulate_paths(self) -> np.ndarray:
        """
        Simulate index price paths using Geometric Brownian Motion
        
        Returns:
            Array of shape (n_simulations,) with final index values
        """
        # Parameters
        S0 = self.calculator.valore_iniziale_indice
        T = self.calculator.giorni / 365.0
        mu = self.calculator.euribor  # drift (risk-free rate)
        sigma = self.volatility
        
        # Generate random shocks
        np.random.seed(42)  # For reproducibility
        Z = np.random.standard_normal(self.n_simulations)
        
        # Geometric Brownian Motion formula
        # S_T = S_0 × exp((μ - σ²/2)T + σ√T × Z)
        ST = S0 * np.exp((mu - 0.5 * sigma**2) * T + sigma * np.sqrt(T) * Z)
        
        return ST
    
    def calculate_outcomes(self) -> Dict:
        """
        Calculate portfolio outcomes for all simulated paths
        
        Returns:
            Dictionary with simulation results
        """
        # Simulate final index values
        final_spots = self.simulate_paths()
        
        # Get key values
        n_turbo = self.calculator.calculate_n_turbo()
        capitale_turbo_base = n_turbo * self.calculator.prezzo_iniziale
        capitale_turbo = capitale_turbo_base * (1 + self.calculator.bid_ask_spread / 100)
        costi_acquisto = capitale_turbo * self.calculator.commissioni / 100
        capitale_totale = self.calculator.valore_portafoglio + capitale_turbo + costi_acquisto
        
        # Initialize result arrays
        valore_portafoglio_array = np.zeros(self.n_simulations)
        valore_turbo_array = np.zeros(self.n_simulations)
        valore_totale_array = np.zeros(self.n_simulations)
        performance_array = np.zeros(self.n_simulations)
        knocked_out = np.zeros(self.n_simulations, dtype=bool)
        
        barrier = self.calculator.calculate_barrier()
        
        for i, spot in enumerate(final_spots):
            # Check knock-out
            if spot >= barrier:
                knocked_out[i] = True
                valore_turbo = 0
            else:
                prezzo_turbo = self.calculator.calculate_turbo_price(spot, giorni_residui=0)
                valore_turbo_gross = prezzo_turbo * n_turbo
                valore_turbo = valore_turbo_gross * (1 - self.calculator.bid_ask_spread / 100)
                
                # Taxes on gains
                pl_turbo = valore_turbo_gross - capitale_turbo_base
                if pl_turbo > 0:
                    tasse = pl_turbo * self.calculator.tasse / 100
                    valore_turbo -= tasse
            
            # Portfolio value (with Beta)
            variazione_indice = (spot / self.calculator.valore_iniziale_indice) - 1
            variazione_portafoglio = variazione_indice * self.calculator.beta
            valore_portafoglio = self.calculator.valore_portafoglio * (1 + variazione_portafoglio)
            
            # Store results
            valore_portafoglio_array[i] = valore_portafoglio
            valore_turbo_array[i] = valore_turbo
            valore_totale = valore_portafoglio + valore_turbo
            valore_totale_array[i] = valore_totale
            performance_array[i] = (valore_totale / capitale_totale - 1) * 100
        
        # Calculate statistics
        results = {
            'final_spots': final_spots,
            'valore_portafoglio': valore_portafoglio_array,
            'valore_turbo': valore_turbo_array,
            'valore_totale': valore_totale_array,
            'performance': performance_array,
            'knocked_out': knocked_out,
            
            # Statistics
            'mean_performance': np.mean(performance_array),
            'median_performance': np.median(performance_array),
            'std_performance': np.std(performance_array),
            'min_performance': np.min(performance_array),
            'max_performance': np.max(performance_array),
            'percentile_5': np.percentile(performance_array, 5),
            'percentile_95': np.percentile(performance_array, 95),
            'knockout_rate': np.sum(knocked_out) / self.n_simulations * 100,
            
            # VaR and CVaR
            'var_95': np.percentile(performance_array, 5),
            'cvar_95': np.mean(performance_array[performance_array <= np.percentile(performance_array, 5)]),
            
            # Probability of loss
            'prob_loss': np.sum(performance_array < 0) / self.n_simulations * 100,
            'prob_gain': np.sum(performance_array > 0) / self.n_simulations * 100,
        }
        
        return results
    
    def calculate_distribution_bins(self, n_bins: int = 50) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculate histogram bins for performance distribution
        
        Args:
            n_bins: Number of bins
        
        Returns:
            Tuple of (bin_edges, counts)
        """
        results = self.calculate_outcomes()
        performance = results['performance']
        
        counts, bin_edges = np.histogram(performance, bins=n_bins)
        
        return bin_edges, counts
    
    def get_summary_dataframe(self) -> pd.DataFrame:
        """
        Get summary statistics as DataFrame
        
        Returns:
            DataFrame with summary statistics
        """
        results = self.calculate_outcomes()
        
        summary = pd.DataFrame({
            'Metrica': [
                'Performance Media',
                'Performance Mediana',
                'Deviazione Standard',
                'Performance Minima',
                'Performance Massima',
                '5° Percentile (VaR 95%)',
                '95° Percentile',
                'CVaR 95%',
                'Tasso di Knock-Out',
                'Probabilità di Perdita',
                'Probabilità di Guadagno',
            ],
            'Valore': [
                f"{results['mean_performance']:.2f}%",
                f"{results['median_performance']:.2f}%",
                f"{results['std_performance']:.2f}%",
                f"{results['min_performance']:.2f}%",
                f"{results['max_performance']:.2f}%",
                f"{results['percentile_5']:.2f}%",
                f"{results['percentile_95']:.2f}%",
                f"{results['cvar_95']:.2f}%",
                f"{results['knockout_rate']:.2f}%",
                f"{results['prob_loss']:.2f}%",
                f"{results['prob_gain']:.2f}%",
            ]
        })
        
        return summary


def run_sensitivity_analysis(calculator, base_volatility: float, 
                             vol_range: Tuple[float, float] = (0.10, 0.40),
                             n_points: int = 7) -> pd.DataFrame:
    """
    Run sensitivity analysis on volatility
    
    Args:
        calculator: TurboCalculator instance
        base_volatility: Base volatility for comparison
        vol_range: Range of volatilities to test
        n_points: Number of points to test
    
    Returns:
        DataFrame with sensitivity results
    """
    volatilities = np.linspace(vol_range[0], vol_range[1], n_points)
    
    results = []
    
    for vol in volatilities:
        simulator = MonteCarloSimulator(calculator, volatility=vol, n_simulations=5000)
        outcomes = simulator.calculate_outcomes()
        
        results.append({
            'Volatilità': f"{vol*100:.0f}%",
            'Performance Media': outcomes['mean_performance'],
            'VaR 95%': outcomes['var_95'],
            'CVaR 95%': outcomes['cvar_95'],
            'Tasso Knock-Out': outcomes['knockout_rate'],
            'Prob. Perdita': outcomes['prob_loss'],
        })
    
    return pd.DataFrame(results)
