"""
Pipeline: Nanobanana (OpenRouter + Gemini Flash Image) → Kling AI 2.6 image-to-video
Uso: python generate.py
Output: file .mp4 in output/
"""

import os
import sys
import json
import time
import base64
import tempfile
import httpx
import higgsfield_client as hf

HF_API_KEY    = os.getenv("HF_API_KEY",    "1c3e9ae8-a47e-4c62-8ebf-786868ed46ad")
HF_API_SECRET = os.getenv("HF_API_SECRET", "c5d1f864ee91c6390bf39398223718701c8c1d8f10961488e02da58c6eebae0a")
NB_API_KEY    = os.getenv("NB_API_KEY",    "f5ecea0d5100fb4587b9ff4881ef813f")

os.environ["HF_API_KEY"]    = HF_API_KEY
os.environ["HF_API_SECRET"] = HF_API_SECRET

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

KLING_ENDPOINT = "kling-video/v2.6/pro/image-to-video"

CHARACTER = (
    "3D photorealistic transparent human figure, semi-transparent frosted glass body "
    "with full ivory skeleton clearly visible inside, realistic detailed eyes. "
    "White seamless studio background, soft cinematic lighting. "
)

SCENES = [
    {
        "id": "01-hook",
        "image_prompt": CHARACTER + (
            "Standing center frame arms spread wide, skeleton fully displayed. "
            "Bold black text overlays: 'Nessun aereo.' 'Nessuna nave.' "
            "Dramatic cinematic spotlight. Vertical 9:16 composition."
        ),
        "video_prompt": (
            "Character raises arms dramatically, text lines slam into frame with shockwave effect "
            "rippling through glass body. Skeleton rattles inside. Quick zoom in. Cinematic."
        ),
    },
    {
        "id": "02-bicicletta",
        "image_prompt": CHARACTER + (
            "Riding a bright red bicycle on Italian road, skeleton legs pumping visibly. "
            "World map overlay with dotted line Italy to Australia. Bold text '20 km/h'. "
            "Vertical 9:16."
        ),
        "video_prompt": (
            "Character pedals confidently then reaches ocean, slams brakes, skeleton jolts forward, "
            "shocked expression arms spread wide, bicycle sinks into water with cartoon splash."
        ),
    },
    {
        "id": "03-materassino",
        "image_prompt": CHARACTER + (
            "Lying exhausted on bright pink inflatable mattress floating on calm Mediterranean sea. "
            "Skeleton slumping, shark fin nearby, blazing sun. Bold text '400 anni'. "
            "Vertical 9:16."
        ),
        "video_prompt": (
            "Character lies miserable on drifting mattress. Shark fin circles slowly. "
            "Sun beats down. Deadpan eyes stare at camera. Gentle ocean sway."
        ),
    },
    {
        "id": "04-aquilone",
        "image_prompt": CHARACTER + (
            "Gripping strings of massive colorful diamond kite being lifted into clear blue sky. "
            "Skeleton arms stretched upward. Wind arrows visible. Vertical 9:16."
        ),
        "video_prompt": (
            "Character soars upward then wind arrows suddenly flip direction. "
            "Character spins wildly, skeleton rotating inside glass shell. "
            "Crashes into desert sand near palm tree."
        ),
    },
    {
        "id": "05-catapulta",
        "image_prompt": CHARACTER + (
            "Sitting inside medieval wooden catapult bucket, wearing helmet over glass skull. "
            "Italian backyard. Bold infographic 'Gittata: 300m vs 16.000km'. Vertical 9:16."
        ),
        "video_prompt": (
            "Catapult launches character in wide arc, skeleton rattling in flight. "
            "Crashes into neighbor's garden crushing flowers. Old Italian woman gasps. "
            "Police car approaches with flashing lights."
        ),
    },
    {
        "id": "06-pallone",
        "image_prompt": CHARACTER + (
            "Standing in basket of large colorful striped hot air balloon over ocean. "
            "Skeleton upright and hopeful. Bold text '30 km/h'. Vertical 9:16."
        ),
        "video_prompt": (
            "Balloon suddenly deflates PSSSSS, character freefalls with skeleton arms flailing. "
            "Lands with BOING on pink mattress in ocean. "
            "Second skeleton figure already there waves awkwardly."
        ),
    },
    {
        "id": "07-skateboard",
        "image_prompt": CHARACTER + (
            "Crouching on red skateboard with large garden rocket duct-taped behind. "
            "Skeleton bracing inside glass body, fuse lit. Suburban street. Vertical 9:16."
        ),
        "video_prompt": (
            "Rocket fires 4 seconds of blazing orange fire, glass body glowing, skeleton rattling. "
            "Abrupt stop with smoke puff. House still visible behind. "
            "Character touches forehead — eyebrows scorched off. Deadpan stare at camera."
        ),
    },
    {
        "id": "08-socrate",
        "image_prompt": CHARACTER + (
            "Sitting on ground among broken catapult, deflated balloon, scorched skateboard. "
            "Ancient Greek philosopher Socrates in white toga stands nearby pointing one finger. "
            "Dramatic spotlight. Vertical 9:16."
        ),
        "video_prompt": (
            "Socrates walks in uninvited, surveys wreckage, strokes beard, raises finger. "
            "Speech bubble appears: 'Perche vuoi raggiungere l altra parte del mondo se non sai dove sei tu?' "
            "Character's skeleton slowly slumps. Long dramatic silence."
        ),
    },
    {
        "id": "09-aereo",
        "image_prompt": CHARACTER + (
            "Standing at bright modern airport ticket counter, laptop open, ticket printing. "
            "Bold price tag '$400'. Clean airport background. Vertical 9:16."
        ),
        "video_prompt": (
            "Character taps laptop, ticket prints. Cut to sitting relaxed in airplane seat, "
            "AC vent blowing, meal tray in front. Deadpan shrug at camera. "
            "Bold green text '16 ore. Fine.' overlays."
        ),
    },
    {
        "id": "10-finale-cta",
        "image_prompt": CHARACTER + (
            "Arms raised wide against solid bright red background, skeleton fully displayed. "
            "Bold white text: 'Con cosa raggiungeresti l altra parte del mondo?' "
            "Comment bubble with typing dots below. Vertical 9:16."
        ),
        "video_prompt": (
            "Character pops into frame raising arms wide. Text bounces in. "
            "Character points directly at viewer with dramatic zoom. Freeze frame."
        ),
    },
]


