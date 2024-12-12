# SEC Filing Sentiment Analyzer

The script helps fintech firms by automating sentiment analysis of SEC filings (10-K/10-Q) using FinBERT, a finance-specific language model. It converts unstructured filing text into quantifiable sentiment scores (positive/negative/neutral percentages), enabling firms to:

1. Track sentiment trends across quarters/years
2. Compare sentiment between companies
3. Flag significant sentiment changes for further analysis
4. Make data-driven investment decisions


## Overview

This tool automates the process of analyzing sentiment in SEC filings by:
- Converting stock tickers to SEC CIK numbers
- Fetching recent 10-K and 10-Q filings from EDGAR
- Extracting and cleaning filing text
- Performing sentiment analysis using FinBERT
- Displaying sentiment scores as percentages

## Named Entity Recognition

The NER (Named Entity Recognition) processing includes all entity types that spaCy recognizes (like PERSON, ORG, GPE, DATE, etc.) except for three specific types that are explicitly excluded:

- CARDINAL (numbers)
- QUANTITY (measurements)
- PERCENT (percentage values)

This filtering happens in the `process_text()` function through the condition `if ent.label_ not in ['CARDINAL', 'QUANTITY', 'PERCENT']`.

## Setup Instructions

1. Create a new conda environment:
   - Open terminal/command prompt
   - Run: conda create -n sec_sentiment_analysis python=3.9
   - Activate: conda activate sec_sentiment_analysis

2. Install required packages:
   - requests: for API calls
   - transformers: for FinBERT model
   - torch: for model inference
   - beautifulsoup4: for HTML parsing
   - lxml: for XML processing

   Install all with: pip install requests transformers torch beautifulsoup4 lxml

## Usage

Simply run main.py and follow the prompts:
1. Enter a stock ticker (e.g., AAPL)
2. Choose from the list of recent filings
3. View the sentiment analysis results

## Technical Details

The script processes filings through several steps:
1. Retrieves company CIK from SEC's company tickers endpoint
2. Fetches filing list using SEC's submissions API
3. Downloads and parses HTML content from EDGAR
4. Chunks text for processing through FinBERT
5. Aggregates sentiment scores across chunks




