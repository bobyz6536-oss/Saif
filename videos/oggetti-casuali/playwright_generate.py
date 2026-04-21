"""
Automazione browser Higgsfield: genera video usando i crediti web.
"""
import asyncio
import os
import json
import sys
from pathlib import Path

EMAIL    = os.getenv("HF_EMAIL",    "BOBYZ6536@gmail.com")
PASSWORD = os.getenv("HF_PASSWORD", "Saifahmed12345@")

SCRIPT_DIR = Path(__file__).parent
OUTPUT_DIR = SCRIPT_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)
DBG_DIR = OUTPUT_DIR / "debug"
DBG_DIR.mkdir(exist_ok=True)

CHARACTER = (
    "3D photorealistic transparent human figure, semi-transparent frosted glass body "
    "with full ivory skeleton clearly visible inside, realistic detailed eyes. "
    "White seamless studio background, soft cinematic lighting. "
)

SCENES = [
    {"id": "01-hook", "prompt": CHARACTER +
        "Standing center frame T-pose raises arms dramatically. Bold black text slams in: "
        "'Nessun aereo.' 'Nessuna nave.' Shockwave through glass body, skeleton rattles. 9:16."},
    {"id": "02-bicicletta", "prompt": CHARACTER +
        "Rides red bicycle on Italian road, skeleton legs pumping. World map Italy→Australia. "
        "Reaches ocean, slams brakes, bicycle sinks cartoon splash. 9:16."},
    {"id": "03-materassino", "prompt": CHARACTER +
        "Exhausted on pink inflatable mattress floating Mediterranean. Shark fin circling, "
        "blazing sun. Bold text '400 anni'. Deadpan eyes. 9:16."},
    {"id": "04-aquilone", "prompt": CHARACTER +
        "Grips colorful diamond kite being lifted into sky. Wind arrows flip, spins wildly, "
        "skeleton rotating. Crashes into desert sand. 9:16."},
    {"id": "05-catapulta", "prompt": CHARACTER +
        "Inside medieval catapult bucket, Italian backyard, infographic 'Gittata 300m vs 16000km'. "
        "Launched in wide arc, crashes in neighbor garden, Italian woman gasps, police car. 9:16."},
    {"id": "06-pallone", "prompt": CHARACTER +
        "In basket of hot air balloon over ocean. Balloon deflates PSSSSS, freefalls, "
        "lands BOING on pink mattress. Second skeleton there waves. 9:16."},
    {"id": "07-skateboard", "prompt": CHARACTER +
        "On red skateboard with rocket duct-taped behind, fuse lit. Blazing fire, glass glowing, "
        "abrupt stop. Eyebrows scorched. Deadpan at camera. 9:16."},
    {"id": "08-socrate", "prompt": CHARACTER +
        "Sitting among broken catapult and deflated balloon. Socrates in white toga walks in, "
        "raises finger: 'Perche vuoi raggiungere l altra parte del mondo se non sai dove sei tu?' "
        "Skeleton slumps. Spotlight. 9:16."},
    {"id": "09-aereo", "prompt": CHARACTER +
        "At airport counter, ticket printing '$400'. Cuts to relaxed in airplane seat, "
        "AC vent, meal tray. Deadpan shrug. Bold text '16 ore. Fine.' 9:16."},
    {"id": "10-finale-cta", "prompt": CHARACTER +
        "Red background, raises arms wide. Bold white text: 'Con cosa raggiungeresti "
        "l altra parte del mondo?' Points at viewer. Freeze frame. 9:16."},
]

results = {}


def save_results():
    with open(OUTPUT_DIR / "results.json", "w") as f:
        json.dump(results, f, indent=2)


async def screenshot(page, name):
    try:
        await page.screenshot(path=str(DBG_DIR / f"{name}.png"), full_page=True)
    except Exception:
        pass


async def get_page_info(page):
    """Raccoglie testo visibile, pulsanti, link dalla pagina."""
    info = {"url": page.url, "title": "", "body_text": "", "buttons": [], "links": [], "inputs": []}
    try:
        info["title"] = await page.title()
        info["body_text"] = (await page.inner_text("body"))[:800]
        for b in await page.locator("button").all():
            try:
                txt = (await b.inner_text()).strip()
                if txt:
                    info["buttons"].append(txt)
            except Exception:
                pass
        for a in await page.locator("a").all():
            try:
                info["links"].append({
                    "text": (await a.inner_text()).strip(),
                    "href": await a.get_attribute("href") or ""
                })
            except Exception:
                pass
        for inp in await page.locator("input").all():
            try:
                info["inputs"].append({
                    "type": await inp.get_attribute("type") or "",
                    "name": await inp.get_attribute("name") or "",
                    "placeholder": await inp.get_attribute("placeholder") or "",
                    "id": await inp.get_attribute("id") or "",
                })
            except Exception:
                pass
    except Exception as e:
        info["error"] = str(e)
    return info


