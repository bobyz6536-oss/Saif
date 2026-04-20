"""
Pipeline: Nano Banana 2 genera immagine per scena → Kling AI anima in video.
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

CHARACTER_PREFIX = (
    "3D photorealistic transparent human figure, semi-transparent frosted glass body "
    "with full ivory skeleton clearly visible inside, realistic detailed eyes. "
    "White seamless studio background, soft shadows. "
)

SCENES = [
    {
        "id": "01-hook",
        "duration": 5,
        "image_prompt": (
            CHARACTER_PREFIX +
            "Standing in T-pose center frame, arms spread wide, skeleton fully displayed. "
            "Bold black text overlays: 'Nessun aereo.' 'Nessuna nave.' "
            "Dramatic cinematic lighting. Vertical 9:16 composition."
        ),
        "video_prompt": (
            "Character raises arms dramatically, text lines slam into frame one by one "
            "with shockwave effect. Skeleton rattles inside glass shell. Quick zoom in."
        ),
    },
    {
        "id": "02-bicicletta",
        "duration": 5,
        "image_prompt": (
            CHARACTER_PREFIX +
            "Riding a bright red bicycle on a flat road, skeleton legs visible pedaling. "
            "Italian countryside background, dotted red line on world map overlay "
            "Italy to Australia. Bold text: '20 km/h — 800 ore'. Vertical 9:16."
        ),
        "video_prompt": (
            "Character pedals confidently then reaches ocean shoreline, slams brakes, "
            "skeleton jolts forward. Arms spread in shock, bicycle tips into water with splash."
        ),
    },
    {
        "id": "03-materassino",
        "duration": 5,
        "image_prompt": (
            CHARACTER_PREFIX +
            "Lying flat on a bright pink inflatable pool mattress floating on calm sea. "
            "Skeleton slumping from exhaustion. Cartoon shark fin nearby. Blazing sun above. "
            "Bold text: '400 anni'. Vertical 9:16."
        ),
        "video_prompt": (
            "Character lies miserable on mattress drifting slowly. Shark circles. "
            "Sun beats down. Character stares deadpan at camera. Slow drift camera movement."
        ),
    },
    {
        "id": "04-aquilone",
        "duration": 5,
        "image_prompt": (
            CHARACTER_PREFIX +
            "Gripping strings of a massive colorful rainbow kite, being lifted into sky. "
            "Skeleton arms stretched upward. Wind arrows visible. Bold text: '15 km/h'. "
            "Clear blue sky background. Vertical 9:16."
        ),
        "video_prompt": (
            "Character soars upward confidently then wind arrows flip direction. "
            "Character spins wildly, skeleton rotating inside glass shell. Crashes into desert sand."
        ),
    },
    {
        "id": "05-catapulta",
        "duration": 5,
        "image_prompt": (
            CHARACTER_PREFIX +
            "Sitting inside a medieval wooden catapult bucket, wearing a helmet over glass skull. "
            "Italian backyard setting. Bold infographic: 'Gittata: 300m vs 16.000km'. "
            "Vertical 9:16."
        ),
        "video_prompt": (
            "Catapult launches character in high arc across screen, skeleton rattling in flight. "
            "Crashes into neighbor's garden. Old Italian woman gasps. Police car approaches."
        ),
    },
    {
        "id": "06-pallone",
        "duration": 5,
        "image_prompt": (
            CHARACTER_PREFIX +
            "Standing in basket of large colorful striped hot air balloon over ocean. "
            "Skeleton upright and hopeful. Bold text: '30 km/h — 22 giorni'. "
            "Blue ocean below. Vertical 9:16."
        ),
        "video_prompt": (
            "Balloon deflates with PSSSSS, character freefalls, skeleton arms flailing. "
            "Lands on pink mattress in ocean. Second skeleton figure already on mattress waves awkwardly."
        ),
    },
    {
        "id": "07-skateboard",
        "duration": 5,
        "image_prompt": (
            CHARACTER_PREFIX +
            "Crouching on red skateboard with large rocket duct-taped to back. "
            "Skeleton bracing inside glass body. Fuse lit, ready to launch. "
            "Suburban street background. Vertical 9:16."
        ),
        "video_prompt": (
            "Rocket fires 4 seconds of blazing orange fire, speed lines, glass body glows orange. "
            "Abrupt stop with smoke puff. Character touches forehead — eyebrows scorched off. "
            "Deadpan stare at camera. Bold text: '200 metri da casa'."
        ),
    },
    {
        "id": "08-socrate",
        "duration": 5,
        "image_prompt": (
            CHARACTER_PREFIX +
            "Sitting on ground among broken catapult, deflated balloon, scorched skateboard. "
            "Ancient Greek philosopher Socrates in white toga stands nearby pointing one finger. "
            "Dramatic spotlight. White background. Vertical 9:16."
        ),
        "video_prompt": (
            "Socrates walks in uninvited, surveys wreckage, strokes beard. Raises finger. "
            "Speech bubble: 'Perche vuoi raggiungere l altra parte del mondo se non sai dove sei tu?' "
            "Character's skeleton slumps. Long silence."
        ),
    },
    {
        "id": "09-aereo",
        "duration": 5,
        "image_prompt": (
            CHARACTER_PREFIX +
            "Standing at bright airport ticket counter, laptop open, ticket printing. "
            "Bold price tag: '$400'. Clean modern airport background. Vertical 9:16."
        ),
        "video_prompt": (
            "Character taps laptop, ticket prints. Cut to character relaxed in airplane seat, "
            "AC vent blowing, meal tray in front. Looks at camera with deadpan shrug. "
            "Bold green text: '16 ore. Fine.'"
        ),
    },
    {
        "id": "10-finale-cta",
        "duration": 3,
        "image_prompt": (
            CHARACTER_PREFIX +
            "Arms raised wide, skeleton fully displayed, against solid bright red background. "
            "Bold white text: 'Con cosa raggiungeresti l altra parte del mondo?' "
            "Comment bubble below with typing dots. Vertical 9:16."
        ),
        "video_prompt": (
            "Character pops into frame, raises arms. Text bounces in. "
            "Grid of 6 object icons flashes. Character points directly at viewer. Freeze frame."
        ),
    },
]


def generate_image(scene: dict) -> str:
    """Genera immagine scena con Nano Banana 2. Restituisce URL immagine."""
    print(f"  [NanoBanana] Generando immagine...")
    result = hf.subscribe(
        "jobs/nano-banana-2",
        arguments={
            "prompt": scene["image_prompt"],
            "aspect_ratio": "9:16",
        },
    )
    # Estrai URL immagine dal risultato
    img_url = (
        result.get("image_url") or
        result.get("url") or
        (result.get("images") or [{}])[0].get("url") or
        result.get("output", {}).get("image_url")
    )
    if not img_url:
        raise RuntimeError(f"Nessun URL immagine nel risultato: {result}")
    print(f"  Immagine: {img_url}")
    return img_url


def generate_video(scene: dict, image_url: str) -> str:
    """Anima l'immagine con Kling image-to-video. Restituisce path MP4."""
    print(f"  [Kling] Animando immagine in video...")
    result = hf.subscribe(
        "jobs/image2video",
        arguments={
            "prompt": scene["video_prompt"],
            "image_url": image_url,
            "duration": scene["duration"],
            "aspect_ratio": "9:16",
            "model": "kling2.6",
        },
    )
    video_url = (
        result.get("video_url") or
        result.get("url") or
        result.get("output", {}).get("video_url")
    )
    if not video_url:
        raise RuntimeError(f"Nessun URL video nel risultato: {result}")

    out_path = os.path.join(OUTPUT_DIR, f"{scene['id']}.mp4")
    with httpx.stream("GET", video_url, follow_redirects=True) as r:
        r.raise_for_status()
        with open(out_path, "wb") as f:
            for chunk in r.iter_bytes():
                f.write(chunk)
    print(f"  Salvato: {out_path}")
    return out_path


def main():
    print("=== Pipeline: NanaBanana → Kling AI ===\n")

    results = {}
    for scene in SCENES:
        print(f"\n[{scene['id']}]")
        try:
            img_url = generate_image(scene)
            time.sleep(1)
            path = generate_video(scene, img_url)
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


if __name__ == "__main__":
    main()
