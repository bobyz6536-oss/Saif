"""
Genera tutti i video delle 10 scene con Higgsfield API.
Usa image-to-video con il personaggio di riferimento (reference.jpg).

Uso:
  python generate.py                      # usa reference.jpg nella stessa cartella
  python generate.py --text-only          # solo text-to-video, ignora reference

Output: file .mp4 nella cartella output/
"""

import os
import sys
import json
import time
import httpx
import higgsfield_client as hf

API_KEY = os.getenv("HF_API_KEY", "afa68010-37cc-42ad-acee-af31b22e6460")
API_SECRET = os.getenv("HF_API_SECRET", "afa68010-37cc-42ad-acee-af31b22e6460")

os.environ["HF_API_KEY"] = API_KEY
os.environ["HF_API_SECRET"] = API_SECRET

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")
REFERENCE_IMG = os.path.join(SCRIPT_DIR, "reference.jpg")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Prefisso stile personaggio da aggiungere a ogni prompt
CHARACTER_PREFIX = (
    "3D photorealistic transparent human figure, semi-transparent frosted glass body "
    "with full ivory skeleton clearly visible inside, realistic eyes. "
    "White seamless studio background, soft shadows. Same character as reference image. "
)

SCENES = [
    {
        "id": "01-hook",
        "duration": 5,
        "prompt": (
            "Character stands in T-pose center frame, arms spread wide, skeleton fully "
            "displayed. Large bold black text slams into frame one line at a time: "
            "'Nessun aereo.' — 'Nessuna nave.' — 'Solo quello che hai in casa.' "
            "Each text impact creates a shockwave ripple through the glass body. "
            "Final frame: character shrugs dramatically, skeleton rattling inside "
            "glass shell. Dramatic cinematic lighting. 9:16 vertical."
        ),
    },
    {
        "id": "02-bicicletta",
        "duration": 7,
        "prompt": (
            "Character riding a bright red bicycle on a flat stylized road. "
            "Skeleton legs pumping visibly inside glass body. World map infographic "
            "overlay: dotted red line Italy to Australia, bold text '20 km/h — 800 ore'. "
            "Reaches cartoon blue ocean shoreline, slams brakes, skeleton jolts forward "
            "comically inside glass shell. Character stares at the water, huge realistic "
            "eyes wide in shock, arms spread. Bicycle tips into ocean with cartoon SPLASH. "
            "9:16 vertical."
        ),
    },
    {
        "id": "03-materassino",
        "duration": 8,
        "prompt": (
            "Character lying flat on a bright pink inflatable pool mattress floating "
            "on a stylized Mediterranean Sea. Skeleton visibly slumping inside glass body "
            "from exhaustion. Cartoonish shark fin circling. Blazing cartoon sun above. "
            "Bold infographic text: '0.5 nodi — 400 anni'. Glass body has a sunburned "
            "pink tint. A dotted map shows character still 5km from Italian coast. "
            "Deadpan realistic eyes staring at camera. Gentle ocean drift camera. "
            "9:16 vertical."
        ),
    },
    {
        "id": "04-aquilone",
        "duration": 8,
        "prompt": (
            "Character gripping strings of a massive colorful diamond kite, being lifted "
            "off the ground. Skeleton arms stretched upward visibly inside glass body. "
            "Bold infographic wind arrows on clear sky. Text overlay: '15 km/h — 44 giorni'. "
            "Wind arrows suddenly flip — WHOOSH graphic — character spins, skeleton "
            "rotating wildly inside glass shell. Flat map shows arc toward desert labeled "
            "'LIBIA'. Character crash-lands in sand, glass body dusty, skeleton crumpled. "
            "9:16 vertical."
        ),
    },
    {
        "id": "05-catapulta",
        "duration": 7,
        "prompt": (
            "Character climbing into a medieval wooden catapult bucket in Italian backyard. "
            "Bold infographic: 'Gittata: 300m' vs 'Distanza: 16.000km'. Character puts on "
            "helmet over glass skull — skeleton visible. LAUNCH — flies in high arc, "
            "skeleton rattling visibly inside glass body. Lands with CRASH in neighbor's "
            "garden, crushing cartoon flowers. Old Italian neighbor woman gasps. Tiny "
            "police car with flashing lights approaches. Red and blue flashes on glass body. "
            "Character waves sheepishly. 9:16 vertical."
        ),
    },
    {
        "id": "06-pallone",
        "duration": 7,
        "prompt": (
            "Character standing in basket of a large colorful striped hot air balloon "
            "over stylized ocean. Bold infographic: '30 km/h — 22 giorni'. Skeleton "
            "upright and hopeful. Sudden PSSSSS deflation — balloon crumples, character "
            "free-falls, skeleton arms and legs flailing wildly inside glass body. "
            "Crash BOING onto pink inflatable mattress in the ocean where another "
            "identical transparent skeleton figure already sits and waves. "
            "Two skeleton figures on tiny mattress, both stare deadpan at camera. "
            "9:16 vertical."
        ),
    },
    {
        "id": "07-skateboard",
        "duration": 7,
        "prompt": (
            "Character riding a red skateboard with a large garden firework rocket "
            "duct-taped to the back. Character crouches, skeleton visibly bracing. "
            "Fuse lit — WHOOOOSH — blazing orange fire, speed lines, glass body glowing "
            "orange, skeleton rattling at extreme speed. Abrupt STOP, smoke puff. "
            "Bold text: '200 metri da casa' — house still visible in background. "
            "Character touches forehead — eyebrow area of glass body scorched black, "
            "skeleton intact. Deadpan stare at camera. Bold green: '$0 spesi'. "
            "Skeleton does defeated shrug. 9:16 vertical."
        ),
    },
    {
        "id": "08-socrate",
        "duration": 7,
        "prompt": (
            "Transparent skeleton character sits on ground surrounded by broken catapult, "
            "deflated balloon, scorched skateboard. Ancient Greek philosopher Socrates — "
            "solid opaque figure in white toga — walks in from frame edge, stroking beard. "
            "He surveys wreckage. Raises one finger. Dramatic speech bubble: "
            "'Perche vuoi raggiungere l altra parte del mondo se non sai ancora dove sei tu?' "
            "Slow zoom onto Socrates' knowing face. Cut to skeleton character's eyes "
            "going wide. Character slowly sits, skeleton slumping. Dramatic spotlight. "
            "9:16 vertical."
        ),
    },
    {
        "id": "09-aereo",
        "duration": 5,
        "prompt": (
            "Character at a bright modern airport ticket counter. Character taps laptop, "
            "ticket prints — bold text '$400'. Skeleton hand reaches for ticket. "
            "Cut to: same character in comfortable airplane seat, AC vent blowing, "
            "meal tray visible. Skeleton visibly relaxed and reclined inside glass body. "
            "Character looks directly at camera with deadpan eyes and slow shrug. "
            "Bold green overlays: '16 ore. Fine.' Soft warm cabin lighting on glass body. "
            "9:16 vertical."
        ),
    },
    {
        "id": "10-finale-cta",
        "duration": 3,
        "prompt": (
            "Solid bright red background. Character pops into center frame, raises both "
            "glass arms wide, skeleton fully displayed. Bold white text bounces in: "
            "'Con cosa raggiungeresti l altra parte del mondo?' Below: animated comment "
            "bubble with typing dots. Grid of 6 tiny icons (bicycle, mattress, kite, "
            "catapult, balloon, skateboard). Character gives final wide-eyed stare "
            "and points directly at viewer. Freeze frame. 9:16 vertical."
        ),
    },
]


