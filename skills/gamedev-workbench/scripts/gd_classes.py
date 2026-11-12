"""Bounded lexical evidence for simple root-level GDScript named inheritance."""
import re

IDENTIFIER = r'[^\W\d]\w*'


def class_evidence(texts, scan_lines):
    definitions = []; pending = []; index = {}; local_names = {}
    for source, text in sorted(texts.items()):
        if not source.endswith('.gd'): continue
        local_names[source] = set()
        for number, code, _, _ in scan_lines(text):
            declaration = re.match(r'^class_name\s+('+IDENTIFIER+r')\b', code)
            if declaration:
                name = declaration[1]
                definitions.append({'name': name, 'source': source, 'line': number})
                index.setdefault(name, []).append(source)
            local = re.match(r'^(?:const|class)\s+('+IDENTIFIER+r')\b', code)
            if local: local_names[source].add(local[1])
            base = re.fullmatch(r'(?:class_name\s+'+IDENTIFIER+r'\s+)?extends\s+('+IDENTIFIER+r')\s*', code)
            if base: pending.append({'source': source, 'line': number, 'name': base[1]})
    references = []
    for row in pending:
        candidates = sorted(index.get(row['name'], []))
        status = ('shadowed' if row['name'] in local_names[row['source']] else
                  'source-resolved' if len(candidates) == 1 else 'ambiguous' if candidates else 'unindexed')
        references.append({**row, 'status': status, 'candidates': candidates})
    return definitions, references
