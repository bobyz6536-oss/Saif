"""
Genera tutti i video delle 10 scene con Higgsfield API.
Uso: python generate.py
Output: file .mp4 nella cartella output/
"""

import os
import json
import time
import higgsfield_client as hf

API_KEY = os.getenv("HF_API_KEY", "afa68010-37cc-42ad-acee-af31b22e6460")
API_SECRET = os.getenv("HF_API_SECRET", "afa68010-37cc-42ad-acee-af31b22e6460")

os.environ["HF_API_KEY"] = API_KEY
os.environ["HF_API_SECRET"] = API_SECRET

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

SCENES = [
    {
        "id": "01-hook",
        "duration": 3,
        "prompt": (
            "Flat 2D cartoon animation, bold graphic style, clean white background. "
            "Three bold black text lines appear one by one with dramatic slam effect: "
            "'Nessun aereo.' then 'Nessuna nave.' then 'Solo quello che hai in casa.' "
            "Each word slams into frame with a quick bounce. Final frame zooms in fast "
            "on a confused cartoon Italian man holding random household objects "
            "(bicycle, kite, catapult). Bold red and yellow accents. Quick smash cuts. "
            "9:16 vertical video."
        ),
    },
    {
        "id": "02-bicicletta",
        "duration": 7,
        "prompt": (
            "Flat 2D cartoon animation. Cheerful cartoon Italian man in a striped shirt "
            "and red helmet riding a bicycle on a road. Animated infographic world map "
            "in background showing Italy to Australia with a dotted red line path. "
            "Bold text overlays: '20 km/h' and '800 ore'. Man pedals confidently until "
            "he reaches a cartoon blue ocean shoreline and stops with a comedic skid, "
            "staring at the water with an exaggerated shocked expression, arms raised. "
            "The bicycle sinks cartoon-style with a bubble. Bold flat colors, white "
            "background with blue sea panel. 9:16 vertical video."
        ),
    },
    {
        "id": "03-materassino",
        "duration": 8,
        "prompt": (
            "Flat 2D cartoon animation. Cartoon Italian man lying on a bright pink "
            "inflatable pool mattress floating on a flat cartoon Mediterranean Sea. "
            "Animated infographic shows '0.5 nodi' with a slow arrow. A cartoonish "
            "shark fin circles nearby. A blazing sun with a sweating face radiates "
            "heat lines. The man looks miserable and sunburned. Bold text overlay: "
            "'400 anni'. Small dotted map shows he is still visible from the Italian "
            "coast. Comedic wilting animation. Flat pastel sea, white background. "
            "9:16 vertical video."
        ),
    },
    {
        "id": "04-aquilone",
        "duration": 8,
        "prompt": (
            "Flat 2D cartoon animation. Cartoon Italian man holding a massive rainbow "
            "diamond kite, being lifted off the ground. Animated wind arrows on a flat "
            "cartoon sky background. Bold infographic text: '15 km/h'. Man soars "
            "confidently, then wind arrows suddenly flip direction with a comical "
            "WHOOSH sound effect graphic. Flat animated map shows trajectory curving "
            "south toward a cartoon 'LIBIA' label with palm trees and desert. Man "
            "arrives confused in the desert, kite tangled in a palm tree. 9:16 vertical video."
        ),
    },
    {
        "id": "05-catapulta",
        "duration": 7,
        "prompt": (
            "Flat 2D cartoon animation. Medieval wooden catapult in a cartoon Italian "
            "backyard. Bold infographic: 'Gittata: 300m' vs 'Distanza: 16.000km' with "
            "a tiny vs huge comparison bar. Cartoon Italian man in a helmet climbs into "
            "the catapult bucket. LAUNCH, exaggerated arc trajectory, lands with a "
            "CRASH in the neighbor's garden next door, crushing flower beds. Neighbor "
            "old Italian woman stares in horror. A tiny cartoon police car with "
            "flashing lights approaches from the street. Bold red and blue flash "
            "overlays. White background, green garden. 9:16 vertical video."
        ),
    },
    {
        "id": "06-pallone",
        "duration": 7,
        "prompt": (
            "Flat 2D cartoon animation. Colorful striped hot air balloon floating over "
            "a flat cartoon ocean. Bold infographic: '30 km/h, 22 giorni'. Suddenly "
            "a PSSSSSS sound graphic appears, the balloon deflates cartoon-style and "
            "plummets. Man falls in freefall with exaggerated wide eyes. Cut to: man "
            "landing with a BOING on the pink inflatable mattress still floating in "
            "the ocean. The mattress man waves awkwardly. New man waves back. Two "
            "miserable men on a tiny mattress in the middle of the ocean. 9:16 vertical video."
        ),
    },
    {
        "id": "07-skateboard",
        "duration": 7,
        "prompt": (
            "Flat 2D cartoon animation. Cartoon Italian man on a red skateboard with "
            "a large firework garden rocket taped to the back with duct tape. He lights "
            "the fuse. WHOOOOSH, 4 seconds of blazing fire, speed lines, the man grins. "
            "Abrupt stop, smoke puff. Bold text: '200 metri da casa'. He looks back and "
            "his house is still clearly visible. His eyebrows are gone, replaced with "
            "scorched marks. He touches his forehead with a confused expression. Bold "
            "text: '$0 spesi' with a green checkmark. 9:16 vertical video."
        ),
    },
    {
        "id": "08-socrate",
        "duration": 7,
        "prompt": (
            "Flat 2D cartoon animation. Ancient Greek philosopher Socrates appears from "
            "off-screen in classic toga and sandals, completely uninvited. He surveys "
            "the scene: the broken catapult, the deflated balloon, the scorched "
            "skateboard. He strokes his beard with a knowing expression. He points at "
            "the man and a speech bubble appears with bold italic text: "
            "'Perche vuoi raggiungere l altra parte del mondo se non sai ancora dove sei tu?' "
            "The man sits on the ground with a stunned expression. White background, "
            "dramatic single spotlight. 9:16 vertical video."
        ),
    },
    {
        "id": "09-aereo",
        "duration": 4,
        "prompt": (
            "Flat 2D cartoon animation. Clean bright airport terminal scene. Cartoon "
            "man stands at a ticket counter. Bold text price tag: '$400'. He clicks "
            "a button on a laptop, ticket printed. Cut to: man sitting in a "
            "comfortable airplane seat with AC vent blowing and a meal tray in front "
            "of him. He looks straight at camera with a deadpan expression and shrugs. "
            "Bold green checkmark overlays. Infographic: '16 ore. Fine.' 9:16 vertical video."
        ),
    },
    {
        "id": "10-finale-cta",
        "duration": 2,
        "prompt": (
            "Flat 2D cartoon animation. Bold white text on solid bright red background: "
            "'Con cosa raggiungeresti l altra parte del mondo?' Text animates in with "
            "a bouncy pop effect. Below: comment bubble icon with animated typing dots. "
            "Bold arrows pointing down. Quick flash of 6 objects in a grid: bicycle, "
            "mattress, kite, catapult, balloon, skateboard. Final freeze on red. 9:16 vertical video."
        ),
    },
]


