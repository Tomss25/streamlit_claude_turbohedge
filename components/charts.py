"""
Chart components for Turbo Hedge Calculator
"""

import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
from typing import Dict, List


def create_time_evolution_chart(giorni: np.ndarray, results: Dict, 
                                capitale_iniziale: float) -> go.Figure:
    """
    Create time evolution chart showing portfolio, turbo, and total value
    
    Args:
        giorni: Array of days
        results: Results dictionary from calculate_time_evolution
        capitale_iniziale: Initial total capital
    
    Returns:
        Plotly figure
    """
    fig = go.Figure()
    
    # Portfolio value
    fig.add_trace(go.Scatter(
        x=giorni,
        y=results['valore_portafoglio'],
        name='Portafoglio',
        line=dict(color='#E53E3E', width=2),
        mode='lines'
    ))
    
    # Turbo value
    fig.add_trace(go.Scatter(
        x=giorni,
        y=results['valore_turbo'],
        name='Turbo Short',
        line=dict(color='#38A169', width=2),
        mode='lines'
    ))
    
    # Total value
    fig.add_trace(go.Scatter(
        x=giorni,
        y=results['valore_totale'],
        name='Totale Coperto',
        line=dict(color='#2c5282', width=3),
        mode='lines'
    ))
    
    # Initial capital line
    fig.add_hline(
        y=capitale_iniziale,
        line_dash="dash",
        line_color="gray",
        annotation_text="Capitale Iniziale",
        annotation_position="right"
    )
    
    fig.update_layout(
        title='Evoluzione Temporale del Portafoglio',
        xaxis_title='Giorni',
        yaxis_title='Valore (EUR)',
        hovermode='x unified',
        template='plotly_white',
        height=500,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(255,255,255,0.8)"
        )
    )
    
    return fig


def create_spot_barrier_chart(giorni: np.ndarray, results: Dict) -> go.Figure:
    """
    Create chart showing index spot vs barrier over time
    
    Args:
        giorni: Array of days
        results: Results dictionary from calculate_time_evolution
    
    Returns:
        Plotly figure
    """
    fig = go.Figure()
    
    # Spot price
    fig.add_trace(go.Scatter(
        x=giorni,
        y=results['spot'],
        name='Indice',
        line=dict(color='#2c5282', width=2),
        mode='lines',
        fill=None
    ))
    
    # Barrier
    fig.add_trace(go.Scatter(
        x=giorni,
        y=results['barrier'],
        name='Barriera Knock-Out',
        line=dict(color='#E53E3E', width=2, dash='dash'),
        mode='lines',
        fill='tonexty',
        fillcolor='rgba(229, 62, 62, 0.1)'
    ))
    
    fig.update_layout(
        title='Indice vs Barriera Knock-Out',
        xaxis_title='Giorni',
        yaxis_title='Livello Indice',
        hovermode='x unified',
        template='plotly_white',
        height=400,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(255,255,255,0.8)"
        )
    )
    
    # Add annotation for danger zone
    fig.add_annotation(
        x=giorni[-1],
        y=results['barrier'][-1],
        text="Zona Knock-Out",
        showarrow=True,
        arrowhead=2,
        arrowcolor="#E53E3E",
        ax=-60,
        ay=-40
    )
    
    return fig


def create_premium_decay_chart(giorni: np.ndarray, results: Dict) -> go.Figure:
    """
    Create chart showing premium decay over time
    
    Args:
        giorni: Array of days
        results: Results dictionary from calculate_time_evolution
    
    Returns:
        Plotly figure
    """
    fig = go.Figure()
    
    # Premium decay
    fig.add_trace(go.Scatter(
        x=giorni,
        y=results['premio'],
        name='Premio (Time Value)',
        line=dict(color='#DD6B20', width=3),
        mode='lines',
        fill='tozeroy',
        fillcolor='rgba(221, 107, 32, 0.2)'
    ))
    
    fig.update_layout(
        title='Decay del Premio nel Tempo (Theta)',
        xaxis_title='Giorni',
        yaxis_title='Premio (EUR)',
        hovermode='x unified',
        template='plotly_white',
        height=350
    )
    
    return fig


def create_scenario_analysis_chart(df: pd.DataFrame) -> go.Figure:
    """
    Create scenario analysis chart
    
    Args:
        df: DataFrame with scenario results
    
    Returns:
        Plotly figure
    """
    fig = go.Figure()
    
    # Portfolio performance (unhedged)
    fig.add_trace(go.Scatter(
        x=df['Variazione Indice %'],
        y=df['Performance Portafoglio %'],
        name='Portafoglio Non Coperto',
        line=dict(color='#E53E3E', width=2, dash='dot'),
        mode='lines+markers'
    ))
    
    # Hedged performance
    fig.add_trace(go.Scatter(
        x=df['Variazione Indice %'],
        y=df['Performance Totale %'],
        name='Portafoglio Coperto',
        line=dict(color='#2c5282', width=3),
        mode='lines+markers'
    ))
    
    # Zero line
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
    fig.add_vline(x=0, line_dash="dash", line_color="gray", opacity=0.5)
    
    fig.update_layout(
        title='Scenario Analysis: Performance vs Variazione Indice',
        xaxis_title='Variazione Indice (%)',
        yaxis_title='Performance (%)',
        hovermode='x unified',
        template='plotly_white',
        height=500,
        legend=dict(
            yanchor="bottom",
            y=0.01,
            xanchor="right",
            x=0.99,
            bgcolor="rgba(255,255,255,0.8)"
        )
    )
    
    return fig


