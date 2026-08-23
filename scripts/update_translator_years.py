#!/usr/bin/env python3
"""Normalise la ligne de commentaire traducteur "# steve <stax@ik.me>, ..." dans
tous les .po sous locale/fr/LC_MESSAGES/ : uniformise le format (casse, virgules,
domaine e-mail) et ajoute 2025, 2026 à la liste des années.

Usage: scripts/update_translator_years.py
"""
import re
from pathlib import Path

LC_MESSAGES = Path("locale/fr/LC_MESSAGES")
TARGET_LINE = "# steve <stax@ik.me>, 2022, 2023, 2024, 2025, 2026\n"
PATTERN = re.compile(r"^# [Ss]teve,? <stax@ik\.\w+>,? [0-9][0-9, ]*\.?\s*$")


def main() -> int:
    changed = []
    for po_path in sorted(LC_MESSAGES.rglob("*.po")):
        lines = po_path.read_text(encoding="utf-8").splitlines(keepends=True)
        touched = False
        for i, line in enumerate(lines):
            if PATTERN.match(line.rstrip("\n")):
                if line != TARGET_LINE:
                    lines[i] = TARGET_LINE
                    touched = True
        if touched:
            po_path.write_text("".join(lines), encoding="utf-8")
            changed.append(po_path)
    for p in changed:
        print(p)
    print(f"\n{len(changed)} fichier(s) modifié(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
