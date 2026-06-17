#!/usr/bin/env python3
"""Rebuild products-data.js with all today's changes + new Solar Wall Light category."""

import re, os, json

fp = r'D:\WorkBuddy\minglu-lighting\assets\js\products-data.js'
base = r'D:\WorkBuddy\minglu-lighting\assets\images\products'

with open(fp, 'r', encoding='utf-8') as f:
    content = f.read()

# ============ Helper ============
def gallery(rel_dir):
    p = os.path.join(base, rel_dir)
    if not os.path.isdir(p): return []
    files = sorted(os.listdir(p), key=lambda x: (int(re.match(r'(\d+)',x).group(1)) if re.match(r'(\d+)',x) else 999, x))
    prefix = 'assets/images/products/' + rel_dir.replace('\\','/') + '/'
    return [prefix + f for f in files]

def mk(pid, name, cat, slug, desc, lb_d, xq_d, apps=None):
    lb = gallery(lb_d + '/lb') if lb_d else []
    xq = gallery(xq_d + '/xq') if xq_d else []
    main = lb[0] if lb else (xq[0] if xq else 'assets/images/placeholder.svg')
    apps = apps or ["Street","Road","Solar"]
    return f'''    {{
        id: "{pid}",
        name: "{name}",
        category: "{cat}",
        categorySlug: "{slug}",
        description: "{desc.replace(chr(10),' ')}",
        image: "{main}",
        galleryImages: {json.dumps(lb)},
        detailImages: {json.dumps(xq)},
        sourceUrl: "",
        featured: false,
        features: ["IP65/IP66 waterproof","All-in-one design","High-efficiency LED","Durable construction","Easy installation","Energy-saving solar","Auto dusk-to-dawn","Certified quality"],
        specs: {{}},
        powerOptions: [],
        applications: {json.dumps(apps)},
    }}'''

# ============ Step 1: Add Solar Wall Light category ============
cat_old = '        name: "Solar Pillar Light"\n    },\n    {\n        slug: "solar-strip-light",'
cat_new = '        name: "Solar Pillar Light"\n    },\n    {\n        slug: "solar-wall-light",\n        name: "Solar Wall Light"\n    },\n    {\n        slug: "solar-strip-light",'
content = content.replace(cat_old, cat_new, 1)

# ============ Step 2: Parse existing products ============
pm = re.search(r'const PRODUCTS = \[([\s\S]*?)\];', content)
prod_text = pm.group(1)

products = []
depth = start = 0
in_str = False; str_char = None; esc = False
for i, ch in enumerate(prod_text):
    if in_str:
        if esc: esc = False; continue
        if ch == '\\': esc = True; continue
        if ch == str_char: in_str = False
        continue
    if ch in ('"',"'"): in_str = True; str_char = ch; continue
    if ch == '{':
        if depth == 0: start = i
        depth += 1
    elif ch == '}':
        depth -= 1
        if depth == 0:
            block = prod_text[start:i+1].strip()
            pid = re.search(r'id:\s*"([^"]+)"', block).group(1)
            products.append((pid, block))

pid_map = {pid: block for pid, block in products}
print(f'Parsed {len(products)} existing products')

# ============ Step 3: Build new products ============
tr348_desc = "Minglu Lighting TR348 All in one solar street light 80W 100W All in one solar street light is a new kind of solar led street light for the road lighting. Its solar panel,LED lamp, controller, battery all in one box. High quality,competitive prices and fast delivery."
p40_desc = "Minglu Lighting MTR-3M All in two solar street light outdoor Subscribe to get the latest on sales, new releases and more Copyright 2026 Zhongshan Minglu Lighting Co., Ltd."
p1_desc = "Minglu Lighting CF2040 High quality all in one solar street lights outdoor waterproof dusk to dawn No wires needed and can be mounted onto wall or pole Turns on and off automatically: Night sensor comes on at dusk. Press the switch once to turn on."
wall_desc = "Minglu Lighting Solar wall light outdoor waterproof with motion sensor high quality all in one design."

