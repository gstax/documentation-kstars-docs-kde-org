#!/usr/bin/env python3
"""Convertit un .po Sphinx du dépôt (locale/fr/LC_MESSAGES/...) au format
attendu côté SVN summit KDE : nom de fichier aplati (kstars_docs[_<sousdossier>]___<nom>.po)
et ajout du commentaire "#. +> trunk5" devant chaque groupe de références.

Usage: scripts/svn_delivery_convert.py locale/fr/LC_MESSAGES/user_manual/ekos-guide.po [...]
Sortie: svn-delivery/fr/<nom_svn>.po
"""
import sys
from pathlib import Path

LC_MESSAGES = Path("locale/fr/LC_MESSAGES")
OUT_DIR = Path("svn-delivery/fr")


def svn_name(po_path: Path) -> str:
    rel = po_path.relative_to(LC_MESSAGES)
    parts = rel.parts
    if len(parts) == 1:
        return f"kstars_docs_{parts[0]}"
    subdir, name = parts[0], parts[1]
    return f"kstars_docs_{subdir}___{name}"


def add_trunk5_tags(lines: list[str]) -> list[str]:
    out = []
    prev_was_ref = False
    for line in lines:
        is_ref = line.startswith("#:")
        if is_ref and not prev_was_ref:
            out.append("#. +> trunk5\n")
        out.append(line)
        prev_was_ref = is_ref
    return out


def convert(po_path: Path) -> Path:
    lines = po_path.read_text(encoding="utf-8").splitlines(keepends=True)
    converted = add_trunk5_tags(lines)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / svn_name(po_path)
    out_path.write_text("".join(converted), encoding="utf-8")
    return out_path


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 1
    for arg in argv:
        po_path = Path(arg)
        out_path = convert(po_path)
        print(f"{po_path} -> {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
