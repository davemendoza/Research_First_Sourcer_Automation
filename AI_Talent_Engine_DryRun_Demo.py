import requests, pandas as pd
from tqdm import tqdm

topic = "reinforcement learning"
url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={topic}&limit=100&fields=title,authors,venue,year,citationCount"

print("🔍 Collecting research evidence...")
response = requests.get(url)
data = response.json()

papers = []
for paper in tqdm(data.get("data", [])):
    authors = ", ".join([a["name"] for a in paper.get("authors", [])])
    papers.append({
        "Title": paper.get("title", ""),
        "Authors": authors,
        "Venue": paper.get("venue", ""),
        "Year": paper.get("year", ""),
        "Citations": paper.get("citationCount", "")
    })

df = pd.DataFrame(papers)
output_file = "AI_Talent_DryRun_Output.xlsx"
df.to_excel(output_file, index=False)
print(f"✅ Export complete — {len(df)} records saved to {output_file}")