def generate_image(scene: dict) -> str:
    """Genera immagine con Seedream v4 (Higgsfield). Restituisce path file."""
    print(f"  [Seedream] Genero immagine...")

    result = hf.subscribe(
        "bytedance/seedream/v4/text-to-image",
        arguments={
            "prompt": scene["image_prompt"],
            "aspect_ratio": "9:16",
            "resolution": "2K",
        },
    )

    img_url = (
        result.get("url") or
        result.get("image_url") or
        (result.get("images") or [{}])[0].get("url")
    )
    if not img_url:
        raise RuntimeError(f"Nessuna immagine: {result}")

    img_path = os.path.join(OUTPUT_DIR, f"{scene['id']}.jpg")
    with httpx.stream("GET", img_url, follow_redirects=True, timeout=60) as r:
        r.raise_for_status()
        with open(img_path, "wb") as f:
            for chunk in r.iter_bytes():
                f.write(chunk)
    print(f"  Immagine: {img_path}")
    return img_path


def upload_image(img_path: str) -> str:
    """Carica immagine su Higgsfield e restituisce URL."""
    print(f"  [Higgsfield] Carico immagine...")
    result = hf.upload_file(img_path)
    url = result.get("url") or result.get("image_url") or result.get("uri")
    if not url:
        raise RuntimeError(f"Upload fallito: {result}")
    print(f"  URL: {url}")
    return url


def generate_video(scene: dict, image_url: str) -> str:
    """Anima l'immagine con Kling AI 2.6. Restituisce path MP4."""
    print(f"  [Kling 2.6] Animo immagine...")
    result = hf.subscribe(
        KLING_ENDPOINT,
        arguments={
            "prompt": scene["video_prompt"],
            "image_url": image_url,
            "duration": "5",
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
    with httpx.stream("GET", video_url, follow_redirects=True, timeout=120) as r:
        r.raise_for_status()
        with open(out_path, "wb") as f:
            for chunk in r.iter_bytes():
                f.write(chunk)
    print(f"  Video: {out_path}")
    return out_path


def main():
    print("=== Pipeline: Nanobanana → Kling AI 2.6 ===\n")
    results = {}
    for scene in SCENES:
        print(f"\n[{scene['id']}]")
        try:
            img_path = generate_image(scene)
            time.sleep(1)
            img_url = upload_image(img_path)
            time.sleep(1)
            mp4_path = generate_video(scene, img_url)
            results[scene["id"]] = {"status": "ok", "path": mp4_path}
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
