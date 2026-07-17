# Brazil Energy Intelligence

Executive dashboard for monitoring the market performance, risk and relative positioning of Brazilian energy and infrastructure companies listed on B3.

## Business objective

The project demonstrates how financial time-series data can be transformed into decision-oriented indicators through a reproducible Business Intelligence workflow.

It focuses on:

- performance monitoring;
- benchmark comparison;
- risk assessment;
- comparative company analysis;
- automated executive insights.

## Features

- Executive KPI cards
- Normalized performance against Ibovespa
- Composite company ranking
- Return, volatility, Sharpe ratio and drawdown
- 30-session momentum
- Correlation heatmap
- Risk-versus-drawdown map
- Automated business insights
- Real-data and demonstration modes

## Companies

The initial universe includes Neoenergia, Eletrobras, ENGIE Brasil, CPFL Energia, Equatorial, Cemig, Copel, ISA Energia, Taesa and Petrobras, with Ibovespa as benchmark.

## Technology

- Python
- pandas
- NumPy
- Plotly
- Streamlit
- yfinance

## Run locally

```bash
git clone <YOUR-REPOSITORY-URL>
cd brazil-energy-intelligence

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

On Windows:

```powershell
.venv\Scripts\activate
```

## Deploy on Streamlit Community Cloud

1. Push this folder to a public GitHub repository.
2. Open Streamlit Community Cloud.
3. Select the repository and branch.
4. Set the main file path to `app.py`.
5. Deploy.

## Methodology

The dashboard calculates:

- cumulative return;
- annualized volatility based on 252 trading sessions;
- simplified Sharpe ratio;
- maximum drawdown;
- approximate 30-session momentum;
- a normalized composite score.

The composite score uses:

- 40% return;
- 25% volatility;
- 20% drawdown;
- 15% momentum.

Each component is converted to a percentile ranking before aggregation.

## Data disclaimer

Market data is retrieved through `yfinance`, an open-source library that accesses Yahoo Finance public data. This application is an educational portfolio project and does not constitute investment advice.

## Portfolio narrative

> Developed an executive intelligence dashboard to monitor the performance of Brazilian energy and infrastructure companies. Built a reproducible Python pipeline, comparative KPIs, benchmark analysis, automated rankings and decision-oriented visualizations.
