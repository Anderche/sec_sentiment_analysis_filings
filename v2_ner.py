import spacy
import matplotlib.pyplot as plt
from collections import Counter
from typing import List, Dict
from main import get_company_cik, get_recent_filings
import logging
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from urllib.parse import urljoin
import time

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

class EdgarParser:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Host': 'www.sec.gov'
        }
        self.request_delay = 0.1

    def get_filing_htm_url(self, directory_url: str, ticker: str) -> str:
        """Find the specific filing HTM link that matches the ticker symbol."""
        try:
            time.sleep(self.request_delay)
            response = requests.get(directory_url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the table with headers
            tables = soup.find_all('table')
            for table in tables:
                headers = table.find_all('th')
                if headers and 'Name' in [h.get_text(strip=True) for h in headers]:
                    # Search for filing link in this table
                    for row in table.find_all('tr'):
                        cells = row.find_all('td')
                        if cells:
                            name_cell = cells[0]
                            link = name_cell.find('a')
                            if link and link.get('href'):
                                href = link.get('href')
                                # Check if link starts with ticker and ends with .htm
                                if href.lower().startswith(ticker.lower()) and href.endswith('.htm'):
                                    return urljoin(directory_url, href)
            
            raise ValueError("No matching HTM file found in directory")
            
        except requests.RequestException as e:
            raise Exception(f"Error accessing SEC EDGAR: {str(e)}")

    def get_table_of_contents(self, filing_url: str) -> str:
        """Extract and return the table of contents from the filing."""
        try:
            time.sleep(self.request_delay)
            response = requests.get(filing_url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for table of contents section
            toc = soup.find('div', string=re.compile(r'TABLE OF CONTENTS', re.I))
            if toc:
                # Get the next table or list element
                content = toc.find_next(['table', 'ul'])
                if content:
                    return content.get_text(separator='\n', strip=True)
            
            return "Table of contents not found"
            
        except requests.RequestException as e:
            raise Exception(f"Error accessing filing: {str(e)}")

    # [Include all EdgarParser methods as in your provided code]
    # ... [get_filing_htm_url, parse_filing, _extract_company_name, etc.]

def process_text(text: str) -> List[str]:
    """Process text and extract named entities."""
    doc = nlp(text)
    entities = [ent.text for ent in doc.ents if ent.label_ not in ['CARDINAL', 'QUANTITY', 'PERCENT']]
    return entities

def analyze_entities(text: str) -> Dict[str, int]:
    """Analyze entities in the text."""
    if isinstance(text, str):
        entities = process_text(text)
        return Counter(entities)
    return Counter()

def plot_top_entities(entity_counts: Dict[str, int], filing_info: dict, ticker: str, n: int = 30):
    """Create histogram of top n most frequent entities."""
    # [Keep the existing plot_top_entities implementation]
    pass

def main():
    # Initialize parser
    parser = EdgarParser()
    
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
    
    # Display filings with URLs
    print("\nRecent filings:")
    for idx, filing in enumerate(filings, 1):
        print(f"{idx}. {filing['form']} filed on {filing['date']}")
        print(f"   URL: {filing['detail_url']}")
    
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
    
    try:
        # Get the directory URL from the selected filing
        directory_url = selected_filing['detail_url']
        
        # Get the HTM filing URL using ticker symbol
        print("\nLocating HTML filing...")
        filing_url = parser.get_filing_htm_url(directory_url, ticker)
        print(f"Found HTM filing: {filing_url}")
        
        # Get and print table of contents
        print("\nExtracting Table of Contents...")
        toc = parser.get_table_of_contents(filing_url)
        print("\nTABLE OF CONTENTS:")
        print(toc)
        print("\n" + "="*50 + "\n")
        
        # Parse the filing
        print("Parsing filing content...")
        filing_data = parser.parse_filing(filing_url)
        
        # Combine all text content for analysis
        text = ' '.join(filing_data['text_content'])
        
        # Analyze entities
        print("\nAnalyzing named entities...")
        entity_counts = analyze_entities(text)
        
        # Plot results
        save_plot = input("\nWould you like to save the entity histogram? (y/n): ").lower().strip()
        if save_plot in ['y', 'yes']:
            plot_top_entities(entity_counts, selected_filing, ticker)
        
        # Print top entities and their counts
        print("\nTop 30 most frequent entities:")
        for entity, count in sorted(entity_counts.items(), key=lambda x: x[1], reverse=True)[:30]:
            print(f"{entity}: {count}")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 