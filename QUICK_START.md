# 🚀 QUICK START - Deploy su Streamlit Cloud in 5 Minuti

## Prerequisito
- ✅ Account GitHub (gratuito)

---

## STEP 1: Carica su GitHub (2 minuti)

### Opzione A: GitHub Desktop (CONSIGLIATA - Più Facile)

1. **Scarica GitHub Desktop** (se non ce l'hai):
   - Vai su https://desktop.github.com
   - Scarica e installa

2. **Apri GitHub Desktop**

3. **File** → **Add Local Repository**

4. Clicca **Browse** e seleziona la cartella `turbo-hedge-streamlit`

5. GitHub Desktop dirà "This directory does not appear to be a Git repository"
   - Clicca **"Create a Repository"**

6. Compila:
   - **Name:** `turbo-hedge-calculator`
   - **Local path:** (già compilato)
   - ✅ Spunta "Initialize this repository with a README"
   - Clicca **"Create Repository"**

7. Clicca **"Publish repository"** (pulsante blu in alto)

8. Scegli:
   - **Name:** `turbo-hedge-calculator`
   - ⭕ Public (raccomandato)
   - oppure ⚫ Private (funziona ugualmente)
   - Clicca **"Publish Repository"**

✅ **FATTO!** Il tuo codice è su GitHub!

---

### Opzione B: Da Terminale (Alternativa)

```bash
cd turbo-hedge-streamlit
git init
git add .
git commit -m "Initial commit - Turbo Hedge Calculator"
git branch -M main

# Vai su github.com/new e crea repository "turbo-hedge-calculator"
# Poi esegui:
git remote add origin https://github.com/TUO_USERNAME/turbo-hedge-calculator.git
git push -u origin main
```

---

## STEP 2: Deploy su Streamlit Cloud (3 minuti)

### 2.1 Accedi a Streamlit Cloud

1. Vai su **https://share.streamlit.io**

2. Clicca **"Sign in with GitHub"**

3. Autorizza Streamlit ad accedere ai tuoi repository GitHub

---

### 2.2 Crea Nuova App

1. Nel Dashboard di Streamlit, clicca **"New app"** (grande pulsante blu)

2. Compila il form:

   | Campo | Valore |
   |-------|--------|
   | **Repository** | `TUO_USERNAME/turbo-hedge-calculator` |
   | **Branch** | `main` |
   | **Main file path** | `app.py` |

3. **Advanced settings** (opzionale):
   - Python version: 3.11 (default va bene)
   - App URL: puoi personalizzare (es. `my-turbo-calc`)

4. Clicca **"Deploy!"**

---

### 2.3 Attendi Deploy

- Vedrai i log di installazione in tempo reale
- **Fase 1:** Cloning repository (~10 sec)
- **Fase 2:** Installing requirements (~60 sec)
  - streamlit
  - numpy
  - pandas
  - plotly
  - scipy
- **Fase 3:** Starting app (~30 sec)

**Tempo totale: 2-3 minuti**

Quando vedi **"Your app is live!"** 🎉 → App pronta!

---

## STEP 3: Accedi all'App

**URL:** `https://TUO-NOME-APP.streamlit.app`

Esempio: `https://turbo-hedge-calculator.streamlit.app`

---

## ✅ Verifica Funzionamento

1. **App si carica** → Vedi titolo "📊 Turbo Hedge Calculator"
2. **Sidebar funziona** → Vedi menu laterale blu
3. **Input compilati** → Valori di default presenti
4. **Clicca "🚀 Calcola Copertura"**
5. **Vedi risultati** → Metriche, grafici, tabelle

Se tutto funziona → **Deploy completato con successo!** ✅

---

## 🔄 Aggiornamenti Futuri

### Per modificare l'app:

**Con GitHub Desktop:**
1. Modifica i file localmente
2. GitHub Desktop mostrerà i cambiamenti
3. Scrivi descrizione commit (es. "Aggiunto feature X")
4. Clicca **"Commit to main"**
5. Clicca **"Push origin"**

**Streamlit Cloud farà auto-deploy in 1-2 minuti!**

---

## 🆘 Problemi Comuni

### ❌ "Repository not found"
**Soluzione:** 
- Verifica che il repository sia pubblico
- Oppure vai su Streamlit Cloud → Settings → Reconnect GitHub

### ❌ "Module not found: utils"
**Soluzione:**
- Verifica che cartelle `utils/` e `components/` siano su GitHub
- In GitHub Desktop: assicurati di aver fatto "Commit" e "Push"

### ❌ App lenta al primo accesso
**Normale:** 
- Cold start richiede 30-60 secondi
- Dopo il primo accesso sarà veloce
- Se nessuno usa l'app per 7 giorni, si addormenta di nuovo

### ❌ "Error: requirements.txt not found"
**Soluzione:**
- Verifica che `requirements.txt` sia nella root del repository
- NON deve essere dentro una sottocartella

---

## 🎯 Tips & Tricks

### Riavviare l'App
Streamlit Cloud → Menu ⋮ (in alto a destra) → **"Reboot app"**

### Vedere i Log
Streamlit Cloud → Menu ⋮ → **"View logs"**

### Condividere l'App
Invia semplicemente l'URL: `https://tuo-nome-app.streamlit.app`
Non serve autenticazione, l'app è pubblica!

### Custom Domain (opzionale, $25/mese)
Streamlit Cloud → Settings → Custom domain

---

## 📊 Cosa Include l'App

✅ **Pricing Turbo Short** completo
✅ **Beta adjustment** per portafoglio
✅ **7 correzioni** vs Excel originale
✅ **Scenario analysis** 13 scenari
✅ **Grafici interattivi** Plotly
✅ **Monte Carlo** 10k simulazioni
✅ **Ottimizzazione** automatica
✅ **Export CSV** risultati

**Tutto il modello matematico è identico alla versione locale.**
**Zero compromessi, zero perdite di funzionalità.**

---

## 🎉 Completato!

Hai deployato con successo una web app professionale per l'hedging di portafogli!

**Cosa puoi fare ora:**
- ✅ Condividi l'URL con colleghi/clienti
- ✅ Usa l'app da qualsiasi dispositivo (anche mobile)
- ✅ Modifica il codice e fai push → auto-deploy
- ✅ Zero manutenzione, hosting gratuito permanente

---

## 📞 Serve Aiuto?

- 📖 Leggi **README.md** per dettagli completi
- 📖 Leggi **NOTA_METODOLOGICA.pdf** per la matematica
- 🐛 Apri issue su GitHub per problemi

---

<div align="center">

**🎊 Congratulazioni! La tua app è LIVE! 🎊**

</div>
