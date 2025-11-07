# Web GUI Redesign – Minimal, Professional, Vanilla JS Checklist

This is a practical, minimal plan to rebuild the Web GUI so it looks professional, stays simple, and preserves existing functionality. No framework or language changes required.

---
## 1) Minimal Goals
- Clean, modern layout (header, left config, right main panel) that scales to mobile.
- One primary action: Upload/Backup. Clear secondary actions: Pause, Resume, Stop.
- Real-time progress that feels responsive (ring + text + ETA), no flashy distractions.
- Stable logs with autoscroll toggle and quick export.
- Zero regressions to existing flows (WebSocket + polling fallback, file validation, notifications, error boundary, connection health monitor).

---
## 2) Must-have UI Elements (IDs/classes)
- Header
  - `#appLogo` (brand)
  - `#connStatus` (badge: Connected/Connecting/Disconnected)
  - `#connHealth` (latency text, e.g., "32 ms – Good")
- Config Panel
  - `#serverInput` (text)
  - `#usernameInput` (text)
  - `#fileInput` (type=file) + `#fileSelectBtn` (button)
  - `#recentFilesBtn` (button, optional)
  - `#themeToggle` (button)
- Main Panel
  - `#phaseText` (e.g., "Encrypting" / "Transferring")
  - Progress
    - `svg#progressRing` with `#progressArc`
    - `#progressPct` (text, e.g., "63%")
    - `#etaText` (text, e.g., "ETA 1m 12s")
  - Controls
    - `#primaryActionBtn` (Connect/Start Upload)
    - `#pauseBtn` (Pause)
    - `#resumeBtn` (Resume)
    - `#stopBtn` (Stop)
- Stats + Log
  - `#statsGrid` (bytes sent, speed, file size, elapsed)
  - `#logContainer` (virtualized or simple list)
  - `#logAutoscrollToggle` (checkbox)
  - `#logExportBtn` (button)

Accessibility helpers
- `#srLive` (aria-live="polite") for phase/progress announcements

---
## 3) Essential Handlers (function names)
- App bootstrap
  - `initApp()` – wire up events, connect feature flags, load saved config
- Config & inputs
  - `onServerChanged(e)`, `onUsernameChanged(e)`
  - `onFileSelectClick()`, `onFileChosen(e)`
- Primary flow
  - `onPrimaryAction()` – connect or start backup depending on state
  - `onPause()`, `onResume()`, `onStop()`
- Transport / realtime
  - `initWebSocket()` – register ws handlers
  - `handleWsOpen()`, `handleWsClose()`, `handleWsError(err)`
  - `handleProgressUpdate(msg)` – update ring, text, stats
  - `startPollingFallback()` / `stopPollingFallback()`
- UI updates
  - `renderProgress(pct)`, `renderPhase(phase)`, `renderStats(model)`
  - `appendLog(entry)`, `exportLogs()`
  - `setButtonsForState(state)` – enable/disable buttons
  - `announce(text)` – writes to `#srLive`
- Validation & helpers
  - `validateInputs()`, `validateFile(file)`
  - `formatBytes(n)`, `formatEta(ms)`, `safeText(el, str)`

---
## 4) Minimal State Shape
```js
const state = {
  connection: { status: 'disconnected', latencyMs: null, quality: 'offline' },
  transfer: {
    phase: 'idle', // idle|connecting|encrypting|transferring|complete|error
    percent: 0,
    etaMs: null,
    speedMbps: 0
  },
  file: { name: null, size: 0 },
  ui: { autoscroll: true, theme: 'dark' },
  logs: []
};
```

---
## 5) Build Order (simple and safe)
1. Static HTML skeleton (header, panels, required IDs above).
2. Minimal CSS: one theme (dark) with good spacing/typography; subtle shadows; no heavy animation.
3. Vanilla JS bootstrap with only the handlers listed.
4. Wire log rendering (cap to 1,000 entries; autoscroll checkbox).
5. Implement WebSocket connect + progress update -> ring + text.
6. Add polling fallback.
7. Add Pause/Resume/Stop + state-driven button enabling.
8. Add validation + friendly toasts for common errors.
9. Tighten a11y (aria-live updates, focus order, key support on buttons).
10. Polish: optional theme toggle, export logs.

