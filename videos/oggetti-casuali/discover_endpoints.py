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
    # Kling — formato corretto dai docs: kling-video/v2.1/pro/image-to-video
    "kling-video/v2.6/pro/image-to-video",
    "kling-video/v2.6/standard/image-to-video",
    "kling-video/v2.6/pro/text-to-video",
    "kling-video/v2.6/standard/text-to-video",
    "kling-video/v2.1/pro/image-to-video",       # noto dai docs
    "kling-video/v2.1/standard/image-to-video",
    "kling-video/v2.1/pro/text-to-video",
    # Nano Banana — stesso pattern: provider/model/version/quality/task
    "nano-banana/v2/pro/text-to-image",
    "nano-banana/v2/standard/text-to-image",
    "nano-banana/v2/text-to-image",
    "nano-banana-2/pro/text-to-image",
    "nano-banana-2/standard/text-to-image",
    "nano-banana-2/text-to-image",
    "google/nano-banana/v2/text-to-image",
    "google/nano-banana-2/text-to-image",
    "aeven/nano-banana/v2/pro/text-to-image",
    "aeven/nano-banana-2/pro/text-to-image",
    # Seedance Pro confermato
    "bytedance/seedance/v1/pro/text-to-video",
    "bytedance/seedance/v1/pro/image-to-video",
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
