import os, re

dir_path = os.path.join(os.path.dirname(__file__), 'clothes')
for fn in os.listdir(dir_path):
    if not fn.endswith('.json'): continue
    p = os.path.join(dir_path, fn)
    with open(p, 'r', encoding='utf8') as f: c = f.read()
    c = c.replace('""','"')
    c = re.sub(r'"(\s*{)', r'\1', c)
    c = re.sub(r'}(\s*)"', r'}\1', c)
    c = re.sub(r',\s*([\]\}])', r'\1', c)
    c = re.sub(r'"\s*(?=\{)', '', c)
    c = c.strip()
    if not c.startswith('['): c = '[\n' + c
    idx = c.rfind('}')
    c = (c[:idx+1].rstrip() if idx != -1 else re.sub(r'\]\s*$', '', c)) + '\n]'
    c = re.sub(
        r'(?m)^(?P<indent>[ \t]*)(?P<author_line>"author"\s*:\s*".*?")\s*,\s*}',
        r'\g<indent>\g<author_line>\n\g<indent>},',
        c
    )
    c = re.sub(r'}\s*,\s*{', '},\n\t{', c)
    with open(p, 'w', encoding='utf8') as f: f.write(c)