def generate_scene(scene: dict) -> str:
    print(f"\n[{scene['id']}] Invio richiesta...")
    result = hf.subscribe(
        "bytedance/seedance/v1/lite/text-to-video",
        arguments={
            "prompt": scene["prompt"],
            "duration": scene["duration"],
            "aspect_ratio": "9:16",
            "resolution": "720p",
        },
    )

    if not result or "video" not in result:
        raise RuntimeError(f"Risposta inattesa: {result}")

    video_url = result["video"]["url"]
    out_path = os.path.join(OUTPUT_DIR, f"{scene['id']}.mp4")

    import httpx
    with httpx.stream("GET", video_url) as r:
        r.raise_for_status()
        with open(out_path, "wb") as f:
            for chunk in r.iter_bytes():
                f.write(chunk)

    print(f"  Salvato: {out_path}")
    return out_path


def main():
    print("=== Generazione video 'Oggetti Casuali' ===")
    print(f"Output: {OUTPUT_DIR}\n")

    results = {}
    for scene in SCENES:
        try:
            path = generate_scene(scene)
            results[scene["id"]] = {"status": "ok", "path": path}
        except Exception as e:
            print(f"  ERRORE: {e}")
            results[scene["id"]] = {"status": "error", "error": str(e)}
        time.sleep(2)

    summary_path = os.path.join(OUTPUT_DIR, "results.json")
    with open(summary_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n=== Completato ===")
    ok = sum(1 for r in results.values() if r["status"] == "ok")
    print(f"{ok}/{len(SCENES)} scene generate con successo.")
    print(f"Riepilogo: {summary_path}")


if __name__ == "__main__":
    main()
