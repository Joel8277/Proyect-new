# Riuman PWA auto-update bundle

This bundle prepares the browser edition of Riuman for GitHub Pages and installation as a Progressive Web App (PWA).

## Included files

- `index.html` — stable launcher; always loads the entry listed in `version.json`.
- `version.json` — release version and exact HTML filename.
- `sw.js` — service worker with network-first navigation and offline fallback after the first successful load.
- `manifest.webmanifest` — PWA install metadata.
- `riuman-icon.svg` — app icon.
- `install_updater.py` — safely injects an update checker into the current single-file game HTML and creates a backup first.

## Setup

1. Upload `index.html`, `version.json`, `sw.js`, `manifest.webmanifest`, and `riuman-icon.svg` to the **root** of `Joel8277/Proyect-new`.
2. Run the patcher on the browser HTML currently in the repository root:

   ```bash
   python install_updater.py "New_Proyect Browser Versión 1_5_6.html" 1.5.6
   ```

   It creates a `.backup` file and leaves all game code and `riuman.*` storage logic intact, adding only the manifest link and update-check script.
3. Commit the changed HTML file and the PWA files to `main`.
4. In GitHub, open **Settings → Pages**. Under **Build and deployment**, choose **Deploy from a branch**, select `main` and `/(root)`, then save.
5. After GitHub Pages publishes the site, open the repository's Pages URL. The PWA launcher is the root URL.

## Publishing future browser versions

For each release:

1. Upload the new HTML file to the repository root.
2. Run `install_updater.py` on that new HTML file and pass its version number.
3. Update `version.json` with the new version and exact filename in `entry`.
4. Commit the release to `main`.

Players who use the HTTPS Pages site will be directed to the latest release at launch. Older browser builds that have the update checker show an **Actualizar** notice while the game is open.

## Important limitations

- The updater does not delete or rewrite the game's existing `riuman.*` localStorage keys. Data stays available when the player continues using the same browser and the same HTTPS Pages origin.
- A downloaded HTML opened as `file://` cannot register a service worker or replace itself. Automatic updates apply to the HTTPS GitHub Pages version, not a standalone local HTML file.
- Moving from a locally downloaded HTML (`file://`) to GitHub Pages changes the storage origin. The old local save does not automatically move; use the game's account export/import feature if a player needs to transfer it.
- The Android APK is separate and is not updated by this browser PWA.
