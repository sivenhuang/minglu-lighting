#!/usr/bin/env python3
"""Scrape all product details from xiuben-donta.com using urllib + regex"""
import json
import re
import urllib.request
import time
import os

OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'products_detail.json')

# Category pages - each has a list of product links
CATEGORY_PAGES = [
    ('Solar Street Light', 'https://www.xiuben-donta.com/Solar_Street_Light.html'),
    ('Solar Garden Light', 'https://www.xiuben-donta.com/Solar_Garden_Light.html'),
    ('LED Street Light', 'https://www.xiuben-donta.com/LED_Street_Light.html'),
    ('LED Flood Light', 'https://www.xiuben-donta.com/LED_Flood_Light.html'),
    ('LED High Bay Light', 'https://www.xiuben-donta.com/LED_High_Bay_Light.html'),
    ('LED Fishing Light', 'https://www.xiuben-donta.com/LED_Fishing_Light.html'),
    ('Solar Flood Light', 'https://www.xiuben-donta.com/Solar_Flood_Light_pqavgo.html'),
    ('Solar Light Tower', 'https://www.xiuben-donta.com/Solar_Light_Tower.html'),
    ('Solar Lawn Light', 'https://www.xiuben-donta.com/solar_lawn_light_1192755.html'),
    ('Solar Pillar Light', 'https://www.xiuben-donta.com/solar_pillar_light_1192770.html'),
    ('Solar Strip Light', 'https://www.xiuben-donta.com/solar_strip_light_1192771.html'),
    ('Solar Energy System', 'https://www.xiuben-donta.com/solar-energy-system.html'),
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}

def fetch(url):
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read().decode('utf-8', errors='replace')
    except Exception as e:
        print(f"  [ERR] fetch {url}: {e}")
        return ''

def extract_product_links(html, base_cat):
    """Extract product detail page links from category page HTML"""
    # Find all links that point to /products/ directory
    links = re.findall(r'href="(/products/[^"]+\.html)"', html)
    # Also try absolute URLs
    links += re.findall(r'href="(https?://www\.xiuben-donta\.com/products/[^"]+\.html)"', html)
    
    # Deduplicate and normalize
    seen = set()
    result = []
    for link in links:
        if link.startswith('/'):
            link = 'https://www.xiuben-donta.com' + link
        if link not in seen and '/products/' in link:
            seen.add(link)
            # Try to extract product name from URL
            name_match = re.search(r'/([^/]+)\.html', link)
            name = name_match.group(1).replace('_', ' ') if name_match else link
            result.append({'href': link, 'name': name, 'category': base_cat})
    
    # Also extract image URLs from the listing page
    # Images are usually in <img> tags near product links
    img_pattern = re.findall(r'(https?://usimg\.bjyyb\.net/sites/[^"\'>\s]+\.webp[^"\'>\s]*)', html)
    
    return result, img_pattern

def extract_product_detail(html, url):
    """Extract full product details from a product detail page"""
    result = {
        'title': '',
        'features': [],
        'applications': [],
        'description': '',
        'mainImage': '',
        'galleryImages': [],
        'detailImages': [],
        'specRows': [],
    }
    
    # Title - try <title> tag first
    title_match = re.search(r'<title>([^<]+)</title>', html)
    if title_match:
        title = title_match.group(1).strip()
        title = title.replace('Xiuben Lighting ', '').replace(' - Xiuben Lighting', '').strip()
        result['title'] = title
    
    # Extract all images
    all_imgs = re.findall(r'(https?://usimg\.bjyyb\.net/[^"\'>\s]+)', html)
    # Filter out grey.png placeholders
    all_imgs = [img for img in all_imgs if 'grey.png' not in img and 'logo' not in img.lower()]
    # Deduplicate while preserving order
    seen = set()
    unique_imgs = []
    for img in all_imgs:
        # Remove query params for dedup, but keep full URL
        base = img.split('?')[0]
        if base not in seen:
            seen.add(base)
            unique_imgs.append(img)
    
    if unique_imgs:
        # Main image is typically the first one with resize parameter
        main = next((img for img in unique_imgs if 'resize' in img), unique_imgs[0])
        result['mainImage'] = main
        # Gallery images (thumbnails - with resize/m_lfit)
        result['galleryImages'] = [img for img in unique_imgs if img != main and ('resize' in img or 'm_lfit' in img)][:10]
        # Detail images (large images without resize - these are the ones after description)
        result['detailImages'] = [img for img in unique_imgs if 'resize' not in img and img != main][:8]
    
    # Extract features (bullet points)
    # Look for bullet point patterns
    bullet_matches = re.findall(r'[•\-\*]\s*([^<\n]{10,150})', html)
    result['features'] = [b.strip() for b in bullet_matches if len(b.strip()) > 5]
    
    # Extract applications
    app_match = re.search(r'APPLICATIONS?\s*:?\s*([^<\n]{10,300})', html, re.IGNORECASE)
    if app_match:
        app_text = app_match.group(1).strip()
        result['applications'] = [a.strip() for a in re.split(r'[,;|/]', app_text) if len(a.strip()) > 2]
    
    # Extract description (paragraphs with meaningful text)
    # Remove HTML tags to get plain text
    text = re.sub(r'<[^>]+>', ' ', html)
    text = re.sub(r'\s+', ' ', text)
    
    # Look for feature descriptions
    feature_section = re.search(r'FEATURES?\s*:?\s*(.*?)(?:APPLICATIONS?|$)', text, re.IGNORECASE | re.DOTALL)
    if feature_section:
        desc_text = feature_section.group(1).strip()
        if len(desc_text) > 30:
            result['description'] = desc_text[:500]
    
    # If no description found, look for longer paragraphs
    if not result['description']:
        paragraphs = re.findall(r'(?<=[.!?])\s+([A-Z][^.!?]{30,300}[.!?])', text)
        for p in paragraphs:
            if 'copyright' not in p.lower() and 'subscribe' not in p.lower():
                result['description'] = p
                break
    
    return result

