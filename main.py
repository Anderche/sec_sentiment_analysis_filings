import requests
import json
from datetime import datetime
from transformers import pipeline
import time
import logging
import re
from bs4 import BeautifulSoup

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_company_cik(ticker):
    """Get CIK number for a company ticker."""
    ticker = ticker.upper()
    headers = {
        'User-Agent': 'Sample Company Name AdminContact@company.com'
    }
    
    response = requests.get(
        "https://www.sec.gov/files/company_tickers.json",
        headers=headers
    )
    companies = response.json()
    
    for entry in companies.values():
        if entry['ticker'] == ticker:
            return str(entry['cik_str']).zfill(10)
    return None

def get_recent_filings(cik):
    """Get the 10 most recent 10-X filings for a company."""
    headers = {
        'User-Agent': 'Sample Company Name AdminContact@company.com'
    }
    
    # Use the SEC's submissions API endpoint
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            logger.error(f"Failed to fetch filings. Status code: {response.status_code}")
            return []
        
        logger.info(f"Submissions URL: {url}")
        
        data = response.json()
        filings = []
        
        recent_forms = data['filings']['recent']['form']
        recent_dates = data['filings']['recent']['filingDate']
        recent_accessions = data['filings']['recent']['accessionNumber']
        
        # Get current date for validation
        current_date = datetime.now().date()
        
        # Zip the data together and filter for 10-K and 10-Q
        for form, date_str, accession in zip(recent_forms, recent_dates, recent_accessions):
            # Convert date string to datetime for comparison
            filing_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            # Skip future dates
            if filing_date > current_date:
                continue
                
            if form in ['10-K', '10-Q']:
                filings.append({
                    'form': form,
                    'date': date_str,
                    'accession': accession.replace('-', ''),
                    'detail_url': f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession.replace('-', '')}"
                })
                
                if len(filings) >= 10:
                    break
        
        return filings
        
    except Exception as e:
        logger.error(f"Error fetching filings: {str(e)}")
        logger.exception(e)  # This will log the full traceback
        return []

def get_filing_text(cik, accession):
    """Get the text content of a filing."""
    headers = {
        'User-Agent': 'Sample Company Name AdminContact@company.com'
    }
    
    time.sleep(0.1)  # SEC rate limit compliance
    
    # First get the filing detail page to find the actual document URL
    detail_url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession}/index.json"
    
    try:
        response = requests.get(detail_url, headers=headers)
        if response.status_code != 200:
            logger.error(f"Failed to fetch filing index. Status code: {response.status_code}")
            return ""
            
        filing_data = response.json()
        
        # Find the main document (usually ends with .htm)
        main_doc = None
        for file in filing_data['directory']['item']:
            if file['name'].endswith('.htm'):
                main_doc = file['name']
                break
                
        if not main_doc:
            logger.error("Could not find main document in filing")
            return ""
            
        # Get the actual document
        doc_url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession}/{main_doc}"
        response = requests.get(doc_url, headers=headers)
        
        if response.status_code != 200:
            logger.error(f"Failed to fetch document. Status code: {response.status_code}")
            return ""
            
        # Parse HTML and extract text
        soup = BeautifulSoup(response.content, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)
        return text
            
    except Exception as e:
        logger.error(f"Failed to fetch filing: {str(e)}")
        return ""

def analyze_sentiment(text):
    """Perform sentiment analysis on text using HuggingFace model."""
    sentiment_analyzer = pipeline(
        "sentiment-analysis",
        model="ProsusAI/finbert"
    )
    
    # Break text into chunks due to model token limits
    chunk_size = 512
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    
    results = []
    for chunk in chunks:
        if chunk.strip():
            result = sentiment_analyzer(chunk)
            results.append(result[0])
    
    # Aggregate results
    sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
    for result in results:
        sentiment_counts[result['label']] += 1
    
    total = sum(sentiment_counts.values())
    if total == 0:
        return {'positive': 0, 'negative': 0, 'neutral': 0}
    return {k: round(v/total * 100, 2) for k, v in sentiment_counts.items()}

def main():
    # Get ticker from user
    ticker = input("Enter stock symbol (e.g., AAPL): ").strip()
    
    # Get CIK
    cik = get_company_cik(ticker)
    if not cik:
        print(f"Could not find CIK for ticker {ticker}")
        return
        
    # Get recent filings
    print(f"\nFetching recent filings for {ticker}...")
    filings = get_recent_filings(cik)
    
    if not filings:
        print("No recent 10-X filings found")
        return
    
    # Display filings
    print("\nRecent filings:")
    for idx, filing in enumerate(filings, 1):
        print(f"{idx}. {filing['form']} filed on {filing['date']}")
    
    # Get user selection
    while True:
        try:
            selection = int(input("\nSelect filing number to analyze (1-10): "))
            if 1 <= selection <= len(filings):
                break
            print("Invalid selection. Please try again.")
        except ValueError:
            print("Please enter a valid number.")
    
    selected_filing = filings[selection-1]
    
    # Get filing text
    print(f"\nFetching {selected_filing['form']} filing from {selected_filing['date']}...")
    text = get_filing_text(cik, selected_filing['accession'])
    
    if not text:
        print("Could not retrieve filing text")
        return
        
    # Display first 500 characters
    print("\nFirst 500 characters of the filing:")
    print(text[:500])
    print("\n" + "="*50 + "\n")
    
    # Perform sentiment analysis
    print("\nPerforming sentiment analysis...")
    sentiment_results = analyze_sentiment(text)
    
    # Display results
    print("\nSentiment Analysis Results:")
    print(f"Positive: {sentiment_results['positive']}%")
    print(f"Neutral: {sentiment_results['neutral']}%")
    print(f"Negative: {sentiment_results['negative']}%")

if __name__ == "__main__":
    main()


    