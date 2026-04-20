"""
Monta le 10 scene generate in un draft CapCut pronto all'uso.
Uso: python capcut_assemble.py
Il draft appare automaticamente in CapCut alla riapertura.

Prerequisiti:
  pip install pycapcut
  Le scene MP4 devono essere in output/ (generate da generate.py)
"""

import os
import sys

try:
    import pycapcut as cc
except ImportError:
    print("Installa pyCapCut: pip install pycapcut")
    sys.exit(1)

# --- Configurazione ---
# Cambia questo percorso con la tua cartella CapCut Drafts:
#   Mac:     ~/Movies/CapCut/User Data/Projects/com.lveditor.draft
#   Windows: C:/Users/<nome>/AppData/Local/CapCut/User Data/Projects/com.lveditor.draft
CAPCUT_DRAFTS = os.path.expanduser(
    "~/Movies/CapCut/User Data/Projects/com.lveditor.draft"
)

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
DRAFT_NAME = "Oggetti Casuali - Come raggiungere l'altra parte del mondo"

# Scene in ordine con durata in secondi
SCENES = [
    ("01-hook",         3),
    ("02-bicicletta",   7),
    ("03-materassino",  8),
    ("04-aquilone",     8),
    ("05-catapulta",    7),
    ("06-pallone",      7),
    ("07-skateboard",   7),
    ("08-socrate",      7),
    ("09-aereo",        4),
    ("10-finale-cta",   2),
]

# Testo dei sottotitoli per ogni scena (voiceover)
SUBTITLES = {
    "01-hook": [
        (0.0,  1.0, "Devi raggiungere l'altra parte del mondo."),
        (1.0,  2.0, "Nessun aereo. Nessuna nave."),
        (2.0,  3.0, "Solo quello che hai in casa. Partiamo."),
    ],
    "02-bicicletta": [
        (0.0,  1.5, "Bicicletta. Velocità media: 20 km/h."),
        (1.5,  3.0, "Distanza dall'Italia all'Australia: 16.000 km."),
        (3.0,  4.5, "Tempo stimato: 800 ore. 33 giorni senza dormire."),
        (4.5,  6.0, "Problemi: il mare. La bici non galleggia."),
        (6.0,  7.0, "Piano fallito al chilometro 1.200."),
    ],
    "03-materassino": [
        (0.0,  2.0, "Materassino gonfiabile. Soluzione al problema del mare."),
        (2.0,  4.0, "Corrente media Mediterraneo: 0.5 nodi."),
        (4.0,  5.5, "Tempo stimato: 400 anni."),
        (5.5,  7.0, "Problemi: squali. Tempeste. Il sole. La fame."),
        (7.0,  8.0, "Piano fallito il giorno due."),
    ],
    "04-aquilone": [
        (0.0,  2.0, "Aquilone gigante. Vento medio Mediterraneo: 15 km/h."),
        (2.0,  4.0, "Se tutto va bene... Velocità: 15 km/h. 44 giorni."),
        (4.0,  6.0, "Problemi: il vento cambia direzione."),
        (6.0,  8.0, "Sei finito in Libia. Non era il piano."),
    ],
    "05-catapulta": [
        (0.0,  2.0, "Catapulta medievale. Gittata massima: 300 metri."),
        (2.0,  4.0, "Distanza dall'Italia all'Australia: 16.000 km."),
        (4.0,  5.5, "Servono 53.333 catapulte in fila."),
        (5.5,  7.0, "Sei atterrato nel giardino del vicino. Ha chiamato la polizia."),
    ],
    "06-pallone": [
        (0.0,  2.0, "Pallone aerostatico. Finalmente qualcosa che vola."),
        (2.0,  4.0, "Velocità media: 30 km/h. 22 giorni."),
        (4.0,  5.5, "Problemi: il gas finisce."),
        (5.5,  7.0, "Sei sceso sul materassino. Almeno non sei solo."),
    ],
    "07-skateboard": [
        (0.0,  2.0, "Skateboard con un razzo da giardino attaccato dietro."),
        (2.0,  3.5, "Velocità reale: per 4 secondi."),
        (3.5,  5.0, "Sei a 200 metri da casa. Record personale."),
        (5.0,  7.0, "$0 spesi. Sopracciglia: perse."),
    ],
    "08-socrate": [
        (0.0,  2.0, "A questo punto arriva Socrate. Nessuno lo ha chiamato."),
        (2.0,  4.5, "Perché vuoi raggiungere l'altra parte del mondo..."),
        (4.5,  6.5, "...se non sai ancora dove sei tu?"),
        (6.5,  7.0, "[sussurro] Aveva ragione. Insopportabile."),
    ],
    "09-aereo": [
        (0.0,  2.0, "La soluzione era semplice. Comprare un biglietto aereo."),
        (2.0,  4.0, "$400. 16 ore. Aria condizionata. Pasto incluso."),
    ],
    "10-finale-cta": [
        (0.0,  2.0, "Con cosa raggiungeresti l'altra parte del mondo?"),
    ],
}


