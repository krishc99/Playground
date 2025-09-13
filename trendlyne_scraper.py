import pandas as pd
import re
import time
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from bs4 import BeautifulSoup

def get_stock_details_playwright(ticker: str) -> tuple:
    """
    Uses Playwright to search Trendlyne for a stock ticker to find its ID and slug.
    """
    print(f"--- Searching for details for ticker: {ticker} ---")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            # Set user agent to avoid detection
            page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })
            
            page.goto("https://trendlyne.com/", timeout=60000)
            
            # Wait for page to load completely
            page.wait_for_load_state('networkidle')
            
            # Try to find and interact with search box
            search_selectors = [
                "input[placeholder*='Search']",
                "input[placeholder*='Stock']",
                "input[type='search']",
                ".search-input",
                "#search",
                "[data-testid*='search']",
                ".search-box input",
                "input[class*='search']"
            ]
            
            search_box = None
            for selector in search_selectors:
                try:
                    search_box = page.locator(selector).first
                    if search_box.is_visible():
                        print(f"Found search box with selector: {selector}")
                        break
                except:
                    continue
            
            if not search_box:
                print("Could not find search box, trying alternative approach...")
                # Try clicking on search icon first
                search_icon_selectors = [
                    "[data-testid*='search']",
                    ".search-icon",
                    ".fa-search",
                    "[class*='search']"
                ]
                
                for icon_selector in search_icon_selectors:
                    try:
                        icon = page.locator(icon_selector).first
                        if icon.is_visible():
                            icon.click()
                            time.sleep(1)
                            # Try to find search box again after clicking
                            for selector in search_selectors:
                                try:
                                    search_box = page.locator(selector).first
                                    if search_box.is_visible():
                                        print(f"Found search box after clicking icon: {selector}")
                                        break
                                except:
                                    continue
                            if search_box:
                                break
                    except:
                        continue
                
                if not search_box:
                    print("Could not find search box with any method")
                    return None, None
            
            # Clear and fill search box
            search_box.clear()
            search_box.fill(ticker)
            search_box.press('Enter')
            
            # Wait for navigation and results
            page.wait_for_load_state('networkidle', timeout=30000)
            
            # Wait a bit more for dynamic content
            time.sleep(5)
            
            final_url = page.url
            print(f"Current URL after search: {final_url}")
            
            # Try multiple URL patterns that might match Trendlyne's structure
            patterns = [
                r'/equity/(\d+)/.+?/(.+?)/?$',
                r'/equity/(\d+)/(.+?)/?$',
                r'/(\d+)/.+?/(.+?)/?$',
                r'/(\d+)/(.+?)/?$'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, final_url)
                if match:
                    stock_id = match.group(1)
                    stock_slug = match.group(2)
                    print(f"Found stock ID: {stock_id}, slug: {stock_slug}")
                    return stock_id, stock_slug
            
            # If no pattern matches, try to extract from page content
            print("No URL pattern matched, trying to extract from page content...")
            
            # Look for stock ID in the page content
            content = page.content()
            
            # Try multiple patterns for stock ID and slug
            id_patterns = [
                r'stock_id["\']?\s*:\s*["\']?(\d+)',
                r'"id"\s*:\s*(\d+)',
                r'equity/(\d+)/',
                r'/(\d+)/'
            ]
            
            slug_patterns = [
                r'stock_slug["\']?\s*:\s*["\']?([^"\']+)',
                r'"slug"\s*:\s*"([^"]+)"',
                r'equity/\d+/.+?/([^/]+)/',
                r'/([^/]+)/?$'
            ]
            
            stock_id = None
            stock_slug = None
            
            for pattern in id_patterns:
                match = re.search(pattern, content)
                if match:
                    stock_id = match.group(1)
                    print(f"Found stock ID with pattern '{pattern}': {stock_id}")
                    break
            
            for pattern in slug_patterns:
                match = re.search(pattern, content)
                if match:
                    stock_slug = match.group(1)
                    print(f"Found stock slug with pattern '{pattern}': {stock_slug}")
                    break
            
            if stock_id and stock_slug:
                print(f"Extracted from content - ID: {stock_id}, slug: {stock_slug}")
                return stock_id, stock_slug
            
            # If still no match, try to find any link containing the ticker
            print("Trying to find links containing the ticker...")
            links = page.locator('a').all()
            for link in links:
                try:
                    href = link.get_attribute('href')
                    if href and ticker.upper() in href.upper():
                        print(f"Found link with ticker: {href}")
                        # Try to extract from this link
                        for pattern in patterns:
                            match = re.search(pattern, href)
                            if match:
                                stock_id = match.group(1)
                                stock_slug = match.group(2)
                                print(f"Extracted from link - ID: {stock_id}, slug: {stock_slug}")
                                return stock_id, stock_slug
                except:
                    continue
                
        except PlaywrightTimeoutError as e:
            print(f"Timeout error: {e}")
            page.screenshot(path=f"debug_playwright_{ticker}.png")
            print(f"A debug screenshot 'debug_playwright_{ticker}.png' has been saved.")
        except Exception as e:
            print(f"Error occurred: {e}")
            page.screenshot(path=f"debug_playwright_{ticker}.png")
            print(f"A debug screenshot 'debug_playwright_{ticker}.png' has been saved.")
        finally:
            browser.close()
            
    return None, None

