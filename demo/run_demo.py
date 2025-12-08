import json, requests, os

def run_demo():
    with open("run_demo_connector.json") as f:
        cfg = json.load(f)

    base = f"https://raw.githubusercontent.com/{cfg['repo']}/{cfg['branch']}/{cfg['output_path']}"
    data = []
    for fname in cfg["files"]:
        url = f"{base}/{fname}"
        print(f"🔗 Loading {fname} ...")
        r = requests.get(url)
        r.raise_for_status()
        data.append(r.json())

    print(f"✅ Loaded {len(data)} candidate files from GitHub")
    print("🚀 Phase-7 demo pipeline ready — integrate your analytic call here.")

if __name__ == "__main__":
    run_demo()
