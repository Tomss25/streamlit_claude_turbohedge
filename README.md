# 📊 Turbo Hedge Calculator

**Strumento professionale per la copertura di portafogli con Certificati Turbo Short**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)
[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)

---

## 🚀 Deploy in 5 Minuti su Streamlit Cloud

### STEP 1: Carica su GitHub (2 min)

**Opzione A: Con GitHub Desktop (FACILE)**
1. Apri **GitHub Desktop**
2. **File** → **Add Local Repository** → Seleziona questa cartella
3. Clicca **"Create Repository"** (se richiesto)
4. Nome: `turbo-hedge-calculator`
5. Clicca **"Publish repository"** → Scegli Public/Private
6. ✅ Fatto!

**Opzione B: Da Terminale**
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/TUO_USERNAME/turbo-hedge-calculator.git
git push -u origin main
```

### STEP 2: Deploy su Streamlit Cloud (3 min)

1. Vai su **https://share.streamlit.io**
2. **Sign in with GitHub**
3. Clicca **"New app"**
4. Compila:
   - **Repository:** `turbo-hedge-calculator`
   - **Branch:** `main`
   - **Main file:** `app.py`
5. Clicca **"Deploy!"**
6. ⏱️ Attendi 2-3 minuti

✅ **App live!** URL: `https://turbo-hedge-calculator.streamlit.app`

---

## 💻 Test Locale

```bash
pip install -r requirements.txt
streamlit run app.py
```

Apri `http://localhost:8501`

---

## 🎯 Funzionalità Implementate

### Core (Sempre Attive)
- ✅ **Pricing Turbo Short:** Fair Value, Premio dinamico, Barriera, Leva
- ✅ **Beta Adjustment:** Portafoglio con sensibilità personalizzata
- ✅ **Dimensionamento:** Calcolo certificati ottimale
- ✅ **Scenario Analysis:** 13 scenari + stress test
- ✅ **Grafici Dinamici:** Evoluzione temporale, barriera, premium decay
- ✅ **Export CSV:** Risultati e scenari

### Advanced (Opzionali in Sidebar)
- ✅ **Costi Transazione:** Bid-ask spread, commissioni, tasse
- ✅ **Dividend Yield:** Adjustment Fair Value
- ✅ **Greeks:** Delta, Gamma, Vega, Theta, Rho, Prob K.O.
- ✅ **Monte Carlo:** 10k simulazioni, VaR 95%, CVaR, distribuzione
- ✅ **Ottimizzazione:** Sensitivity, Grid Search, Auto-optimize

---

## 📊 Validazione vs Excel

**Match 100%:** 11/11 metriche identiche

| Metrica | Excel | Web App | ✓ |
|---------|-------|---------|---|
| Fair Value | 7.2628 | 7.2628 | ✅ |
| Barriera | 7482.06 | 7482.06 | ✅ |
| Leva | 7.59 | 7.59 | ✅ |
| Performance | -0.32% | -0.32% | ✅ |
| **Tutte le altre** | ✓ | ✓ | ✅ |

---

## 🔄 Aggiornamenti Auto-Deploy

Ogni push su GitHub → deploy automatico in 1-2 minuti:

```bash
git add .
git commit -m "Update feature X"
git push origin main
```

Streamlit Cloud rileva il push e rideploya automaticamente.

---

## 📁 Struttura Progetto

```
turbo-hedge-calculator/
├── app.py (700+ righe)          # Applicazione Streamlit
├── requirements.txt              # Dipendenze (5 pacchetti)
├── README.md                     # Questa guida
├── .streamlit/config.toml       # Tema e configurazione
├── .gitignore                    # File da ignorare
│
├── utils/ (1,163 righe)         # Moduli di calcolo
│   ├── calculations.py           # Core + 7 correzioni
│   ├── greeks.py                # Greeks opzionali
│   ├── monte_carlo.py           # Simulazioni probabilistiche
│   └── optimization.py          # Ottimizzazione parametri
│
├── components/                   # UI components
│   ├── charts.py                # 10+ grafici Plotly
│   └── scenarios.py             # Tabelle scenario analysis
│
└── assets/
    └── style.css                # CSS professionale
```

