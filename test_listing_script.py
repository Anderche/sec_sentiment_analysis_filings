from main import get_company_cik, get_recent_filings

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
    
    # Display first 5 filings with all dictionary keys/values
    print("\nDetailed view of first 5 filings:")
    for idx, filing in enumerate(filings[:5], 1):
        print(f"\nFiling #{idx}:")
        for key, value in filing.items():
            print(f"{key}: {value}")
        print("-" * 50)

if __name__ == "__main__":
    main()