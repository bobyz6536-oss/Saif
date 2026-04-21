"""
Automazione browser Higgsfield: genera video usando i crediti web (non API).
"""
import asyncio, os, json, re
from pathlib import Path
from playwright.async_api import async_playwright, TimeoutError as PWTimeout

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
        "Character stands center frame in T-pose, raises arms dramatically. "
        "Bold black text slams into frame: 'Nessun aereo.' 'Nessuna nave.' "
        "Shockwave ripples through glass body, skeleton rattles. Quick zoom in. 9:16 vertical."},
    {"id": "02-bicicletta", "prompt": CHARACTER +
        "Rides bright red bicycle on Italian road, skeleton legs pumping visibly. "
        "World map overlay dotted line Italy to Australia. Bold text '20 km/h'. "
        "Reaches ocean, slams brakes, bicycle sinks into water with cartoon splash. 9:16 vertical."},
    {"id": "03-materassino", "prompt": CHARACTER +
        "Lies exhausted on bright pink inflatable mattress floating on Mediterranean sea. "
        "Shark fin circling, blazing sun. Bold text '400 anni'. "
        "Deadpan eyes stare at camera. Gentle ocean sway. 9:16 vertical."},
    {"id": "04-aquilone", "prompt": CHARACTER +
        "Grips strings of massive colorful kite being lifted into clear blue sky. "
        "Wind arrows suddenly flip, character spins wildly, skeleton rotating inside glass shell. "
        "Crashes into desert sand near palm tree. 9:16 vertical."},
    {"id": "05-catapulta", "prompt": CHARACTER +
        "Sits inside medieval wooden catapult bucket wearing helmet. Italian backyard. "
        "Bold infographic 'Gittata: 300m vs 16.000km'. Catapult launches character in wide arc. "
        "Crashes into neighbor garden, old Italian woman gasps, police car approaches. 9:16 vertical."},
    {"id": "06-pallone", "prompt": CHARACTER +
        "Stands in basket of large colorful hot air balloon over ocean. "
        "Balloon suddenly deflates, character freefalls skeleton arms flailing. "
        "Lands BOING on pink mattress in ocean, second skeleton figure waves awkwardly. 9:16 vertical."},
    {"id": "07-skateboard", "prompt": CHARACTER +
        "Crouches on red skateboard with garden rocket duct-taped behind, fuse lit. "
        "Blazing orange fire, glass body glowing, skeleton rattling at extreme speed. "
        "Abrupt stop with smoke puff. Character touches forehead, eyebrows scorched. 9:16 vertical."},
    {"id": "08-socrate", "prompt": CHARACTER +
        "Sits on ground among broken catapult and deflated balloon. "
        "Ancient Greek philosopher Socrates in white toga walks in, raises one finger. "
        "Speech bubble: 'Perche vuoi raggiungere l altra parte del mondo se non sai dove sei tu?' "
        "Skeleton slowly slumps. Dramatic spotlight. 9:16 vertical."},
    {"id": "09-aereo", "prompt": CHARACTER +
        "At bright modern airport ticket counter, laptop open, ticket printing, bold price '$400'. "
        "Cuts to sitting relaxed in airplane seat, AC vent blowing, meal tray. "
        "Deadpan shrug at camera. Bold green text '16 ore. Fine.' 9:16 vertical."},
    {"id": "10-finale-cta", "prompt": CHARACTER +
        "Pops into frame against solid bright red background, raises both arms wide. "
        "Bold white text: 'Con cosa raggiungeresti l altra parte del mondo?' "
        "Points directly at viewer with dramatic zoom. Freeze frame. 9:16 vertical."},
]


async def ss(page, name):
    path = str(DBG_DIR / f"{name}.png")
    try:
        await page.screenshot(path=path, full_page=True)
        print(f"  [screenshot] {name}.png")
    except Exception:
        pass