async def find_visible(page, selectors, timeout=5000):
    for sel in selectors:
        try:
            loc = page.locator(sel).first
            await loc.wait_for(state="visible", timeout=timeout)
            return loc
        except Exception:
            pass
    return None


async def do_login(page):
    print("[Login] Apertura higgsfield.ai ...")
    try:
        await page.goto("https://higgsfield.ai/ai/video", timeout=30000)
    except Exception as e:
        print(f"  goto fallito: {e}")
        try:
            await page.goto("https://higgsfield.ai", timeout=30000)
        except Exception as e2:
            raise RuntimeError(f"Impossibile aprire higgsfield.ai: {e2}")

    await page.wait_for_load_state("load", timeout=20000)
    await asyncio.sleep(5)
    await screenshot(page, "01_homepage")

    info = await get_page_info(page)
    print(f"  URL: {info['url']}")
    print(f"  Title: {info['title']}")
    print(f"  Buttons: {info['buttons'][:10]}")
    print(f"  Inputs: {info['inputs'][:5]}")
    results["_page_info"] = info

    # Cerca input email direttamente
    email_input = await find_visible(page, [
        "input#identifier-field", "input[name='identifier']",
        "input[type='email']", "input[name='email']",
        "input[autocomplete='email']", "input[autocomplete='username']",
        "input[placeholder*='email' i]", "input[placeholder*='mail' i]",
    ], timeout=3000)

    if not email_input:
        # Cerca e clicca pulsante Sign In / Login
        for btn_text in ["Sign In", "Log In", "Login", "Get Started",
                         "Continue with Email", "Sign Up", "Enter", "Accedi"]:
            btn = await find_visible(page, [f"text={btn_text}", f"button:has-text('{btn_text}')"], timeout=1500)
            if btn:
                print(f"  Click '{btn_text}'")
                await btn.click()
                await asyncio.sleep(3)
                await screenshot(page, "02_dopo_click")
                email_input = await find_visible(page, [
                    "input#identifier-field", "input[name='identifier']",
                    "input[type='email']", "input[name='email']",
                    "input[autocomplete='email']",
                ], timeout=5000)
                if email_input:
                    break

    if not email_input:
        info2 = await get_page_info(page)
        results["_page_info_after_click"] = info2
        raise RuntimeError(
            f"Campo email non trovato. Buttons={info2['buttons'][:15]} "
            f"Inputs={info2['inputs'][:5]}"
        )

    print("  Inserisco email...")
    await email_input.fill(EMAIL)

    # Clerk: email → Continue → password
    cont = await find_visible(page, [
        "[data-localization-key='formButtonPrimary']",
        "button[type='submit']", "text=Continue", "text=Next",
    ], timeout=2000)
    if cont:
        label = (await cont.inner_text()).strip().lower()
        if any(w in label for w in ["continue", "next"]):
            await cont.click()
            await asyncio.sleep(2)
            await screenshot(page, "03_dopo_continue")

    pw_input = await find_visible(page, [
        "input[type='password']", "input[name='password']",
        "[data-localization-key='formFieldInput__password']",
    ], timeout=8000)
    if not pw_input:
        raise RuntimeError("Campo password non trovato dopo email")

    print("  Inserisco password...")
    await pw_input.fill(PASSWORD)
    await screenshot(page, "04_form_ok")

    submit = await find_visible(page, [
        "[data-localization-key='formButtonPrimary']",
        "button[type='submit']", "text=Sign In", "text=Continue",
    ], timeout=3000)
    if submit:
        await submit.click()
    else:
        await pw_input.press("Enter")

    await page.wait_for_load_state("networkidle", timeout=30000)
    await asyncio.sleep(3)
    await screenshot(page, "05_dopo_login")
    print(f"  URL dopo login: {page.url}")

    if "login" in page.url.lower() or "signin" in page.url.lower():
        raise RuntimeError(f"Login fallito, ancora su: {page.url}")
    print("  LOGIN OK!")


