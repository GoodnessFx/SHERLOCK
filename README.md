

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)
![LangGraph](https://img.shields.io/badge/Orchestration-LangGraph-green.svg)
![Anthropic](https://img.shields.io/badge/Reasoning-Claude_3.5_Sonnet-orange.svg)
![Polymarket](https://img.shields.io/badge/Markets-Polymarket_CLOB-purple.svg)

**SHERLOCK** is a multi-agent AI for predicting markets by identifying exploitable edges 24/7. 

Built on the LangGraph framework and powered by Claude 3.5 Sonnet, it combines real-time signal processing with a persistent KAIROS memory system to learn and improve from every market it watches.

---

##  What is this?
SHERLOCK is not just a bot; it's a swarm of specialized agents working in concert to find high-probability outcomes on Polymarket.
- **Multi-Agent Orchestration:** Uses LangGraph to route tasks between research, probability, and execution agents, now incorporating advanced Bayesian updating and market-making strategies.
- **KAIROS Memory:** Persistent local vector store (ChromaDB) that stores every signal, prediction, and outcome to improve over time.
- **Advanced Signal Processing:** Integrates real-time data for weather, crypto, news, on-chain activity, and now includes sophisticated spread analysis, Sentiment AI, and Volatility Monitoring.
- **6 Layers of Prediction Math:**
    1. **Bayesian Updating:** Claude 3.5 Sonnet acts as a Bayesian reasoner, using market price as a prior.
    2. **Expected Value Filtering:** Trades are filtered for net profit after fees and slippage.
    3. **Spread Analysis:** Detects discrepancies between related markets and platforms.
    4. **Market-Making Execution:** Sophisticated order management (Layer 4 setup).
    5. **Sentiment AI:** Real-time social media and news sentiment scanning.
    6. **Calendar + Volatility:** Exploits price spikes 15-20 minutes before events.
- **24/7 Daemon:** Runs continuously in a background loop, monitoring markets every 15 minutes.
- **Stunning 3D Dashboard:** A "Dark Terminal Luxury" dashboard built with Three.js that broadcasts live activity, confidence scores, and discovered edges.
- **Zero-Fee Open Source:** Fully open source, one-click deployable, and designed to run on free-tier infrastructure.

---

##  How it Works
SHERLOCK follows a structured agentic workflow for every market it analyzes, now enhanced with a multi-layered approach to identify and exploit market inefficiencies:

```ascii
[ DAEMON ] -> [ ORCHESTRATOR ]
                   |
        +----------+----------+
        |                     |
[ RESEARCH AGENT ]   [ MEMORY AGENT ]
(Signals: Weather,   (Recall similar
 Crypto, News,       past events from
 On-chain,           ChromaDB)
 Spread Analysis)
        |                     |
        +----------+----------+
                   |
        [ PROBABILITY AGENT ]
        (Claude 3.5 Sonnet
         Bayesian Updating &
         Probability Scoring)
                   |
        [ EXECUTION AGENT ]
        (Expected Value Filtering,
         Kelly Criterion &
         Market-Making Execution)
                   |
        [ BROADCAST / STORE ]
        (WS to Dashboard &
         SQLite Logger)
```

---

## 🚀 Quick Start (3 Commands)

1. **Clone the repo**
   ```bash
   git clone https://github.com/yourusername/SHERLOCK.git
   cd SHERLOCK
   ```

2. **Install dependencies**
   ```bash
   make install
   ```

3. **Configure & Run**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   make daemon
   ```

---

## 🌐 Dashboard
The dashboard is a single-file static HTML page that connects to the SHERLOCK API via WebSockets. It features:
- **Three.js Wireframe Globe:** Real-time 3D visualization of the agent's "consciousness."
- **Live Terminal Feed:** Scrolling logs of every agent action and signal found.
- **Edge Cards:** High-confidence trade recommendations with Kelly sizing.
- **Track Record:** Verified accuracy stats and simulated P&L.

---
## How to Make Money
SHERLOCK finds edges—the difference between the agent's estimated probability and the current market price.
1. **Find an Edge:** Monitor the "LIVE EDGES" panel on your dashboard.
2. **Review Reasoning:** Read the agent's logic for why it thinks the market is mispriced.
3. **Execute:** If you agree, place the trade on Polymarket using the suggested Kelly fraction.
*Note: This is not financial advice. Prediction markets involve risk.*

---


