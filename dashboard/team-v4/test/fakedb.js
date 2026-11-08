// In-memory stand-in for the Brain database + claude runtime, injected before the page loads.
window.__DB = window.__SEED;
window.__writes = [];
(function () {
  const D = window.__DB, subs = [];
  const get = path => { const [c, ...r] = path.split("/"); return (D[c] || {})[r.join("/")]; };
  const put = (path, v) => { const [c, ...r] = path.split("/"); (D[c] = D[c] || {})[r.join("/")] = v; window.__writes.push([path, JSON.parse(JSON.stringify(v))]); subs.forEach(f => f()); };
  const snapOf = (c, f, dir, lim) => { let rows = Object.entries(D[c] || {}).map(([id, v]) => ({ id, v })); if (f) { rows = rows.filter(r => r.v[f] !== undefined); rows.sort((a, b) => String(a.v[f]).localeCompare(String(b.v[f])) * (dir === "desc" ? -1 : 1)); } if (lim) rows = rows.slice(0, lim); return { docs: rows.map(r => ({ id: r.id, data: () => JSON.parse(JSON.stringify(r.v)) })) }; };
  const db = {
    collection: c => { const q = { f: null, dir: "asc", lim: 0 }; const o = {
      orderBy(f, d) { q.f = f; q.dir = d || "asc"; return o; }, limit(n) { q.lim = n; return o; },
      onSnapshot(cb) { const run = () => cb(snapOf(c, q.f, q.dir, q.lim)); subs.push(run); run(); return () => {}; },
      async add(v) { const id = "new" + Math.random().toString(36).slice(2, 8); put(c + "/" + id, v); return { id }; } }; return o; },
    doc: path => ({ onSnapshot(cb) { const run = () => { const v = get(path); cb({ exists: v !== undefined, data: () => v && JSON.parse(JSON.stringify(v)), id: path.split("/").pop() }); }; subs.push(run); run(); },
      async set(v) { put(path, v); }, async update(v) { put(path, { ...(get(path) || {}), ...v }); }, async delete() { const [c, ...r] = path.split("/"); delete (D[c] || {})[r.join("/")]; subs.forEach(f => f()); } }),
  };
  window.claude = { use: async name => name === "db" ? db : name === "mcp" ? { callTool: async () => ({ payload: {} }) } : name === "sample" ? { json: async p => { const t = ((p.match(/"""([\s\S]*?)"""/) || [])[1] || ""); return /remind me/i.test(t) ? { agent: "cos", reminder: { text: "pack my hockey bag", when: "2099-01-01T16:00", channel: "sms" } } : /barber|book/i.test(t) ? { agent: "research", reminder: null } : { agent: "outreach", reminder: null }; } } : null };
})();