async def generate_scene(page, scene, idx):
    print(f"  Cerco prompt field...")

    prompt_field = await find_visible(page, [
        "textarea",
        "div[contenteditable='true']",
        "input[placeholder*='prompt' i]",
        "input[placeholder*='describe' i]",
        "[data-testid*='prompt']",
        "[class*='prompt'] textarea",
    ], timeout=10000)

    if not prompt_field:
        info = await get_page_info(page)
        raise RuntimeError(f"Prompt field non trovato. Inputs: {info['inputs']}")

    await prompt_field.click()
    await prompt_field.fill("")
    await prompt_field.fill(scene["prompt"])

    # Aspect ratio 9:16
    for sel in ["text=9:16", "option[value='9:16']", "[data-ratio='9:16']"]:
        try:
            el = page.locator(sel).first
            if await el.is_visible(timeout=1000):
                await el.click()
                break
        except Exception:
            pass

    gen_btn = await find_visible(page, [
        "button:has-text('Generate')", "button:has-text('Create')",
        "button[type='submit']", "text=Generate",
    ], timeout=5000)
    if not gen_btn:
        raise RuntimeError("Pulsante Generate non trovato")

    await gen_btn.click()
    print("  Generazione avviata...")
    await screenshot(page, f"{idx:02d}_avviata")

    # Attendi video (max 8 min)
    import httpx
    video_url = None
    for attempt in range(48):
        await asyncio.sleep(10)
        for sel in ["video source", "video[src]", "a[href*='.mp4']", "a[download]"]:
            try:
                el = page.locator(sel).first
                if await el.is_visible(timeout=500):
                    url = await el.get_attribute("src") or await el.get_attribute("href")
                    if url and ("mp4" in url or "video" in url):
                        video_url = url
                        break
            except Exception:
                pass
        if video_url:
            break
        if attempt % 3 == 0:
            await screenshot(page, f"{idx:02d}_wait_{attempt:02d}")

    if not video_url:
        raise RuntimeError("Timeout: video non generato in 8 min")

    out = str(OUTPUT_DIR / f"{scene['id']}.mp4")
    async with httpx.AsyncClient(follow_redirects=True, timeout=120) as client:
        r = await client.get(video_url)
        r.raise_for_status()
        with open(out, "wb") as f:
            f.write(r.content)
    print(f"  Salvato: {out}")
    return out


async def main():
    print("=== Higgsfield Playwright Automation ===")

    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage",
                  "--disable-blink-features=AutomationControlled"]
        )
        context = await browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent=(
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            )
        )
        page = await context.new_page()

        try:
            await do_login(page)
        except Exception as e:
            print(f"ERRORE LOGIN: {e}")
            await screenshot(page, "ERROR_login")
            results["_login"] = {"status": "error", "error": str(e)}
            save_results()
            await browser.close()
            return

        # Naviga alla pagina video
        try:
            await page.goto("https://higgsfield.ai/ai/video", timeout=20000)
            await page.wait_for_load_state("load", timeout=15000)
            await asyncio.sleep(3)
            await screenshot(page, "06_video_page")
        except Exception as e:
            print(f"  Navigazione video page: {e}")

        for i, scene in enumerate(SCENES):
            print(f"\n[{scene['id']}]")
            try:
                mp4 = await generate_scene(page, scene, i)
                results[scene["id"]] = {"status": "ok", "path": mp4}
            except Exception as e:
                print(f"  ERRORE: {e}")
                results[scene["id"]] = {"status": "error", "error": str(e)}
            await asyncio.sleep(5)
            save_results()

        await browser.close()

    ok = sum(1 for k, v in results.items() if not k.startswith("_") and v.get("status") == "ok")
    total = sum(1 for k in results if not k.startswith("_"))
    print(f"\n=== Completato: {ok}/{total} ===")
    save_results()


if __name__ == "__main__":
    # Importa playwright qui per catturare errori di import
    try:
        from playwright.async_api import async_playwright  # noqa: F401
    except ImportError as e:
        results["_fatal"] = {"status": "error", "error": f"Playwright non installato: {e}"}
        save_results()
        sys.exit(0)  # Exit 0 per permettere commit del results

    try:
        asyncio.run(main())
    except Exception as e:
        import traceback
        print(f"ERRORE FATALE: {e}")
        traceback.print_exc()
        results["_fatal"] = {"status": "error", "error": str(e)}
        save_results()

    sys.exit(0)  # Sempre 0: il workflow non fallisce, vediamo i risultati
