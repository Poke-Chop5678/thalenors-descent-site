#!/usr/bin/env python3
"""Generate website quickstart/rulebook pages from game doc txt files."""
from __future__ import annotations

from pathlib import Path
import html
import re

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "website"
DOCS = WEB / "docs"

SEP_EQ = re.compile(r"^={10,}\s*$")
SEP_DASH = re.compile(r"^-{10,}\s*$")
ALL_CAPS = re.compile(r"^[A-Z0-9][A-Z0-9 /:&()'.,§+\-–—×]+$")

NAV_TEMPLATE = """
			<nav class="site-nav" aria-label="Primary">
				<a href="index.html"{home}>Home</a>
				<details class="nav-group"{guides_open}>
					<summary{guides_sum}>Guides</summary>
					<div class="nav-group__menu">
						<a href="how-to-play.html"{howto}>How to Play</a>
						<a href="quickstart.html"{quick}>Quickstart</a>
						<a href="rulebook.html"{rules}>Rulebook</a>
						<a href="hints.html"{hints}>Hints</a>
					</div>
				</details>
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

GUIDE_PAGES = {"howto", "quick", "rules", "hints"}


def nav(active: str) -> str:
	flags = {
		k: ""
		for k in ("home", "howto", "quick", "rules", "hints", "updates", "about", "guides_open", "guides_sum")
	}
	if active in flags:
		flags[active] = ' aria-current="page"'
	if active in GUIDE_PAGES:
		flags["guides_open"] = " open"
		flags["guides_sum"] = ' aria-current="page"'
	return NAV_TEMPLATE.format(**flags)


def _bold_lead(text: str) -> str:
	text = re.sub(r"\s+", " ", text).strip()
	m = re.match(r"^(.+?)\s+[—–]\s+(.+)$", text)
	if m and len(m.group(1).split()) <= 8:
		return f"<strong>{html.escape(m.group(1).strip())}</strong> — {html.escape(m.group(2).strip())}"
	# ALL-CAPS title then sentence: "START A RUN From the main menu..."
	m = re.match(r"^((?:[A-Z0-9][A-Z0-9/&+'’.-]*\s+){0,6}[A-Z0-9][A-Z0-9/&+'’.-]*)\s+([A-Z][a-z].+)$", text)
	if m and m.group(1) == m.group(1).upper():
		return f"<strong>{html.escape(m.group(1))}</strong> — {html.escape(m.group(2))}"
	m = re.match(r"^([A-Za-z][^:]{0,40}):\s+(.+)$", text)
	if m and len(m.group(1).split()) <= 5 and len(m.group(2)) > 12:
		return f"<strong>{html.escape(m.group(1).strip())}</strong>: {html.escape(m.group(2).strip())}"
	return html.escape(text)


def _line_indent(raw: str) -> tuple[int, str]:
	expanded = raw.expandtabs(4)
	indent = len(expanded) - len(expanded.lstrip(" "))
	return indent, expanded.strip()


def txt_to_article_html(text: str) -> str:
	"""Convert game ASCII docs into readable article HTML (one-level lists + sections)."""
	raw_lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
	# Drop top ==== banner ====
	i = 0
	n = len(raw_lines)
	if i < n and SEP_EQ.match(raw_lines[i].strip()):
		i += 1
		while i < n and not SEP_EQ.match(raw_lines[i].strip()):
			i += 1
		if i < n:
			i += 1
	lines = raw_lines[i:]

	parts: list[str] = ['<article class="doc-article">']
	# Open list state: None | ("ul"|"ol", items[])
	list_kind: str | None = None
	list_items: list[str] = []

	def close_list() -> None:
		nonlocal list_kind, list_items
		if not list_kind:
			return
		parts.append(f"<{list_kind}>")
		for it in list_items:
			parts.append(f"<li>{it}</li>")
		parts.append(f"</{list_kind}>")
		list_kind = None
		list_items = []

	def open_list(kind: str) -> None:
		nonlocal list_kind
		if list_kind and list_kind != kind:
			close_list()
		list_kind = kind

	def add_item(kind: str, body: str) -> None:
		open_list(kind)
		list_items.append(body)

	idx = 0
	total = len(lines)
	while idx < total:
		raw = lines[idx]
		stripped = raw.strip()

		if SEP_EQ.match(stripped):
			close_list()
			break

		if SEP_DASH.match(stripped):
			close_list()
			j = idx + 1
			while j < total and not lines[j].strip():
				j += 1
			if j < total and not SEP_DASH.match(lines[j].strip()):
				title = lines[j].strip()
				j += 1
				while j < total and not lines[j].strip():
					j += 1
				if j < total and SEP_DASH.match(lines[j].strip()):
					j += 1
				parts.append(f"<h2>{html.escape(title)}</h2>")
				idx = j
				continue
			idx += 1
			continue

		if not stripped:
			idx += 1
			continue

		indent, content = _line_indent(raw)

		# Subsection headings
		if indent <= 2 and len(content) < 80 and ALL_CAPS.match(content) and not re.match(r"^\d+\.", content):
			close_list()
			parts.append(f"<h3>{html.escape(content)}</h3>")
			idx += 1
			continue
		if (
			indent <= 2
			and len(content) < 70
			and content[0].isupper()
			and not content.endswith((".", "!", "?"))
			and not re.match(r"^[-·•\dA-Z]\.|^\d+", content)
			and ("(" in content or content.isupper())
			and not content.lower().startswith(("for ", "this ", "the ", "you ", "a ", "an ", "keep "))
		):
			close_list()
			parts.append(f"<h3>{html.escape(content)}</h3>")
			idx += 1
			continue

		# Letter blocks
		m_let = re.match(r"^([A-Z])\.\s+(.*)$", content)
		if m_let and indent <= 5:
			close_list()
			parts.append(
				f'<p class="doc-letter"><strong>{html.escape(m_let.group(1))}. '
				f"{html.escape(m_let.group(2))}</strong></p>"
			)
			idx += 1
			continue

		# Numbered items (top-level)
		m_num = re.match(r"^(\d+)\.\s+(.*)$", content)
		if m_num and indent <= 6:
			body_parts = [m_num.group(2).strip()]
			idx += 1
			# Pull wrapped lines + nested 1)/- lines into this item as nested HTML
			nested_html = ""
			nested_ol: list[str] = []
			nested_ul: list[str] = []
			while idx < total:
				nr = lines[idx]
				if not nr.strip():
					# allow blank inside item if indented content continues
					k = idx + 1
					while k < total and not lines[k].strip():
						k += 1
					if k >= total:
						break
					pi, pc = _line_indent(lines[k])
					if pi >= 3:
						idx += 1
						continue
					break
				ni, nc = _line_indent(nr)
				if ni <= 2 and (SEP_DASH.match(nc) or SEP_EQ.match(nc) or ALL_CAPS.match(nc)):
					break
				if re.match(r"^\d+\.\s+", nc) and ni <= 4:
					break
				if re.match(r"^[A-Z]\.\s+", nc) and ni <= 5:
					break
				m_n = re.match(r"^(\d+)\)\s+(.*)$", nc)
				if m_n and ni >= 3:
					# flush prior plain wraps into body
					sub = m_n.group(2).strip()
					idx += 1
					while idx < total:
						sr = lines[idx]
						if not sr.strip():
							break
						si, sc = _line_indent(sr)
						if si <= ni:
							break
						if re.match(r"^(\d+)\)\s+", sc) or re.match(r"^[-·•]\s+", sc) or re.match(r"^\d+\.\s+", sc):
							break
						sub += " " + sc
						idx += 1
					# following dash choices under this sub-step
					sub_choices: list[str] = []
					while idx < total:
						sr = lines[idx]
						if not sr.strip():
							break
						si, sc = _line_indent(sr)
						mb = re.match(r"^[-·•]\s+(.*)$", sc)
						if mb and si > ni:
							choice = mb.group(1).strip()
							idx += 1
							while idx < total:
								cr = lines[idx]
								if not cr.strip():
									break
								ci, cc = _line_indent(cr)
								if ci <= si:
									break
								if re.match(r"^[-·•]\s+", cc) or re.match(r"^\d+[.)]\s+", cc):
									break
								choice += " " + cc
								idx += 1
							sub_choices.append(choice)
							continue
						break
					if sub_choices:
						nested_ol.append(
							html.escape(sub)
							+ "<ul>"
							+ "".join(f"<li>{_bold_lead(c)}</li>" for c in sub_choices)
							+ "</ul>"
						)
					else:
						nested_ol.append(html.escape(sub))
					continue
				mb = re.match(r"^[-·•]\s+(.*)$", nc)
				if mb and ni >= 3:
					sub = mb.group(1).strip()
					idx += 1
					while idx < total:
						sr = lines[idx]
						if not sr.strip():
							break
						si, sc = _line_indent(sr)
						if si <= ni:
							break
						if re.match(r"^[-·•]\s+", sc) or re.match(r"^\d+[.)]\s+", sc):
							break
						sub += " " + sc
						idx += 1
					nested_ul.append(sub)
					continue
				if ni >= 3:
					body_parts.append(nc)
					idx += 1
					continue
				break
			body = _bold_lead(" ".join(body_parts))
			if body_parts and len(body_parts) == 1 and body_parts[0] == body_parts[0].upper() and len(body_parts[0]) < 60:
				body = f"<strong>{html.escape(body_parts[0])}</strong>"
			if nested_ol:
				body += "<ol>" + "".join(f"<li>{x}</li>" for x in nested_ol) + "</ol>"
			if nested_ul:
				body += "<ul>" + "".join(f"<li>{_bold_lead(x)}</li>" for x in nested_ul) + "</ul>"
			add_item("ol", body)
			continue

		# Bullets (allow deeper indent under A./B. blocks)
		m_bull = re.match(r"^[-·•]\s+(.*)$", content)
		if m_bull and indent <= 12:
			body_parts = [m_bull.group(1).strip()]
			idx += 1
			nested_ol: list[str] = []
			nested_ul: list[str] = []
			while idx < total:
				nr = lines[idx]
				if not nr.strip():
					k = idx + 1
					while k < total and not lines[k].strip():
						k += 1
					if k >= total:
						break
					pi, pc = _line_indent(lines[k])
					if pi > indent:
						idx += 1
						continue
					break
				ni, nc = _line_indent(nr)
				if ni <= 2 and (SEP_DASH.match(nc) or SEP_EQ.match(nc) or ALL_CAPS.match(nc)):
					break
				if re.match(r"^[-·•]\s+", nc) and ni <= indent:
					break
				if re.match(r"^\d+\.\s+", nc) and ni <= 4:
					break
				if re.match(r"^[A-Z]\.\s+", nc) and ni <= 5:
					break
				m_n = re.match(r"^(\d+)[.)]\s+(.*)$", nc)
				if m_n and ni > indent:
					sub = m_n.group(2).strip()
					idx += 1
					while idx < total:
						sr = lines[idx]
						if not sr.strip():
							break
						si, sc = _line_indent(sr)
						if si <= ni:
							break
						if re.match(r"^(\d+)[.)]\s+", sc) or re.match(r"^[-·•]\s+", sc):
							break
						sub += " " + sc
						idx += 1
					sub_choices: list[str] = []
					while idx < total:
						sr = lines[idx]
						if not sr.strip():
							break
						si, sc = _line_indent(sr)
						mb2 = re.match(r"^[-·•]\s+(.*)$", sc)
						if mb2 and si > ni:
							choice = mb2.group(1).strip()
							idx += 1
							while idx < total:
								cr = lines[idx]
								if not cr.strip():
									break
								ci, cc = _line_indent(cr)
								if ci <= si:
									break
								if re.match(r"^[-·•]\s+", cc) or re.match(r"^\d+[.)]\s+", cc):
									break
								choice += " " + cc
								idx += 1
							sub_choices.append(choice)
							continue
						break
					if sub_choices:
						nested_ol.append(
							html.escape(sub)
							+ "<ul>"
							+ "".join(f"<li>{_bold_lead(c)}</li>" for c in sub_choices)
							+ "</ul>"
						)
					else:
						nested_ol.append(html.escape(sub))
					continue
				mb2 = re.match(r"^[-·•]\s+(.*)$", nc)
				if mb2 and ni > indent:
					sub = mb2.group(1).strip()
					idx += 1
					while idx < total:
						sr = lines[idx]
						if not sr.strip():
							break
						si, sc = _line_indent(sr)
						if si <= ni:
							break
						if re.match(r"^[-·•]\s+", sc) or re.match(r"^\d+[.)]\s+", sc):
							break
						sub += " " + sc
						idx += 1
					nested_ul.append(sub)
					continue
				if ni > indent:
					body_parts.append(nc)
					idx += 1
					continue
				break
			body = _bold_lead(" ".join(body_parts))
			if nested_ol:
				body += "<ol>" + "".join(f"<li>{x}</li>" for x in nested_ol) + "</ol>"
			if nested_ul:
				body += "<ul>" + "".join(f"<li>{_bold_lead(x)}</li>" for x in nested_ul) + "</ul>"
			add_item("ul", body)
			continue

		# Flow diagram lines
		if content.startswith("→") or content.startswith("->"):
			close_list()
			flow = content
			idx += 1
			while idx < total:
				nr = lines[idx]
				if not nr.strip():
					break
				ni, nc = _line_indent(nr)
				if SEP_DASH.match(nc) or SEP_EQ.match(nc) or re.match(r"^[-·•\dA-Z]", nc) or nc.startswith("→"):
					break
				if ni <= 2 and ALL_CAPS.match(nc):
					break
				flow += " " + nc
				idx += 1
			parts.append(f'<p class="doc-flow">{html.escape(flow)}</p>')
			continue
		if indent >= 2 and idx + 1 < total:
			ni, nc = _line_indent(lines[idx + 1]) if lines[idx + 1].strip() else (0, "")
			if nc.startswith("→") or nc.startswith("->"):
				close_list()
				parts.append(f'<p class="doc-flow-label"><strong>{html.escape(content)}</strong></p>')
				idx += 1
				continue

		# Paragraph (may span multiple non-list lines)
		close_list()
		para = [content]
		idx += 1
		while idx < total:
			nr = lines[idx]
			if not nr.strip():
				break
			ni, nc = _line_indent(nr)
			if SEP_DASH.match(nc) or SEP_EQ.match(nc):
				break
			if ni <= 2 and ALL_CAPS.match(nc):
				break
			if re.match(r"^[-·•]\s+", nc) or re.match(r"^\d+\.\s+", nc) or re.match(r"^[A-Z]\.\s+", nc):
				break
			if nc.startswith("→"):
				break
			para.append(nc)
			idx += 1
		parts.append(f"<p>{html.escape(' '.join(para))}</p>")

	close_list()
	parts.append("</article>")
	return "\n".join(parts)


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
		<div class="wrap doc-page">
			{body_html}
		</div>
	</main>

{FOOTER}
</body>
</html>
"""


