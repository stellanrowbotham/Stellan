#!/usr/bin/env python3
"""Builds the v4 Brain page: original page fragment + team.css/partA/partB/team.js patches.
usage: build.py <saved_original.html> <out_fragment.html>   (the Artifact service adds the document skeleton)"""
import sys, re, pathlib
src, out = sys.argv[1], sys.argv[2]
here = pathlib.Path(__file__).parent
h = open(src, encoding='utf8').read()
m = re.search(r'<body>\n(.*)\n</body></html>\s*$', h, re.S)
assert m, 'skeleton not found'
f = m.group(1)

def once(old, new):
    global f
    assert f.count(old) == 1, f'anchor not unique/found ({f.count(old)}): {old[:70]!r}'
    f = f.replace(old, new)

css = (here/'team.css').read_text(); a = (here/'partA.html').read_text(); b = (here/'partB.html').read_text(); js = (here/'team.js').read_text()
once("@media (prefers-reduced-motion: reduce) { *, *::before, *::after { animation: none !important; transition: none !important; } }\n</style>",
     "@media (prefers-reduced-motion: reduce) { *, *::before, *::after { animation: none !important; transition: none !important; } }\n" + css + "</style>")
once('<button type="button" data-go="p-research">Research</button>',
     '<button type="button" data-go="p-research">Research</button>\n    <button type="button" data-go="p-team">Team</button><button type="button" data-go="p-daily">Daily update</button><button type="button" data-go="p-outreach">Outreach</button><button type="button" data-go="p-perf">Training</button><button type="button" data-go="p-log">Activity</button>')
once('  <div class="bento">\n', a + '  <div class="bento">\n')
once('    <section class="map span-12" id="p-map"', b + '\n    <section class="map span-12" id="p-map"')
once('placeholder="e.g. Which Claude idea could I test with one local shop this week?"></textarea></div>',
     'placeholder="e.g. Which Claude idea could I test with one local shop this week?"></textarea><label class="sub"><input type="checkbox" id="q-near"> Use my location for &quot;near me&quot; questions</label></div>')
once('await dbRef.collection("questions").add({ section, text: text.slice(0, 600), status: "queued", askedAt: new Date().toISOString(), askedDate: torontoDate() }); ta.value = ""; }',
     'const loc = section === "research" && $("q-near") && $("q-near").checked ? await getLoc() : null; await dbRef.collection("questions").add({ section, text: text.slice(0, 600), status: "queued", askedAt: new Date().toISOString(), askedDate: torontoDate(), ...(loc ? { location: loc } : {}) }); ta.value = ""; }')
once('{ id: "a-research", group: "agent", label: "Research Agent", size: 8, own: "research" },', '{ id: "a-research", group: "agent", label: "Research Brain", size: 8, own: "research" },')
once('{ id: "a-call", group: "agent", label: "Brain Calls", size: 8, own: "call" },',
     '{ id: "a-call", group: "agent", label: "Brain Calls", size: 8, own: "call" },\n  { id: "a-cos", group: "agent", label: "Chief of Staff", size: 9, own: "cos" },\n  { id: "a-outreach", group: "agent", label: "Outreach", size: 8, own: "outreach" },\n  { id: "a-performance", group: "agent", label: "Performance", size: 8, own: "performance" },')
once('["a-research","a-scheduling"],["a-research","a-call"],["a-scheduling","a-call"],',
     '["a-research","a-scheduling"],["a-research","a-call"],["a-scheduling","a-call"],\n  ["core","a-cos"],["a-cos","a-research"],["a-cos","a-outreach"],["a-cos","a-performance"],["a-cos","a-call"],["a-research","a-outreach"],["a-performance","a-scheduling"],["s-daily","a-cos"],["s-daily","a-performance"],["s-flowpilot","a-outreach"],["app-brain","a-cos"],["app-brain","a-outreach"],["app-brain","a-performance"],')
once('/* ---------- boot ---------- */', js + '\n/* ---------- boot ---------- */')
once('  dbRef = db;\n', '  dbRef = db;\n  bootTeam(db);\n')
once('state.agents = s.docs.map(d => ({ id: d.id, ...d.data() })); renderAgents(); renderPulse(); draw();', 'state.agents = s.docs.map(d => ({ id: d.id, ...d.data() })); renderAgents(); renderPulse(); renderTeamStrip(); draw();')
once('state.questions = rows(s); renderQA("research"); renderQA("schedule");', 'state.questions = rows(s); renderQA("research"); renderQA("schedule"); renderRb(); renderTalkList();')
open(out, 'w', encoding='utf8').write(f)
print('built', out, len(f), 'bytes')
