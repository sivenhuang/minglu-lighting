#!/usr/bin/env python3
"""Convert scraped products_detail.json to products-data.js, merging with existing rich data."""

import json
import re
import os

# Load scraped data
with open('products_detail.json', 'r', encoding='utf-8') as f:
    scraped = json.load(f)

# Load existing JS data by parsing the file
with open('assets/js/products-data.js', 'r', encoding='utf-8') as f:
    js_content = f.read()

# Extract existing PRODUCTS array using regex
existing_match = re.search(r'const PRODUCTS = \[(.*?)\];', js_content, re.DOTALL)
existing_products = []
if existing_match:
    products_str = existing_match.group(1)
    # Find individual product objects with balanced braces
    # Simple approach: split by category comments
    pass

# Load current products by evaluating the JS (safer: just parse JSON-like structure)
# Instead, let's use a manual approach to extract products
# Find all product objects by tracking brace depth

def parse_products_from_js(content):
    """Parse PRODUCTS array from JS file using brace tracking."""
    match = re.search(r'const PRODUCTS = \[(.*?)\];', content, re.DOTALL)
    if not match:
        return []
    body = match.group(1)
    
    products = []
    depth = 0
    start = -1
    
    for i, ch in enumerate(body):
        if ch == '{':
            if depth == 0:
                start = i
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0 and start >= 0:
                obj_str = body[start:i+1]
                try:
                    # Convert JS object to JSON-compatible then parse
                    # Remove comments, trailing commas
                    obj = parse_js_obj(obj_str)
                    if obj:
                        products.append(obj)
                except Exception as e:
                    print(f"  WARN: Could not parse product: {str(e)[:80]}")
                start = -1
    
    return products

def parse_js_obj(js_str):
    """Parse a single JS object string (not full JSON compatible)."""
    # Extract simple key-value pairs
    obj = {}
    
    # id
    m = re.search(r"id:\s*'([^']+)'", js_str)
    if m: obj['id'] = m.group(1)
    
    # name
    m = re.search(r"name:\s*'([^']+)'", js_str)
    if m: obj['name'] = m.group(1)
    
    # category
    m = re.search(r"category:\s*'([^']+)'", js_str)
    if m: obj['category'] = m.group(1)
    
    # categorySlug
    m = re.search(r"categorySlug:\s*'([^']+)'", js_str)
    if m: obj['categorySlug'] = m.group(1)
    
    # description (can be multiline, use raw string)
    m = re.search(r"description:\s*'((?:[^'\\]|\\.)*)'", js_str)
    if m: obj['description'] = m.group(1)
    
    # image
    m = re.search(r"image:\s*'([^']+)'", js_str)
    if m: obj['image'] = m.group(1)
    
    # featured
    m = re.search(r"featured:\s*(true|false)", js_str)
    if m: obj['featured'] = m.group(1) == 'true'
    
    # features array
    m = re.search(r"features:\s*\[(.*?)\]", js_str, re.DOTALL)
    if m:
        feats = re.findall(r"'([^']+)'", m.group(1))
        obj['features'] = feats
    
    # specs
    m = re.search(r"specs:\s*\{(.*?)\}", js_str, re.DOTALL)
    if m:
        specs = {}
        for kv in re.findall(r"(\w+):\s*'([^']+)'", m.group(1)):
            specs[kv[0]] = kv[1]
        obj['specs'] = specs
    
    # powerOptions
    m = re.search(r"powerOptions:\s*\[(.*?)\]", js_str, re.DOTALL)
    if m:
        opts = re.findall(r"'([^']+)'", m.group(1))
        obj['powerOptions'] = opts
    
    # applications
    m = re.search(r"applications:\s*\[(.*?)\]", js_str, re.DOTALL)
    if m:
        apps = re.findall(r"'([^']+)'", m.group(1))
        obj['applications'] = apps
    
    return obj

# Parse existing products
existing = parse_products_from_js(js_content)
print(f"Parsed {len(existing)} existing products from products-data.js")
print(f"Scraped {len(scraped)} products from products_detail.json")

# Map categories between scraped data and existing data
# Scraped data uses category names like "Solar Street Light"
# Current data uses same names
# Build a merge map: for each scraped product, find matching existing by category + index