new_entries = {
    'p142': mk('p142', 'SG-1-Wall Solar wall light', 'Solar Wall Light', 'solar-wall-light', wall_desc, 'SG-1-Wall', 'SG-1-Wall', ["Wall","Outdoor","Solar"]),
    'p143': mk('p143', 'TX-07 Solar wall light', 'Solar Wall Light', 'solar-wall-light', wall_desc, 'TX-07', 'TX-07', ["Wall","Outdoor","Solar"]),
    'p134': mk('p134', 'TR408 All in one solar street light', 'Solar Street Light', 'solar-street-light', tr348_desc, 'TR408', 'TR408'),
    'p137': mk('p137', 'TR348 with camera All in one solar street light', 'Solar Street Light', 'solar-street-light', tr348_desc, None, 'TR348 with camera'),
    'p135': mk('p135', 'TL All in one solar street light', 'Solar Street Light', 'solar-street-light', tr348_desc, 'TL', 'TL'),
    'p138': mk('p138', 'BY All in two solar street light', 'Solar Street Light', 'solar-street-light', p40_desc, 'BY', 'BY'),
    'p136': mk('p136', 'TK348 All in one solar street light', 'Solar Street Light', 'solar-street-light', tr348_desc, 'TK348', 'TK348'),
    'p139': mk('p139', 'MTR All in two solar street light', 'Solar Street Light', 'solar-street-light', p40_desc, 'MTR', 'MTR'),
    'p140': mk('p140', 'CF All in one solar street light', 'Solar Street Light', 'solar-street-light', p1_desc, 'CF', 'CF'),
    'p141': mk('p141', 'SG-6 Solar Lawn Light', 'Solar Lawn Light', 'solar-lawn-light', "Subscribe to get the latest on sales new releases and more", None, None),
}

# p141 uses single dir (no lb/xq) - special case
def gallery_single(rel_dir):
    p = os.path.join(base, rel_dir)
    if not os.path.isdir(p): return []
    files = sorted(os.listdir(p), key=lambda x: (int(re.match(r'(\d+)',x).group(1)) if re.match(r'(\d+)',x) else 999, x))
    prefix = 'assets/images/products/' + rel_dir.replace('\\','/') + '/'
    return [prefix + f for f in files]

sg6_imgs = gallery_single('SG-6')
new_entries['p141'] = f'''    {{
        id: "p141",
        name: "SG-6 Solar Lawn Light",
        category: "Solar Lawn Light",
        categorySlug: "solar-lawn-light",
        description: "Subscribe to get the latest on sales new releases and more Copyright 2026 Zhongshan Minglu Lighting Co Ltd",
        image: "{sg6_imgs[0] if sg6_imgs else ''}",
        galleryImages: {json.dumps(sg6_imgs)},
        detailImages: {json.dumps(sg6_imgs)},
        sourceUrl: "",
        featured: false,
        features: ["IP65/IP66 waterproof","All-in-one design","High-efficiency LED","Durable construction","Easy installation","Energy-saving solar","Auto dusk-to-dawn","Certified quality"],
        specs: {{}},
        powerOptions: [],
        applications: ["Lawn","Garden","Outdoor","Solar"],
    }}'''

# Fix p140: swap first gallery to 5.jpg
if 'p140' in pid_map:
    # CF already registered above as new
    pass

# Fix p95: first gallery → 17748
# Fix p96: first gallery → 06483
if 'p95' in pid_map:
    p95_block = pid_map['p95']
    p95_block = p95_block.replace(
        '"assets/images/all-products/20220921112206483.webp", "assets/images/all-products/20220921112217748.webp"',
        '"assets/images/all-products/20220921112217748.webp", "assets/images/all-products/20220921112206483.webp"')
    p95_block = p95_block.replace(
        'image: "assets/images/all-products/20220921112206483.webp"',
        'image: "assets/images/all-products/20220921112217748.webp"')
    pid_map['p95'] = p95_block

if 'p96' in pid_map:
    p96_block = pid_map['p96']
    p96_block = p96_block.replace(
        '"assets/images/all-products/20220921112217748.webp", "assets/images/all-products/20220921112206483.webp"',
        '"assets/images/all-products/20220921112206483.webp", "assets/images/all-products/20220921112217748.webp"')
    p96_block = p96_block.replace(
        'image: "assets/images/all-products/20220921112217748.webp"',
        'image: "assets/images/all-products/20220921112206483.webp"')
    pid_map['p96'] = p96_block

# Fix p9: add TR348-1.jpg
if 'p9' in pid_map:
    p9_block = pid_map['p9']
    p9_block = p9_block.replace(
        'image: "assets/images/all-products/20240426163307990.webp"',
        'image: "assets/images/all-products/TR348-1.jpg"')
    p9_block = p9_block.replace(
        'galleryImages: ["assets/images/all-products/20240426163307990.webp"',
        'galleryImages: ["assets/images/all-products/TR348-1.jpg", "assets/images/all-products/20240426163307990.webp"')
    p9_block = p9_block.replace(
        'detailImages: ["assets/images/all-products/20240426163257929.webp"',
        'detailImages: ["assets/images/all-products/TR348-1.jpg", "assets/images/all-products/20240426163257929.webp"')
    pid_map['p9'] = p9_block

# ============ Step 4: Move p31 to Solar Wall Light ============
if 'p31' in pid_map:
    p31_block = pid_map['p31']
    p31_block = p31_block.replace(
        'category: "Solar Street Light"',
        'category: "Solar Wall Light"')
    p31_block = p31_block.replace(
        'categorySlug: "solar-street-light"',
        'categorySlug: "solar-wall-light"')
    p31_block = p31_block.replace(
        'applications: ["Street","Outdoor","Solar"]',
        'applications: ["Wall","Outdoor","Solar"]')
    p31_block = p31_block.replace(
        '"Integrated solar wall lights outdoor led solar motion sensor lights waterproof security lights fo..."',
        '"Integrated solar wall lights outdoor"')
    pid_map['p31'] = p31_block

