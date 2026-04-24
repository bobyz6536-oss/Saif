"""
Pipeline: NanoBanana v1 (text-to-image) + Kling AI 2.6 (image-to-video)
Campagna: "Come viaggiare nel tempo" — scheletro di vetro trasparente
Uso: python generate.py
Output: file .png e .mp4 in output/
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

# Endpoint NanoBanana v1 — candidati in ordine di priorità
NANO_CANDIDATES = [
    "nano-banana/v1/pro/text-to-image",
    "nano-banana/v1/standard/text-to-image",
    "nano-banana/v1/text-to-image",
    "nano-banana-1/pro/text-to-image",
    "nano-banana-1/text-to-image",
    "aeven/nano-banana/v1/pro/text-to-image",
]

# Endpoint Kling 2.6
KLING_I2V = "kling-video/v2.6/standard/image-to-video"
KLING_T2V = "kling-video/v2.6/standard/text-to-video"

CHARACTER = (
    "Hyper-realistic 3D render, 9:16 vertical. "
    "A transparent glass humanoid skeleton with brown human eyes, "
    "semi-transparent frosted glass body with full skeleton clearly visible inside. "
    "Ultra detailed, cinematic, 8K. "
)

SCENES = [
    {
        "id": "01-hook",
        "image": [
            CHARACTER + (
                "Stands in a modern living room surrounded by random household objects — "
                "a bicycle, a freezer, a mirror, a kite, a skateboard. "
                "Looks at all of them with a determined expression. Warm home lighting."
            ),
            CHARACTER + (
                "Close up holding a handwritten list that says COME VIAGGIARE NEL TEMPO. "
                "Below it a list of crossed out failed methods. "
                "Looks at the camera with complete seriousness. Warm lighting."
            ),
            CHARACTER + (
                "Wide shot of a modern living room in complete chaos. A bicycle in the corner. "
                "An open freezer. A mirror on the wall. A kite on the floor. A broken skateboard. "
                "Stands in the middle looking at the camera. Warm chaotic lighting."
            ),
        ],
        "video": [
            CHARACTER + (
                "Camera slowly reveals a modern living room full of random objects. "
                "Stands in the center looking at each object one by one. Turns to camera. "
                "Long pause. Points at the bicycle. Then the freezer. Then the mirror. Then back at camera. "
                "Hyper-realistic 3D, cinematic, 8K."
            ),
            CHARACTER + (
                "Close up on the skeleton's brown eyes scanning the room. "
                "Camera cuts rapidly between each object — bicycle, freezer, mirror, kite, skateboard. "
                "Back to face. Nods slowly. Determined. Single bass note. "
                "Hyper-realistic 3D, cinematic, 8K."
            ),
        ],
    },
    {
        "id": "02-girare-veloce",
        "image": [
            CHARACTER + (
                "Spinning rapidly on the spot in a modern living room. "
                "Motion blur visible. Expression intense and focused. Furniture visible around. "
                "Warm home lighting."
            ),
            CHARACTER + (
                "Lying flat on the floor after falling. Looks up at the ceiling. "
                "Expression blank. The room is exactly the same as before. Nothing has changed. "
                "Warm home lighting."
            ),
            CHARACTER + (
                "Close up face looking directly at camera from the floor. "
                "One hand on glass knee. Expression of complete resignation. Ceiling visible behind. "
                "Ultra detailed."
            ),
        ],
        "video": [
            CHARACTER + (
                "Starts spinning on the spot faster and faster. Camera circles accelerating. "
                "Spin blur increases. Then sudden stop. Falls sideways. Hits the floor. Long pause. "
                "Looks up at the ceiling. Same ceiling. Same room. Same time. "
                "Camera slow zooms on face on the floor. Hyper-realistic 3D, cinematic, 8K."
            ),
            CHARACTER + (
                "On the floor. Slowly sits up. Looks at his hands. Looks at the room. "
                "Looks at window — same light outside. Same time of day. Looks at camera. "
                "Long pause. Gets up slowly. Brushes himself off. Hyper-realistic 3D, cinematic, 8K."
            ),
        ],
    },
    {
        "id": "03-freezer",
        "image": [
            CHARACTER + (
                "Stands inside an open freezer. Ice and frost forming on glass body. "
                "Expression determined but already slightly cold. Kitchen background, bright freezer light."
            ),
            CHARACTER + (
                "Stumbles out of the freezer covered in frost. Checks watch. Looks at kitchen clock. "
                "Same time. Expression completely flat. A defrosted pizza visible on freezer shelf. "
                "Kitchen lighting."
            ),
            CHARACTER + (
                "Close up on a defrosted pizza sitting sadly on the freezer shelf. "
                "Glass skeleton's hand visible closing the freezer door beside it. Kitchen lighting."
            ),
        ],
        "video": [
            CHARACTER + (
                "Opens the freezer door. Steps inside. Closes it behind. "
                "Camera holds on the closed freezer door. Four minutes pass shown by kitchen clock. "
                "Door opens. Stumbles out covered in frost. Looks at clock. Same time. "
                "Looks at camera. Long pause. Hyper-realistic 3D, cinematic, 8K."
            ),
            CHARACTER + (
                "Opens freezer to get pizza. Finds it defrosted. Looks at it. "
                "Looks at camera. Long pause. Closes the freezer. Walks away. "
                "Camera holds on the closed freezer door. Hyper-realistic 3D, cinematic, 8K."
            ),
        ],
    },
    {
        "id": "04-dormire-tanto",
        "image": [
            CHARACTER + (
                "Lies in bed completely covered by blankets. Only glass skull visible on pillow. "
                "Alarm clock showing 20 hours. Dark bedroom, soft morning light through curtains."
            ),
            CHARACTER + (
                "Sits up in bed looking at the window. It is tomorrow outside — different light quality. "
                "Looks at the clock. Nods slowly. Technically it worked. Bedroom, morning light."
            ),
            CHARACTER + (
                "Close up face sitting in bed looking at camera with a conflicted expression. "
                "Traveled to tomorrow. But lost all of today. Stares at camera."
            ),
        ],
        "video": [
            CHARACTER + (
                "Gets into bed. Pulls covers over himself. Camera time lapse — "
                "light changes through window from day to night to morning. 20 hours pass. "
                "Wakes up. Sits up. Looks at clock. It is tomorrow. Long pause. "
                "Looks at camera. Nods slowly. Technically. Hyper-realistic 3D, cinematic, 8K."
            ),
            CHARACTER + (
                "Sits in bed looking at phone. Yesterday's notifications gone. Today's starting. "
                "Looks at window — tomorrow's light. Looks at camera. "
                "Raises one finger like he has a point. Then lowers it. Long pause. "
                "Hyper-realistic 3D, cinematic, 8K."
            ),
        ],
    },
    {
        "id": "05-specchio-torcia",
        "image": [
            CHARACTER + (
                "Stands in a completely dark room holding a flashlight pointed at a mirror. "
                "Light reflections bounce everywhere. Expression intense and focused. "
                "Dark room, multiple light reflections."
            ),
            CHARACTER + (
                "A cat flying off a shelf in absolute terror as light reflections flash around a dark room. "
                "Stands frozen holding a flashlight. Expression shifts from focus to guilt. "
                "Dark room, scattered light."
            ),
            CHARACTER + (
                "Stands alone in dark room. Mirror in front. Flashlight in hand. Cat gone. "
                "Looks at camera. Nothing happened. The continuum is intact."
            ),
        ],
        "video": [
            CHARACTER + (
                "Enters dark room carrying flashlight and mirror. Sets up mirror against wall. "
                "Points flashlight at it. Light bounces everywhere. Watches intensely. Nothing happens. "
                "Angles mirror differently. Still nothing. Then cat leaps off shelf in terror. "
                "Freezes. Cat runs out. Long pause. Hyper-realistic 3D, cinematic, 8K."
            ),
            CHARACTER + (
                "Stands alone in dark room after cat left. Looks at mirror. Looks at flashlight. "
                "Looks at empty shelf. Looks at camera. Turns flashlight off. Walks out. "
                "Camera holds on the empty dark room. Mirror still there. "
                "Hyper-realistic 3D, cinematic, 8K."
            ),
        ],
    },
    {
        "id": "06-velocita-luce",
        "image": [
            CHARACTER + (
                "Stands in a running position ready to sprint. Wears running shoes. "
                "Expression absolutely determined. Behind him a starting line. Open road ahead. "
                "Golden light."
            ),
            CHARACTER + (
                "Running at full speed down a road. Motion blur behind. Expression of maximum effort. "
                "Above a speed indicator showing current speed vs speed of light — "
                "his speed is laughably small. Ultra detailed."
            ),
            CHARACTER + (
                "Albert Einstein as a ghost figure visible in background watching skeleton "
                "try to run at speed of light. Einstein's expression deeply disappointed. "
                "Skeleton stopped and looks at Einstein. Long pause."
            ),
        ],
        "video": [
            CHARACTER + (
                "Crouches at starting line. Takes a deep breath. Sprints as fast as he can. "
                "Camera follows in fast motion. Speed counter appears — 18 km/h. "
                "Speed of light counter beside it — 1.08 billion km/h. "
                "Slows down. Stops. Looks at counters. Long pause. "
                "Hyper-realistic 3D, cinematic, 8K."
            ),
            CHARACTER + (
                "Einstein ghost figure appears behind skeleton looking with deep disappointment. "
                "Turns around. Sees Einstein. Long pause. Einstein slowly shakes his head. "
                "Turns and walks away. Skeleton watches him go. Looks at camera. "
                "Hyper-realistic 3D, cinematic, 8K."
            ),
        ],
    },
    {
        "id": "07-buco-nero",
        "image": [
            CHARACTER + (
                "Stands in living room looking at a star map on the wall. "
                "Points at a location 1000 light years away circled in red — nearest black hole. "
                "Expression shifts from determination to realization. Warm home lighting."
            ),
            CHARACTER + (
                "Close up on the star map showing distance from Earth to nearest black hole — 1000 light years. "
                "Glass finger points at distance marker. Expression completely flat."
            ),
            CHARACTER + (
                "Looks at bicycle in the corner of the room. Looks at star map. "
                "Looks at bicycle again. Looks at camera. Puts hand on glass skull."
            ),
        ],
        "video": [
            CHARACTER + (
                "Unrolls a star map on kitchen table. Finds Earth. Traces finger across map "
                "to nearest black hole. Distance counter appears — 1000 light years. "
                "Looks at bicycle in corner. Camera cuts between map and bicycle three times. "
                "Long pause. Rolls map back up. Hyper-realistic 3D, cinematic, 8K."
            ),
            CHARACTER + (
                "Stands at window looking at night sky. Stars visible. Somewhere among them the black hole. "
                "Raises one glass hand and points at a random star. Long pause. "
                "Lowers hand. Turns away from window. Looks at camera. "
                "Hyper-realistic 3D, cinematic, 8K."
            ),
        ],
    },
    {
        "id": "08-socrate",
        "image": [
            CHARACTER + (
                "An old Greek philosopher with half bald head and long white messy beard stands in "
                "a modern living room surrounded by all the failed time travel equipment — "
                "bicycle, freezer door open, mirror, broken skateboard, star map. "
                "He looks at each item calmly. Skeleton stands in center watching him."
            ),
            CHARACTER + (
                "The old philosopher points one finger at the skeleton with a calm but devastating expression. "
                "Skeleton stands completely still. All failed equipment visible around them. "
                "Modern living room, warm lighting."
            ),
            CHARACTER + (
                "Sits on floor of living room surrounded by all failed time travel equipment. "
                "The philosopher walks away calmly in background. "
                "Looks at camera. Expression of complete stillness. Warm home lighting."
            ),
        ],
        "video": [
            CHARACTER + (
                "Old philosopher enters living room. Walks slowly through all failed equipment without reacting. "
                "Stops in front of skeleton. Looks at him. Says something slowly. "
                "Camera close on skeleton's face as words land. Expression shifts. "
                "Sits down slowly on floor. Philosopher turns and walks away. "
                "Hyper-realistic 3D, cinematic, 8K."
            ),
            CHARACTER + (
                "Sits on floor looking at all failed equipment around. "
                "Bicycle. Open freezer. Mirror. Broken skateboard. Star map. "
                "Looks at each one slowly. Then looks at camera. Long pause. Single piano note. "
                "Hyper-realistic 3D, cinematic, 8K."
            ),
        ],
    },
    {
        "id": "09-soluzione",
        "image": [
            CHARACTER + (
                "Sits completely still in a modern living room. A clock on wall ticking. "
                "Light slowly changing through window — morning to afternoon. "
                "Sits and watches time pass naturally. Calm warm lighting."
            ),
            CHARACTER + (
                "Close up on a clock on the wall ticking. "
                "Glass skeleton's reflection visible in the clock face watching it. "
                "Time moving forward naturally. Warm home lighting."
            ),
            CHARACTER + (
                "Sits in a chair at golden sunset light. Has been sitting all day. "
                "Light has changed. Is in the future now — tomorrow approaching. "
                "Looks at camera with a small nod. Warm golden light."
            ),
        ],
        "video": [
            CHARACTER + (
                "Sits completely still in living room chair. Camera holds perfectly still. "
                "Time lapse — light moves across room from morning to afternoon to golden hour. "
                "Sits through all of it without moving. Just watching time pass. "
                "Single piano note throughout. Hyper-realistic 3D, cinematic, 8K."
            ),
            CHARACTER + (
                "Close up on clock ticking. Each second visible. Camera slowly pulls back "
                "to reveal skeleton watching from chair. Watches each second pass. "
                "Camera pulls back further showing whole room — all failed equipment still there. "
                "But he just sits. Time passes. Hyper-realistic 3D, cinematic, 8K."
            ),
        ],
    },
    {
        "id": "10-finale",
        "image": [
            CHARACTER + (
                "Stands directly facing the camera in living room. "
                "All the failed time travel equipment visible behind. "
                "Points one glass finger directly at the viewer. Warm home lighting."
            ),
            CHARACTER + (
                "Close up on brown eyes. Reflection of all failed methods visible in them — "
                "bicycle, freezer, mirror, skateboard, star map. Looks directly at camera."
            ),
            CHARACTER + (
                "Wide shot of living room at night. All failed equipment in background. "
                "Sits alone in chair. A clock ticking on wall. Time still passing. "
                "Single lamp lighting. Looks at camera. Single piano note. Fade to black."
            ),
        ],
        "video": [
            CHARACTER + (
                "Walks toward camera slowly from across living room. "
                "All failed equipment visible behind. Stops one meter from lens. "
                "Points one glass finger at the viewer. Long pause. Single piano note. "
                "Fade to black. Hyper-realistic 3D, cinematic, 8K."
            ),
            CHARACTER + (
                "Camera slow zooms into skeleton's brown eyes. Reflection of all failed methods "
                "flash rapidly — spinning, freezer, mirror, running, star map, Socrates. "
                "Then eyes look directly at camera. Complete silence. "
                "Title card fades in: In quale anno vorresti andare? "
                "Single piano note. Fade to black. Hyper-realistic 3D, cinematic, 8K."
            ),
        ],
    },
]


def discover_nano_endpoint() -> str | None:
    """Trova il primo endpoint NanoBanana v1 funzionante."""
    print("  [NanoBanana] Ricerca endpoint...")
    for ep in NANO_CANDIDATES:
        try:
            hf.subscribe(ep, arguments={"prompt": "test", "aspect_ratio": "9:16"})
            print(f"  [NanoBanana] Endpoint attivo: {ep}")
            return ep
        except Exception as e:
            err = str(e).lower()
            # "not found" / "unknown model" = endpoint sbagliato → prossimo
            # altri errori (crediti, rate limit) = endpoint esiste
            if any(x in err for x in ("not found", "unknown model", "no such", "invalid model")):
                continue
            print(f"  [NanoBanana] {ep} risponde (errore non-404): {e}")
            return ep
    return None


def download(url: str, path: str) -> None:
    with httpx.stream("GET", url, follow_redirects=True, timeout=120) as r:
        r.raise_for_status()
        with open(path, "wb") as f:
            for chunk in r.iter_bytes():
                f.write(chunk)


def generate_image(nano_ep: str, prompt: str, out_path: str) -> str | None:
    """Genera un'immagine con NanoBanana v1. Restituisce il percorso locale o None."""
    try:
        result = hf.subscribe(
            nano_ep,
            arguments={
                "prompt": prompt,
                "aspect_ratio": "9:16",
                "num_images": 1,
            },
        )
        img_url = (
            result.get("image_url")
            or result.get("url")
            or (result.get("images") or [{}])[0].get("url")
            or result.get("output", {}).get("image_url")
        )
        if not img_url:
            print(f"    WARN: nessun URL immagine in risposta: {result}")
            return None
        download(img_url, out_path)
        print(f"    Immagine: {out_path}")
        return out_path
    except Exception as e:
        print(f"    WARN immagine: {e}")
        return None