# Group existing by category
existing_by_cat = {}
for p in existing:
    cat = p['category']
    if cat not in existing_by_cat:
        existing_by_cat[cat] = []
    existing_by_cat[cat].append(p)

# Group scraped by category
scraped_by_cat = {}
for s in scraped:
    cat = s['category']
    if cat not in scraped_by_cat:
        scraped_by_cat[cat] = []
    scraped_by_cat[cat].append(s)

print(f"\nCategories in scraped: {list(scraped_by_cat.keys())}")
print(f"Categories in existing: {list(existing_by_cat.keys())}")

# Generate merged products
merged = []
cat_order = [
    'Solar Street Light', 'Solar Garden Light', 'Solar Lawn Light',
    'Solar Pillar Light', 'Solar Strip Light', 'Solar Flood Light',
    'Solar Light Tower', 'Solar Energy System',
    'LED Street Light', 'LED Flood Light', 'LED High Bay Light', 'LED Fishing Light'
]

product_id = 0
stats = {'merged': 0, 'new': 0, 'missing_existing': 0}

for cat in cat_order:
    scraped_in_cat = scraped_by_cat.get(cat, [])
    existing_in_cat = existing_by_cat.get(cat, [])
    
    for idx, s in enumerate(scraped_in_cat):
        product_id += 1
        pid = f'p{product_id}'
        
        # Try to find matching existing product by index in category
        existing_match = existing_in_cat[idx] if idx < len(existing_in_cat) else None
        
        # Build merged product
        p = {
            'id': pid,
            'name': s['name'],
            'category': s['category'],
            'categorySlug': s['categorySlug'],
            'featured': (existing_match or {}).get('featured', False),
        }
        
        # Description: use scraped description if it's meaningful, else use existing
        scraped_desc = s.get('description', '').strip()
        if scraped_desc and len(scraped_desc) > 20 and scraped_desc != s.get('name', ''):
            p['description'] = scraped_desc
        elif existing_match and existing_match.get('description'):
            p['description'] = existing_match['description']
        else:
            p['description'] = f"Professional-grade {s['category'].lower()} for commercial and municipal outdoor lighting applications. High efficiency, durable construction, and reliable performance."
        
        # Main image: use scraped image, preferring the first detail image or gallery image
        main_img = s.get('image', '')
        if not main_img and s.get('detailImages'):
            main_img = s['detailImages'][0]
        elif not main_img and s.get('galleryImages'):
            main_img = s['galleryImages'][0]
        if not main_img and existing_match:
            main_img = existing_match.get('image', '')
        p['image'] = main_img
        
        # Gallery images (for product detail gallery/thumbnails)
        p['galleryImages'] = s.get('galleryImages', [])
        
        # Detail images (for product detail page below description)
        p['detailImages'] = s.get('detailImages', [])
        
        # Source URL
        p['sourceUrl'] = s.get('sourceUrl', '')
        
        # Features: use scraped features if available, else existing, else generate
        scraped_feats = s.get('features', [])
        if scraped_feats:
            p['features'] = scraped_feats
        elif existing_match and existing_match.get('features'):
            p['features'] = existing_match['features']
        else:
            p['features'] = ['High quality LED chips', 'Energy efficient', 'Durable construction', 'Weather resistant', 'Easy installation']
        
        # Specs: use existing specs if available
        if existing_match and existing_match.get('specs'):
            p['specs'] = existing_match['specs']
        else:
            p['specs'] = {}
        
        # Power options
        if existing_match and existing_match.get('powerOptions'):
            p['powerOptions'] = existing_match['powerOptions']
        else:
            p['powerOptions'] = []
        
        # Applications
        scraped_apps = s.get('applications', [])
        if scraped_apps:
            # Split by common delimiters
            apps_text = ' '.join(scraped_apps)
            apps = [a.strip() for a in re.split(r'[,/]', apps_text) if a.strip()]
            p['applications'] = apps[:6]  # max 6
        elif existing_match and existing_match.get('applications'):
            p['applications'] = existing_match['applications']
        else:
            p['applications'] = ['Outdoor', 'Commercial', 'Municipal']
        
        if existing_match:
            stats['merged'] += 1
        else:
            stats['new'] += 1
        
        merged.append(p)

print(f"\nMerge stats: {stats}")

