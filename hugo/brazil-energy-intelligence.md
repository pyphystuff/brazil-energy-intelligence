---
title: "Brazil Energy Intelligence"
date: 2026-07-17
draft: false
description: "Executive dashboard for monitoring performance and risk across Brazilian energy and infrastructure companies."
tags: ["Python", "Streamlit", "Business Intelligence", "B3", "Energy"]
categories: ["Data Analytics"]
featured: true
---

## Overview

Brazil Energy Intelligence is an executive dashboard developed to transform financial time-series data into business-oriented performance indicators.

The application monitors a selected group of Brazilian energy and infrastructure companies and compares their results with the Ibovespa benchmark.

## Business problem

Executives and analysts need to identify:

- which companies outperform the market;
- where volatility and downside risk are concentrated;
- which assets show positive or negative momentum;
- how performance changes across different time horizons.

The dashboard consolidates these questions into a single analytical interface.

## Main features

- Executive KPI summary
- Performance normalized to a common base
- Company ranking through a composite score
- Benchmark comparison
- Volatility and maximum-drawdown analysis
- Correlation matrix
- Automated executive insights

## Technology

`Python` · `pandas` · `NumPy` · `Plotly` · `Streamlit` · `yfinance`

## Methodology

The composite score combines return, volatility, drawdown and momentum. Each variable is normalized through percentile ranking to make the indicators comparable.

## Project links

- **Live dashboard:** ADD_STREAMLIT_URL
- **Source code:** ADD_GITHUB_URL

> This project is educational and does not constitute investment advice.