---
## 6) Accessibility & Security Basics
- Use `textContent` for any user/server strings; never set `innerHTML` with untrusted data.
- Announce phase/progress changes via `#srLive` (aria-live polite) sparingly to avoid spam.
- Keyboard: Enter/Space activates buttons; ESC closes modals.
- Min control size ~44px on touch.
- Respect `prefers-reduced-motion`: no continuous animation if true.

---
## 7) Small HTML + JS Skeleton
```html
<!-- index.html (skeleton excerpt) -->
<header class="app-header">
  <div id="appLogo">CyberBackup</div>
  <div class="status">
    <span id="connStatus" class="badge">Disconnected</span>
    <span id="connHealth" class="muted">–</span>
  </div>
</header>
<main class="app-main">
  <section class="config">
    <label>Server <input id="serverInput" /></label>
    <label>Username <input id="usernameInput" /></label>
    <button id="fileSelectBtn">Choose File</button>
    <input id="fileInput" type="file" hidden />
  </section>
  <section class="status">
    <div id="phaseText">Idle</div>
    <svg id="progressRing" viewBox="0 0 100 100">
      <circle cx="50" cy="50" r="45" stroke="#0bf" stroke-width="6" fill="none" opacity=".2"/>
      <circle id="progressArc" cx="50" cy="50" r="45" stroke="#0bf" stroke-width="6" fill="none" stroke-linecap="round" stroke-dasharray="282.743" stroke-dashoffset="282.743"/>
    </svg>
    <div><span id="progressPct">0%</span> · <span id="etaText">ETA —</span></div>
    <div class="controls">
      <button id="primaryActionBtn">Connect / Start</button>
      <button id="pauseBtn" disabled>Pause</button>
      <button id="resumeBtn" disabled>Resume</button>
      <button id="stopBtn" disabled>Stop</button>
    </div>
  </section>
</main>
<section class="logs">
  <div class="row">
    <label><input id="logAutoscrollToggle" type="checkbox" checked /> Autoscroll</label>
    <button id="logExportBtn">Export</button>
  </div>
  <pre id="logContainer"></pre>
</section>
<div id="srLive" class="sr-only" aria-live="polite"></div>
```

```js
// app.js (skeleton excerpt)
const TAU = Math.PI * 2;
const R = 45, C = TAU * R; // 282.743...
const $ = sel => document.querySelector(sel);

const st = { /* see state in §4 */ };

function setProgress(pct){
  st.transfer.percent = Math.max(0, Math.min(100, pct));
  const off = C * (1 - st.transfer.percent/100);
  $('#progressArc').style.strokeDasharray = `${C}`;
  $('#progressArc').style.strokeDashoffset = `${off}`;
  $('#progressPct').textContent = `${Math.round(st.transfer.percent)}%`;
}

function announce(t){ $('#srLive').textContent = t; }

function appendLog(text){
  const box = $('#logContainer');
  const line = `[${new Date().toLocaleTimeString()}] ${text}`;
  st.logs.push(line);
  if(st.logs.length > 1000) st.logs.shift();
  box.textContent = st.logs.join('\n');
  if($('#logAutoscrollToggle').checked){ box.scrollTop = box.scrollHeight; }
}

function onPrimaryAction(){ /* connect or start upload */ }
function onPause(){ /* pause */ }
function onResume(){ /* resume */ }
function onStop(){ /* stop */ }

function initApp(){
  $('#fileSelectBtn').addEventListener('click', ()=> $('#fileInput').click());
  $('#fileInput').addEventListener('change', onFileChosen);
  $('#primaryActionBtn').addEventListener('click', onPrimaryAction);
  $('#pauseBtn').addEventListener('click', onPause);
  $('#resumeBtn').addEventListener('click', onResume);
  $('#stopBtn').addEventListener('click', onStop);
  setProgress(0);
}

document.addEventListener('DOMContentLoaded', initApp);
```

---
## 8) Done Criteria
- Clean layout, professional look, mobile-friendly.
- File can be selected and uploaded; progress ring updates; logs stream.
- Pause/Resume/Stop work; buttons reflect state; no UI jank.
- Works with WebSocket and gracefully with polling fallback.
- No framework added; only vanilla JS/CSS/HTML.