def generate_video(prompt: str, image_path: str | None, out_path: str) -> str:
    """Genera video con Kling 2.6 (i2v se disponibile immagine, t2v altrimenti)."""
    if image_path and os.path.exists(image_path):
        print(f"    [Kling 2.6 I2V] uso immagine di riferimento...")
        args = {
            "prompt": prompt,
            "duration": 5,
            "aspect_ratio": "9:16",
            "cfg_scale": 0.5,
        }
        try:
            with open(image_path, "rb") as f:
                img_bytes = f.read()
            import base64
            args["image"] = base64.b64encode(img_bytes).decode()
            result = hf.subscribe(KLING_I2V, arguments=args)
        except Exception:
            # fallback t2v
            del args["image"]
            result = hf.subscribe(KLING_T2V, arguments=args)
    else:
        print(f"    [Kling 2.6 T2V]...")
        result = hf.subscribe(
            KLING_T2V,
            arguments={
                "prompt": prompt,
                "duration": 5,
                "aspect_ratio": "9:16",
                "cfg_scale": 0.5,
            },
        )

    video_url = (
        result.get("video_url")
        or result.get("url")
        or (result.get("videos") or [{}])[0].get("url")
        or result.get("output", {}).get("video_url")
    )
    if not video_url:
        raise RuntimeError(f"Nessun URL video: {result}")

    download(video_url, out_path)
    print(f"    Video: {out_path}")
    return out_path