def upload_reference(img_path: str) -> str:
    """Carica l'immagine di riferimento su Higgsfield e restituisce l'URL."""
    print(f"Upload reference image: {img_path}")
    result = hf.upload_image(img_path)
    url = result.get("url") or result.get("image_url") or result.get("uri")
    if not url:
        raise RuntimeError(f"Upload fallito, risposta: {result}")
    print(f"  Reference URL: {url}")
    return url


def download_video(url: str, out_path: str):
    with httpx.stream("GET", url, follow_redirects=True) as r:
        r.raise_for_status()
        with open(out_path, "wb") as f:
            for chunk in r.iter_bytes():
                f.write(chunk)


def generate_scene(scene: dict, reference_url: str | None) -> str:
    print(f"\n[{scene['id']}] Invio richiesta...")

    full_prompt = CHARACTER_PREFIX + scene["prompt"]

    args = {
        "prompt": full_prompt,
        "duration": scene["duration"],
        "aspect_ratio": "9:16",
        "resolution": "720",
    }

    if reference_url:
        # image-to-video: Higgsfield attiva questo mode quando image_url è presente
        args["image_url"] = reference_url
        endpoint = "bytedance/seedance/v1/lite/image-to-video"
    else:
        endpoint = "bytedance/seedance/v1/lite/text-to-video"

    result = hf.subscribe(endpoint, arguments=args)

    if not result or "video" not in result:
        raise RuntimeError(f"Risposta inattesa: {result}")

    video_url = result["video"]["url"]
    out_path = os.path.join(OUTPUT_DIR, f"{scene['id']}.mp4")
    download_video(video_url, out_path)
    print(f"  Salvato: {out_path}")
    return out_path


def main():
    text_only = "--text-only" in sys.argv

    print("=== Generazione video 'Oggetti Casuali' ===")
    print(f"Output: {OUTPUT_DIR}\n")

    # Upload reference image
    reference_url = None
    if not text_only:
        if os.path.exists(REFERENCE_IMG):
            try:
                reference_url = upload_reference(REFERENCE_IMG)
            except Exception as e:
                print(f"ATTENZIONE: upload reference fallito ({e}), uso text-to-video.")
        else:
            print(
                f"ATTENZIONE: reference.jpg non trovato in {SCRIPT_DIR}\n"
                "  Salva il personaggio come 'reference.jpg' nella stessa cartella.\n"
                "  Oppure usa --text-only per generare senza reference.\n"
            )

    results = {}
    for scene in SCENES:
        try:
            path = generate_scene(scene, reference_url)
            results[scene["id"]] = {"status": "ok", "path": path}
        except Exception as e:
            print(f"  ERRORE: {e}")
            results[scene["id"]] = {"status": "error", "error": str(e)}
        time.sleep(2)

    summary_path = os.path.join(OUTPUT_DIR, "results.json")
    with open(summary_path, "w") as f:
        json.dump(results, f, indent=2)

    ok = sum(1 for r in results.values() if r["status"] == "ok")
    print(f"\n=== Completato: {ok}/{len(SCENES)} scene ===")
    print(f"Riepilogo: {summary_path}")


if __name__ == "__main__":
    main()
