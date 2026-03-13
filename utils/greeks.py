"""
Greeks calculation for Turbo Short certificates
Optional advanced metrics
"""

import numpy as np
from scipy.stats import norm
from typing import Dict


class GreeksCalculator:
    """Calculate Greeks for Turbo Short certificates"""
    
    def __init__(self, params: Dict):
        """
        Initialize Greeks calculator
        
        Args:
            params: Dictionary with parameters including volatility
        """
        self.spot = params['spot']
        self.strike = params['strike']
        self.barrier = params['barrier']
        self.time_to_maturity = params['time_to_maturity']  # in years
        self.volatility = params['volatility']  # annualized
        self.risk_free_rate = params['risk_free_rate']
        self.dividend_yield = params.get('dividend_yield', 0.0)
        self.multiplo = params['multiplo']
        self.cambio = params['cambio']
    
    def _d1(self) -> float:
        """Calculate d1 for Black-Scholes"""
        if self.volatility == 0 or self.time_to_maturity == 0:
            return 0
        
        numerator = np.log(self.spot / self.strike) + \
                   (self.risk_free_rate - self.dividend_yield + 0.5 * self.volatility**2) * self.time_to_maturity
        denominator = self.volatility * np.sqrt(self.time_to_maturity)
        
        return numerator / denominator if denominator != 0 else 0
    
    def _d2(self) -> float:
        """Calculate d2 for Black-Scholes"""
        return self._d1() - self.volatility * np.sqrt(self.time_to_maturity)
    
    def calculate_delta(self) -> float:
        """
        Calculate Delta (rate of change of price with respect to underlying)
        
        For Turbo Short (put-like):
        Delta ≈ -N(-d1) × Multiplo / Cambio
        
        Returns:
            Delta value (negative for short)
        """
        if self.volatility == 0:
            # Simple approximation without vol
            if self.spot < self.strike:
                return -self.multiplo / self.cambio
            else:
                return 0
        
        d1 = self._d1()
        delta = -norm.cdf(-d1) * self.multiplo / self.cambio
        
        return delta
    
    def calculate_gamma(self) -> float:
        """
        Calculate Gamma (rate of change of delta with respect to underlying)
        
        Gamma = N'(d1) / (Spot × Vol × sqrt(T))
        
        Returns:
            Gamma value
        """
        if self.volatility == 0 or self.time_to_maturity == 0:
            return 0
        
        d1 = self._d1()
        denominator = self.spot * self.volatility * np.sqrt(self.time_to_maturity)
        
        if denominator == 0:
            return 0
        
        gamma = norm.pdf(d1) / denominator * self.multiplo / self.cambio
        
        return gamma
    
    def calculate_vega(self) -> float:
        """
        Calculate Vega (sensitivity to volatility)
        
        Vega = Spot × N'(d1) × sqrt(T) / 100
        (divided by 100 for 1% change in volatility)
        
        Returns:
            Vega value
        """
        if self.time_to_maturity == 0:
            return 0
        
        d1 = self._d1()
        vega = self.spot * norm.pdf(d1) * np.sqrt(self.time_to_maturity) / 100
        vega = vega * self.multiplo / self.cambio
        
        return vega
    
    def calculate_theta(self) -> float:
        """
        Calculate Theta (time decay)
        
        Theta = -(Spot × N'(d1) × Vol) / (2 × sqrt(T)) - r × K × e^(-rT) × N(-d2)
        (per day: divide by 365)
        
        Returns:
            Theta value (negative, per day)
        """
        if self.time_to_maturity == 0:
            return 0
        
        d1 = self._d1()
        d2 = self._d2()
        
        term1 = -(self.spot * norm.pdf(d1) * self.volatility) / (2 * np.sqrt(self.time_to_maturity))
        term2 = -self.risk_free_rate * self.strike * np.exp(-self.risk_free_rate * self.time_to_maturity) * norm.cdf(-d2)
        
        theta = (term1 + term2) * self.multiplo / self.cambio / 365
        
        return theta
    
    def calculate_rho(self) -> float:
        """
        Calculate Rho (sensitivity to interest rate)
        
        Rho = -K × T × e^(-rT) × N(-d2) / 100
        (divided by 100 for 1% change in rate)
        
        Returns:
            Rho value
        """
        if self.time_to_maturity == 0:
            return 0
        
        d2 = self._d2()
        rho = -self.strike * self.time_to_maturity * \
              np.exp(-self.risk_free_rate * self.time_to_maturity) * \
              norm.cdf(-d2) / 100
        rho = rho * self.multiplo / self.cambio
        
        return rho
    
    def calculate_knockout_probability(self) -> float:
        """
        Calculate approximate probability of hitting barrier (knock-out)
        
        Using barrier option formula:
        P(knockout) ≈ N(d_barrier)
        
        where d_barrier = (ln(S/H) - (r - q - 0.5*σ²)T) / (σ√T)
        
        Returns:
            Probability between 0 and 1
        """
        if self.volatility == 0 or self.time_to_maturity == 0:
            # Deterministic case
            return 1.0 if self.spot >= self.barrier else 0.0
        
        mu = self.risk_free_rate - self.dividend_yield - 0.5 * self.volatility**2
        
        numerator = np.log(self.spot / self.barrier) - mu * self.time_to_maturity
        denominator = self.volatility * np.sqrt(self.time_to_maturity)
        
        if denominator == 0:
            return 0.0
        
        d_barrier = numerator / denominator
        prob = norm.cdf(-d_barrier)
        
        return max(0, min(1, prob))
    
    def calculate_all_greeks(self) -> Dict:
        """
        Calculate all Greeks and metrics
        
        Returns:
            Dictionary with all Greeks
        """
        return {
            'delta': self.calculate_delta(),
            'gamma': self.calculate_gamma(),
            'vega': self.calculate_vega(),
            'theta': self.calculate_theta(),
            'rho': self.calculate_rho(),
            'knockout_prob': self.calculate_knockout_probability(),
        }


