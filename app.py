"""
Turbo Hedge Calculator - Streamlit Web App
Professional tool for Turbo Short certificate hedging strategy
"""

import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path

# Import custom modules
from utils import TurboCalculator, GreeksCalculator, MonteCarloSimulator, StrategyOptimizer
from components import (
    create_time_evolution_chart, create_spot_barrier_chart, create_premium_decay_chart,
    create_scenario_analysis_chart, create_monte_carlo_histogram, create_heatmap_strike_maturity,
    create_sensitivity_chart, create_greeks_chart, generate_scenario_table,
    generate_scenario_summary, create_stress_test_table
)
from utils.optimization import sensitivity_to_spot

# Page configuration
st.set_page_config(
    page_title="Turbo Hedge Calculator",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
def load_css():
    css_file = Path(__file__).parent / "assets" / "style.css"
    if css_file.exists():
        with open(css_file) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css()

# Title and description
st.title("📊 Turbo Hedge Calculator")
st.markdown("""
<div class="info-box">
<strong>Tool professionale per la copertura di portafogli azionari tramite Certificati Turbo Short</strong><br>
Calcola il dimensionamento ottimale, simula scenari, e analizza l'efficacia della copertura con metriche avanzate.
</div>
""", unsafe_allow_html=True)

# Initialize session state
if 'calculated' not in st.session_state:
    st.session_state.calculated = False

# ============================================================================
# SIDEBAR - Advanced Metrics (Optional)
# ============================================================================

st.sidebar.header("⚙️ Metriche Aggiuntive")
st.sidebar.markdown("*Parametri opzionali per analisi avanzate*")

with st.sidebar.expander("📈 Beta e Correlazione", expanded=False):
    beta_portafoglio = st.number_input(
        "Beta del Portafoglio",
        min_value=0.0,
        max_value=2.0,
        value=1.0,
        step=0.05,
        help="Sensibilità del portafoglio all'indice. 1.0 = replica perfetta, <1 = meno volatile, >1 = più volatile"
    )

with st.sidebar.expander("💰 Costi di Transazione", expanded=False):
    bid_ask_spread = st.number_input(
        "Bid-Ask Spread (%)",
        min_value=0.0,
        max_value=5.0,
        value=0.0,
        step=0.1,
        help="Spread denaro-lettera sul Turbo"
    )
    
    commissioni = st.number_input(
        "Commissioni (%)",
        min_value=0.0,
        max_value=2.0,
        value=0.0,
        step=0.05,
        help="Commissioni di acquisto/vendita"
    )
    
    tasse = st.number_input(
        "Tasse su Capital Gains (%)",
        min_value=0.0,
        max_value=50.0,
        value=0.0,
        step=1.0,
        help="Tasse sui guadagni (es. 26% in Italia)"
    )

with st.sidebar.expander("📊 Dividend Yield", expanded=False):
    dividend_yield = st.number_input(
        "Dividend Yield Indice (%)",
        min_value=0.0,
        max_value=10.0,
        value=0.0,
        step=0.1,
        help="Rendimento da dividendi dell'indice (annualizzato)"
    )

with st.sidebar.expander("🎲 Volatilità e Greeks", expanded=False):
    enable_greeks = st.checkbox("Abilita Calcolo Greeks", value=False)
    
    if enable_greeks:
        volatility = st.number_input(
            "Volatilità Implicita (%)",
            min_value=5.0,
            max_value=100.0,
            value=20.0,
            step=1.0,
            help="Volatilità annualizzata dell'indice"
        ) / 100
    else:
        volatility = 0.20  # Default

with st.sidebar.expander("🎯 Monte Carlo Simulation", expanded=False):
    enable_monte_carlo = st.checkbox("Abilita Simulazione Monte Carlo", value=False)
    
    if enable_monte_carlo:
        n_simulations = st.select_slider(
            "Numero di Simulazioni",
            options=[1000, 5000, 10000, 25000, 50000],
            value=10000
        )
        
        mc_volatility = st.number_input(
            "Volatilità per Monte Carlo (%)",
            min_value=5.0,
            max_value=100.0,
            value=20.0,
            step=1.0,
            help="Volatilità per le simulazioni"
        ) / 100
    else:
        n_simulations = 10000
        mc_volatility = 0.20

st.sidebar.markdown("---")
st.sidebar.markdown("*Sviluppato per analisi professionale di hedging*")

# ============================================================================
# MAIN PAGE - Original Inputs
# ============================================================================

st.header("📝 Parametri di Input")

# Create three columns for inputs
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("🎯 Turbo Short Certificate")
    
    prezzo_iniziale = st.number_input(
        "Prezzo Iniziale (EUR)",
        min_value=0.01,
        max_value=1000.0,
        value=7.64,
        step=0.01,
        help="Prezzo di mercato del certificato Turbo Short"
    )
    
    strike = st.number_input(
        "Strike",
        min_value=1000.0,
        max_value=50000.0,
        value=7505.97,
        step=0.01,
        help="Livello di strike del Turbo Short"
    )
    
    cambio = st.number_input(
        "Tasso di Cambio (EUR/USD)",
        min_value=0.5,
        max_value=2.0,
        value=1.15,
        step=0.01,
        help="Tasso di cambio per conversione valuta"
    )
    
    multiplo = st.number_input(
        "Multiplo",
        min_value=0.001,
        max_value=1.0,
        value=0.01,
        step=0.001,
        format="%.3f",
        help="Ratio di conversione punti indice / valore nominale"
    )
    
    euribor = st.number_input(
        "Euribor 12M",
        min_value=0.0,
        max_value=0.20,
        value=0.02456,
        step=0.0001,
        format="%.5f",
        help="Tasso Euribor 12 mesi (es. 0.02456 = 2.456%)"
    )

with col2:
    st.subheader("📈 Indice di Riferimento")
    
    valore_iniziale_indice = st.number_input(
        "Valore Iniziale Indice",
        min_value=1000.0,
        max_value=50000.0,
        value=6670.75,
        step=0.01,
        help="Valore corrente dell'indice"
    )
    
    valore_ipotetico_indice = st.number_input(
        "Valore Ipotetico Indice",
        min_value=1000.0,
        max_value=50000.0,
        value=6000.0,
        step=0.01,
        help="Valore futuro dell'indice nello scenario da simulare"
    )
    
    variazione_pct = (valore_ipotetico_indice / valore_iniziale_indice - 1) * 100
    st.metric("Variazione Scenario", f"{variazione_pct:+.2f}%")
    
    giorni = st.number_input(
        "Giorni a Scadenza",
        min_value=1,
        max_value=365,
        value=60,
        step=1,
        help="Orizzonte temporale della copertura"
    )

with col3:
    st.subheader("💼 Portafoglio")
    
    valore_portafoglio = st.number_input(
        "Valore Portafoglio (EUR)",
        min_value=1000.0,
        max_value=10000000.0,
        value=200000.0,
        step=1000.0,
        help="Valore del portafoglio da coprire"
    )
    
    st.markdown("###")
    
    if st.button("🚀 Calcola Copertura", type="primary", use_container_width=True):
        st.session_state.calculated = True

# ============================================================================
# CALCULATIONS
# ============================================================================

if st.session_state.calculated:
    
    # Prepare parameters dictionary
    params = {
        'prezzo_iniziale': prezzo_iniziale,
        'strike': strike,
        'cambio': cambio,
        'multiplo': multiplo,
        'euribor': euribor,
        'valore_iniziale_indice': valore_iniziale_indice,
        'valore_ipotetico_indice': valore_ipotetico_indice,
        'giorni': giorni,
        'valore_portafoglio': valore_portafoglio,
        # Enhanced parameters
        'beta': beta_portafoglio,
        'dividend_yield': dividend_yield / 100 if dividend_yield > 0 else 0.0,
        'bid_ask_spread': bid_ask_spread,
        'commissioni': commissioni,
        'tasse': tasse,
    }
    
    # Create calculator
    calculator = TurboCalculator(params)
    
    # Calculate results
    results = calculator.calculate_hedge_results()
    
    st.markdown("---")
    
    # ============================================================================
    # MAIN RESULTS
    # ============================================================================
    
    st.header("📊 Risultati della Copertura")
    
    # Key metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Fair Value Turbo",
            f"€{results['fair_value']:.2f}",
            f"{results['premio_pct']:.2f}% premio"
        )
    
    with col2:
        st.metric(
            "Leva Finanziaria",
            f"{results['leverage']:.2f}x",
            "Esposizione effettiva"
        )
    
    with col3:
        st.metric(
            "N° Certificati",
            f"{results['n_turbo']:.0f}",
            f"€{results['capitale_turbo']:,.0f}"
        )
    
    with col4:
        st.metric(
            "Capitale Investito",
            f"{results['capitale_investito_pct']:.2f}%",
            "del portafoglio"
        )
    
    st.markdown("###")
    
    # Performance metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        perf_color = "normal" if results['performance_portafoglio'] >= 0 else "inverse"
        st.metric(
            "Performance Portafoglio",
            f"{results['performance_portafoglio']*100:.2f}%",
            f"€{results['pl_portafoglio']:,.0f}",
            delta_color=perf_color
        )
    
    with col2:
        st.metric(
            "Performance Turbo",
            f"{results['performance_turbo']*100:.2f}%",
            f"€{results['pl_turbo']:,.0f}"
        )
    
    with col3:
        perf_tot_color = "normal" if results['performance_totale'] >= 0 else "inverse"
        st.metric(
            "Performance Coperta",
            f"{results['performance_totale']*100:.2f}%",
            f"€{results['pl_netto']:,.0f}",
            delta_color=perf_tot_color
        )
    
    # Hedge effectiveness
    st.markdown("###")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        hedge_ratio_pct = results['hedge_ratio'] * 100
        if hedge_ratio_pct >= 95:
            hedge_class = "success-box"
            hedge_icon = "✅"
        elif hedge_ratio_pct >= 85:
            hedge_class = "info-box"
            hedge_icon = "✓"
        else:
            hedge_class = "warning-box"
            hedge_icon = "⚠️"
        
        st.markdown(f"""
        <div class="{hedge_class}">
        <strong>{hedge_icon} Hedge Ratio: {hedge_ratio_pct:.1f}%</strong><br>
        Efficacia della copertura nel compensare le perdite
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        barrier_dist = results['distanza_barriera_pct']
        if barrier_dist >= 10:
            barrier_class = "success-box"
            barrier_icon = "✅"
        elif barrier_dist >= 5:
            barrier_class = "warning-box"
            barrier_icon = "⚠️"
        else:
            barrier_class = "danger-box"
            barrier_icon = "❌"
        
        st.markdown(f"""
        <div class="{barrier_class}">
        <strong>{barrier_icon} Distanza Barriera: {barrier_dist:+.2f}%</strong><br>
        Barriera K.O. a {results['barrier_future']:,.2f} punti
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        total_cost = results['costi_acquisto'] + results['costi_vendita'] + results['tasse_pagate']
        st.markdown(f"""
        <div class="info-box">
        <strong>💰 Costi Totali: €{total_cost:,.2f}</strong><br>
        Acquisto + Vendita + Tasse
        </div>
        """, unsafe_allow_html=True)
    
    # Detailed breakdown
    with st.expander("📋 Dettaglio Completo dei Calcoli", expanded=False):
        detail_col1, detail_col2 = st.columns(2)
        
        with detail_col1:
            st.markdown("**Turbo Certificate:**")
            detail_data_turbo = {
                'Metrica': [
                    'Prezzo Iniziale',
                    'Fair Value',
                    'Premio (Time Value)',
                    'Premio %',
                    'Strike',
                    'Barriera Iniziale',
                    'Barriera Futura',
                    'Leva',
                ],
                'Valore': [
                    f'€{prezzo_iniziale:.2f}',
                    f'€{results["fair_value"]:.2f}',
                    f'€{results["premio"]:.2f}',
                    f'{results["premio_pct"]:.2f}%',
                    f'{strike:,.2f}',
                    f'{results["barrier_initial"]:,.2f}',
                    f'{results["barrier_future"]:,.2f}',
                    f'{results["leverage"]:.2f}x',
                ]
            }
            st.dataframe(pd.DataFrame(detail_data_turbo), hide_index=True, use_container_width=True)
        
        with detail_col2:
            st.markdown("**Posizione e Costi:**")
            detail_data_position = {
                'Metrica': [
                    'N° Certificati',
                    'Capitale Base',
                    'Bid-Ask Spread',
                    'Costi Acquisto',
                    'Capitale Totale Turbo',
                    'Capitale Totale',
                    'Capitale Investito %',
                ],
                'Valore': [
                    f'{results["n_turbo"]:.2f}',
                    f'€{results["capitale_turbo_base"]:,.2f}',
                    f'€{results["capitale_turbo"] - results["capitale_turbo_base"]:,.2f}',
                    f'€{results["costi_acquisto"]:,.2f}',
                    f'€{results["capitale_turbo"]:,.2f}',
                    f'€{results["capitale_totale"]:,.2f}',
                    f'{results["capitale_investito_pct"]:.2f}%',
                ]
            }
            st.dataframe(pd.DataFrame(detail_data_position), hide_index=True, use_container_width=True)
        
        st.markdown("**Scenario Futuro:**")
        detail_col3, detail_col4 = st.columns(2)
        
        with detail_col3:
            detail_data_scenario1 = {
                'Metrica': [
                    'Variazione Indice',
                    'Variazione Ptf (Beta adjusted)',
                    'Valore Portafoglio Futuro',
                    'P&L Portafoglio',
                    'Performance Portafoglio',
                ],
                'Valore': [
                    f'{results["variazione_indice_pct"]:.2f}%',
                    f'{results["variazione_portafoglio_pct"]:.2f}%',
                    f'€{results["valore_portafoglio_futuro"]:,.2f}',
                    f'€{results["pl_portafoglio"]:,.2f}',
                    f'{results["performance_portafoglio"]*100:.2f}%',
                ]
            }
            st.dataframe(pd.DataFrame(detail_data_scenario1), hide_index=True, use_container_width=True)
        
        with detail_col4:
            detail_data_scenario2 = {
                'Metrica': [
                    'Prezzo Turbo Futuro',
                    'Valore Turbo Gross',
                    'Costi Vendita',
                    'Tasse Pagate',
                    'Valore Turbo Net',
                    'P&L Turbo',
                    'Performance Turbo',
                ],
                'Valore': [
                    f'€{results["prezzo_turbo_futuro"]:.2f}',
                    f'€{results["valore_turbo_futuro_gross"]:,.2f}',
                    f'€{results["costi_vendita"]:,.2f}',
                    f'€{results["tasse_pagate"]:,.2f}',
                    f'€{results["valore_turbo_futuro"]:,.2f}',
                    f'€{results["pl_turbo"]:,.2f}',
                    f'{results["performance_turbo"]*100:.2f}%',
                ]
            }
            st.dataframe(pd.DataFrame(detail_data_scenario2), hide_index=True, use_container_width=True)
    
    # ============================================================================
    # CHARTS AND VISUALIZATIONS
    # ============================================================================
    
    st.markdown("---")
    st.header("📈 Analisi Grafiche")
    
    # Time evolution
    with st.expander("⏱️ Evoluzione Temporale", expanded=True):
        giorni_array, time_results = calculator.calculate_time_evolution(n_points=30)
        
        chart_col1, chart_col2 = st.columns([2, 1])
        
        with chart_col1:
            fig_evolution = create_time_evolution_chart(
                giorni_array, 
                time_results, 
                results['capitale_totale']
            )
            st.plotly_chart(fig_evolution, use_container_width=True)
        
        with chart_col2:
            fig_premium = create_premium_decay_chart(giorni_array, time_results)
            st.plotly_chart(fig_premium, use_container_width=True)
        
        fig_barrier = create_spot_barrier_chart(giorni_array, time_results)
        st.plotly_chart(fig_barrier, use_container_width=True)
    
    # ============================================================================
    # SCENARIO ANALYSIS
    # ============================================================================
    
    st.markdown("---")
    st.header("🎯 Scenario Analysis")
    
    tab1, tab2, tab3 = st.tabs(["📊 Tabella Scenari", "📈 Grafico", "⚠️ Stress Test"])
    
    with tab1:
        st.markdown("Simulazione di multipli scenari di mercato:")
        
        # Generate scenario table
        scenario_df = generate_scenario_table(
            calculator,
            scenario_range=(-30, 30),
            n_scenarios=13
        )
        
        # Display with conditional formatting
        st.dataframe(
            scenario_df,
            hide_index=True,
            use_container_width=True,
            height=500
        )
        
        # Download button
        csv = scenario_df.to_csv(index=False)
        st.download_button(
            label="📥 Scarica Tabella Scenari (CSV)",
            data=csv,
            file_name="scenario_analysis.csv",
            mime="text/csv"
        )
    
    with tab2:
        # Prepare data for chart
        scenario_chart_data = []
        for var_pct in np.linspace(-30, 30, 25):
            new_spot = valore_iniziale_indice * (1 + var_pct / 100)
            calc_temp = TurboCalculator({**params, 'valore_ipotetico_indice': new_spot})
            res_temp = calc_temp.calculate_hedge_results()
            
            scenario_chart_data.append({
                'Variazione Indice %': var_pct,
                'Performance Portafoglio %': res_temp['performance_portafoglio'] * 100,
                'Performance Totale %': res_temp['performance_totale'] * 100,
            })
        
        scenario_df_chart = pd.DataFrame(scenario_chart_data)
        
        fig_scenario = create_scenario_analysis_chart(scenario_df_chart)
        st.plotly_chart(fig_scenario, use_container_width=True)
    
    with tab3:
        st.markdown("Analisi di scenari estremi e situazioni di stress:")
        
        stress_df = create_stress_test_table(calculator)
        st.dataframe(stress_df, hide_index=True, use_container_width=True)
    
    # ============================================================================
    # GREEKS (Optional)
    # ============================================================================
    
    if enable_greeks:
        st.markdown("---")
        st.header("🎲 Analisi Greeks")
        
        greeks_params = {
            'spot': valore_iniziale_indice,
            'strike': strike,
            'barrier': results['barrier_future'],
            'time_to_maturity': giorni / 365.0,
            'volatility': volatility,
            'risk_free_rate': euribor,
            'dividend_yield': dividend_yield / 100 if dividend_yield > 0 else 0.0,
            'multiplo': multiplo,
            'cambio': cambio,
        }
        
        greeks_calc = GreeksCalculator(greeks_params)
        greeks = greeks_calc.calculate_all_greeks()
        
        greek_col1, greek_col2, greek_col3 = st.columns(3)
        
        with greek_col1:
            st.metric("Delta", f"{greeks['delta']:.4f}", "Sensibilità al prezzo")
            st.metric("Gamma", f"{greeks['gamma']:.6f}", "Convessità")
        
        with greek_col2:
            st.metric("Vega", f"{greeks['vega']:.4f}", "Sensibilità a vol")
            st.metric("Theta", f"{greeks['theta']:.4f}", "Time decay/giorno")
        
        with greek_col3:
            st.metric("Rho", f"{greeks['rho']:.4f}", "Sensibilità a tasso")
            st.metric("Prob. K.O.", f"{greeks['knockout_prob']*100:.2f}%", "Probabilità knock-out")
        
        fig_greeks = create_greeks_chart(greeks)
        st.plotly_chart(fig_greeks, use_container_width=True)
    
    # ============================================================================
    # MONTE CARLO SIMULATION (Optional)
    # ============================================================================
    
    if enable_monte_carlo:
        st.markdown("---")
        st.header("🎲 Simulazione Monte Carlo")
        
        with st.spinner(f"Esecuzione di {n_simulations:,} simulazioni..."):
            mc_simulator = MonteCarloSimulator(calculator, mc_volatility, n_simulations)
            mc_results = mc_simulator.calculate_outcomes()
        
        # Summary statistics
        mc_col1, mc_col2, mc_col3, mc_col4 = st.columns(4)
        
        with mc_col1:
            st.metric(
                "Performance Media",
                f"{mc_results['mean_performance']:.2f}%",
                f"σ = {mc_results['std_performance']:.2f}%"
            )
        
        with mc_col2:
            st.metric(
                "VaR 95%",
                f"{mc_results['var_95']:.2f}%",
                "5° percentile"
            )
        
        with mc_col3:
            st.metric(
                "CVaR 95%",
                f"{mc_results['cvar_95']:.2f}%",
                "Expected shortfall"
            )
        
        with mc_col4:
            st.metric(
                "Tasso Knock-Out",
                f"{mc_results['knockout_rate']:.2f}%",
                f"{int(mc_results['knockout_rate'] * n_simulations / 100)} casi"
            )
        
        # Distribution chart
        fig_mc = create_monte_carlo_histogram(
            mc_results['performance'],
            mc_results['mean_performance'],
            mc_results['percentile_5'],
            mc_results['percentile_95']
        )
        st.plotly_chart(fig_mc, use_container_width=True)
        
        # Detailed statistics table
        with st.expander("📊 Statistiche Dettagliate Monte Carlo"):
            mc_summary = mc_simulator.get_summary_dataframe()
            st.dataframe(mc_summary, hide_index=True, use_container_width=True)
    
    # ============================================================================
    # OPTIMIZATION
    # ============================================================================
    
    st.markdown("---")
    st.header("🎯 Ottimizzazione Strategia")
    
    opt_tab1, opt_tab2, opt_tab3 = st.tabs([
        "🔍 Sensitivity Analysis",
        "🗺️ Grid Search",
        "⚡ Auto-Optimize"
    ])
    
    with opt_tab1:
        st.markdown("Analisi di sensibilità al variare del livello dell'indice:")
        
        sens_range = st.slider(
            "Range di variazione indice (%)",
            min_value=-50,
            max_value=50,
            value=(-30, 30),
            step=5
        )
        
        spot_min = valore_iniziale_indice * (1 + sens_range[0] / 100)
        spot_max = valore_iniziale_indice * (1 + sens_range[1] / 100)
        
        sensitivity_df = sensitivity_to_spot(
            params,
            (spot_min, spot_max),
            n_points=30
        )
        
        fig_sensitivity = create_sensitivity_chart(sensitivity_df)
        st.plotly_chart(fig_sensitivity, use_container_width=True)
    
    with opt_tab2:
        st.markdown("Esplora lo spazio dei parametri Strike e Scadenza:")
        
        optimizer = StrategyOptimizer(params)
        
        grid_col1, grid_col2 = st.columns(2)
        
        with grid_col1:
            strike_min_pct = st.number_input(
                "Strike Min (% sopra spot)",
                min_value=1,
                max_value=30,
                value=5,
                step=1
            )
            strike_max_pct = st.number_input(
                "Strike Max (% sopra spot)",
                min_value=5,
                max_value=50,
                value=20,
                step=1
            )
        
        with grid_col2:
            giorni_min = st.number_input("Giorni Min", 30, 180, 30, 10)
            giorni_max = st.number_input("Giorni Max", 60, 365, 180, 10)
        
        if st.button("🔍 Esegui Grid Search"):
            with st.spinner("Calcolo in corso..."):
                strike_range = (
                    valore_iniziale_indice * (1 + strike_min_pct / 100),
                    valore_iniziale_indice * (1 + strike_max_pct / 100)
                )
                
                grid_results = optimizer.grid_search_parameters(
                    strike_points=10,
                    giorni_points=6,
                    strike_range=strike_range,
                    giorni_range=(giorni_min, giorni_max),
                    target_scenario=valore_ipotetico_indice
                )
                
                # Heatmap
                fig_heatmap = create_heatmap_strike_maturity(grid_results, 'Hedge Ratio')
                st.plotly_chart(fig_heatmap, use_container_width=True)
                
                # Best configurations
                st.markdown("**Top 5 Configurazioni:**")
                top_5 = grid_results.nlargest(5, 'Hedge Ratio')[
                    ['Strike', 'Giorni', 'Leva', 'Capitale %', 'Hedge Ratio', 'Performance %']
                ]
                st.dataframe(top_5, hide_index=True, use_container_width=True)
    
    with opt_tab3:
        st.markdown("Trova automaticamente la configurazione ottimale:")
        
        opt_col1, opt_col2 = st.columns(2)
        
        with opt_col1:
            target_hedge_ratio = st.slider(
                "Target Hedge Ratio",
                min_value=0.80,
                max_value=1.0,
                value=0.95,
                step=0.01
            )
        
        with opt_col2:
            max_capital_pct = st.slider(
                "Max Capitale (%)",
                min_value=5,
                max_value=30,
                value=20,
                step=1
            )
        
        if st.button("⚡ Ottimizza Automaticamente"):
            with st.spinner("Ottimizzazione in corso..."):
                optimizer = StrategyOptimizer(params)
                optimal = optimizer.find_best_tradeoff(
                    target_scenario=valore_ipotetico_indice,
                    max_capital_pct=max_capital_pct,
                    min_hedge_ratio=target_hedge_ratio * 0.9  # Allow 10% tolerance
                )
                
                if optimal['success']:
                    st.success("✅ Configurazione ottimale trovata!")
                    
                    opt_res_col1, opt_res_col2, opt_res_col3 = st.columns(3)
                    
                    with opt_res_col1:
                        st.metric("Strike Ottimale", f"{optimal['recommended_strike']:,.2f}")
                        st.metric("Giorni Ottimali", f"{optimal['recommended_giorni']}")
                    
                    with opt_res_col2:
                        st.metric("Leva", f"{optimal['leverage']:.2f}x")
                        st.metric("Capitale %", f"{optimal['capitale_pct']:.2f}%")
                    
                    with opt_res_col3:
                        st.metric("Hedge Ratio", f"{optimal['hedge_ratio']:.2%}")
                        st.metric("Dist. Barriera", f"{optimal['distanza_barriera_pct']:+.2f}%")
                else:
                    st.error("❌ " + optimal['message'])
    
    # ============================================================================
    # EXPORT AND REPORT
    # ============================================================================
    
    st.markdown("---")
    st.header("📄 Esporta Risultati")
    
    export_col1, export_col2 = st.columns(2)
    
    with export_col1:
        # Create summary report
        report_data = {
            'Parametro': [
                'Data Analisi',
                'Strike',
                'Giorni a Scadenza',
                'Valore Portafoglio',
                'N° Turbo',
                'Capitale Investito',
                'Leva',
                'Hedge Ratio',
                'Performance Coperta',
            ],
            'Valore': [
                pd.Timestamp.now().strftime('%Y-%m-%d %H:%M'),
                f'{strike:,.2f}',
                f'{giorni}',
                f'€{valore_portafoglio:,.2f}',
                f'{results["n_turbo"]:.2f}',
                f'€{results["capitale_turbo"]:,.2f}',
                f'{results["leverage"]:.2f}x',
                f'{results["hedge_ratio"]:.2%}',
                f'{results["performance_totale"]*100:.2f}%',
            ]
        }
        report_df = pd.DataFrame(report_data)
        
        st.download_button(
            label="📥 Scarica Report Riepilogativo",
            data=report_df.to_csv(index=False),
            file_name="turbo_hedge_report.csv",
            mime="text/csv"
        )
    
    with export_col2:
        st.info("💡 **Tip**: Salva i risultati per confrontare diverse configurazioni nel tempo.")

else:
    # Show placeholder when not calculated
    st.info("👆 Inserisci i parametri e premi 'Calcola Copertura' per iniziare l'analisi.")
    
    st.markdown("###")
    st.markdown("### 🎯 Caratteristiche Principali")
    
    features_col1, features_col2, features_col3 = st.columns(3)
    
    with features_col1:
        st.markdown("""
        **📊 Core Analytics**
        - Fair Value pricing
        - Leva dinamica
        - Hedge ratio calculation
        - Beta adjustment
        - Premium decay
        """)
    
    with features_col2:
        st.markdown("""
        **📈 Advanced Features**
        - Greeks calculation
        - Monte Carlo simulation
        - Scenario analysis
        - Sensitivity testing
        - Stress testing
        """)
    
    with features_col3:
        st.markdown("""
        **🎯 Optimization**
        - Strike/Maturity grid search
        - Auto-optimization
        - Cost-benefit analysis
        - Risk metrics
        - Export capabilities
        """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9em;'>
    <strong>Turbo Hedge Calculator</strong> | Versione 1.0<br>
    Tool professionale per analisi di copertura con Certificati Turbo Short<br>
    ⚠️ <em>Questo tool è fornito a scopo educativo. Non costituisce consulenza finanziaria.</em>
</div>
""", unsafe_allow_html=True)