def main():
    print("=== Pipeline: NanoBanana v1 (immagini) + Kling 2.6 (video) ===")
    print("=== Campagna: Come viaggiare nel tempo ===\n")

    nano_ep = discover_nano_endpoint()
    if not nano_ep:
        print("  WARN: nessun endpoint NanoBanana trovato, salto generazione immagini.\n")

    results = {}

    for scene in SCENES:
        sid = scene["id"]
        print(f"\n[{sid}]")
        scene_results = {"images": [], "videos": []}

        # --- IMMAGINI ---
        if nano_ep:
            for i, img_prompt in enumerate(scene["image"], 1):
                img_path = os.path.join(OUTPUT_DIR, f"{sid}_img{i}.png")
                path = generate_image(nano_ep, img_prompt, img_path)
                scene_results["images"].append(
                    {"index": i, "status": "ok" if path else "error", "path": path}
                )
                time.sleep(2)
        else:
            scene_results["images"] = [{"status": "skipped"}]

        # --- VIDEO ---
        ref_image = None
        if scene_results["images"] and scene_results["images"][0].get("path"):
            ref_image = scene_results["images"][0]["path"]

        for i, vid_prompt in enumerate(scene["video"], 1):
            vid_path = os.path.join(OUTPUT_DIR, f"{sid}_vid{i}.mp4")
            try:
                generate_video(vid_prompt, ref_image, vid_path)
                scene_results["videos"].append(
                    {"index": i, "status": "ok", "path": vid_path}
                )
            except Exception as e:
                print(f"    ERRORE video {i}: {e}")
                scene_results["videos"].append(
                    {"index": i, "status": "error", "error": str(e)}
                )
            time.sleep(3)

        results[sid] = scene_results

    out_json = os.path.join(OUTPUT_DIR, "results.json")
    with open(out_json, "w") as f:
        json.dump(results, f, indent=2)

    ok_img = sum(
        1 for s in results.values()
        for r in s.get("images", []) if r.get("status") == "ok"
    )
    ok_vid = sum(
        1 for s in results.values()
        for r in s.get("videos", []) if r.get("status") == "ok"
    )
    total_img = sum(len(s.get("image", [])) for s in SCENES)
    total_vid = sum(len(s.get("video", [])) for s in SCENES)

    print(f"\n=== Completato ===")
    print(f"  Immagini: {ok_img}/{total_img}")
    print(f"  Video:    {ok_vid}/{total_vid}")
    print(f"  Risultati: {out_json}")


if __name__ == "__main__":
    main()