NAV_BLOCK_RE = re.compile(r'<nav class="site-nav" aria-label="Primary">.*?</nav>', re.DOTALL)
FOOTER_NAV_RE = re.compile(r'<footer class="site-footer">.*?</footer>', re.DOTALL)


def active_for_file(name: str) -> str:
	return {
		"index.html": "home",
		"how-to-play.html": "howto",
		"quickstart.html": "quick",
		"rulebook.html": "rules",
		"hints.html": "hints",
		"updates.html": "updates",
		"about.html": "about",
	}.get(name, "home")


def patch_static_pages() -> None:
	for path in WEB.glob("*.html"):
		if path.name in ("quickstart.html", "rulebook.html"):
			continue
		text = path.read_text(encoding="utf-8")
		active = active_for_file(path.name)
		text2, n1 = NAV_BLOCK_RE.subn(nav(active).strip(), text, count=1)
		text3, n2 = FOOTER_NAV_RE.subn(FOOTER.strip(), text2, count=1)
		if n1 or n2:
			path.write_text(text3, encoding="utf-8")
			print(f"patched nav/footer: {path.name}")


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
		article = txt_to_article_html(text)
		out = make_page(title, desc, active, kicker, h1, intro, article, f"docs/{src_name}", dl_label)
		(WEB / out_name).write_text(out, encoding="utf-8")
		print(f"wrote {out_name} ({len(out)} chars)")

	patch_static_pages()
	print("docs copied + nav patched")


if __name__ == "__main__":
	main()
