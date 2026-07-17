from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Dict, Iterable, Tuple

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf


st.set_page_config(
    page_title="Brazil Energy Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

ASSETS: Dict[str, str] = {
    "Neoenergia": "NEOE3.SA",
    "Eletrobras": "ELET3.SA",
    "ENGIE Brasil": "EGIE3.SA",
    "CPFL Energia": "CPFE3.SA",
    "Equatorial": "EQTL3.SA",
    "Cemig": "CMIG4.SA",
    "Copel": "CPLE6.SA",
    "ISA Energia": "ISAE4.SA",
    "Taesa": "TAEE11.SA",
    "Petrobras": "PETR4.SA",
    "Ibovespa": "^BVSP",
}

BENCHMARK = "Ibovespa"
TRADING_DAYS = 252
RISK_FREE_RATE = 0.105  # illustrative annual rate; editable in sidebar


CUSTOM_CSS = """
<style>
    :root {
        --bg: #081018;
        --panel: #101a24;
        --panel-2: #152230;
        --text: #edf4f7;
        --muted: #91a3b0;
        --accent: #4de3a8;
        --line: rgba(255,255,255,.09);
    }
    .stApp { background: var(--bg); color: var(--text); }
    [data-testid="stSidebar"] { background: #0b151f; border-right: 1px solid var(--line); }
    [data-testid="stMetric"] {
        background: linear-gradient(145deg, var(--panel), var(--panel-2));
        border: 1px solid var(--line);
        padding: 16px 18px;
        border-radius: 14px;
        min-height: 116px;
    }
    [data-testid="stMetricLabel"] { color: var(--muted); }
    [data-testid="stMetricValue"] { font-weight: 700; letter-spacing: -0.03em; }
    .hero {
        padding: 26px 28px;
        border-radius: 18px;
        background:
            radial-gradient(circle at 90% 20%, rgba(77,227,168,.17), transparent 26%),
            linear-gradient(135deg, #111f2d 0%, #0a141e 70%);
        border: 1px solid var(--line);
        margin-bottom: 18px;
    }
    .eyebrow {
        color: var(--accent);
        text-transform: uppercase;
        font-size: .76rem;
        font-weight: 700;
        letter-spacing: .18em;
    }
    .hero h1 {
        margin: 8px 0 6px 0;
        font-size: clamp(2rem, 5vw, 3.3rem);
        line-height: 1.02;
        letter-spacing: -.055em;
    }
    .hero p { color: var(--muted); margin: 0; max-width: 820px; font-size: 1rem; }
    .section-label {
        margin-top: 24px;
        margin-bottom: 8px;
        font-size: .78rem;
        color: var(--accent);
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: .15em;
    }
    .insight {
        background: var(--panel);
        border-left: 3px solid var(--accent);
        border-top: 1px solid var(--line);
        border-right: 1px solid var(--line);
        border-bottom: 1px solid var(--line);
        padding: 14px 16px;
        border-radius: 0 12px 12px 0;
        margin-bottom: 10px;
        color: var(--text);
    }
    .fine-print { color: var(--muted); font-size: .76rem; }
    .block-container { padding-top: 1.7rem; padding-bottom: 3rem; max-width: 1500px; }
    hr { border-color: var(--line); }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


@dataclass(frozen=True)
class Period:
    label: str
    value: str


PERIODS = [
    Period("1 mês", "1mo"),
    Period("3 meses", "3mo"),
    Period("6 meses", "6mo"),
    Period("1 ano", "1y"),
    Period("2 anos", "2y"),
    Period("5 anos", "5y"),
]


def clean_prices(raw: pd.DataFrame, ticker_map: Dict[str, str]) -> pd.DataFrame:
    """Extract adjusted close/close and rename tickers to company names."""
    if raw.empty:
        return pd.DataFrame()

    if isinstance(raw.columns, pd.MultiIndex):
        first_level = raw.columns.get_level_values(0)
        if "Close" in first_level:
            prices = raw["Close"].copy()
        elif "Adj Close" in first_level:
            prices = raw["Adj Close"].copy()
        else:
            prices = raw.xs(raw.columns.levels[0][0], axis=1, level=0).copy()
    else:
        close_col = "Close" if "Close" in raw.columns else "Adj Close"
        prices = raw[[close_col]].copy()
        prices.columns = [next(iter(ticker_map.values()))]

    reverse_map = {ticker: name for name, ticker in ticker_map.items()}
    prices = prices.rename(columns=reverse_map)
    prices = prices.loc[:, [c for c in ticker_map if c in prices.columns]]
    prices = prices.dropna(axis=1, how="all").ffill().dropna(how="all")
    return prices


@st.cache_data(ttl=3600, show_spinner=False)
def load_market_data(ticker_items: Tuple[Tuple[str, str], ...], period: str) -> pd.DataFrame:
    ticker_map = dict(ticker_items)
    raw = yf.download(
        tickers=list(ticker_map.values()),
        period=period,
        interval="1d",
        auto_adjust=True,
        progress=False,
        group_by="column",
        threads=True,
    )
    return clean_prices(raw, ticker_map)


def make_demo_data(names: Iterable[str], period: str) -> pd.DataFrame:
    periods = {"1mo": 23, "3mo": 66, "6mo": 126, "1y": 252, "2y": 504, "5y": 1260}
    n = periods.get(period, 252)
    dates = pd.bdate_range(end=pd.Timestamp.today().normalize(), periods=n)
    rng = np.random.default_rng(42)
    data = {}
    for idx, name in enumerate(names):
        drift = 0.00015 + idx * 0.000015
        vol = 0.009 + (idx % 4) * 0.0015
        returns = rng.normal(drift, vol, n)
        data[name] = 100 * np.exp(np.cumsum(returns))
    return pd.DataFrame(data, index=dates)


def total_return(series: pd.Series) -> float:
    series = series.dropna()
    if len(series) < 2:
        return np.nan
    return series.iloc[-1] / series.iloc[0] - 1


def max_drawdown(series: pd.Series) -> float:
    series = series.dropna()
    if series.empty:
        return np.nan
    drawdown = series / series.cummax() - 1
    return drawdown.min()


def metrics_table(prices: pd.DataFrame, risk_free_rate: float) -> pd.DataFrame:
    returns = prices.pct_change(fill_method=None)
    rows = []
    for company in prices.columns:
        s = prices[company].dropna()
        r = returns[company].dropna()
        annual_return = r.mean() * TRADING_DAYS
        annual_vol = r.std() * np.sqrt(TRADING_DAYS)
        sharpe = (annual_return - risk_free_rate) / annual_vol if annual_vol > 0 else np.nan
        momentum_30d = s.iloc[-1] / s.iloc[-min(30, len(s))] - 1 if len(s) > 1 else np.nan
        rows.append(
            {
                "Empresa": company,
                "Retorno": total_return(s),
                "Volatilidade": annual_vol,
                "Sharpe": sharpe,
                "Drawdown": max_drawdown(s),
                "Momentum 30d": momentum_30d,
            }
        )

    table = pd.DataFrame(rows).set_index("Empresa")
    score_inputs = pd.DataFrame(index=table.index)
    score_inputs["Retorno"] = percentile_score(table["Retorno"], higher_is_better=True)
    score_inputs["Volatilidade"] = percentile_score(table["Volatilidade"], higher_is_better=False)
    score_inputs["Drawdown"] = percentile_score(table["Drawdown"], higher_is_better=True)
    score_inputs["Momentum"] = percentile_score(table["Momentum 30d"], higher_is_better=True)
    table["Score"] = (
        0.40 * score_inputs["Retorno"]
        + 0.25 * score_inputs["Volatilidade"]
        + 0.20 * score_inputs["Drawdown"]
        + 0.15 * score_inputs["Momentum"]
    ).round(0)
    return table.sort_values("Score", ascending=False)


def percentile_score(series: pd.Series, higher_is_better: bool = True) -> pd.Series:
    # For favorable high values, ascending=True gives the maximum a score of 100.
    # For favorable low values, ascending=False gives the minimum a score of 100.
    ranks = series.rank(pct=True, ascending=higher_is_better)
    return (ranks * 100).clip(0, 100)


def normalized_prices(prices: pd.DataFrame) -> pd.DataFrame:
    return prices.divide(prices.iloc[0]).multiply(100)


def pct(value: float, digits: int = 1) -> str:
    if pd.isna(value):
        return "—"
    return f"{value * 100:.{digits}f}%"


def number(value: float, digits: int = 2) -> str:
    if pd.isna(value):
        return "—"
    return f"{value:.{digits}f}"


def executive_insights(table: pd.DataFrame, benchmark: str) -> list[str]:
    universe = table.drop(index=benchmark, errors="ignore")
    if universe.empty:
        return ["Não há dados suficientes para gerar insights."]

    best = universe["Score"].idxmax()
    best_score = universe.loc[best, "Score"]
    highest_return = universe["Retorno"].idxmax()
    highest_vol = universe["Volatilidade"].idxmax()
    lowest_dd = universe["Drawdown"].idxmax()

    insights = [
        f"{best} lidera o score composto ({best_score:.0f}/100), combinando retorno, risco, drawdown e momentum.",
        f"{highest_return} apresenta o maior retorno acumulado no período selecionado ({pct(universe.loc[highest_return, 'Retorno'])}).",
        f"{highest_vol} registra a maior volatilidade anualizada ({pct(universe.loc[highest_vol, 'Volatilidade'])}), indicando maior oscilação de preço.",
        f"{lowest_dd} possui o drawdown mais controlado do grupo ({pct(universe.loc[lowest_dd, 'Drawdown'])}).",
    ]

    if benchmark in table.index:
        benchmark_return = table.loc[benchmark, "Retorno"]
        outperformers = universe.index[universe["Retorno"] > benchmark_return].tolist()
        insights.append(
            f"{len(outperformers)} de {len(universe)} empresas superaram o Ibovespa no período."
        )
    return insights


def style_plot(fig: go.Figure, height: int = 430) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=48, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#dce8ed"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        hovermode="x unified",
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="rgba(255,255,255,.08)", zeroline=False)
    return fig


# Sidebar
st.sidebar.markdown("## ⚡ Brazil Energy")
period_label = st.sidebar.selectbox("Período", [p.label for p in PERIODS], index=3)
period = next(p.value for p in PERIODS if p.label == period_label)
selected_companies = st.sidebar.multiselect(
    "Empresas",
    [name for name in ASSETS if name != BENCHMARK],
    default=[name for name in ASSETS if name != BENCHMARK],
)
risk_free_rate = st.sidebar.number_input(
    "Taxa livre de risco anual (%)",
    min_value=0.0,
    max_value=30.0,
    value=RISK_FREE_RATE * 100,
    step=0.5,
) / 100
demo_mode = st.sidebar.toggle("Usar dados demonstrativos", value=False)
st.sidebar.caption("Dados de mercado via Yahoo Finance. Projeto educacional; não constitui recomendação de investimento.")

selection = selected_companies + [BENCHMARK]
ticker_map = {name: ASSETS[name] for name in selection}

with st.spinner("Carregando dados de mercado..."):
    if demo_mode:
        prices = make_demo_data(selection, period)
    else:
        try:
            prices = load_market_data(tuple(ticker_map.items()), period)
        except Exception:
            prices = pd.DataFrame()

if prices.empty or len(prices.columns) < 2:
    st.warning(
        "Não foi possível obter dados suficientes agora. O painel foi alternado para dados demonstrativos."
    )
    prices = make_demo_data(selection, period)
    demo_mode = True

available = [name for name in selection if name in prices.columns]
prices = prices[available].dropna(how="all").ffill()

if len(prices) < 2:
    st.error("Dados insuficientes para calcular os indicadores.")
    st.stop()

table = metrics_table(prices, risk_free_rate)
universe = table.drop(index=BENCHMARK, errors="ignore")

st.markdown(
    """
    <div class="hero">
        <div class="eyebrow">Business Performance · B3 · Utilities</div>
        <h1>Brazil Energy Intelligence</h1>
        <p>Monitoramento executivo de performance, risco e posicionamento relativo de companhias brasileiras de energia e infraestrutura.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if demo_mode:
    st.info("Modo demonstrativo ativo. Os valores abaixo são sintéticos e servem apenas para validar a interface.")

# KPI row
best_company = universe["Score"].idxmax()
sector_return = universe["Retorno"].mean()
benchmark_return = table.loc[BENCHMARK, "Retorno"] if BENCHMARK in table.index else np.nan
sector_vol = universe["Volatilidade"].mean()
outperformers = int((universe["Retorno"] > benchmark_return).sum()) if not pd.isna(benchmark_return) else 0

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Líder do score", best_company, f"{universe.loc[best_company, 'Score']:.0f}/100")
k2.metric("Retorno médio do setor", pct(sector_return), pct(sector_return - benchmark_return))
k3.metric("Ibovespa", pct(benchmark_return), "benchmark")
k4.metric("Volatilidade média", pct(sector_vol), "anualizada")
k5.metric("Acima do benchmark", f"{outperformers}/{len(universe)}", "empresas")

tabs = st.tabs(["Visão geral", "Performance", "Ranking", "Risco", "Metodologia"])

with tabs[0]:
    st.markdown('<div class="section-label">Visão executiva</div>', unsafe_allow_html=True)
    left, right = st.columns([1.75, 1])

    with left:
        norm = normalized_prices(prices)
        fig = px.line(
            norm,
            x=norm.index,
            y=norm.columns,
            title="Performance normalizada · base 100",
            labels={"value": "Índice", "index": "Data", "variable": "Ativo"},
        )
        fig.add_hline(y=100, line_dash="dot", opacity=0.35)
        st.plotly_chart(style_plot(fig), use_container_width=True)

    with right:
        st.markdown("#### Executive insights")
        for insight in executive_insights(table, BENCHMARK):
            st.markdown(f'<div class="insight">{insight}</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-label">Top performers</div>', unsafe_allow_html=True)
    top = universe.head(5).reset_index()
    bar = px.bar(
        top.sort_values("Score"),
        x="Score",
        y="Empresa",
        orientation="h",
        text="Score",
        title="Score composto de performance",
        range_x=[0, 100],
    )
    bar.update_traces(texttemplate="%{text:.0f}", textposition="outside")
    st.plotly_chart(style_plot(bar, height=350), use_container_width=True)

with tabs[1]:
    st.markdown('<div class="section-label">Retorno e benchmark</div>', unsafe_allow_html=True)
    norm = normalized_prices(prices)
    fig = px.line(
        norm,
        x=norm.index,
        y=norm.columns,
        labels={"value": "Índice base 100", "index": "Data", "variable": "Ativo"},
    )
    st.plotly_chart(style_plot(fig, 500), use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        return_chart = (
            table["Retorno"]
            .sort_values()
            .rename("Retorno")
            .reset_index()
        )
        fig_return = px.bar(
            return_chart,
            x="Retorno",
            y="Empresa",
            orientation="h",
            title="Retorno acumulado",
            text="Retorno",
        )
        fig_return.update_traces(texttemplate="%{text:.1%}", textposition="outside")
        fig_return.update_xaxes(tickformat=".0%")
        st.plotly_chart(style_plot(fig_return), use_container_width=True)

    with c2:
        momentum_chart = (
            table["Momentum 30d"]
            .sort_values()
            .rename("Momentum 30d")
            .reset_index()
        )
        fig_momentum = px.bar(
            momentum_chart,
            x="Momentum 30d",
            y="Empresa",
            orientation="h",
            title="Momentum dos últimos 30 pregões",
            text="Momentum 30d",
        )
        fig_momentum.update_traces(texttemplate="%{text:.1%}", textposition="outside")
        fig_momentum.update_xaxes(tickformat=".0%")
        st.plotly_chart(style_plot(fig_momentum), use_container_width=True)

with tabs[2]:
    st.markdown('<div class="section-label">Ranking consolidado</div>', unsafe_allow_html=True)
    display = table.copy()
    for col in ["Retorno", "Volatilidade", "Drawdown", "Momentum 30d"]:
        display[col] = display[col].map(lambda x: pct(x))
    display["Sharpe"] = display["Sharpe"].map(lambda x: number(x))
    display["Score"] = display["Score"].map(lambda x: f"{x:.0f}")
    st.dataframe(
        display,
        use_container_width=True,
        height=455,
    )
    st.caption("Score = 40% retorno + 25% volatilidade + 20% drawdown + 15% momentum. Cada componente é normalizado por ranking percentil.")

with tabs[3]:
    st.markdown('<div class="section-label">Monitor de risco</div>', unsafe_allow_html=True)
    daily_returns = prices.pct_change(fill_method=None).dropna(how="all")
    corr = daily_returns.corr()

    c1, c2 = st.columns([1.25, 1])
    with c1:
        heatmap = px.imshow(
            corr,
            text_auto=".2f",
            aspect="auto",
            zmin=-1,
            zmax=1,
            title="Correlação dos retornos diários",
        )
        st.plotly_chart(style_plot(heatmap, 540), use_container_width=True)

    with c2:
        risk = table[["Volatilidade", "Drawdown"]].copy().reset_index()
        scatter = px.scatter(
            risk,
            x="Volatilidade",
            y="Drawdown",
            text="Empresa",
            size=np.clip(table["Score"].values, 10, None),
            title="Mapa risco × drawdown",
            labels={"Volatilidade": "Volatilidade anualizada", "Drawdown": "Maximum drawdown"},
        )
        scatter.update_traces(textposition="top center")
        scatter.update_xaxes(tickformat=".0%")
        scatter.update_yaxes(tickformat=".0%")
        st.plotly_chart(style_plot(scatter, 540), use_container_width=True)

with tabs[4]:
    st.markdown('<div class="section-label">Metodologia e limitações</div>', unsafe_allow_html=True)
    st.markdown(
        """
        **Objetivo.** Demonstrar um fluxo de Business Intelligence que transforma séries temporais financeiras em indicadores comparáveis e insights executivos.

        **Indicadores.**
        - Retorno acumulado no período selecionado.
        - Volatilidade anualizada com 252 pregões.
        - Sharpe simplificado com taxa livre de risco configurável.
        - Maximum drawdown.
        - Momentum aproximado dos últimos 30 pregões.
        - Score composto normalizado por ranking percentil.

        **Fonte.** Cotações obtidas por `yfinance`, biblioteca não oficial que consulta dados públicos do Yahoo Finance.

        **Limitações.** O painel não incorpora fundamentos contábeis, dividendos projetados, custos de transação ou avaliação de valor justo. O conteúdo é educacional e não representa recomendação de investimento.
        """
    )

st.divider()
last_date = prices.index.max()
last_date_text = pd.Timestamp(last_date).strftime("%d/%m/%Y")
st.markdown(
    f'<div class="fine-print">Atualização dos dados: {last_date_text} · Desenvolvido com Python, pandas, Plotly e Streamlit.</div>',
    unsafe_allow_html=True,
)
