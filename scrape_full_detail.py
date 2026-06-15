import urllib.request, re, json, time, sys

OUTPUT = 'D:/WorkBuddy/minglu-lighting/products_detail.json'

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

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

def fetch(url):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        resp = urllib.request.urlopen(req, timeout=20)
        return resp.read().decode('utf-8', 'replace')
    except Exception as e:
        print(f'  [ERR] {e}', file=sys.stderr)
        return ''

def clean_html(html):
    """Remove script, style, head tags and get body content only"""
    # Remove script/style blocks
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL|re.IGNORECASE)
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL|re.IGNORECASE)
    html = re.sub(r'<head[^>]*>.*?</head>', '', html, flags=re.DOTALL|re.IGNORECASE)
    # Remove nav, footer
    html = re.sub(r'<nav[^>]*>.*?</nav>', '', html, flags=re.DOTALL|re.IGNORECASE)
    html = re.sub(r'<footer[^>]*>.*?</footer>', '', html, flags=re.DOTALL|re.IGNORECASE)
    return html

def extract_product_links(html):
    links = re.findall(r'href="(/products/[^"]+\.html)"', html)
    return list(set(links))

def extract_detail_images(html):
    """Extract all product images from detail page, filtered properly"""
    imgs = re.findall(r'(https?://usimg\.bjyyb\.net/sites/[^"\'><\s]+)', html)
    # Filter out: grey.png, .ico, .ttf, .woff, logo, cert, icon
    filtered = []
    seen_bases = set()
    for img in imgs:
        base = img.split('?')[0]
        if base in seen_bases:
            continue
        if any(x in img.lower() for x in ['grey.png', '.ico', '.ttf', '.woff', 'logo', 'cert', 'icon', 'yyb_icons']):
            continue
        # Remove trailing ) or other artifacts
        img = img.rstrip(')')
        seen_bases.add(base)
        filtered.append(img)
    return filtered

def parse_product_detail(html, url):
    result = {
        'title': '',
        'features': [],
        'applications': [],
        'description': '',
        'mainImage': '',
        'galleryImages': [],
        'detailImages': [],
    }
    
    # Title from <title> tag
    title_m = re.search(r'<title>([^<]+)</title>', html)
    if title_m:
        t = title_m.group(1).strip()
        t = re.sub(r'\s*[-|]\s*(Xiuben|xiuben).*$', '', t).strip()
        result['title'] = t
    
    # Images
    all_imgs = extract_detail_images(html)
    if all_imgs:
        # Main image: first one with resize parameter or just first
        main = next((i for i in all_imgs if 'resize' in i or 'w600' in i or '@!' in i), all_imgs[0])
        result['mainImage'] = main
        # Gallery (smaller thumbnails with resize/m_lfit)
        result['galleryImages'] = [i for i in all_imgs if i != main and ('resize' in i or 'm_lfit' in i or 'w600' in i or '@!' in i)][:10]
        # Detail images (larger without resize)
        result['detailImages'] = [i for i in all_imgs if i != main and 'resize' not in i and 'm_lfit' not in i and 'w600' not in i and '@!' not in i][:10]
    
    # Clean HTML for text extraction
    clean = clean_html(html)
    # Get plain text
    text = re.sub(r'<[^>]+>', '\n', clean)
    text = re.sub(r'\n\s*\n', '\n', text)
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    
    # Find FEATURES section
    in_features = False
    in_apps = False
    feature_lines = []
    desc_lines = []
    
    for i, line in enumerate(lines):
        # Detect FEATURES header
        if re.match(r'^FEATURES?\s*:', line, re.IGNORECASE):
            in_features = True
            in_apps = False
            continue
        # Detect APPLICATIONS header
        if re.match(r'^APPLICATIONS?\s*:', line, re.IGNORECASE):
            in_features = False
            in_apps = True
            app_text = re.sub(r'^APPLICATIONS?\s*:?\s*', '', line, flags=re.IGNORECASE)
            if app_text:
                result['applications'] = [a.strip() for a in re.split(r'[,;|/]', app_text) if len(a.strip()) > 2]
            continue
        
        if in_features:
            # Feature bullet points
            if line.startswith(('•', '-', '*', '\u2022')):
                feat = re.sub(r'^[•\-\*\u2022]\s*', '', line).strip()
                if len(feat) > 5 and not feat.startswith(('http', 'var ', 'function', '{', '//', '/*')):
                    feature_lines.append(feat)
            elif len(line) > 20 and not line.startswith(('http', 'var ', 'function', '{', '//', '/*', 'window', 'document', 'if(', 'try', 'catch', 'return', 'const', 'let')):
                # Might be a description line within features
                if not any(kw in line.lower() for kw in ['copyright', 'subscribe', 'newsletter', 'search', 'login', 'password', 'cookie']):
                    feature_lines.append(line)
        
        if in_apps and not result['applications']:
            # Sometimes applications are on following lines
            apps_text = line.strip()
            if len(apps_text) > 3 and not apps_text.startswith(('http', 'var ', '{', '//')):
                result['applications'] = [a.strip() for a in re.split(r'[,;|/]', apps_text) if len(a.strip()) > 2]
                in_apps = False
    
    result['features'] = feature_lines[:15]
    
    # Description: find the paragraph after features that describes the product
    # Look for sentences that describe the product
    for line in lines:
        line = line.strip()
        if len(line) > 40 and not line.startswith(('•', '-', '*', 'http', 'var ', 'function', '{', '//', '/*', 'window', 'document')):
            if not any(kw in line.lower() for kw in ['copyright', 'subscribe', 'newsletter', 'search', 'login', 'cookie', 'your name', 'your email', 'phone', 'message']):
                if 'LED' in line or 'solar' in line.lower() or 'light' in line.lower() or 'energy' in line.lower():
                    result['description'] = line[:500]
                    break
    
    return result

