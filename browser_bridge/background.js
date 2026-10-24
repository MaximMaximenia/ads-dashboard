/* Локальный мост: раз в секунду спрашивает у 127.0.0.1:8765 команду
   и выполняет её в твоём Chrome. Ничего не закрывает и не открывает
   без явной команды. */

const PORT = 8765;
const TOKEN = "0c689ac52222d755d6bde0886f1051c7";
const BASE = `http://127.0.0.1:${PORT}`;

async function post(path, body) {
  return fetch(`${BASE}${path}?token=${TOKEN}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  });
}

async function handle(cmd) {
  const op = cmd.op;
  const args = cmd.args || {};

  if (op === "ping") return "pong";

  if (op === "list_groups") {
    return await chrome.tabGroups.query({});
  }

  if (op === "list_tabs") {
    const tabs = await chrome.tabs.query({});
    return tabs.map(t => ({
      id: t.id, windowId: t.windowId, groupId: t.groupId,
      active: t.active, pinned: t.pinned, title: t.title, url: t.url, status: t.status
    }));
  }

  if (op === "group") {
    const groups = await chrome.tabGroups.query({});
    const needle = (args.title || "").toLowerCase();
    const found = needle ? groups.filter(g => (g.title || "").toLowerCase().includes(needle)) : groups;
    const out = [];
    for (const g of found) {
      out.push({ group: g, tabs: await chrome.tabs.query({ groupId: g.id }) });
    }
    return out;
  }

  if (op === "get") {
    const what = args.what || "text";
    const sel = args.selector || "";
    const results = await chrome.scripting.executeScript({
      target: { tabId: args.tabId },
      func: (what, sel) => {
        if (what === "text") return document.body ? document.body.innerText : "";
        if (what === "html") return document.documentElement.outerHTML;
        if (what === "title") return document.title;
        if (what === "url") return location.href;
        if (what === "query") {
          const el = document.querySelector(sel);
          return el ? el.innerText : null;
        }
        if (what === "links") {
          return [...document.querySelectorAll("a")].map(a => ({ text: (a.innerText || "").trim(), href: a.href })).slice(0, 500);
        }
        return null;
      },
      args: [what, sel]
    });
    return results && results[0] ? results[0].result : null;
  }

  if (op === "click") {
    const results = await chrome.scripting.executeScript({
      target: { tabId: args.tabId },
      func: (sel, text) => {
        let el = null;
        if (sel) el = document.querySelector(sel);
        if (!el && text) {
          const all = [...document.querySelectorAll("button,a,div[role=button],span,li,td")];
          const exact = all.find(e => (e.innerText || "").trim() === text);
          el = exact || all.find(e => (e.innerText || "").includes(text));
        }
        if (!el) return false;
        el.click();
        return true;
      },
      args: [args.selector || "", args.text || ""]
    });
    return results && results[0] ? results[0].result : false;
  }

  if (op === "eval") {
    const results = await chrome.scripting.executeScript({
      target: { tabId: args.tabId },
      func: (code) => {
        try { return { ok: true, value: eval(code) }; }
        catch (e) { return { ok: false, error: String(e) }; }
      },
      args: [args.code || "1"]
    });
    return results && results[0] ? results[0].result : null;
  }

  if (op === "navigate") {
    const tab = await chrome.tabs.update(args.tabId, { url: args.url });
    return { id: tab.id, url: tab.url };
  }

  if (op === "open_tab") {
    const tab = await chrome.tabs.create({ url: args.url, active: false });
    return { id: tab.id, url: tab.url };
  }

  if (op === "close_tab") {
    await chrome.tabs.remove(args.tabId);
    return true;
  }

  if (op === "activate") {
    const tab = await chrome.tabs.update(args.tabId, { active: true });
    if (tab.windowId) await chrome.windows.update(tab.windowId, { focused: true });
    return true;
  }

  throw new Error("unknown op: " + op);
}

let busy = false;

async function poll() {
  if (busy) return;
  busy = true;
  try {
    const r = await fetch(`${BASE}/poll?token=${TOKEN}`, { cache: "no-store" });
    if (r.status === 200) {
      const cmd = await r.json();
      let data = null, error = null;
      try { data = await handle(cmd); }
      catch (e) { error = String(e); }
      await post("/result", { id: cmd.id, ok: !error, data, error });
    }
  } catch (e) {
    /* сервер выключен — просто ждём */
  }
  busy = false;
}

setInterval(poll, 1000);
chrome.alarms.create("poll", { periodInMinutes: 1 });
chrome.alarms.onAlarm.addListener(poll);
chrome.runtime.onInstalled.addListener(poll);
chrome.runtime.onStartup.addListener(poll);
poll();
