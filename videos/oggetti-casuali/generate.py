"""
Pipeline: Kling AI 2.6 text-to-video (direct, no image step)
Uso: python generate.py
Output: file .mp4 in output/
"""

import os
import json
import time
import httpx
import higgsfield_client as hf

HF_API_KEY    = os.getenv("HF_API_KEY",    "1c3e9ae8-a47e-4c62-8ebf-786868ed46ad")
HF_API_SECRET = os.getenv("HF_API_SECRET", "c5d1f864ee91c6390bf39398223718701c8c1d8f10961488e02da58c6eebae0a")

os.environ["HF_API_KEY"]    = HF_API_KEY
os.environ["HF_API_SECRET"] = HF_API_SECRET

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

KLING_T2V = "kling-video/v2.6/standard/text-to-video"

CHARACTER = (
    "3D photorealistic transparent human figure, semi-transparent frosted glass body "
    "with full ivory skeleton clearly visible inside, realistic detailed eyes. "
    "White seamless studio background, soft cinematic lighting. "
)

SCENES = [
    {
        "id": "01-hook",
        "prompt": CHARACTER + (
            "Character stands center frame in T-pose, raises arms dramatically. "
            "Bold black text slams into frame: 'Nessun aereo.' 'Nessuna nave.' "
            "Shockwave ripples through glass body, skeleton rattles inside. "
            "Quick zoom in. Dramatic cinematic spotlight. Vertical 9:16."
        ),
    },
    {
        "id": "02-bicicletta",
        "prompt": CHARACTER + (
            "Character rides bright red bicycle on Italian road, skeleton legs pumping visibly. "
            "World map overlay dotted line Italy to Australia. Bold text '20 km/h'. "
            "Reaches ocean, slams brakes, skeleton jolts forward, shocked expression arms spread wide, "
            "bicycle sinks into water with cartoon splash. Vertical 9:16."
        ),
    },
    {
        "id": "03-materassino",
        "prompt": CHARACTER + (
            "Character lies exhausted on bright pink inflatable mattress floating on calm Mediterranean sea. "
            "Skeleton slumping, shark fin circling nearby, blazing sun. Bold text '400 anni'. "
            "Deadpan eyes stare at camera. Gentle ocean sway. Vertical 9:16."
        ),
    },
    {
        "id": "04-aquilone",
        "prompt": CHARACTER + (
            "Character grips strings of massive colorful diamond kite being lifted into clear blue sky. "
            "Skeleton arms stretched upward. Wind arrows suddenly flip direction. "
            "Character spins wildly, skeleton rotating inside glass shell. "
            "Crashes into desert sand near palm tree. Vertical 9:16."
        ),
    },
    {
        "id": "05-catapulta",
        "prompt": CHARACTER + (
            "Character sits inside medieval wooden catapult bucket wearing helmet over glass skull. "
            "Italian backyard. Bold infographic 'Gittata: 300m vs 16.000km'. "
            "Catapult launches character in wide arc, skeleton rattling in flight. "
            "Crashes into neighbor's garden crushing flowers. Old Italian woman gasps. "
            "Police car approaches with flashing lights. Vertical 9:16."
        ),
    },
    {
        "id": "06-pallone",
        "prompt": CHARACTER + (
            "Character stands in basket of large colorful striped hot air balloon over ocean. "
            "Skeleton upright and hopeful. Bold text '30 km/h'. "
            "Balloon suddenly deflates PSSSSS, character freefalls skeleton arms flailing. "
            "Lands with BOING on pink mattress in ocean. Second skeleton figure already there waves awkwardly. "
            "Vertical 9:16."
        ),
    },
    {
        "id": "07-skateboard",
        "prompt": CHARACTER + (
            "Character crouches on red skateboard with large garden rocket duct-taped behind, "
            "skeleton bracing inside glass body, fuse lit. "
            "Rocket fires blazing orange fire, glass body glowing, skeleton rattling at extreme speed. "
            "Abrupt stop with smoke puff. House still visible behind. "
            "Character touches forehead, eyebrows scorched off. Deadpan stare at camera. Vertical 9:16."
        ),
    },
    {
        "id": "08-socrate",
        "prompt": CHARACTER + (
            "Character sits on ground among broken catapult, deflated balloon, scorched skateboard. "
            "Ancient Greek philosopher Socrates in white toga walks in, surveys wreckage, raises one finger. "
            "Speech bubble: 'Perche vuoi raggiungere l altra parte del mondo se non sai dove sei tu?' "
            "Character skeleton slowly slumps. Dramatic single spotlight. Vertical 9:16."
        ),
    },
    {
        "id": "09-aereo",
        "prompt": CHARACTER + (
            "Character at bright modern airport ticket counter, laptop open, ticket printing, bold price '$400'. "
            "Cut to character sitting relaxed in airplane seat, AC vent blowing, meal tray in front. "
            "Deadpan shrug at camera. Bold green text '16 ore. Fine.' overlays. Vertical 9:16."
        ),
    },
    {
        "id": "10-finale-cta",
        "prompt": CHARACTER + (
            "Character pops into frame center against solid bright red background, raises both arms wide, "
            "skeleton fully displayed. Bold white text bounces in: 'Con cosa raggiungeresti l altra parte del mondo?' "
            "Comment bubble with typing dots below. Character points directly at viewer with dramatic zoom. "
            "Freeze frame. Vertical 9:16."
        ),
    },
]


def generate_video(scene: dict) -> str:
    print(f"  [Kling 2.6 T2V] Genero video...")
    result = hf.subscribe(
        KLING_T2V,
        arguments={
            "prompt": scene["prompt"],
            "duration": 5,
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
    print("=== Pipeline: Kling AI 2.6 text-to-video ===\n")
    results = {}
    for scene in SCENES:
        print(f"\n[{scene['id']}]")
        try:
            mp4_path = generate_video(scene)
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