def scrape_table_playwright(url: str) -> pd.DataFrame:
    """
    Uses Playwright and BeautifulSoup to scrape a table from a given URL.
    """
    print(f"\n--- Fetching data from: {url} ---")
    df = pd.DataFrame()
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            # Set user agent
            page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })
            
            page.goto(url, timeout=60000)
            page.wait_for_load_state('networkidle')
            
            # Wait a bit for dynamic content to load
            time.sleep(3)
            
            # Try multiple table selectors
            table_selectors = [
                "table.tl-dataTable",
                "table",
                ".data-table",
                ".table",
                "[class*='table']",
                "[class*='data']"
            ]
            
            table_found = False
            for selector in table_selectors:
                try:
                    page.wait_for_selector(selector, timeout=10000)
                    table_found = True
                    break
                except:
                    continue
            
            if not table_found:
                print("No table found with any of the selectors")
                page.screenshot(path="debug_no_table.png")
                return df
            
            html_content = page.content()
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find the table
            table = None
            for selector in table_selectors:
                table = soup.select_one(selector)
                if table:
                    break
            
            if table:
                try:
                    # Try pandas.read_html first
                    tables = pd.read_html(str(table))
                    if tables:
                        df = tables[0]
                        print(f"Successfully scraped table with {len(df)} rows")
                    else:
                        print("pandas.read_html returned empty list")
                except Exception as e:
                    print(f"pandas.read_html failed: {e}")
                    # Fallback to manual parsing
                    df = parse_table_manually(table)
            else:
                print("Error: Could not find the table.")
                
        except PlaywrightTimeoutError as e:
            print(f"Timeout error: {e}")
            page.screenshot(path="debug_playwright_scrape.png")
            print("A debug screenshot has been saved.")
        except Exception as e:
            print(f"Error occurred: {e}")
            page.screenshot(path="debug_playwright_scrape.png")
            print("A debug screenshot has been saved.")
        finally:
            browser.close()
            
    return df

def parse_table_manually(table):
    """
    Manually parse table when pandas.read_html fails
    """
    df = pd.DataFrame()
    
    try:
        rows = table.find_all('tr')
        if not rows:
            return df
            
        # Extract headers
        headers = []
        header_row = rows[0]
        for th in header_row.find_all(['th', 'td']):
            headers.append(th.get_text(strip=True))
        
        # Extract data rows
        data = []
        for row in rows[1:]:
            row_data = []
            for cell in row.find_all(['td', 'th']):
                row_data.append(cell.get_text(strip=True))
            if row_data:
                data.append(row_data)
        
        if headers and data:
            df = pd.DataFrame(data, columns=headers)
            print(f"Manually parsed table with {len(df)} rows")
        
    except Exception as e:
        print(f"Manual parsing failed: {e}")
    
    return df

# --- Main execution block ---
if __name__ == "__main__":
    stock_ticker = "TCS"
    
    print("Starting Trendlyne scraper...")
    print("=" * 50)
    
    stock_id, stock_slug = get_stock_details_playwright(stock_ticker)
    
    if stock_id and stock_slug:
        print(f"\n✅ Found stock details:")
        print(f"   ID: {stock_id}")
        print(f"   Slug: {stock_slug}")
        
        # Construct URLs
        insider_trading_url = f"https://trendlyne.com/equity/insider-trading-sast/all/{stock_ticker}/{stock_id}/{stock_slug}/"
        bulk_deals_url = f"https://trendlyne.com/equity/bulk-block-deals/{stock_ticker}/{stock_id}/{stock_slug}/"
        
        print(f"\n📊 Scraping insider trading data...")
        insider_df = scrape_table_playwright(insider_trading_url)
        
        print(f"\n📊 Scraping bulk deals data...")
        bulk_deals_df = scrape_table_playwright(bulk_deals_url)
        
        print("\n" + "=" * 50)
        print("✅ Scraping Complete!")
        print("=" * 50)
        
        # Display results
        if not insider_df.empty:
            print(f"\n📈 Insider Trading Data ({len(insider_df)} rows):")
            print(insider_df.head())
        else:
            print("\n❌ No insider trading data found")
            
        if not bulk_deals_df.empty:
            print(f"\n📈 Bulk Deals Data ({len(bulk_deals_df)} rows):")
            print(bulk_deals_df.head())
        else:
            print("\n❌ No bulk deals data found")
        
        # Combine data if both are available
        if not insider_df.empty and not bulk_deals_df.empty:
            combined_df = pd.concat([insider_df, bulk_deals_df], ignore_index=True)
            print(f"\n📊 Combined Data ({len(combined_df)} total rows):")
            print(combined_df.head(10))
        elif not insider_df.empty:
            print(f"\n📊 Using only insider trading data ({len(insider_df)} rows)")
        elif not bulk_deals_df.empty:
            print(f"\n📊 Using only bulk deals data ({len(bulk_deals_df)} rows)")
            
    else:
        print(f"\n❌ Could not find details for {stock_ticker}")
        print("This could be due to:")
        print("1. The ticker symbol not existing on Trendlyne")
        print("2. The website structure has changed")
        print("3. Anti-bot measures are blocking the request")
        print("4. Network connectivity issues")