**Totale:** ~1,900 righe di codice Python

---

## 🎨 Design & UX

- 📱 **Responsive:** Funziona su mobile, tablet, desktop
- 🎨 **Tema Professionale:** Navy blue sidebar, contrasto alto
- 📊 **Grafici Interattivi:** Plotly con zoom e hover
- ⚡ **Performance:** Calcoli istantanei, Monte Carlo ~10s

---

## 🆘 Troubleshooting

### App non si avvia
**Problema:** Errore durante deploy
**Soluzione:** Verifica che `app.py` e `requirements.txt` siano nel repository

### Errore "Module not found"
**Problema:** Mancano file `utils/` o `components/`
**Soluzione:** Verifica che le cartelle siano presenti su GitHub

### Modifiche non visibili
**Problema:** App mostra versione vecchia
**Soluzione:** 
1. Streamlit Cloud → Menu ⋮ → **Reboot app**
2. Oppure attendi 1-2 minuti per auto-deploy

### App lenta
**Problema:** Primo caricamento lento
**Normale:** Cold start richiede 30-60 sec. Poi veloce.

---

## ⚙️ Configurazione Avanzata

### Secrets (per API keys future)
```toml
# Streamlit Cloud → Settings → Secrets
[secrets]
api_key = "your-api-key"
```

### Custom Domain (Piano Team $25/mese)
Streamlit Cloud → Settings → Custom domain

### Resource Limits Piano Free
- ✅ **1 GB RAM** (sufficiente per questa app)
- ✅ **1 CPU core**
- ✅ **Sleeping:** Si addormenta dopo inattività, risveglio in 30-60s
- ✅ **Bandwidth illimitato**

---

## 📖 Documentazione Completa

File inclusi nel progetto:
- **README.md** - Questa guida
- **NOTA_METODOLOGICA.pdf** - Matematica completa (18 pagine)
- **QUICK_START.md** - Setup rapidissimo
- **DELIVERABLE_SUMMARY.md** - Overview progetto

---

## 📊 Metriche Progetto

- **1,900+ righe** di codice Python
- **7 correzioni** matematiche implementate
- **11/11 validazione** vs Excel originale
- **10+ grafici** Plotly interattivi
- **3 modalità** di ottimizzazione
- **10,000** simulazioni Monte Carlo
- **13 scenari** + 5 stress test

---

## ⚠️ Disclaimer

**Questo tool è fornito a scopo esclusivamente educativo e informativo.**

❌ Non costituisce consulenza finanziaria, fiscale o legale
❌ I risultati sono basati su modelli matematici semplificati
❌ I mercati reali comportano rischi aggiuntivi non modellati
⚠️ I certificati Turbo comportano **rischio di perdita totale** del capitale

✅ Consultare sempre un professionista qualificato prima di implementare strategie di hedging

---

## 🤝 Contributi

Contributi benvenuti! Per favore:
1. Fork il progetto
2. Crea branch (`git checkout -b feature/AmazingFeature`)
3. Commit (`git commit -m 'Add AmazingFeature'`)
4. Push (`git push origin feature/AmazingFeature`)
5. Apri Pull Request

---

## 📄 Licenza

**MIT License** - Uso libero con attribuzione

---

## 📞 Supporto

- 🐛 **Bug Report:** Apri issue su GitHub
- 💡 **Feature Request:** Issue con label "enhancement"
- 📧 **Contatto:** [Il tuo contatto]

---

## 🙏 Credits

- **Streamlit** - Framework applicazione
- **Plotly** - Grafici interattivi
- **NumPy/SciPy** - Calcoli scientifici
- **Pandas** - Data manipulation

---

<div align="center">

**⭐ Se trovi utile questo progetto, lascia una stella su GitHub! ⭐**

**Made with ❤️ for professional portfolio hedging**

[🚀 Deploy Now](https://share.streamlit.io) | [📖 Streamlit Docs](https://docs.streamlit.io/)

</div>