def check_output_files():
    missing = []
    for scene_id, _ in SCENES:
        path = os.path.join(OUTPUT_DIR, f"{scene_id}.mp4")
        if not os.path.exists(path):
            missing.append(path)
    return missing


def build_srt(scenes):
    """Genera un file SRT con i sottotitoli di tutte le scene."""
    lines = []
    idx = 1
    cursor = 0.0

    for scene_id, duration in scenes:
        subs = SUBTITLES.get(scene_id, [])
        for start_rel, end_rel, text in subs:
            start_abs = cursor + start_rel
            end_abs = cursor + end_rel

            def fmt(t):
                h = int(t // 3600)
                m = int((t % 3600) // 60)
                s = int(t % 60)
                ms = int((t - int(t)) * 1000)
                return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

            lines.append(str(idx))
            lines.append(f"{fmt(start_abs)} --> {fmt(end_abs)}")
            lines.append(text)
            lines.append("")
            idx += 1
        cursor += duration

    return "\n".join(lines)


def main():
    print("=== Montaggio CapCut — Oggetti Casuali ===\n")

    # Verifica file MP4
    missing = check_output_files()
    if missing:
        print("Mancano questi file MP4 (esegui prima generate.py):")
        for p in missing:
            print(f"  {p}")
        sys.exit(1)

    # Salva SRT
    srt_path = os.path.join(OUTPUT_DIR, "sottotitoli.srt")
    srt_content = build_srt(SCENES)
    with open(srt_path, "w", encoding="utf-8") as f:
        f.write(srt_content)
    print(f"Sottotitoli generati: {srt_path}")

    # Crea draft CapCut
    if not os.path.isdir(CAPCUT_DRAFTS):
        print(f"\nATTENZIONE: cartella CapCut Drafts non trovata:\n  {CAPCUT_DRAFTS}")
        print("Modifica la variabile CAPCUT_DRAFTS nello script con il percorso corretto.")
        sys.exit(1)

    draft_folder = cc.DraftFolder(CAPCUT_DRAFTS)
    # 9:16 verticale = 1080x1920
    script = draft_folder.create_draft(DRAFT_NAME, 1080, 1920)

    # Aggiungi traccia video
    script.add_track(cc.TrackType.video)

    # Aggiungi ogni scena in sequenza
    cursor_ms = 0
    for scene_id, duration_s in SCENES:
        mp4_path = os.path.abspath(os.path.join(OUTPUT_DIR, f"{scene_id}.mp4"))
        duration_ms = duration_s * 1000
        seg = cc.VideoSegment(
            mp4_path,
            cc.Timerange(cursor_ms, duration_ms),
        )
        script.add_segment(seg)
        print(f"  + {scene_id} ({duration_s}s)")
        cursor_ms += duration_ms

    # Importa sottotitoli
    script.import_srt(
        srt_path,
        track_name="Sottotitoli",
        text_style=cc.TextStyle(
            size=6.0,
            color=(1.0, 1.0, 1.0),
            auto_wrapping=True,
            max_line_width=0.85,
        ),
    )

    script.save()
    print(f"\nDraft salvato: '{DRAFT_NAME}'")
    print("Riapri CapCut — il progetto è pronto nel tab Bozze.")


if __name__ == "__main__":
    main()