# Generate JS output
def escape_js_str(s):
    """Escape a string for JS single-quoted string."""
    return s.replace('\\', '\\\\').replace("'", "\\'").replace('\n', ' ').replace('\r', '')

def format_js_arr(arr):
    """Format a JS array of strings."""
    if not arr:
        return '[]'
    items = ', '.join(f"'{escape_js_str(x)}'" for x in arr)
    return f"[{items}]"

def format_js_obj(obj):
    """Format a JS object (simple key-value pairs)."""
    if not obj:
        return '{}'
    items = ', '.join(f"{k}: '{escape_js_str(v)}'" for k, v in obj.items())
    return f"{{ {items} }}"

# Generate the JS file
lines = []
lines.append("const CATEGORIES = [")
lines.append("    { slug: 'solar-street-light', name: 'Solar Street Light' },")
lines.append("    { slug: 'solar-garden-light', name: 'Solar Garden Light' },")
lines.append("    { slug: 'solar-lawn-light', name: 'Solar Lawn Light' },")
lines.append("    { slug: 'solar-pillar-light', name: 'Solar Pillar Light' },")
lines.append("    { slug: 'solar-strip-light', name: 'Solar Strip Light' },")
lines.append("    { slug: 'solar-flood-light', name: 'Solar Flood Light' },")
lines.append("    { slug: 'solar-light-tower', name: 'Solar Light Tower' },")
lines.append("    { slug: 'solar-energy-system', name: 'Solar Energy System' },")
lines.append("    { slug: 'led-street-light', name: 'LED Street Light' },")
lines.append("    { slug: 'led-flood-light', name: 'LED Flood Light' },")
lines.append("    { slug: 'led-high-bay-light', name: 'LED High Bay Light' },")
lines.append("    { slug: 'led-fishing-light', name: 'LED Fishing Light' },")
lines.append("];")
lines.append("")
lines.append("// ===== All Products — 71 products from xiuben-donta.com =====")
lines.append("")
lines.append("const PRODUCTS = [")

last_cat = None
for p in merged:
    if p['category'] != last_cat:
        if last_cat is not None:
            lines.append("")
        lines.append(f"    // {'=' * 20} {p['category']} {'=' * 20}")
        last_cat = p['category']
    
    lines.append("    {")
    lines.append(f"        id: '{p['id']}',")
    lines.append(f"        name: '{escape_js_str(p['name'])}',")
    lines.append(f"        category: '{p['category']}',")
    lines.append(f"        categorySlug: '{p['categorySlug']}',")
    
    desc = p.get('description', '')
    lines.append(f"        description: '{escape_js_str(desc)}',")
    lines.append(f"        image: '{p.get('image', '')}',")
    
    if p.get('galleryImages'):
        lines.append(f"        galleryImages: {format_js_arr(p['galleryImages'])},")
    else:
        lines.append(f"        galleryImages: [],")
    
    if p.get('detailImages'):
        lines.append(f"        detailImages: {format_js_arr(p['detailImages'])},")
    else:
        lines.append(f"        detailImages: [],")
    
    lines.append(f"        sourceUrl: '{p.get('sourceUrl', '')}',")
    lines.append(f"        featured: {'true' if p.get('featured') else 'false'},")
    lines.append(f"        features: {format_js_arr(p.get('features', []))},")
    lines.append(f"        specs: {format_js_obj(p.get('specs', {}))},")
    lines.append(f"        powerOptions: {format_js_arr(p.get('powerOptions', []))},")
    lines.append(f"        applications: {format_js_arr(p.get('applications', []))},")
    lines.append("    },")

lines.append("];")
lines.append("")

output = '\n'.join(lines)

# Write output
output_path = 'assets/js/products-data.js'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(output)

print(f"\nWrote {len(merged)} products to {output_path}")
print(f"File size: {os.path.getsize(output_path):,} bytes")

# Print some stats
for p in merged:
    has_gallery = len(p.get('galleryImages', [])) > 0
    has_detail = len(p.get('detailImages', [])) > 0
    has_features = len(p.get('features', [])) > 0
    if not has_gallery:
        print(f"  WARN: {p['id']} ({p['name'][:50]}) has no gallery images")
    if not has_detail:
        print(f"  WARN: {p['id']} ({p['name'][:50]}) has no detail images")
