"""
Script di discovery: trova gli endpoint corretti per Nano Banana e Kling su Higgsfield.
"""
import os
import json
import higgsfield_client as hf

API_KEY    = "1c3e9ae8-a47e-4c62-8ebf-786868ed46ad"
API_SECRET = "c5d1f864ee91c6390bf39398223718701c8c1d8f10961488e02da58c6eebae0a"
os.environ["HF_API_KEY"]    = API_KEY
os.environ["HF_API_SECRET"] = API_SECRET

# Candidati endpoint da testare
CANDIDATES = [
    # Nano Banana image endpoints
    "aeven/nano-banana/v2/text-to-image",
    "google/nano-banana/v2/text-to-image",
    "nano-banana/v2/text-to-image",
    "nano-banana-2/text-to-image",
    "/jobs/nano-banana-2",
    "jobs/nano-banana-2",
    "nano-banana-2",
    "aeven/nano-banana-2/text-to-image",
    "nano-banana/v2.0/text-to-image",
    # Kling video endpoints
    "kling/v2.6/text-to-video",
    "kling-ai/kling/v2.6/text-to-video",
    "kuaishou/kling/v2.6/text-to-video",
    "kling/v2.6/image-to-video",
    "kling-ai/v2.6/image-to-video",
    "/jobs/kling",
    "jobs/kling",
    "jobs/v2/kling3_0",
    "/jobs/v2/kling3_0",
    "kling3_0",
    "kling-ai/kling/v3.0/text-to-video",
]

ARGS = {"prompt": "test", "aspect_ratio": "9:16"}
results = {}

for ep in CANDIDATES:
    try:
        hf.subscribe(ep, arguments=ARGS)
        results[ep] = "SUCCESS"
    except Exception as e:
        results[ep] = str(e)
    print(f"{ep}: {results[ep]}")

# Salva risultati
with open("output/discovery.json", "w") as f:
    json.dump(results, f, indent=2)
print("\nSalvato in output/discovery.json")
