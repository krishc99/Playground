# Trendlyne Stock Data Scraper

A Python web scraper that extracts stock data from Trendlyne.com using Playwright for browser automation.

## Features

- 🔍 **Stock Search**: Automatically searches for stock tickers on Trendlyne
- 📊 **Data Extraction**: Scrapes insider trading and bulk deals data
- 🤖 **Browser Automation**: Uses Playwright for reliable web scraping
- 🛡️ **Anti-Detection**: Includes user agent spoofing and proper wait times
- 📈 **Data Processing**: Returns clean pandas DataFrames

## Installation

1. **Install Python dependencies:**
   ```bash
   pip3 install --break-system-packages -r requirements.txt
   ```

2. **Install Playwright browsers:**
   ```bash
   python3 -m playwright install chromium
   ```

3. **Test the installation:**
   ```bash
   python3 test_scraper.py
   ```

## Usage

### Basic Usage

```python
from trendlyne_scraper import get_stock_details_playwright, scrape_table_playwright

# Search for a stock
stock_id, stock_slug = get_stock_details_playwright("TCS")

if stock_id and stock_slug:
    # Scrape insider trading data
    insider_url = f"https://trendlyne.com/equity/insider-trading-sast/all/TCS/{stock_id}/{stock_slug}/"
    insider_df = scrape_table_playwright(insider_url)
    
    # Scrape bulk deals data
    bulk_url = f"https://trendlyne.com/equity/bulk-block-deals/TCS/{stock_id}/{stock_slug}/"
    bulk_df = scrape_table_playwright(bulk_url)
```

### Run the Complete Scraper

```bash
python3 trendlyne_scraper.py
```

## Configuration

You can modify the following in the script:

- **Stock Ticker**: Change `stock_ticker = "TCS"` to any valid ticker
- **Timeouts**: Adjust timeout values for different network conditions
- **User Agent**: Modify the user agent string for different browser simulation

## Troubleshooting

### Common Issues

1. **"Could not find search box"**
   - The website structure may have changed
   - Try running the script again (sometimes it's a temporary issue)
   - Check if Trendlyne is accessible in your browser

2. **"No table found"**
   - The stock might not have insider trading or bulk deals data
   - The page structure may have changed
   - Check the debug screenshots for visual inspection

3. **Timeout errors**
   - Increase timeout values in the script
   - Check your internet connection
   - The website might be slow or under maintenance

### Debug Features

The scraper automatically saves debug screenshots when errors occur:
- `debug_playwright_{ticker}.png` - When stock search fails
- `debug_playwright_scrape.png` - When table scraping fails
- `debug_no_table.png` - When no table is found

## File Structure

```
trendlyne_scraper.py    # Main scraper script
test_scraper.py         # Installation test script
requirements.txt        # Python dependencies
README.md              # This file
```

## Dependencies

- **pandas**: Data manipulation and analysis
- **playwright**: Browser automation
- **beautifulsoup4**: HTML parsing
- **lxml**: XML/HTML parser

## Legal Notice

This scraper is for educational and research purposes only. Please ensure you comply with Trendlyne's terms of service and robots.txt file. Consider using official APIs when available.

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is open source and available under the MIT License.