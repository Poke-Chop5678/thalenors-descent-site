"""Copy updated Steam capsule/logo art into website/assets/images."""
from __future__ import annotations

from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "website" / "Steam images"
DST = ROOT / "website" / "assets" / "images"

# Source filename in Steam images/ → site asset used by HTML
MAPPING: dict[str, str] = {
	"Header Capsule.png": "header-capsule.png",
	"Small Capsule.png": "small-capsule.png",
	"TD Logo (1).png": "logo.png",
	"Main Capsule.png": "main-capsule.png",
	"Vertical Capsule.png": "vertical-capsule.png",
	"Library Header.png": "hero-banner.png",
	"library capsule.png": "library-capsule.png",
	"Icon.png": "icon.png",
}


def main() -> None:
	if not SRC.is_dir():
		raise SystemExit(f"missing source folder: {SRC}")
	DST.mkdir(parents=True, exist_ok=True)
	for src_name, dst_name in MAPPING.items():
		sp = SRC / src_name
		dp = DST / dst_name
		if not sp.is_file():
			print(f"SKIP missing: {src_name}")
			continue
		shutil.copy2(sp, dp)
		print(f"OK {src_name} -> {dst_name} ({dp.stat().st_size} bytes)")
	# Showcase figure: reuse library capsule (no separate board shot in Steam set)
	lib = SRC / "library capsule.png"
	if lib.is_file():
		dp = DST / "gameplay-board.png"
		shutil.copy2(lib, dp)
		print(f"OK library capsule.png -> gameplay-board.png ({dp.stat().st_size} bytes)")


if __name__ == "__main__":
	main()
