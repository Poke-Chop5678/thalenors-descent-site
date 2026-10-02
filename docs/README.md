# Thalenor's Descent — public landing page

Static site for **GitHub Pages**. Keep this in the public repo `thalenors-descent-site`. Do **not** make the Godot game repository public just for the website.

## Live URL

https://poke-chop5678.github.io/thalenors-descent-site/

## Pages

| File | Tab |
|------|-----|
| `index.html` | Home |
| `how-to-play.html` | How to Play (hub) |
| `quickstart.html` | Quickstart (`PLAYER_GUIDE.txt`) |
| `rulebook.html` | Rulebook (`PLAYERS_RULEBOOK.txt`) |
| `hints.html` | Hints |
| `updates.html` | Updates |
| `about.html` | About |

Plain-text downloads live in `docs/PLAYER_GUIDE.txt` and `docs/PLAYERS_RULEBOOK.txt`.

### Refresh docs from the game

When you update the game's guide or rulebook:

```powershell
python website/build_docs.py
```

That recopies `PLAYER_GUIDE.txt` / `PLAYERS_RULEBOOK.txt` into `website/docs/` and regenerates the Quickstart / Rulebook HTML pages.

## Upload checklist (repo root)

```
index.html
how-to-play.html
quickstart.html
rulebook.html
hints.html
updates.html
about.html
styles.css
.nojekyll
docs/
  PLAYER_GUIDE.txt
  PLAYERS_RULEBOOK.txt
assets/
  fonts/game_font.ttf
  images/… (pngs used by the site)
```

Skip PSD files and huge unused art (`party-art.png`).

## GitHub Pages

1. Upload / commit the files above to `main`.
2. **Settings → Pages** → Deploy from branch `main`, folder `/ (root)`.
3. Hard-refresh after 1–2 minutes (`Ctrl+F5`).
