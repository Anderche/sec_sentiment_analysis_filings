# SEC Filing Sentiment Analyzer

A Python script that performs sentiment analysis on SEC 10-K and 10-Q filings using FinBERT. Enter a stock ticker to analyze the sentiment of recent financial reports.

## Overview

This tool automates the process of analyzing sentiment in SEC filings by:
- Converting stock tickers to SEC CIK numbers
- Fetching recent 10-K and 10-Q filings from EDGAR
- Extracting and cleaning filing text
- Performing sentiment analysis using FinBERT
- Displaying sentiment scores as percentages

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

## Requirements

- Python 3.9 or higher
- ~4GB RAM recommended
- Internet connection
- ~1GB storage for models

## Limitations

- Subject to SEC EDGAR rate limits
- Processing time varies with filing size
- Limited to 10-K and 10-Q filings
- Requires proper SEC API headers

The tool provides detailed logging for troubleshooting and handles various edge cases like invalid tickers, missing filings, and network errors. 