def main():
    print('=== Step 1: Collecting product URLs from category pages ===')
    all_products = []
    
    for cat_name, cat_url in CATEGORY_PAGES:
        print(f'\nCategory: {cat_name}')
        html = fetch(cat_url)
        if not html:
            print(f'  Empty response')
            continue
        
        links = extract_product_links(html)
        print(f'  Found {len(links)} product links')
        
        for link in links:
            full_url = 'https://www.xiuben-donta.com' + link if link.startswith('/') else link
            name = link.split('/')[-1].replace('_', ' ').replace('.html', '')
            all_products.append({
                'href': full_url,
                'name': name,
                'category': cat_name,
            })
    
    print(f'\nTotal products: {len(all_products)}')
    
    # Step 2: Scrape each product detail
    print('\n=== Step 2: Scraping product details ===')
    results = []
    
    for i, prod in enumerate(all_products):
        sys.stdout.write(f'[{i+1}/{len(all_products)}] {prod["name"][:50]}... ')
        sys.stdout.flush()
        
        html = fetch(prod['href'])
        if html:
            detail = parse_product_detail(html, prod['href'])
            results.append({
                'id': f'p{i+1}',
                'name': detail['title'] or prod['name'],
                'category': prod['category'],
                'categorySlug': prod['category'].lower().replace(' ', '-'),
                'description': detail['description'],
                'image': detail['mainImage'],
                'galleryImages': detail['galleryImages'],
                'detailImages': detail['detailImages'],
                'features': detail['features'],
                'applications': detail['applications'],
                'sourceUrl': prod['href'],
            })
            print(f'OK ({len(detail["features"])} feat, {len(detail["galleryImages"])} gallery, {len(detail["detailImages"])} detail)')
        else:
            results.append({
                'id': f'p{i+1}',
                'name': prod['name'],
                'category': prod['category'],
                'categorySlug': prod['category'].lower().replace(' ', '-'),
                'description': '',
                'image': '',
                'galleryImages': [],
                'detailImages': [],
                'features': [],
                'applications': [],
                'sourceUrl': prod['href'],
            })
            print('FAILED')
        
        # Save progress every 15 products
        if (i + 1) % 15 == 0:
            with open(OUTPUT, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f'  [SAVED] {i+1} products')
        
        time.sleep(0.3)
    
    # Final save
    with open(OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f'\n=== DONE! Total: {len(results)} products ===')
    
    # Summary
    cats = {}
    for p in results:
        cats[p['category']] = cats.get(p['category'], 0) + 1
        if p['features']:
            cats.setdefault(p['category'] + '_w_features', 0)
    print('\nBy category:')
    for cat, count in sorted(cats.items()):
        print(f'  {cat}: {count}')

if __name__ == '__main__':
    main()
