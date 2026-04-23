#!/usr/bin/env python3
"""
Higgsfield API client — genera video da prompt testuali.
Uso: python higgsfield_api.py "descrizione del video"
"""

import sys
import time
import json
import os
import urllib.request
import urllib.error

API_KEY    = os.getenv("HIGGSFIELD_API_KEY",    "027ac888-fce3-4586-b237-9925dedb1b49")
API_SECRET = os.getenv("HIGGSFIELD_SECRET",     "eae675dab37f677ce84f8ac0313f32206d18490f9e7fde5c9fe6ef79a44c6123")
BASE_URL   = "https://api.higgsfield.ai"

HEADERS = {
    "Content-Type":  "application/json",
    "X-Api-Key":     API_KEY,
    "X-Api-Secret":  API_SECRET,
}


def request(method: str, path: str, data: dict | None = None) -> dict:
    url = BASE_URL + path
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"[HTTP {e.code}] {path}\n{body}")
        sys.exit(1)


def generate_video(prompt: str, model: str = "seedance-1-pro", duration: int = 5,
                   ratio: str = "16:9", resolution: str = "1080p") -> str:
    """Avvia generazione video e restituisce l'ID del job."""
    print(f"Avvio generazione...\nPrompt: {prompt}\n")
    payload = {
        "prompt":     prompt,
        "model":      model,
        "duration":   duration,
        "ratio":      ratio,
        "resolution": resolution,
    }
    resp = request("POST", "/v1/video/generate", payload)
    job_id = resp.get("id") or resp.get("job_id") or resp.get("task_id")
    if not job_id:
        print("Risposta inattesa:", json.dumps(resp, indent=2))
        sys.exit(1)
    print(f"Job avviato: {job_id}")
    return job_id


def poll(job_id: str, interval: int = 5, timeout: int = 300) -> str:
    """Attende il completamento e restituisce l'URL del video."""
    print("In attesa del risultato", end="", flush=True)
    deadline = time.time() + timeout
    while time.time() < deadline:
        resp = request("GET", f"/v1/video/{job_id}")
        status = resp.get("status", "").lower()
        if status in ("completed", "succeeded", "done", "success"):
            url = resp.get("url") or resp.get("video_url") or resp.get("output_url")
            print(f"\nCompletato! URL: {url}")
            return url
        if status in ("failed", "error"):
            print(f"\nErrore: {resp.get('error', 'sconosciuto')}")
            sys.exit(1)
        print(".", end="", flush=True)
        time.sleep(interval)
    print("\nTimeout raggiunto.")
    sys.exit(1)


def list_models() -> None:
    resp = request("GET", "/v1/models")
    print(json.dumps(resp, indent=2, ensure_ascii=False))


def account_info() -> None:
    resp = request("GET", "/v1/user/me")
    print(json.dumps(resp, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso:")
        print("  python higgsfield_api.py info             — info account")
        print("  python higgsfield_api.py models           — lista modelli")
        print("  python higgsfield_api.py \"<prompt>\"       — genera video")
        sys.exit(0)

    cmd = sys.argv[1]

    if cmd == "info":
        account_info()
    elif cmd == "models":
        list_models()
    else:
        job_id = generate_video(prompt=cmd)
        video_url = poll(job_id)
        print(f"\nVideo pronto: {video_url}")