async def wait_visible(page, selectors, timeout=5000):
    for sel in selectors:
        try:
            loc = page.locator(sel).first
            await loc.wait_for(state="visible", timeout=timeout)
            return loc
        except PWTimeout:
            pass
    return None


async def debug_page(page, label):
    """Stampa info di debug e salva HTML per ispezione."""
    try:
        title = await page.title()
        url = page.url
        inputs = await page.locator("input").all()
        buttons = await page.locator("button").all()
        anchors = await page.locator("a").all()
        print(f"  [{label}] URL={url} | Title={title}")
        print(f"  [{label}] Inputs:{len(inputs)} Buttons:{len(buttons)} Links:{len(anchors)}")
        for i, inp in enumerate(inputs[:8]):
            try:
                t = await inp.get_attribute("type") or "?"
                n = await inp.get_attribute("name") or "?"
                ph = await inp.get_attribute("placeholder") or "?"
                cls = (await inp.get_attribute("class") or "")[:30]
                print(f"    input[{i}] type={t} name={n} ph={ph!r} class={cls!r}")
            except Exception:
                pass
        for i, btn in enumerate(buttons[:8]):
            try:
                txt = (await btn.inner_text()).strip()[:50]
                print(f"    button[{i}] text={txt!r}")
            except Exception:
                pass
        for i, a in enumerate(anchors[:8]):
            try:
                href = await a.get_attribute("href") or "?"
                txt = (await a.inner_text()).strip()[:30]
                print(f"    a[{i}] href={href!r} text={txt!r}")
            except Exception:
                pass
        # Salva HTML per ispezione
        html = await page.content()
        html_path = str(DBG_DIR / f"{label}.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html[:50000])
        print(f"  [debug] HTML salvato: {html_path}")
    except Exception as e:
        print(f"  [debug] errore: {e}")


async def login(page):
    print("[Login] Apro platform.higgsfield.ai ...")

    # Prima prova URL di login diretto
    for login_url in [
        "https://higgsfield.ai/login",
        "https://higgsfield.ai/signin",
        "https://higgsfield.ai",
        "https://app.higgsfield.ai/login",
        "https://app.higgsfield.ai/signin",
        "https://app.higgsfield.ai",
    ]:
        await page.goto(login_url, timeout=30000)
        await page.wait_for_load_state("domcontentloaded", timeout=15000)
        await asyncio.sleep(3)  # attendi JS
        await ss(page, f"01_goto_{login_url.split('/')[-1] or 'home'}")
        await debug_page(page, "goto")

        # Cerca campo email direttamente
        email_field = await wait_visible(page, [
            "input[type='email']",
            "input[name='email']",
            "input[placeholder*='email' i]",
            "input[autocomplete='email']",
            "input[autocomplete='username']",
        ], timeout=4000)

        if email_field:
            print(f"  Campo email trovato su {login_url}")
            break

        # Cerca pulsante Sign In e cliccalo
        sign_in = await wait_visible(page, [
            "text=Sign In", "text=Log In", "text=Login", "text=Continue with Email",
            "a[href*='/login']", "a[href*='/signin']",
            "button:has-text('Sign')", "button:has-text('Login')",
            "button:has-text('Email')",
        ], timeout=3000)
        if sign_in:
            await sign_in.click()
            await page.wait_for_load_state("domcontentloaded", timeout=10000)
            await asyncio.sleep(2)
            await ss(page, "02_dopo_signin_click")
            await debug_page(page, "after_click")
            email_field = await wait_visible(page, [
                "input[type='email']", "input[name='email']",
                "input[placeholder*='email' i]", "input[autocomplete='email']",
            ], timeout=5000)
            if email_field:
                break

    if not email_field:
        await debug_page(page, "FALLITO")
        raise RuntimeError("Campo email non trovato su nessun URL di login")

    await email_field.fill(EMAIL)

    # Alcuni siti usano flusso email-first: inserisci email → Next → poi password
    next_btn = await wait_visible(page, [
        "button[type='submit']", "text=Continue", "text=Next", "text=Avanti"
    ], timeout=2000)
    if next_btn:
        btn_txt = (await next_btn.inner_text()).strip()
        if "continue" in btn_txt.lower() or "next" in btn_txt.lower() or "avanti" in btn_txt.lower():
            await next_btn.click()
            await asyncio.sleep(2)
            await ss(page, "03_dopo_next")

    # Inserisci password
    pw_field = await wait_visible(page, [
        "input[type='password']", "input[name='password']",
        "input[placeholder*='password' i]",
    ], timeout=8000)
    if pw_field:
        await pw_field.fill(PASSWORD)
    else:
        await debug_page(page, "no_password")
        raise RuntimeError("Campo password non trovato")

    await ss(page, "04_form_compilato")

    # Submit
    submit = await wait_visible(page, [
        "button[type='submit']", "text=Sign In", "text=Continue",
        "text=Log In", "button:has-text('Sign')", "button:has-text('Accedi')",
    ], timeout=4000)
    if submit:
        await submit.click()
    else:
        await pw_field.press("Enter")

    await page.wait_for_load_state("networkidle", timeout=30000)
    await asyncio.sleep(3)
    await ss(page, "05_dopo_login")
    await debug_page(page, "dopo_login")
    print(f"  URL dopo login: {page.url}")

    if "login" in page.url.lower() or "signin" in page.url.lower():
        raise RuntimeError(f"Login fallito, ancora su: {page.url}")
    print("  Login OK!")


async def navigate_to_kling(page):
    """Naviga alla sezione Kling text-to-video."""
    await ss(page, "05_dashboard")

    # Prova URL diretti comuni
    for url in [
        "https://platform.higgsfield.ai/create",
        "https://platform.higgsfield.ai/generate",
        "https://platform.higgsfield.ai/studio",
        "https://platform.higgsfield.ai/video",
    ]:
        await page.goto(url, timeout=15000)
        await page.wait_for_load_state("networkidle", timeout=10000)
        if page.url == url or "404" not in await page.title():
            await ss(page, "06_create_page")
            print(f"  Pagina trovata: {url}")
            return True

    # Prova click su link di navigazione
    for sel in ["text=Create", "text=Generate", "text=Studio",
                "a[href*='create']", "a[href*='generate']", "a[href*='studio']"]:
        try:
            el = page.locator(sel).first
            if await el.is_visible(timeout=2000):
                await el.click()
                await page.wait_for_load_state("networkidle", timeout=10000)
                await ss(page, "06_create_page")
                return True
        except Exception:
            pass

    await ss(page, "06_navigation_fallback")
    return False


async def select_kling_model(page):
    """Seleziona Kling 2.6 text-to-video se necessario."""
    for sel in [
        "text=Kling", "text=kling", "[data-model*='kling' i]",
        "button:has-text('Kling')", "option:has-text('Kling')"
    ]:
        try:
            el = page.locator(sel).first
            if await el.is_visible(timeout=2000):
                await el.click()
                await asyncio.sleep(1)
                await ss(page, "07_kling_selected")
                print("  Kling selezionato")
                return
        except Exception:
            pass
    print("  (modello non selezionato manualmente, uso quello attivo)")


async def generate_scene(page, scene, idx):
    print(f"  Cerco campo prompt...")

    # Trova textarea / prompt input
    prompt_field = await wait_visible(page, [
        "textarea",
        "div[contenteditable='true']",
        "input[placeholder*='prompt' i]",
        "input[placeholder*='describe' i]",
        "[data-testid*='prompt']",
        ".prompt-input textarea",
        "[class*='prompt'] textarea",
    ], timeout=10000)

    if not prompt_field:
        await ss(page, f"ERROR_{idx:02d}_no_prompt_field")
        raise RuntimeError("Campo prompt non trovato")

    await prompt_field.click()
    await prompt_field.fill("")
    await prompt_field.fill(scene["prompt"])
    await ss(page, f"{idx:02d}_prompt_inserito")
    print("  Prompt inserito")

    # Imposta aspect ratio 9:16 se disponibile
    for sel in ["text=9:16", "option[value='9:16']", "[data-ratio='9:16']"]:
        try:
            el = page.locator(sel).first
            if await el.is_visible(timeout=1500):
                await el.click()
                break
        except Exception:
            pass

    # Click Generate
    generate_btn = await wait_visible(page, [
        "button:has-text('Generate')", "button:has-text('Create')",
        "button[type='submit']", "text=Generate", "text=Create video",
        "[data-testid*='generate']",
    ], timeout=5000)

    if not generate_btn:
        await ss(page, f"ERROR_{idx:02d}_no_generate_btn")
        raise RuntimeError("Pulsante Generate non trovato")

    await generate_btn.click()
    print("  Generazione avviata — attendo (max 8 min)...")
    await ss(page, f"{idx:02d}_generazione_avviata")

    # Attendi video pronto (polling ogni 10s, max 48 tentativi = 8 min)
    video_url = None
    for attempt in range(48):
        await asyncio.sleep(10)

        # Cerca video element o link download
        for sel in [
            "video source", "video[src]", "a[href*='.mp4']",
            "a[download]", "button:has-text('Download')", "text=Download"
        ]:
            try:
                el = page.locator(sel).first
                if await el.is_visible(timeout=1000):
                    url = (await el.get_attribute("src") or
                           await el.get_attribute("href") or
                           await el.get_attribute("data-url"))
                    if url and ("mp4" in url or "video" in url or "download" in url.lower()):
                        video_url = url
                        break
            except Exception:
                pass

        if video_url:
            await ss(page, f"{idx:02d}_video_pronto")
            break

        if attempt % 3 == 0:
            await ss(page, f"{idx:02d}_attesa_{attempt:02d}")
            print(f"    ...attendo ({(attempt+1)*10}s)")

    if not video_url:
        await ss(page, f"ERROR_{idx:02d}_timeout")
        raise RuntimeError(f"Timeout: video non generato dopo 8 min")

    # Scarica MP4
    import httpx
    out = str(OUTPUT_DIR / f"{scene['id']}.mp4")
    async with httpx.AsyncClient(follow_redirects=True, timeout=120) as client:
        r = await client.get(video_url)
        r.raise_for_status()
        with open(out, "wb") as f:
            f.write(r.content)

    print(f"  Salvato: {out}")
    return out


async def main():
    print("=== Higgsfield Web Automation (Playwright) ===\n")

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

        # Login
        try:
            await login(page)
        except Exception as e:
            print(f"ERRORE LOGIN: {e}")
            await ss(page, "FATAL_login_error")
            # Salva HTML per debug in results così lo leggo via GitHub API
            try:
                html = await page.content()
                html_excerpt = html[:3000]
            except Exception:
                html_excerpt = "N/A"
            with open(OUTPUT_DIR / "results.json", "w") as f:
                json.dump({"_login": {"status": "error", "error": str(e),
                                      "url": page.url, "html_excerpt": html_excerpt}}, f, indent=2)
            await browser.close()
            return

        # Naviga alla sezione generate
        await navigate_to_kling(page)
        await select_kling_model(page)

        results = {}
        for i, scene in enumerate(SCENES):
            print(f"\n[{scene['id']}]")
            try:
                mp4 = await generate_scene(page, scene, i)
                results[scene["id"]] = {"status": "ok", "path": mp4}
            except Exception as e:
                print(f"  ERRORE: {e}")
                results[scene["id"]] = {"status": "error", "error": str(e)}
            await asyncio.sleep(5)

        await browser.close()

    with open(OUTPUT_DIR / "results.json", "w") as f:
        json.dump(results, f, indent=2)

    ok = sum(1 for r in results.values() if r["status"] == "ok")
    print(f"\n=== Completato: {ok}/{len(SCENES)} ===")


if __name__ == "__main__":
    asyncio.run(main())