# ============ Step 5: Build final ordered list ============
# Order:
# 1. Solar Street Light: p134, p137, p135, p138, p136, then existing solar-street (p9,p1,p2,p3,p5,p6,p7,p8,p18,p19,p23,p24,p25,p26,p27,p28,p29,p30,p33,p34,p35,p36,p37,p38,p39,p41,p42,p43,p44,p45,p46,p47,p48,p49,p50,p52,p53,p54)
# 2. Then p139, p140 at end of solar-street (before p55)
# 3. Solar Garden Light: p55, p56, p57, p58, p60, p61, p63, p65, p66, p68, p70, p71, p73, p74, p75
# 4. Solar Lawn Light: p141, p84 (ex-p77), p78, p79, p80, p81, p82, p83, p85
# 5. Solar Pillar Light: p86, p87, p88, p89, p90, p91, p92, p93, p94
# 6. Solar Wall Light: p142, p143, p31
# 7. Solar Strip Light: p95, p96
# 8. Solar Flood Light
# 9. Solar Light Tower
# 10-12. LED categories

# Remove deleted products
del_ids = {'p40', 'p51'}
for did in del_ids:
    if did in pid_map:
        del pid_map[did]

# Build ordered list
cats = [
    ('Solar Street Light', ['p134','p137','p135','p138','p136']),
    ('Solar Street Light', []),  # rest of solar street + p139,p140 at end
    ('Solar Garden Light', []),
    ('Solar Lawn Light', ['p141']),
    ('Solar Pillar Light', []),
    ('Solar Wall Light', ['p142','p143','p31']),
    ('Solar Strip Light', []),
    ('Solar Flood Light', []),
    ('Solar Light Tower', []),
    ('LED Street Light', []),
    ('LED Flood Light', []),
    ('LED High Bay Light', []),
]

# Get existing products for each category
existing_by_cat = {}
for pid, block in products:
    cat_m = re.search(r'category:\s*"([^"]+)"', block)
    cat = cat_m.group(1) if cat_m else 'Unknown'
    if cat not in existing_by_cat:
        existing_by_cat[cat] = []
    existing_by_cat[cat].append((pid, block))

final_order = []
for cat, prepend_ids in cats:
    if cat == 'Solar Street Light':
        # First batch: prepended new products
        for pid in ['p134','p137','p135','p138','p136']:
            if pid in new_entries:
                final_order.append(new_entries[pid])
        # Then existing solar street products (excluding deleted and p31)
        skip = {'p134','p137','p135','p138','p136','p31','p40','p51'}
        for pid, block in existing_by_cat.get('Solar Street Light', []):
            if pid not in skip:
                final_order.append(block)
        # p139, p140 at end
        for pid in ['p139','p140']:
            if pid in new_entries:
                final_order.append(new_entries[pid])
    else:
        for pid in prepend_ids:
            if pid in new_entries:
                final_order.append(new_entries[pid])
            elif pid in pid_map:
                final_order.append(pid_map[pid])
        skip_pre = set(prepend_ids)
        for pid, block in existing_by_cat.get(cat, []):
            if pid not in skip_pre and pid not in del_ids:
                final_order.append(block)

result = '\n' + ',\n'.join(final_order) + '\n'
content = content[:pm.start(1)] + result + content[pm.end(1):]

with open(fp, 'w', encoding='utf-8') as f:
    f.write(content)

import subprocess
r = subprocess.run(['node','-e',"const c=require('fs').readFileSync('"+fp.replace('\\','/')+"','utf8');new Function(c);console.log('Syntax OK')"],capture_output=True,text=True)
if r.returncode != 0:
    print('SYNTAX ERROR:', r.stderr[:500])
    # Save debug
    with open(r'D:\WorkBuddy\minglu-lighting\err.txt', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Saved to err.txt')
else:
    print('Syntax OK')

pids = re.findall(r'id:\s*"(p\d+)"', content)
print(f'Total: {len(pids)} products')
print(f'First 10: {pids[:10]}')

# Check wall products
for pid, block in final_order:
    pm = re.search(r'category:\s*"Solar Wall Light"', block)
    if pm:
        pid_m = re.search(r'id:\s*"(p\d+)"', block)
        name_m = re.search(r'name:\s*"([^"]+)"', block)
        print(f'  Wall: {pid_m.group(1)} {name_m.group(1)}')

# Verify p40,p51 removed
if 'p40' not in pids and 'p51' not in pids:
    print('p40,p51 confirmed deleted')
else:
    print('WARNING: p40/p51 still exist')
