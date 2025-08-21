#!/usr/bin/env python3
"""
Debug script to analyze Google Patents HTML structure
"""

import requests
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
import re
import json

def debug_google_patents_scraping(query: str):
    """Debug the Google Patents scraping process"""
    
    # Emulate real browser behavior
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Cache-Control': 'max-age=0'
    }
    
    search_url = f"https://patents.google.com/?q={quote_plus(query)}"
    print(f"🌐 Fetching: {search_url}")
    
    session = requests.Session()
    response = session.get(search_url, headers=headers, timeout=30)
    
    print(f"📄 Status: {response.status_code}")
    print(f"📄 Response size: {len(response.text)} characters")
    print(f"📄 Content-Type: {response.headers.get('content-type', 'unknown')}")
    
    # Save HTML to file for analysis
    with open('patent_data/debug_google_patents.html', 'w', encoding='utf-8') as f:
        f.write(response.text)
    print("💾 Saved HTML to patent_data/debug_google_patents.html")
    
    # Analyze the content
    html_content = response.text
    
    print("\n🔍 ANALYZING HTML STRUCTURE:")
    print("=" * 50)
    
    # Look for common patterns
    patterns_to_check = [
        (r'href="(/patent/[^"]+)"', "Patent links"),
        (r'<title[^>]*>([^<]+)</title>', "Page title"),
        (r'window\.__data__\s*=\s*({.*?});', "Window data"),
        (r'AF_initDataCallback\(({.*?})\)', "Google JS callbacks"),
        (r'"results":\s*(\[.*?\])', "Results arrays"),
        (r'<script[^>]*>.*?window\.jsl.*?</script>', "JSL scripts"),
        (r'<div[^>]*data-[^>]*patent[^>]*>', "Patent divs"),
        (r'<article[^>]*>', "Article elements"),
        (r'<section[^>]*>', "Section elements")
    ]
    
    for pattern, description in patterns_to_check:
        matches = re.findall(pattern, html_content, re.IGNORECASE | re.DOTALL)
        print(f"📊 {description}: {len(matches)} matches")
        if matches and len(matches) <= 5:
            for i, match in enumerate(matches[:3]):
                preview = str(match)[:100] + "..." if len(str(match)) > 100 else str(match)
                print(f"   {i+1}. {preview}")
    
    # Try BeautifulSoup parsing
    print(f"\n🥄 BEAUTIFULSOUP ANALYSIS:")
    print("=" * 50)
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Look for various selectors
    selectors_to_check = [
        ('a[href*="/patent/"]', "Patent links"),
        ('div[data-patent]', "Patent divs"),
        ('article', "Article elements"),
        ('.result', "Result elements"),
        ('.patent', "Patent elements"),
        ('h1, h2, h3, h4, h5', "Headings"),
        ('script', "Script tags"),
        ('[data-result]', "Data result attributes"),
        ('.search-result', "Search result classes")
    ]
    
    for selector, description in selectors_to_check:
        elements = soup.select(selector)
        print(f"📊 {description} ({selector}): {len(elements)} found")
        if elements and len(elements) <= 3:
            for i, elem in enumerate(elements[:2]):
                text_preview = elem.get_text(strip=True)[:100] + "..." if len(elem.get_text(strip=True)) > 100 else elem.get_text(strip=True)
                print(f"   {i+1}. {text_preview}")
    
    # Check for JavaScript-rendered content indicators
    print(f"\n🔬 JAVASCRIPT ANALYSIS:")
    print("=" * 50)
    
    js_indicators = [
        ("React", "React framework"),
        ("Angular", "Angular framework"),
        ("Vue", "Vue framework"),
        ("__NEXT_DATA__", "Next.js data"),
        ("window.__INITIAL_STATE__", "Initial state"),
        ("dynamically loaded", "Dynamic loading"),
        ("client-side", "Client-side rendering"),
        ("noscript", "No-script tags")
    ]
    
    for indicator, description in js_indicators:
        if indicator.lower() in html_content.lower():
            print(f"✅ Found: {description}")
        else:
            print(f"❌ Not found: {description}")
    
    # Look for specific Google Patents patterns
    print(f"\n🎯 GOOGLE PATENTS SPECIFIC PATTERNS:")
    print("=" * 50)
    
    google_patterns = [
        (r'patents\.google\.com', "Google Patents domain"),
        (r'patent/[A-Z0-9]+', "Patent identifiers"),
        (r'publicationNumber', "Publication numbers"),
        (r'assignee', "Assignee information"),
        (r'inventor', "Inventor information"),
        (r'abstract', "Abstract content"),
        (r'title.*patent', "Patent titles"),
        (r'Prior art', "Prior art sections")
    ]
    
    for pattern, description in google_patterns:
        matches = re.findall(pattern, html_content, re.IGNORECASE)
        print(f"📊 {description}: {len(matches)} matches")
    
    # Try to find the actual search results container
    print(f"\n🔍 SEARCHING FOR RESULTS CONTAINER:")
    print("=" * 50)
    
    # Common result container patterns
    result_containers = soup.find_all(['div', 'section', 'article'], 
                                    attrs={'class': re.compile(r'result|search|patent', re.I)})
    
    if result_containers:
        print(f"Found {len(result_containers)} potential result containers:")
        for i, container in enumerate(result_containers[:3]):
            print(f"  {i+1}. Tag: {container.name}, Classes: {container.get('class', [])}")
            print(f"     Text preview: {container.get_text(strip=True)[:150]}...")
    else:
        print("No obvious result containers found")
    
    # Final recommendation
    print(f"\n💡 RECOMMENDATIONS:")
    print("=" * 50)
    
    if len(html_content) < 5000:
        print("⚠️ Small HTML response - likely a redirect or error page")
    
    script_tags = soup.find_all('script')
    if len(script_tags) > 10:
        print("⚠️ Many script tags detected - likely JavaScript-heavy site")
        print("   Consider using Selenium WebDriver for dynamic content")
    
    patent_links = re.findall(r'href="(/patent/[^"]+)"', html_content)
    if patent_links:
        print(f"✅ Found {len(patent_links)} patent links - parsing possible!")
        print("   First few patent numbers:")
        for link in patent_links[:3]:
            patent_num = link.split('/')[-1] if '/' in link else link
            print(f"     - {patent_num}")
    else:
        print("❌ No patent links found - may need Selenium or API access")

if __name__ == "__main__":
    debug_google_patents_scraping("FOXP2")