def create_monte_carlo_histogram(performance: np.ndarray, 
                                 mean_perf: float,
                                 percentile_5: float,
                                 percentile_95: float) -> go.Figure:
    """
    Create histogram of Monte Carlo simulation results
    
    Args:
        performance: Array of performance values
        mean_perf: Mean performance
        percentile_5: 5th percentile (VaR)
        percentile_95: 95th percentile
    
    Returns:
        Plotly figure
    """
    fig = go.Figure()
    
    # Histogram
    fig.add_trace(go.Histogram(
        x=performance,
        nbinsx=50,
        name='Distribuzione',
        marker_color='#2c5282',
        opacity=0.7
    ))
    
    # Mean line
    fig.add_vline(
        x=mean_perf,
        line_dash="solid",
        line_color="#38A169",
        line_width=2,
        annotation_text=f"Media: {mean_perf:.2f}%",
        annotation_position="top"
    )
    
    # VaR 95% line
    fig.add_vline(
        x=percentile_5,
        line_dash="dash",
        line_color="#E53E3E",
        line_width=2,
        annotation_text=f"VaR 95%: {percentile_5:.2f}%",
        annotation_position="bottom left"
    )
    
    # 95th percentile line
    fig.add_vline(
        x=percentile_95,
        line_dash="dash",
        line_color="#38A169",
        line_width=2,
        annotation_text=f"95°: {percentile_95:.2f}%",
        annotation_position="top right"
    )
    
    fig.update_layout(
        title='Distribuzione Performance (Monte Carlo)',
        xaxis_title='Performance (%)',
        yaxis_title='Frequenza',
        template='plotly_white',
        height=450,
        showlegend=False
    )
    
    return fig


def create_heatmap_strike_maturity(df: pd.DataFrame, metric: str = 'Hedge Ratio') -> go.Figure:
    """
    Create heatmap for Strike vs Maturity optimization
    
    Args:
        df: DataFrame with grid search results
        metric: Metric to display
    
    Returns:
        Plotly figure
    """
    # Pivot data
    pivot = df.pivot_table(
        values=metric,
        index='Strike',
        columns='Giorni',
        aggfunc='mean'
    )
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns,
        y=pivot.index,
        colorscale='RdYlGn',
        text=pivot.values,
        texttemplate='%{text:.2f}',
        textfont={"size": 10},
        colorbar=dict(title=metric)
    ))
    
    fig.update_layout(
        title=f'Ottimizzazione: {metric} vs Strike e Scadenza',
        xaxis_title='Giorni a Scadenza',
        yaxis_title='Strike',
        template='plotly_white',
        height=500
    )
    
    return fig


def create_sensitivity_chart(df: pd.DataFrame) -> go.Figure:
    """
    Create sensitivity analysis chart
    
    Args:
        df: DataFrame with sensitivity results (from sensitivity_to_spot)
    
    Returns:
        Plotly figure
    """
    fig = go.Figure()
    
    # Performance
    fig.add_trace(go.Scatter(
        x=df['Spot'],
        y=df['Performance Tot %'],
        name='Performance Coperta',
        line=dict(color='#2c5282', width=3),
        mode='lines'
    ))
    
    # Hedge ratio
    fig.add_trace(go.Scatter(
        x=df['Spot'],
        y=df['Hedge Ratio'] * 100,
        name='Hedge Ratio (%)',
        line=dict(color='#38A169', width=2, dash='dash'),
        mode='lines',
        yaxis='y2'
    ))
    
    # Mark knocked out zones
    knocked_out = df[df['Knocked Out'] == True]
    if len(knocked_out) > 0:
        fig.add_vrect(
            x0=knocked_out['Spot'].min(),
            x1=knocked_out['Spot'].max(),
            fillcolor="red",
            opacity=0.1,
            layer="below",
            line_width=0,
        )
    
    fig.update_layout(
        title='Analisi di Sensibilità al Livello dell\'Indice',
        xaxis_title='Livello Indice',
        yaxis_title='Performance (%)',
        yaxis2=dict(
            title='Hedge Ratio (%)',
            overlaying='y',
            side='right'
        ),
        hovermode='x unified',
        template='plotly_white',
        height=500,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(255,255,255,0.8)"
        )
    )
    
    return fig


def create_greeks_chart(greeks_dict: Dict) -> go.Figure:
    """
    Create bar chart showing Greeks values
    
    Args:
        greeks_dict: Dictionary with Greeks values
    
    Returns:
        Plotly figure
    """
    # Prepare data
    greeks_names = ['Delta', 'Gamma', 'Vega', 'Theta', 'Rho']
    greeks_values = [
        greeks_dict.get('delta', 0),
        greeks_dict.get('gamma', 0) * 100,  # Scale for visibility
        greeks_dict.get('vega', 0),
        greeks_dict.get('theta', 0) * 100,  # Scale for visibility
        greeks_dict.get('rho', 0),
    ]
    
    colors = ['#E53E3E', '#DD6B20', '#D69E2E', '#38A169', '#2c5282']
    
    fig = go.Figure(data=[
        go.Bar(
            x=greeks_names,
            y=greeks_values,
            marker_color=colors,
            text=[f'{v:.4f}' for v in greeks_values],
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        title='Greeks del Turbo Certificate',
        yaxis_title='Valore',
        template='plotly_white',
        height=400,
        showlegend=False
    )
    
    return fig
