#!/usr/bin/env python3
"""Safely add the Riuman PWA update checker to an existing single-file HTML game.

Usage:
  python install_updater.py "New_Proyect Browser Versión 1_5_6.html" 1.5.6

The script creates a .backup copy before changing the original file.
"""
from pathlib import Path
import sys

UPDATE_SCRIPT = r"""
<!-- RIUMAN WEB UPDATE CHECKER: preserves all existing riuman.* localStorage data -->
<script>
(function () {
  "use strict";
  const CURRENT_VERSION = "__CURRENT_VERSION__";
  const base = new URL("./", window.location.href);
  const secure = window.isSecureContext &&
    (location.protocol === "https:" || location.hostname === "localhost" || location.hostname === "127.0.0.1");
  if (!secure) return;

  let dismissedVersion = "";
  let checking = false;

  function compareVersions(a, b) {
    const aa = String(a).match(/\d+/g) || [];
    const bb = String(b).match(/\d+/g) || [];
    const count = Math.max(aa.length, bb.length);
    for (let i = 0; i < count; i++) {
      const x = Number(aa[i] || 0), y = Number(bb[i] || 0);
      if (x > y) return 1;
      if (x < y) return -1;
    }
    return 0;
  }

  function showUpdate(version, target) {
    if (dismissedVersion === version || document.getElementById("riuman-update-notice")) return;
    const panel = document.createElement("section");
    panel.id = "riuman-update-notice";
    panel.setAttribute("role", "status");
    panel.setAttribute("aria-live", "polite");
    panel.style.cssText = [
      "position:fixed","top:calc(12px + env(safe-area-inset-top, 0px))",
      "left:50%","transform:translateX(-50%)","width:min(560px, calc(100vw - 24px))",
      "box-sizing:border-box","z-index:2147483000","display:flex","align-items:center",
      "flex-wrap:wrap","gap:10px","padding:12px 14px",
      "border:1px solid rgba(255,224,138,.9)","border-radius:16px",
      "background:linear-gradient(135deg,rgba(48,25,105,.97),rgba(10,10,30,.98))",
      "box-shadow:0 10px 32px rgba(0,0,0,.5)","color:#fff1c9",
      "font:14px 'Courier New',monospace","backdrop-filter:blur(12px)",
      "-webkit-backdrop-filter:blur(12px)"
    ].join(";");
    const message = document.createElement("div");
    message.style.cssText = "flex:1 1 190px;line-height:1.4";
    message.textContent = "🆕 Riuman " + version + " está disponible. Tu progreso se conserva en este dispositivo.";
    const update = document.createElement("button");
    update.type = "button";
    update.textContent = "Actualizar";
    update.style.cssText = "border:1px solid #ffe08a;border-radius:10px;padding:9px 13px;background:#5b3bb5;color:#fff;font:bold 14px 'Courier New',monospace;cursor:pointer";
    update.addEventListener("click", function () {
      update.disabled = true;
      update.textContent = "Abriendo…";
      window.location.assign(target.href);
    });
    const later = document.createElement("button");
    later.type = "button";
    later.textContent = "Después";
    later.style.cssText = "border:1px solid rgba(255,255,255,.3);border-radius:10px;padding:9px 12px;background:rgba(255,255,255,.08);color:#fff;font:13px 'Courier New',monospace;cursor:pointer";
    later.addEventListener("click", function () {
      dismissedVersion = version;
      panel.remove();
    });
    panel.append(message, update, later);
    document.body.appendChild(panel);
  }

  async function checkForUpdates() {
    if (checking || document.visibilityState === "hidden") return;
    checking = true;
    try {
      const url = new URL("version.json", base);
      url.searchParams.set("check", String(Date.now()));
      const response = await fetch(url.href, { cache: "no-store", credentials: "same-origin" });
      if (!response.ok) return;
      const release = await response.json();
      if (!release || typeof release.version !== "string" || typeof release.entry !== "string") return;
      if (compareVersions(release.version, CURRENT_VERSION) <= 0) return;
      const target = new URL(release.entry, base);
      if (target.origin !== location.origin || !target.pathname.startsWith(base.pathname) ||
          !target.pathname.toLowerCase().endsWith(".html")) return;
      showUpdate(release.version, target);
    } catch (_) {
      /* La comprobación es opcional: nunca debe impedir que el juego arranque. */
    } finally {
      checking = false;
    }
  }

  if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register(new URL("sw.js", base).href, {
      scope: base.pathname,
      updateViaCache: "none"
    }).catch(function () {
      /* El juego continúa funcionando aunque el navegador no permita instalar el PWA. */
    });
  }

  checkForUpdates();
  window.setInterval(checkForUpdates, 5 * 60 * 1000);
  document.addEventListener("visibilitychange", function () {
    if (document.visibilityState === "visible") checkForUpdates();
  });
})();
</script>
"""
MANIFEST_TAG = '<link rel="manifest" href="./manifest.webmanifest">\n<meta name="theme-color" content="#1b1050">'

def main() -> int:
    if len(sys.argv) < 2:
        print('Usage: python install_updater.py "game.html" [current-version]')
        return 2

    game_path = Path(sys.argv[1])
    version = sys.argv[2] if len(sys.argv) > 2 else "1.5.6"

    if not game_path.is_file():
        print(f"File not found: {game_path}")
        return 2

    original = game_path.read_text(encoding="utf-8")
    if "</head>" not in original or "</body>" not in original:
        print("The HTML file does not contain the expected </head> and </body> tags. Nothing changed.")
        return 2

    if "RIUMAN WEB UPDATE CHECKER" in original:
        print("The update checker is already installed. Nothing changed.")
        return 0

    backup = game_path.with_suffix(game_path.suffix + ".backup")
    if not backup.exists():
        backup.write_bytes(game_path.read_bytes())

    updated = original
    if 'rel="manifest"' not in updated:
        updated = updated.replace("</head>", MANIFEST_TAG + "\n</head>", 1)

    updater = UPDATE_SCRIPT.replace("__CURRENT_VERSION__", version)
    updated = updated.replace("</body>", updater + "\n</body>", 1)

    if updated == original:
        print("No changes were necessary.")
        return 0

    game_path.write_text(updated, encoding="utf-8")
    print(f"Updated: {game_path}")
    print(f"Backup:  {backup}")
    print(f"Current version configured: {version}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
