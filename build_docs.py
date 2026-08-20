#!/usr/bin/env python3
"""Generate website quickstart/rulebook pages from game doc txt files."""
from __future__ import annotations

from pathlib import Path
import html

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "website"
DOCS = WEB / "docs"

NAV = """
			<nav class="site-nav" aria-label="Primary">
				<a href="index.html"{home}>Home</a>
				<a href="how-to-play.html"{howto}>How to Play</a>
				<a href="quickstart.html"{quick}>Quickstart</a>
				<a href="rulebook.html"{rules}>Rulebook</a>
				<a href="hints.html"{hints}>Hints</a>
				<a href="updates.html"{updates}>Updates</a>
				<a href="about.html"{about}>About</a>
				<a class="nav-cta" href="https://store.steampowered.com/app/4846410/" rel="noopener noreferrer">Wishlist</a>
			</nav>
"""

FOOTER = """
	<footer class="site-footer">
		<nav aria-label="Footer">
			<a href="index.html">Home</a>
			<a href="how-to-play.html">How to Play</a>
			<a href="quickstart.html">Quickstart</a>
			<a href="rulebook.html">Rulebook</a>
			<a href="hints.html">Hints</a>
			<a href="updates.html">Updates</a>
			<a href="about.html">About</a>
		</nav>
		<p>Thalenor's Descent — Tournament of Heroes</p>
	</footer>
"""


def nav(active: str) -> str:
	flags = {k: "" for k in ("home", "howto", "quick", "rules", "hints", "updates", "about")}
	flags[active] = ' aria-current="page"'
	return NAV.format(**flags)


def make_page(
	title: str,
	desc: str,
	active: str,
	kicker: str,
	h1: str,
	intro_html: str,
	body_html: str,
	download_href: str | None = None,
	download_label: str | None = None,
) -> str:
	dl = ""
	if download_href and download_label:
		dl = (
			f'<p class="doc-actions">'
			f'<a class="btn ghost" href="{download_href}" download>{html.escape(download_label)}</a>'
			f"</p>"
		)
	return f"""<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="utf-8">
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<title>{html.escape(title)}</title>
	<meta name="description" content="{html.escape(desc)}">
	<link rel="icon" href="assets/images/small-capsule.png" type="image/png">
	<link rel="stylesheet" href="styles.css">
</head>
<body>
	<a class="skip-link" href="#main">Skip to content</a>

	<header class="site-header">
		<div class="wrap site-header__inner">
			<a class="brand" href="index.html" aria-label="Thalenor's Descent home">
				<img src="assets/images/logo.png" alt="Thalenor's Descent" width="220" height="80" decoding="async">
			</a>
{nav(active)}
		</div>
	</header>

	<main id="main">
		<div class="wrap page-hero">
			<p class="kicker">{html.escape(kicker)}</p>
			<h1>{html.escape(h1)}</h1>
			<p>{intro_html}</p>
			{dl}
		</div>
		{body_html}
	</main>

{FOOTER}
</body>
</html>
"""


def main() -> None:
	DOCS.mkdir(parents=True, exist_ok=True)
	(DOCS / "PLAYER_GUIDE.txt").write_text(
		(ROOT / "PLAYER_GUIDE.txt").read_text(encoding="utf-8"), encoding="utf-8"
	)
	(DOCS / "PLAYERS_RULEBOOK.txt").write_text(
		(ROOT / "PLAYERS_RULEBOOK.txt").read_text(encoding="utf-8"), encoding="utf-8"
	)

	pages = [
		(
			"PLAYER_GUIDE.txt",
			"quickstart.html",
			"quick",
			"Quickstart — Thalenor's Descent",
			"Player guide / quickstart for Thalenor's Descent.",
			"Player guide",
			"Quickstart",
			'Get from first launch to a solid first tournament. For edge cases, see the <a href="rulebook.html">Rulebook</a>.',
			"Download PLAYER_GUIDE.txt",
		),
		(
			"PLAYERS_RULEBOOK.txt",
			"rulebook.html",
			"rules",
			"Rulebook — Thalenor's Descent",
			"Full players rulebook for Thalenor's Descent — the single source of truth for gameplay rules.",
			"Full rules",
			"Players Rulebook",
			'Authoritative rules for the current build. For a shorter on-ramp, see the <a href="quickstart.html">Quickstart</a>.',
			"Download PLAYERS_RULEBOOK.txt",
		),
	]

	for src_name, out_name, active, title, desc, kicker, h1, intro, dl_label in pages:
		text = (DOCS / src_name).read_text(encoding="utf-8")
		body = f'<div class="wrap doc-page"><pre class="doc-pre">{html.escape(text)}</pre></div>'
		out = make_page(
			title,
			desc,
			active,
			kicker,
			h1,
			intro,
			body,
			f"docs/{src_name}",
			dl_label,
		)
		(WEB / out_name).write_text(out, encoding="utf-8")
		print(f"wrote {out_name} ({len(out)} chars)")

	print("docs copied")


if __name__ == "__main__":
	main()
