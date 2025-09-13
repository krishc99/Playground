#!/usr/bin/env python3
"""
Example usage of the Trendlyne scraper
"""

from trendlyne_scraper import get_stock_details_playwright, scrape_table_playwright
import pandas as pd

def scrape_stock_data(ticker):
    """
    Scrape data for a specific stock ticker
    """
    print(f"🔍 Searching for {ticker}...")
    
    # Get stock details
    stock_id, stock_slug = get_stock_details_playwright(ticker)
    
    if not stock_id or not stock_slug:
        print(f"❌ Could not find details for {ticker}")
        return None, None, None
    
    print(f"✅ Found {ticker}: ID={stock_id}, Slug={stock_slug}")
    
    # Construct URLs
    insider_url = f"https://trendlyne.com/equity/insider-trading-sast/all/{ticker}/{stock_id}/{stock_slug}/"
    bulk_url = f"https://trendlyne.com/equity/bulk-block-deals/{ticker}/{stock_id}/{stock_slug}/"
    
    # Scrape data
    print(f"📊 Scraping insider trading data...")
    insider_df = scrape_table_playwright(insider_url)
    
    print(f"📊 Scraping bulk deals data...")
    bulk_df = scrape_table_playwright(bulk_url)
    
    return insider_df, bulk_df, stock_id

def main():
    """
    Main function demonstrating usage
    """
    # List of stocks to scrape
    stocks = ["TCS", "RELIANCE", "HDFC", "INFY"]
    
    all_data = {}
    
    for ticker in stocks:
        print(f"\n{'='*50}")
        print(f"Processing {ticker}")
        print(f"{'='*50}")
        
        insider_df, bulk_df, stock_id = scrape_stock_data(ticker)
        
        if stock_id:
            all_data[ticker] = {
                'insider': insider_df,
                'bulk': bulk_df,
                'stock_id': stock_id
            }
            
            # Display results
            if not insider_df.empty:
                print(f"\n📈 Insider Trading Data for {ticker} ({len(insider_df)} rows):")
                print(insider_df.head())
            else:
                print(f"\n❌ No insider trading data for {ticker}")
            
            if not bulk_df.empty:
                print(f"\n📈 Bulk Deals Data for {ticker} ({len(bulk_df)} rows):")
                print(bulk_df.head())
            else:
                print(f"\n❌ No bulk deals data for {ticker}")
        else:
            print(f"\n❌ Skipping {ticker} - could not find details")
    
    # Summary
    print(f"\n{'='*50}")
    print("📊 SCRAPING SUMMARY")
    print(f"{'='*50}")
    
    successful = len(all_data)
    total = len(stocks)
    
    print(f"Successfully scraped: {successful}/{total} stocks")
    
    for ticker, data in all_data.items():
        insider_rows = len(data['insider']) if not data['insider'].empty else 0
        bulk_rows = len(data['bulk']) if not data['bulk'].empty else 0
        print(f"  {ticker}: {insider_rows} insider trades, {bulk_rows} bulk deals")
    
    # Save data to CSV files
    print(f"\n💾 Saving data to CSV files...")
    
    for ticker, data in all_data.items():
        if not data['insider'].empty:
            filename = f"{ticker}_insider_trading.csv"
            data['insider'].to_csv(filename, index=False)
            print(f"  Saved {filename}")
        
        if not data['bulk'].empty:
            filename = f"{ticker}_bulk_deals.csv"
            data['bulk'].to_csv(filename, index=False)
            print(f"  Saved {filename}")

if __name__ == "__main__":
    main()