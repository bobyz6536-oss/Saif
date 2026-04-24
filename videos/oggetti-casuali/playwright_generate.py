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


async def save_html(page, name):
    try:
        html = await page.content()
        with open(str(DBG_DIR / f"{name}.html"), "w", encoding="utf-8") as f:
            f.write(html)
    except Exception:
        pass


async def get_page_info(page):
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
    print("[Login] STEP 1: goto higgsfield.ai/ai/video")
    try:
        await page.goto("https://higgsfield.ai/ai/video", timeout=30000)
        await page.wait_for_load_state("domcontentloaded", timeout=20000)
    except Exception as e:
        print(f"  STEP 1 WARN: {e}")
    await asyncio.sleep(4)
    await screenshot(page, "01_homepage")
    await save_html(page, "01_homepage")

    info = await get_page_info(page)
    results["_page_info"] = info
    print(f"  URL: {page.url}")
    print(f"  Buttons: {info['buttons'][:10]}")
    print(f"  Inputs: {info['inputs'][:5]}")

    # Cookie banner
    print("[Login] STEP 2: cookie banner")
    for sel in ["button:has-text('Accept All')", "button:has-text('Accept')",
                "button:has-text('OK')", "button:has-text('Agree')"]:
        try:
            btn = page.locator(sel).first
            if await btn.is_visible(timeout=1500):
                await btn.click(force=True, timeout=3000)
                await asyncio.sleep(2)
                print(f"  Cookie chiuso: {sel}")
                break
        except Exception:
            pass

    # Try direct /sign-in navigation
    print("[Login] STEP 3: provo /sign-in diretto")
    try:
        await page.goto("https://higgsfield.ai/sign-in", timeout=15000)
        await page.wait_for_load_state("domcontentloaded", timeout=10000)
        await asyncio.sleep(3)
    except Exception as e:
        print(f"  STEP 3 WARN: {e}")
    await screenshot(page, "02_signin")
    await save_html(page, "02_signin")
    info_si = await get_page_info(page)
    print(f"  /sign-in URL: {page.url}")
    print(f"  /sign-in Buttons: {info_si['buttons'][:8]}")
    print(f"  /sign-in Inputs: {info_si['inputs'][:5]}")
    results["_signin_page"] = {
        "url": page.url,
        "buttons": info_si['buttons'][:10],
        "inputs": info_si['inputs'][:5],
    }

    # Check if email input appeared after /sign-in redirect
    email_input = await find_visible(page, [
        "input[type='email']", "input[name='identifier']",
        "input[autocomplete='email']", "input[placeholder*='email' i]",
    ], timeout=3000)

    if not email_input:
        # Go back home and open login modal
        print("[Login] STEP 4: torno a home, click Login")
        try:
            await page.goto("https://higgsfield.ai/ai/video", timeout=20000)
            await page.wait_for_load_state("domcontentloaded", timeout=15000)
        except Exception as e:
            print(f"  STEP 4 WARN: {e}")
        await asyncio.sleep(3)

        print("[Login] STEP 5: click Login link")
        try:
            login = page.locator("a:has-text('Login')").first
            await login.wait_for(state="visible", timeout=5000)
            await login.click(force=True, timeout=5000)
            print("  Login cliccato via Playwright")
        except Exception as e:
            print(f"  Login Playwright fallito: {e}")
            r = await page.evaluate("""
                () => {
                    const el = [...document.querySelectorAll('a')]
                        .find(a => /login/i.test(a.textContent.trim()));
                    if (el) {
                        el.dispatchEvent(new MouseEvent('click', {bubbles:true, cancelable:true}));
                        return el.outerHTML.slice(0, 120);
                    }
                    return null;
                }
            """)
            print(f"  Login via JS: {r}")

        await asyncio.sleep(6)
        await screenshot(page, "03_dopo_login_click")
        await save_html(page, "03_dopo_login_click")

        print("[Login] STEP 6: aspetto Continue with Email (max 30s)")
        email_btn_found = False
        for attempt in range(15):
            await asyncio.sleep(2)

            if attempt % 3 == 0:
                snap = await get_page_info(page)
                print(f"  attempt {attempt}: btns={snap['buttons'][:8]}")
                results[f"_btns_{attempt}"] = snap['buttons'][:10]
            if attempt == 6:
                await screenshot(page, "03b_modal_6s")
                await save_html(page, "03b_modal_6s")

            clicked = await page.evaluate("""
                () => {
                    // Try Clerk data-localization-key attributes
                    const byKey = document.querySelector(
                        '[data-localization-key="socialButtonsBlockButton__email"],' +
                        '[data-localization-key*="emailAddress"],' +
                        '[data-localization-key*="email"]'
                    );
                    if (byKey) {
                        byKey.click();
                        return 'clerk-key:' + (byKey.textContent || byKey.outerHTML).slice(0, 60);
                    }
                    const all = [...document.querySelectorAll('button, [role="button"]')];
                    const btn = all.find(b =>
                        b.textContent.trim().includes('Continue with Email') ||
                        b.textContent.trim() === 'Email' ||
                        /email/i.test(b.getAttribute('data-localization-key') || '')
                    );
                    if (btn) { btn.click(); return btn.textContent.trim(); }
                    return null;
                }
            """)
            if clicked:
                print(f"  STEP 6 OK: '{clicked}'")
                email_btn_found = True
                break

        if not email_btn_found:
            snap3 = await get_page_info(page)
            await save_html(page, "ERROR_no_email_btn")
            raise RuntimeError(
                f"Continue with Email non trovato dopo 30s. Buttons={snap3['buttons'][:15]}"
            )

        await asyncio.sleep(3)
        await screenshot(page, "04_email_form")
        await save_html(page, "04_email_form")

        email_input = await find_visible(page, [
            "input[type='email']", "input[name='identifier']",
            "input[autocomplete='email']", "input[placeholder*='email' i]",
        ], timeout=8000)
        if not email_input:
            snap4 = await get_page_info(page)
            await save_html(page, "ERROR_no_email_input")
            raise RuntimeError(f"Campo email non trovato. Inputs={snap4['inputs']}")

    print("[Login] STEP 7: inserisci email")
    await email_input.click(timeout=5000)
    await email_input.fill(EMAIL)
    await screenshot(page, "05_email_filled")

    print("[Login] STEP 8: submit email")
    submit = page.locator("button[type='submit']").first
    await submit.wait_for(state="visible", timeout=5000)
    await submit.click(force=True, timeout=5000)
    await asyncio.sleep(3)
    await screenshot(page, "06_dopo_submit")
    await save_html(page, "06_dopo_submit")
    snap5 = await get_page_info(page)
    print(f"  Dopo submit: btns={snap5['buttons'][:8]}, inputs={snap5['inputs'][:4]}")
    results["_after_email_submit"] = {
        "buttons": snap5['buttons'][:10],
        "inputs": snap5['inputs'][:5],
    }

    print("[Login] STEP 9: password")
    pw = await find_visible(page, [
        "input[type='password']", "input[name='password']",
    ], timeout=10000)
    if pw:
        print("  Password field trovato, inserisco...")
        await pw.click(timeout=5000)
        await pw.fill(PASSWORD)
        await screenshot(page, "07_pw_filled")
        submit2 = page.locator("button[type='submit']").first
        await submit2.wait_for(state="visible", timeout=5000)
        await submit2.click(force=True, timeout=5000)
        print("  Password submitted")
    else:
        snap6 = await get_page_info(page)
        print(f"  WARN: password field non trovato. btns={snap6['buttons'][:8]}")

    print("[Login] STEP 10: attendo caricamento")
    try:
        await page.wait_for_load_state("networkidle", timeout=20000)
    except Exception as e:
        print(f"  networkidle WARN: {e}")
    await asyncio.sleep(3)
    await screenshot(page, "08_dopo_login")
    await save_html(page, "08_dopo_login")
    print(f"  URL finale: {page.url}")

    if "sign-in" in page.url or "/login" in page.url:
        snap7 = await get_page_info(page)
        raise RuntimeError(f"Ancora su pagina login: {page.url}, btns={snap7['buttons'][:10]}")

    print("  LOGIN OK!")


