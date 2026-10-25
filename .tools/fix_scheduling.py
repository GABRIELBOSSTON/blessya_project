from pathlib import Path
p=Path('src/scheduling/algorithms.py')
s=p.read_text(encoding='utf-8')
# Apply one definition consistently to every algorithm result.
s=s.replace('    return res\n', '    res.context_switches = count_context_switches(res.timeline)\n    return res\n')
# Preserve quantum boundaries even when the same process is scheduled again.
start=s.index('def round_robin('); end=s.index('\ndef priority(',start)
part=s[start:end].replace('res.timeline = merge_adjacent(raw)', 'res.timeline = raw')
s=s[:start]+part+s[end:]
p.write_text(s,encoding='utf-8')
