import os, re, csv, json

# Load real-spec product ids from products-data.js
js = open('assets/js/products-data.js', encoding='utf-8').read()
import subprocess
# use node to get specs map
node_code = """
const fs=require('fs');
let c=fs.readFileSync('assets/js/products-data.js','utf8');
eval(c+'\\nglobalThis.__P=PRODUCTS;');
const out={};
globalThis.__P.forEach(p=>{
  out[p.id]={name:p.name, cat:p.category, catSlug:p.categorySlug,
    realSpecs: (p.specs&&Object.keys(p.specs).length>0)?Object.keys(p.specs):[]};
});
console.log(JSON.stringify(out));
"""
r = subprocess.run(['C:/Users/hwei_/.workbuddy/binaries/node/versions/22.22.2/node.exe', '-e', node_code],
                   capture_output=True, text=True, cwd='.')
meta = json.loads(r.stdout.strip().split('\n')[-1])

# Common spec columns to extract
COMMON = ['Model','Material','Power','Wattage','IP Rating','Ingress Protection',
           'Lumens','Luminous Flux','Light Efficiency','Battery','Battery Capacity',
           'Solar Panel','Panel','Charging Time','Working Time','Color Temperature',
           'CCT','Beam Angle','Input Voltage','Warranty','Certifications','Certificates',
           'Application','Applications','Dimension','Size','Weight','CRI','Lifespan','Finish']

def norm(s):
    return re.sub(r'\s+',' ', s.strip())

rows = []
for f in sorted(os.listdir('product')):
    if not f.endswith('.html') or f == 'product.html':
        continue
    pid = f[:-5]
    h = open(f'product/{f}', encoding='utf-8', errors='ignore').read()
    # name
    h1 = re.search(r'<h1[^>]*>(.*?)</h1>', h, re.S)
    name = norm(re.sub(r'<[^>]+>','',h1.group(1))) if h1 else ''
    # category from breadcrumb
    bc = re.search(r'class="breadcrumb"[^>]*>(.*?)</(?:nav|div)>', h, re.S)
    cat = ''
    if bc:
        crumbs = re.findall(r'>([^<]+)</a>', bc.group(1))
        if crumbs: cat = crumbs[-1].strip()
    # parse spec table
    st = re.search(r'<table class="spec-table">(.*?)</table>', h, re.S)
    specs = {}
    group = ''
    if st:
        for tr in re.findall(r'<tr>(.*?)</tr>', st.group(1), re.S):
            tds = re.findall(r'<td(?:[^>]*)>(.*?)</td>', tr, re.S)
            tds = [norm(re.sub(r'<[^>]+>','',t)) for t in tds]
            if not tds: continue
            if len(tds) == 1:
                group = tds[0]
            elif len(tds) >= 2:
                key = tds[0]; val = tds[1]
                specs[f"{group} > {key}" if group else key] = val
    # build common map (case-insensitive)
    cm = {}
    for k, v in specs.items():
        base = k.split(' > ')[-1]
        for c in COMMON:
            if base.lower() == c.lower():
                cm[c] = v
    real = pid in meta and len(meta[pid]['realSpecs']) > 0
    # raw specs string
    raw = ' | '.join(f"{k}: {v}" for k, v in specs.items())
    row = {
        'page': f'product/{f}',
        'id': pid,
        'name': name,
        'category': cat or (meta.get(pid,{}).get('cat','')),
        'spec_source': 'REAL(ima)' if real else 'GENERATED',
        'spec_count': len(specs),
    }
    for c in COMMON:
        row[c] = cm.get(c, '')
    row['raw_specs'] = raw
    rows.append(row)

# Write CSV
cols = ['page','id','name','category','spec_source','spec_count'] + COMMON + ['raw_specs']
os.makedirs('marketing', exist_ok=True)
with open('marketing/product-spec-review.csv','w',newline='',encoding='utf-8-sig') as fh:
    w = csv.DictWriter(fh, fieldnames=cols)
    w.writeheader()
    for r in rows: w.writerow(r)

# Summary
gen = [r for r in rows if r['spec_source']=='GENERATED']
real = [r for r in rows if r['spec_source']=='REAL(ima)']
print(f"Total products: {len(rows)}")
print(f"  REAL specs (from ima): {len(real)}")
print(f"  GENERATED specs (need review): {len(gen)}")
print(f"  Products with <6 spec rows (thin): {sum(1 for r in rows if r['spec_count']<6)}")
# category breakdown
from collections import Counter
cc = Counter(r['category'] for r in rows)
print("  By category:", dict(cc))
print("  CSV -> marketing/product-spec-review.csv")
# list generated ids for priority
print("  GENERATED (priority review) ids:", ', '.join(r['id'] for r in gen))
