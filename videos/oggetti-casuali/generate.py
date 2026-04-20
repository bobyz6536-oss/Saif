"""
Genera 10 scene video con Kling AI 2.6 (text-to-video) via Higgsfield API.
Uso: python generate.py
Output: file .mp4 in output/
"""

import os
import sys
import json
import time
import httpx
import higgsfield_client as hf

API_KEY    = os.getenv("HF_API_KEY",    "1c3e9ae8-a47e-4c62-8ebf-786868ed46ad")
API_SECRET = os.getenv("HF_API_SECRET", "c5d1f864ee91c6390bf39398223718701c8c1d8f10961488e02da58c6eebae0a")
os.environ["HF_API_KEY"]    = API_KEY
os.environ["HF_API_SECRET"] = API_SECRET

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

ENDPOINT = "kling-video/v2.6/pro/text-to-video"

CHARACTER = (
    "3D photorealistic transparent human figure, semi-transparent frosted glass body "
    "with full ivory skeleton clearly visible inside, realistic eyes. "
    "White seamless studio background, soft cinematic lighting. "
)

SCENES = [
    {
        "id": "01-hook",
        "duration": "5",
        "prompt": CHARACTER + (
            "Character stands center frame arms spread wide, skeleton fully displayed. "
            "Bold black text slams in one line at a time: 'Nessun aereo.' 'Nessuna nave.' "
            "'Solo quello che hai in casa.' Each impact sends shockwave through glass body. "
            "Final frame: dramatic shrug, skeleton rattling. Vertical 9:16."
        ),
    },
    {
        "id": "02-bicicletta",
        "duration": "5",
        "prompt": CHARACTER + (
            "Riding a bright red bicycle, skeleton legs pumping visibly inside glass body. "
            "Italian countryside, world map overlay with dotted line Italy to Australia. "
            "Bold text '20 km/h — 800 ore'. Reaches ocean, slams brakes, skeleton jolts forward, "
            "shocked expression, bicycle sinks with splash. Vertical 9:16."
        ),
    },
    {
        "id": "03-materassino",
        "duration": "5",
        "prompt": CHARACTER + (
            "Lying exhausted on a bright pink inflatable mattress floating on calm sea. "
            "Skeleton slumping inside glass body. Cartoon shark fin circling. Blazing sun above. "
            "Bold text '400 anni'. Deadpan eyes stare at camera. Slow ocean drift. Vertical 9:16."
        ),
    },
    {
        "id": "04-aquilone",
        "duration": "5",
        "prompt": CHARACTER + (
            "Gripping a massive colorful kite strings, lifted into sky, skeleton arms stretched up. "
            "Wind arrows flip direction suddenly — WHOOSH — character spins wildly, "
            "skeleton rotating inside glass shell. Crashes into desert sand near palm tree labeled LIBIA. "
            "Vertical 9:16."
        ),
    },
    {
        "id": "05-catapulta",
        "duration": "5",
        "prompt": CHARACTER + (
            "Sitting in medieval catapult bucket wearing helmet over glass skull. "
            "Bold text 'Gittata: 300m vs 16.000km'. LAUNCH — high arc, skeleton rattling in flight. "
            "Crashes into neighbor's garden, old Italian woman gasps, police car arrives. Vertical 9:16."
        ),
    },
    {
        "id": "06-pallone",
        "duration": "5",
        "prompt": CHARACTER + (
            "Standing in basket of colorful hot air balloon over ocean. Bold text '30 km/h — 22 giorni'. "
            "Balloon deflates with PSSSSS, character freefalls, skeleton arms flailing. "
            "Lands BOING on pink mattress in ocean where second skeleton figure already sits and waves. "
            "Vertical 9:16."
        ),
    },
    {
        "id": "07-skateboard",
        "duration": "5",
        "prompt": CHARACTER + (
            "On red skateboard with garden rocket duct-taped behind. WHOOOOSH — 4 seconds blazing fire, "
            "glass body glowing orange, skeleton rattling at speed. Abrupt stop, smoke puff. "
            "House still visible in background. Eyebrows scorched off. Bold '$0 spesi'. Vertical 9:16."
        ),
    },
    {
        "id": "08-socrate",
        "duration": "5",
        "prompt": CHARACTER + (
            "Sitting on ground among broken catapult, deflated balloon, scorched skateboard. "
            "Socrates in white toga walks in uninvited, strokes beard, raises finger. "
            "Speech bubble: 'Perche vuoi raggiungere l altra parte del mondo se non sai dove sei tu?' "
            "Skeleton slumps. Dramatic spotlight silence. Vertical 9:16."
        ),
    },
    {
        "id": "09-aereo",
        "duration": "5",
        "prompt": CHARACTER + (
            "At bright airport ticket counter, taps laptop, ticket prints — bold '$400'. "
            "Cut to relaxed in airplane seat, AC vent blowing, meal tray in front. "
            "Deadpan shrug at camera. Bold green '16 ore. Fine.' Vertical 9:16."
        ),
    },
    {
        "id": "10-finale-cta",
        "duration": "5",
        "prompt": CHARACTER + (
            "Against solid bright red background, arms raised wide, skeleton fully displayed. "
            "Bold white text bounces in: 'Con cosa raggiungeresti l altra parte del mondo?' "
            "Comment bubble with typing dots. Character points directly at viewer. Freeze frame. Vertical 9:16."
        ),
    },
]


def download(url: str, path: str):
    with httpx.stream("GET", url, follow_redirects=True, timeout=60) as r:
        r.raise_for_status()
        with open(path, "wb") as f:
            for chunk in r.iter_bytes():
                f.write(chunk)


def generate_scene(scene: dict) -> str:
    print(f"  Invio a Kling 2.6...")
    result = hf.subscribe(
        ENDPOINT,
        arguments={
            "prompt": scene["prompt"],
            "duration": scene["duration"],
            "aspect_ratio": "9:16",
            "cfg_scale": 0.5,
        },
    )
    video_url = (
        result.get("video_url") or
        result.get("url") or
        (result.get("videos") or [{}])[0].get("url") or
        result.get("output", {}).get("video_url")
    )
    if not video_url:
        raise RuntimeError(f"Nessun URL video: {result}")

    out_path = os.path.join(OUTPUT_DIR, f"{scene['id']}.mp4")
    download(video_url, out_path)
    print(f"  Salvato: {out_path}")
    return out_path


def main():
    print(f"=== Kling AI 2.6 — 10 scene ===\n")
    results = {}
    for scene in SCENES:
        print(f"\n[{scene['id']}]")
        try:
            path = generate_scene(scene)
            results[scene["id"]] = {"status": "ok", "path": path}
        except Exception as e:
            print(f"  ERRORE: {e}")
            results[scene["id"]] = {"status": "error", "error": str(e)}
        time.sleep(3)

    with open(os.path.join(OUTPUT_DIR, "results.json"), "w") as f:
        json.dump(results, f, indent=2)

    ok = sum(1 for r in results.values() if r["status"] == "ok")
    print(f"\n=== Completato: {ok}/{len(SCENES)} ===")


if __name__ == "__main__":
    main()