def main():
    # Step 1: Collect all product links from category pages
    print('=== Step 1: Collecting product URLs ===')
    all_products = []
    category_images = {}  # category -> list of image URLs
    
    for cat_name, cat_url in CATEGORY_PAGES:
        print(f'\n[INFO] Category: {cat_name}')
        html = fetch(cat_url)
        if not html:
            print(f'  [WARN] Empty response for {cat_url}')
            continue
        
        links, images = extract_product_links(html, cat_name)
        category_images[cat_name] = images
        print(f'  Found {len(links)} product links, {len(images)} images')
        
        for link in links:
            all_products.append(link)
    
    print(f'\n[INFO] Total products found: {len(all_products)}')
    
    # Save URLs for reference
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'product_urls.json'), 'w', encoding='utf-8') as f:
        json.dump(all_products, f, ensure_ascii=False, indent=2)
    
    # Step 2: Visit each product detail page
    print('\n=== Step 2: Scraping product details ===')
    results = []
    
    for i, product in enumerate(all_products):
        print(f'[{i+1}/{len(all_products)}] {product["name"][:50]}...')
        html = fetch(product['href'])
        
        if html:
            detail = extract_product_detail(html, product['href'])
            # Try to match category images as fallback
            cat_imgs = category_images.get(product['category'], [])
            if not detail['mainImage'] and cat_imgs:
                # Find an image that might match this product
                idx = i % len(cat_imgs) if cat_imgs else 0
                detail['mainImage'] = cat_imgs[idx] if idx < len(cat_imgs) else ''
            
            results.append({
                'id': f'p{i+1}',
                'name': detail['title'] or product['name'],
                'category': product['category'],
                'categorySlug': product['category'].lower().replace(' ', '-'),
                'description': detail['description'],
                'image': detail['mainImage'],
                'galleryImages': detail['galleryImages'],
                'detailImages': detail['detailImages'],
                'features': detail['features'],
                'applications': detail['applications'],
                'specRows': detail['specRows'],
                'sourceUrl': product['href'],
            })
            print(f'  OK - {len(detail["features"])} features, {len(detail["galleryImages"])} gallery, {len(detail["detailImages"])} detail imgs')
        else:
            # Use category images as fallback
            cat_imgs = category_images.get(product['category'], [])
            idx = i % len(cat_imgs) if cat_imgs else 0
            results.append({
                'id': f'p{i+1}',
                'name': product['name'],
                'category': product['category'],
                'categorySlug': product['category'].lower().replace(' ', '-'),
                'description': '',
                'image': cat_imgs[idx] if idx < len(cat_imgs) else '',
                'galleryImages': [],
                'detailImages': [],
                'features': [],
                'applications': [],
                'specRows': [],
                'sourceUrl': product['href'],
            })
            print(f'  FAILED - using basic data')
        
        # Save progress every 10 products
        if (i + 1) % 10 == 0:
            with open(OUTPUT, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f'  [SAVED] Progress: {i+1} products')
        
        # Rate limiting
        time.sleep(0.5)
    
    # Final save
    with open(OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f'\n=== DONE! Total products: {len(results)} ===')
    
    # Print summary
    cats = {}
    for p in results:
        cats[p['category']] = cats.get(p['category'], 0) + 1
    print('\nSummary by category:')
    for cat, count in sorted(cats.items()):
        print(f'  {cat}: {count}')

if __name__ == '__main__':
    main()
