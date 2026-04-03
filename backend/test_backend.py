"""
Quick smoke tests for AmpCraft backend.
Run with: python test_backend.py
Backend must be running on port 8000.
"""
import requests, json, sys

BASE = "http://localhost:8000"
UPLOADS = "uploads"

TESTS = [
    {
        "file":     f"{UPLOADS}/freesound_community-guitar-solo-27194.wav",
        "label":    "Guitar solo (dark gritty)",
        "expected": ["blues", "rock"],   # acceptable classes
    },
    {
        "file":     f"{UPLOADS}/Saanware  Classical Rock Fusion  P A L  Cover  2021.mp3",
        "label":    "Saanware (full band rock)",
        "expected": ["rock", "blues"],
    },
]

REQUIRED_CHAIN_KEYS = ["style", "tone_character", "noise_gate", "efx", "amp", "cab", "mod", "delay", "reverb"]
REQUIRED_FEATURES   = ["centroid", "zcr", "rms", "rolloff", "flatness"]

passed = 0
failed = 0

# Health check
try:
    r = requests.get(f"{BASE}/")
    assert r.status_code == 200
    print("✅ GET /  →  server is up")
except Exception as e:
    print(f"❌ Server not reachable: {e}")
    sys.exit(1)

# Analyze tests
for t in TESTS:
    print(f"\n🎵  {t['label']}")
    try:
        with open(t["file"], "rb") as f:
            fname = t["file"].split("/")[-1]
            r = requests.post(f"{BASE}/analyze", files={"file": (fname, f)})

        assert r.status_code == 200, f"HTTP {r.status_code}"
        data = r.json()

        # Structure checks
        assert "chain"    in data, "missing 'chain'"
        assert "features" in data, "missing 'features'"
        for k in REQUIRED_CHAIN_KEYS:
            assert k in data["chain"], f"chain missing '{k}'"
        for k in REQUIRED_FEATURES:
            assert k in data["features"], f"features missing '{k}'"

        style = data["chain"]["style"]
        tone  = data["chain"]["tone_character"]
        amp   = data["chain"]["amp"]["type"]
        cab   = data["chain"]["cab"]["type"]

        print(f"   style          : {style}")
        print(f"   tone_character : {tone}")
        print(f"   amp            : {amp}  →  cab: {cab}")
        print(f"   centroid: {data['features']['centroid']:.0f} Hz  |  zcr: {data['features']['zcr']:.4f}  |  rms: {data['features']['rms']:.4f}")

        # Class check
        style_key = style.lower().replace(" ", "_")
        if style_key in t["expected"]:
            print(f"   ✅ class '{style}' is expected")
            passed += 1
        else:
            print(f"   ⚠️  class '{style}' — expected one of {t['expected']}")
            failed += 1

    except FileNotFoundError:
        print(f"   ⏭️  skipped (file not found)")
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        failed += 1

print(f"\n{'='*40}")
print(f"Results: {passed} passed, {failed} failed")
sys.exit(0 if failed == 0 else 1)
