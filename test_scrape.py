import urllib.request, re, json, sys

# Test scraping a category page
url = 'https://www.xiuben-donta.com/Solar_Street_Light.html'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
resp = urllib.request.urlopen(req, timeout=15)
html = resp.read().decode('utf-8', 'replace')

# Find product links
links = re.findall(r'href="(/products/[^"]+\.html)"', html)
links2 = re.findall(r'href="(https?://www\.xiuben-donta\.com/products/[^"]+\.html)"', html)
all_links = list(set(links + links2))
print(f'Found {len(all_links)} product links:')
for l in all_links[:15]:
    print(f'  {l}')

# Find images
imgs = re.findall(r'(https?://usimg\.bjyyb\.net/[^"\'><\s]+)', html)
imgs = [i for i in imgs if 'grey.png' not in i]
print(f'\nFound {len(imgs)} images (first 5):')
for i in imgs[:5]:
    print(f'  {i[:100]}')

# Now test a product detail page
if all_links:
    detail_url = all_links[0]
    if detail_url.startswith('/'):
        detail_url = 'https://www.xiuben-donta.com' + detail_url
    print(f'\n=== Testing detail page: {detail_url} ===')
    req2 = urllib.request.Request(detail_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
    resp2 = urllib.request.urlopen(req2, timeout=15)
    dhtml = resp2.read().decode('utf-8', 'replace')
    
    # Extract title
    title_m = re.search(r'<title>([^<]+)</title>', dhtml)
    print(f'Title: {title_m.group(1) if title_m else "N/A"}')
    
    # Extract images
    dimgs = re.findall(r'(https?://usimg\.bjyyb\.net/[^"\'><\s]+)', dhtml)
    dimgs = [i for i in dimgs if 'grey.png' not in i and 'logo' not in i.lower()]
    print(f'Detail images: {len(dimgs)}')
    for i in dimgs[:5]:
        print(f'  {i[:100]}')
    
    # Extract features (bullet points)
    bullets = re.findall(r'[^<]*[•\-\*]\s*([A-Za-z][^<\n]{5,150})', dhtml)
    bullets = [b.strip() for b in bullets if len(b.strip()) > 5]
    print(f'\nFeatures ({len(bullets)}):')
    for b in bullets[:10]:
        print(f'  {b}')
    
    # Extract applications
    app_m = re.search(r'APPLICATIONS?\s*:?\s*([^<\n]{5,300})', dhtml, re.IGNORECASE)
    if app_m:
        apps = [a.strip() for a in re.split(r'[,;|/]', app_m.group(1)) if len(a.strip()) > 2]
        print(f'\nApplications: {apps}')
