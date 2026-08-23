#!/usr/bin/env python3
"""Harmonise le bloc d'en-tête (commentaires avant msgid) de tous les .po sous
locale/fr/LC_MESSAGES/user_manual/ selon le format :
    # Translation of <nom>.po to french
    # Traduction de <nom>.po en Français
    #
    <lignes de crédit existantes préservées telles quelles : Copyright, SPDX, "Nom <email>, années">

- Le nom de fichier source est extrait du bloc existant (motif kstars[...].po) ; sinon
  pris dans NAME_OVERRIDE (fichiers sans nom exploitable dans leur en-tête actuel).
- N'ajoute jamais de crédit non vérifiable : les fichiers de EXCLUDE (SPDX légal
  ou attribution collective "KDE Francophone" sans historique personnel) ne sont
  pas touchés.

Usage: scripts/harmonize_po_headers.py
"""
import re
from pathlib import Path

LC_MESSAGES = Path("locale/fr/LC_MESSAGES")

EXCLUDE = {
    "gnu-fdl.po", "legal-notice.po", "gpl-3.0.po",
    "404.po", "index.po", "sphinx.po",
    "ekos-mcp.po", "ekos-tilt-correction.po",
    "commands.po", "config.po",
}

ADD_BLOCK = {"doc-index.po", "ekos-scheduler-taskqueue.po", "fits-viewer-livestacker.po"}

NAME_OVERRIDE = {
    "user_manual.po": "kstars_user_manual.po",
    "introduction.po": "kstars_introduction.po",
    "ekos-analyze.po": "kstars_ekos-analyze.po",
    "ekos-tutorials.po": "kstars_ekos-tutorials.po",
    "doc-index.po": "kstars_doc-index.po",
    "ekos-scheduler-taskqueue.po": "kstars_ekos-scheduler-taskqueue.po",
    "fits-viewer-livestacker.po": "kstars_fits-viewer-livestacker.po",
    # Ces fichiers n'ont qu'un titre générique "Translation to French" (aucun nom
    # exploitable dans leur en-tête) : nom repris du Project-Id-Version, tirets
    # normalisés pour rester cohérent avec le reste du corpus.
    "ai-cosmicdist.po": "kstars_cosmicdist.po",
    "ai-epoch.po": "kstars_epoch.po",
    "ai-telescopes.po": "kstars_telescopes.po",
    "ekos-align.po": "kstars_ekos-align.po",
    "ekos-capture.po": "kstars_ekos-capture.po",
    "ekos-focus.po": "kstars_ekos-focus.po",
    "ekos-logs.po": "kstars_ekos-logs.po",
    "ekos-profile-editor.po": "kstars_ekos-profile-editor.po",
    "ekos-profile-wizard.po": "kstars_ekos-profile-wizard.po",
    "ekos-setup.po": "kstars_ekos-setup.po",
    "ekos.po": "kstars_ekos.po",
    "hips.po": "kstars_hips.po",
    "tool-obsplanner.po": "kstars_obsplanner.po",
}

NAME_RE = re.compile(r"kstars[\w-]+\.po|kstars[\w-]+", re.IGNORECASE)
CREDIT_EMAIL_RE = re.compile(r"<[^>]+@[^>]+>")
STEVE_LINE = "# steve <stax@ik.me>, 2022, 2023, 2024, 2025, 2026\n"


def sourcename(filename, header_lines):
    if filename in NAME_OVERRIDE:
        return NAME_OVERRIDE[filename]
    for line in header_lines:
        m = NAME_RE.search(line)
        if m:
            name = m.group(0)
            if not name.lower().endswith(".po"):
                name += ".po"
            return name
    return None


def is_credit_line(stripped: str) -> bool:
    return bool(
        CREDIT_EMAIL_RE.search(stripped)
        or stripped.startswith("# Copyright")
        or stripped.startswith("# SPDX-FileCopyrightText")
    )


def main() -> int:
    ok, skipped = [], []
    for po_path in sorted(LC_MESSAGES.rglob("*.po")):
        filename = po_path.name
        if filename in EXCLUDE:
            continue

        lines = po_path.read_text(encoding="utf-8").splitlines(keepends=True)
        idx = next(i for i, l in enumerate(lines) if l.startswith('msgid ""'))
        header, rest = lines[:idx], lines[idx:]

        if filename in ADD_BLOCK:
            name = NAME_OVERRIDE[filename]
            new_header = [
                f"# Translation of {name} to french\n",
                f"# Traduction de {name} en Français\n",
                "#\n",
                STEVE_LINE,
            ]
        else:
            name = sourcename(filename, header)
            if name is None:
                skipped.append(po_path)
                continue
            credits = [l for l in header if is_credit_line(l.rstrip("\n"))]
            new_header = [
                f"# Translation of {name} to french\n",
                f"# Traduction de {name} en Français\n",
                "#\n",
            ] + credits

        po_path.write_text("".join(new_header + rest), encoding="utf-8")
        ok.append((po_path, name))

    for p, n in ok:
        print(f"{p} -> {n}")
    if skipped:
        print("\nIGNORÉS (pas de nom extrait) :")
        for p in skipped:
            print(p)
    print(f"\n{len(ok)} fichier(s) harmonisé(s), {len(skipped)} ignoré(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
