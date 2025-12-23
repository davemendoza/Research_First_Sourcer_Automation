import subprocess, sys

if __name__ == "__main__":
    scenario = sys.argv[1]
    subprocess.check_call([
        sys.executable, "-m", "tracks.track_d.run_track_d",
        "--scenario", scenario
    ])
