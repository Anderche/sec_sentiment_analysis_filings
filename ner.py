import spacy
import matplotlib.pyplot as plt
from collections import Counter
from typing import List, Dict
from main import get_company_cik, get_recent_filings, get_filing_text
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

def process_text(text: str) -> List[str]:
    """Process text and extract named entities."""
    doc = nlp(text)
    # Extract named entities (excluding numbers and quantities)
    entities = [ent.text for ent in doc.ents if ent.label_ not in ['CARDINAL', 'QUANTITY', 'PERCENT']]
    return entities

def analyze_entities(text: str) -> Dict[str, int]:
    """Analyze entities in the text."""
    if isinstance(text, str):
        entities = process_text(text)
        # Count entity frequencies
        entity_counts = Counter(entities)
        return entity_counts
    return Counter()

def plot_top_entities(entity_counts: Dict[str, int], filing_info: dict, ticker: str, n: int = 30):
    """Create histogram of top n most frequent entities."""
    # Get top n entities
    top_entities = dict(sorted(entity_counts.items(), key=lambda x: x[1], reverse=True)[:n])
    
    plt.figure(figsize=(15, 8))
    plt.bar(range(len(top_entities)), list(top_entities.values()))
    plt.xticks(range(len(top_entities)), list(top_entities.keys()), rotation=45, ha='right')
    
    # Update title to use filing info detail URL and ticker
    filing_url = filing_info.get('detail_url', 'N/A')
    plt.title(f'Top {n} Most Frequent Named Entities for {ticker.upper()}\n{filing_info["form"]} filed on {filing_info["date"]}\nSource: {filing_url}')
    
    plt.xlabel('Entity')
    plt.ylabel('Frequency')
    plt.tight_layout()
    
    # Generate timestamp and default filename with ticker
    timestamp = datetime.now().strftime("%d%b%Y")
    default_filename = f"ner_plot_{ticker.upper()}_{filing_info['form']}_{timestamp}.png"
    
    # Save plot with more descriptive filename by default
    plt.savefig(default_filename, bbox_inches='tight', dpi=300)
    print(f"\nPlot saved as: {default_filename}")
    
    plt.close()

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
    
    # Get filing text
    print(f"\nFetching {selected_filing['form']} filing from {selected_filing['date']}...")
    text = get_filing_text(cik, selected_filing['accession'])
    
    if not text:
        print("Could not retrieve filing text")
        return
    
    # Analyze entities
    print("\nAnalyzing named entities...")
    entity_counts = analyze_entities(text)
    
    # Plot results
    save_plot = input("\nWould you like to save the entity histogram? (y/n): ").lower().strip()
    if save_plot in ['y', 'yes']:
        plot_top_entities(entity_counts, selected_filing, ticker)
        print("\nEntity histogram has been saved as 'entity_histogram.png'")
    # Print top entities and their counts
    print("\nTop 30 most frequent entities:")
    for entity, count in sorted(entity_counts.items(), key=lambda x: x[1], reverse=True)[:30]:
        print(f"{entity}: {count}")

if __name__ == "__main__":
    main() 