def calculate_implied_volatility(market_price: float, spot: float, strike: float, 
                                 barrier: float, time_to_maturity: float,
                                 risk_free_rate: float, multiplo: float, 
                                 cambio: float, tolerance: float = 0.01,
                                 max_iterations: int = 100) -> float:
    """
    Calculate implied volatility using Newton-Raphson method
    (Simplified version for Turbo certificates)
    
    Args:
        market_price: Observed market price
        Other parameters as in GreeksCalculator
        tolerance: Convergence tolerance
        max_iterations: Maximum iterations
    
    Returns:
        Implied volatility (annualized)
    """
    # Initial guess
    vol = 0.20  # Start with 20%
    
    for _ in range(max_iterations):
        # Create calculator with current vol
        params = {
            'spot': spot,
            'strike': strike,
            'barrier': barrier,
            'time_to_maturity': time_to_maturity,
            'volatility': vol,
            'risk_free_rate': risk_free_rate,
            'dividend_yield': 0,
            'multiplo': multiplo,
            'cambio': cambio,
        }
        
        calc = GreeksCalculator(params)
        
        # Simple pricing approximation
        d1 = calc._d1()
        d2 = calc._d2()
        
        theoretical_price = (strike * np.exp(-risk_free_rate * time_to_maturity) * norm.cdf(-d2) - 
                           spot * norm.cdf(-d1)) * multiplo / cambio
        
        # Calculate vega
        vega = calc.calculate_vega()
        
        # Price difference
        diff = theoretical_price - market_price
        
        if abs(diff) < tolerance or vega == 0:
            return vol
        
        # Newton-Raphson update
        vol = vol - diff / (vega * 100)  # vega is per 1% change
        
        # Keep vol positive and reasonable
        vol = max(0.01, min(2.0, vol))
    
    return vol
