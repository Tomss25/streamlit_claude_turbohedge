"""
Core calculation logic for Turbo Short hedge calculator
Includes corrections for Beta, dynamic premium, transaction costs, and dividends
"""

import numpy as np
from typing import Dict, Tuple


class TurboCalculator:
    """Calculator for Turbo Short certificate hedging"""
    
    def __init__(self, params: Dict):
        """
        Initialize calculator with parameters
        
        Args:
            params: Dictionary containing all input parameters
        """
        # Original parameters
        self.prezzo_iniziale = params['prezzo_iniziale']
        self.strike = params['strike']
        self.cambio = params['cambio']
        self.multiplo = params['multiplo']
        self.euribor = params['euribor']
        self.spread = params.get('spread', 0.0056)  # Default 0.56%
        
        self.valore_iniziale_indice = params['valore_iniziale_indice']
        self.valore_ipotetico_indice = params['valore_ipotetico_indice']
        self.giorni = params['giorni']
        
        self.valore_portafoglio = params['valore_portafoglio']
        
        # Enhanced parameters
        self.beta = params.get('beta', 1.0)
        self.dividend_yield = params.get('dividend_yield', 0.0)
        self.bid_ask_spread = params.get('bid_ask_spread', 0.0)
        self.commissioni = params.get('commissioni', 0.0)
        self.tasse = params.get('tasse', 0.0)
    
    def calculate_fair_value(self, spot: float, strike: float = None) -> float:
        """
        Calculate fair value with dividend adjustment
        
        Formula (corrected):
        Fair Value = (Strike × e^(-q×T) - Spot) × Multiplo / FX
        
        Args:
            spot: Current index value
            strike: Strike price (uses self.strike if None)
        
        Returns:
            Fair value in EUR
        """
        if strike is None:
            strike = self.strike
        
        # Time to maturity in years
        T = self.giorni / 360.0
        
        # Adjust strike for dividend yield
        adjusted_strike = strike * np.exp(-self.dividend_yield * T)
        
        fair_value = (adjusted_strike - spot) * self.multiplo / self.cambio
        
        return max(fair_value, 0)
    
    def calculate_initial_premium(self) -> float:
        """
        Calculate initial premium (time value)
        
        Formula:
        Premio = Prezzo_Mercato - Fair_Value
        """
        fair_value = self.calculate_fair_value(self.valore_iniziale_indice)
        premium = self.prezzo_iniziale - fair_value
        
        return max(premium, 0)
    
    def calculate_premium_decay(self, giorni_residui: int, premio_iniziale: float) -> float:
        """
        Calculate premium decay over time
        
        Formula:
        Premio(t) = Premio_Iniziale × (Giorni_Residui / Giorni_Iniziali)^k
        where k ≈ 1.5 (non-linear decay)
        
        Args:
            giorni_residui: Days remaining
            premio_iniziale: Initial premium
        
        Returns:
            Decayed premium
        """
        if self.giorni == 0:
            return 0
        
        decay_exponent = 1.5
        decay_factor = (giorni_residui / self.giorni) ** decay_exponent
        
        return premio_iniziale * decay_factor
    
    def calculate_barrier(self, giorni_elapsed: int = None) -> float:
        """
        Calculate knock-out barrier at a given time
        
        Formula:
        Barriera(t) = Strike × (1 - Euribor + Spread)^(t/360)
        
        Args:
            giorni_elapsed: Days elapsed (uses self.giorni if None)
        
        Returns:
            Barrier level
        """
        if giorni_elapsed is None:
            giorni_elapsed = self.giorni
        
        rate_net = 1 - self.euribor + self.spread
        barrier = self.strike * (rate_net ** (giorni_elapsed / 360.0))
        
        return barrier
    
    def calculate_turbo_price(self, spot: float, giorni_residui: int = None) -> float:
        """
        Calculate Turbo price at future point with dynamic premium
        
        Formula (corrected):
        Prezzo = MAX(0, Fair_Value(spot) + Premio_Decayed)
        
        Args:
            spot: Index value at future point
            giorni_residui: Days remaining (uses 0 if None)
        
        Returns:
            Turbo price in EUR
        """
        if giorni_residui is None:
            giorni_residui = 0
        
        # Calculate barrier at future point
        giorni_elapsed = self.giorni - giorni_residui
        barrier = self.calculate_barrier(giorni_elapsed)
        
        # Check knock-out
        if spot >= barrier:
            return 0.0
        
        # Calculate fair value at future point
        fair_value = self.calculate_fair_value(spot, strike=barrier)
        
        # Calculate decayed premium
        premio_iniziale = self.calculate_initial_premium()
        premio_decayed = self.calculate_premium_decay(giorni_residui, premio_iniziale)
        
        # Total price
        price = fair_value + premio_decayed
        
        return max(price, 0)
    
    def calculate_leverage(self) -> float:
        """
        Calculate Turbo leverage
        
        Formula:
        Leva = Spot / (Prezzo × (1/Multiplo) × Cambio)
        """
        denominator = self.prezzo_iniziale * (1 / self.multiplo) * self.cambio
        
        if denominator == 0:
            return 0
        
        leverage = self.valore_iniziale_indice / denominator
        
        return leverage
    
    def calculate_n_turbo(self) -> float:
        """
        Calculate number of Turbo certificates needed
        
        Formula:
        N_Turbo = Portafoglio / Leva / Prezzo
        """
        leverage = self.calculate_leverage()
        
        if leverage == 0 or self.prezzo_iniziale == 0:
            return 0
        
        n_turbo = self.valore_portafoglio / leverage / self.prezzo_iniziale
        
        return n_turbo
    
    def calculate_hedge_results(self) -> Dict:
        """
        Calculate complete hedge results with all corrections
        
        Returns:
            Dictionary with all calculated values
        """
        # Initial values
        fair_value = self.calculate_fair_value(self.valore_iniziale_indice)
        premio = self.calculate_initial_premium()
        barrier_initial = self.calculate_barrier(0)
        barrier_future = self.calculate_barrier(self.giorni)
        leverage = self.calculate_leverage()
        n_turbo = self.calculate_n_turbo()
        
        # Capital invested in Turbo (with bid-ask spread)
        capitale_turbo_base = n_turbo * self.prezzo_iniziale
        capitale_turbo = capitale_turbo_base * (1 + self.bid_ask_spread / 100)
        
        # Transaction costs on purchase
        costi_acquisto = capitale_turbo * self.commissioni / 100
        capitale_totale = self.valore_portafoglio + capitale_turbo + costi_acquisto
        
        # Future scenario with Beta adjustment
        variazione_indice = (self.valore_ipotetico_indice / self.valore_iniziale_indice) - 1
        variazione_portafoglio = variazione_indice * self.beta
        valore_portafoglio_futuro = self.valore_portafoglio * (1 + variazione_portafoglio)
        
        # Turbo price at future point
        prezzo_turbo_futuro = self.calculate_turbo_price(self.valore_ipotetico_indice, giorni_residui=0)
        
        # Value of Turbo position (with bid-ask spread on sale)
        valore_turbo_futuro_gross = prezzo_turbo_futuro * n_turbo
        valore_turbo_futuro = valore_turbo_futuro_gross * (1 - self.bid_ask_spread / 100)
        
        # Transaction costs on sale
        costi_vendita = valore_turbo_futuro * self.commissioni / 100
        
        # Profit/Loss on Turbo
        pl_turbo_gross = valore_turbo_futuro - capitale_turbo_base
        
        # Taxes on gains (only if positive)
        tasse_pagate = 0
        if pl_turbo_gross > 0:
            tasse_pagate = pl_turbo_gross * self.tasse / 100
        
        valore_turbo_futuro_net = valore_turbo_futuro - tasse_pagate - costi_vendita
        
        # Total portfolio value
        valore_totale_futuro = valore_portafoglio_futuro + valore_turbo_futuro_net
        
        # Performance
        performance_portafoglio = (valore_portafoglio_futuro / self.valore_portafoglio - 1)
        performance_turbo = (valore_turbo_futuro_gross / capitale_turbo_base - 1) if capitale_turbo_base > 0 else 0
        performance_totale = (valore_totale_futuro / capitale_totale - 1)
        
        # Hedge effectiveness
        perdita_portafoglio = valore_portafoglio_futuro - self.valore_portafoglio
        guadagno_turbo = valore_turbo_futuro_gross - capitale_turbo_base
        
        if perdita_portafoglio < 0:
            hedge_ratio = min(abs(guadagno_turbo / perdita_portafoglio), 1.0)
        else:
            hedge_ratio = 0
        
        # Distance to barrier
        distanza_barriera_pct = (barrier_future - self.valore_iniziale_indice) / self.valore_iniziale_indice * 100
        
        return {
            # Original calculations
            'fair_value': fair_value,
            'premio': premio,
            'premio_pct': premio / self.prezzo_iniziale * 100 if self.prezzo_iniziale > 0 else 0,
            'barrier_initial': barrier_initial,
            'barrier_future': barrier_future,
            'leverage': leverage,
            'n_turbo': n_turbo,
            
            # Capital
            'capitale_turbo_base': capitale_turbo_base,
            'capitale_turbo': capitale_turbo,
            'costi_acquisto': costi_acquisto,
            'capitale_totale': capitale_totale,
            
            # Future scenario
            'variazione_indice_pct': variazione_indice * 100,
            'variazione_portafoglio_pct': variazione_portafoglio * 100,
            'valore_portafoglio_futuro': valore_portafoglio_futuro,
            'prezzo_turbo_futuro': prezzo_turbo_futuro,
            'valore_turbo_futuro_gross': valore_turbo_futuro_gross,
            'valore_turbo_futuro': valore_turbo_futuro,
            'costi_vendita': costi_vendita,
            'tasse_pagate': tasse_pagate,
            'valore_totale_futuro': valore_totale_futuro,
            
            # Performance
            'performance_portafoglio': performance_portafoglio,
            'performance_turbo': performance_turbo,
            'performance_totale': performance_totale,
            
            # P&L
            'pl_portafoglio': perdita_portafoglio,
            'pl_turbo': guadagno_turbo,
            'pl_netto': valore_totale_futuro - capitale_totale,
            
            # Metrics
            'hedge_ratio': hedge_ratio,
            'distanza_barriera_pct': distanza_barriera_pct,
            'capitale_investito_pct': capitale_turbo / self.valore_portafoglio * 100,
        }
    
    def calculate_time_evolution(self, n_points: int = 30) -> Tuple[np.ndarray, Dict]:
        """
        Calculate evolution of portfolio over time
        
        Args:
            n_points: Number of time points to calculate
        
        Returns:
            Tuple of (days_array, results_dict)
        """
        giorni_array = np.linspace(0, self.giorni, n_points)
        
        # Assume linear interpolation of index value
        spot_array = np.linspace(self.valore_iniziale_indice, self.valore_ipotetico_indice, n_points)
        
        results = {
            'giorni': giorni_array,
            'spot': spot_array,
            'barrier': [],
            'prezzo_turbo': [],
            'valore_portafoglio': [],
            'valore_turbo': [],
            'valore_totale': [],
            'premio': [],
        }
        
        n_turbo = self.calculate_n_turbo()
        premio_iniziale = self.calculate_initial_premium()
        capitale_turbo = n_turbo * self.prezzo_iniziale
        
        for i, (giorni_elapsed, spot) in enumerate(zip(giorni_array, spot_array)):
            giorni_residui = self.giorni - giorni_elapsed
            
            # Barrier at this point
            barrier = self.calculate_barrier(giorni_elapsed)
            results['barrier'].append(barrier)
            
            # Turbo price
            prezzo_turbo = self.calculate_turbo_price(spot, giorni_residui)
            results['prezzo_turbo'].append(prezzo_turbo)
            
            # Premium at this point
            premio = self.calculate_premium_decay(giorni_residui, premio_iniziale)
            results['premio'].append(premio)
            
            # Portfolio value (with Beta)
            variazione_indice = (spot / self.valore_iniziale_indice) - 1
            variazione_portafoglio = variazione_indice * self.beta
            valore_portafoglio = self.valore_portafoglio * (1 + variazione_portafoglio)
            results['valore_portafoglio'].append(valore_portafoglio)
            
            # Turbo value
            valore_turbo = prezzo_turbo * n_turbo
            results['valore_turbo'].append(valore_turbo)
            
            # Total value
            valore_totale = valore_portafoglio + valore_turbo
            results['valore_totale'].append(valore_totale)
        
        return giorni_array, results
