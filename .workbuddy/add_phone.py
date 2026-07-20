import glob, os

root = 'E:/WorkBuddy/minglu-lighting'
pattern = '<a href="https://wa.me/8618098910947" target="_blank">WhatsApp: +86 18098910947</a>'
replacement = '<a href="tel:+8618098910947">Phone: +86 18098910947</a>\n        <a href="https://wa.me/8618098910947" target="_blank">WhatsApp: +86 18098910947</a>'

files = glob.glob(os.path.join(root, '**', '*.html'), recursive=True)
updated = 0
skipped = 0
for f in files:
    with open(f, 'r', encoding='utf-8') as fh:
        content = fh.read()
    if 'tel:+8618098910947' in content:
        skipped += 1
        continue
    if pattern in content:
        content = content.replace(pattern, replacement, 1)
        with open(f, 'w', encoding='utf-8') as fh:
            fh.write(content)
        updated += 1
print('Updated:', updated)
print('Skipped (already had tel):', skipped)
