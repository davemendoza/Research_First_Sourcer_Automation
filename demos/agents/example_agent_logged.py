import datetime, os

LOG_FILE = "logs/example_agent.log"

def run_demo():
    msg = f"✅ GPT–Python sync verified at {datetime.datetime.now()}"
    print(msg)
    os.makedirs("logs", exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(msg + "\n")

if __name__ == "__main__":
    run_demo()