async def dismiss_overlay(page):
    """Chiude overlay/modal residui premendo Escape e aspettando che spariscano."""
    await page.keyboard.press("Escape")
    await asyncio.sleep(1)
    # Clicca eventuale pulsante X/close nel modal del risultato
    for sel in ["button[aria-label='Close']", "button:has-text('×')",
                "button:has-text('Close')", "[data-testid='modal-close']"]:
        try:
            el = page.locator(sel).first
            if await el.is_visible(timeout=500):
                await el.click(force=True, timeout=2000)
                await asyncio.sleep(1)
                break
        except Exception:
            pass


async def generate_scene(page, scene, idx):
    # Skip if already generated in a previous run
    out = str(OUTPUT_DIR / f"{scene['id']}.mp4")
    if os.path.exists(out) and os.path.getsize(out) > 10000:
        print(f"  Già esistente, skip: {out}")
        return out

    # Fresh navigation removes overlay left from previous generation
    print(f"  Nav fresh a /ai/video...")
    try:
        await page.goto("https://higgsfield.ai/ai/video", timeout=20000)
        await page.wait_for_load_state("domcontentloaded", timeout=15000)
        await asyncio.sleep(3)
    except Exception as e:
        print(f"  Nav WARN: {e}")

    await dismiss_overlay(page)
    await screenshot(page, f"{idx:02d}_start")

    print(f"  Cerco prompt field...")

    prompt_field = await find_visible(page, [
        "div[contenteditable='true']",
        "textarea",
        "input[placeholder*='prompt' i]",
        "input[placeholder*='describe' i]",
        "[data-testid*='prompt']",
        "[class*='prompt'] textarea",
    ], timeout=10000)

    if not prompt_field:
        info = await get_page_info(page)
        raise RuntimeError(f"Prompt field non trovato. Inputs: {info['inputs']}")

    # force=True bypasses any residual overlay
    await prompt_field.click(force=True, timeout=5000)
    # Use JS to set value in Lexical editor (fill() alone may not trigger React state)
    await prompt_field.fill(scene["prompt"])
    await page.keyboard.press("End")  # ensure cursor at end to confirm text was accepted

    # Aspect ratio 9:16
    for sel in ["text=9:16", "option[value='9:16']", "[data-ratio='9:16']"]:
        try:
            el = page.locator(sel).first
            if await el.is_visible(timeout=1000):
                await el.click(force=True, timeout=3000)
                break
        except Exception:
            pass

    gen_btn = await find_visible(page, [
        "button:has-text('Generate')", "button:has-text('Create')",
        "button[type='submit']", "text=Generate",
    ], timeout=5000)
    if not gen_btn:
        raise RuntimeError("Pulsante Generate non trovato")

    await gen_btn.click(force=True, timeout=5000)
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
            await save_html(page, "ERROR_login")
            results["_login"] = {"status": "error", "error": str(e)}
            save_results()
            await browser.close()
            return

        # Naviga alla pagina video
        try:
            await page.goto("https://higgsfield.ai/ai/video", timeout=20000)
            await page.wait_for_load_state("load", timeout=15000)
            await asyncio.sleep(3)
            await screenshot(page, "09_video_page")
            await save_html(page, "09_video_page")
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
    try:
        from playwright.async_api import async_playwright  # noqa: F401
    except ImportError as e:
        results["_fatal"] = {"status": "error", "error": f"Playwright non installato: {e}"}
        save_results()
        sys.exit(0)

    try:
        asyncio.run(main())
    except Exception as e:
        import traceback
        print(f"ERRORE FATALE: {e}")
        traceback.print_exc()
        results["_fatal"] = {"status": "error", "error": str(e)}
        save_results()

    sys.exit(0)
