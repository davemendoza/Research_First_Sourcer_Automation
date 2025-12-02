# ============================================================
# AI TALENT ENGINE – Phase 2 Demo
# Version: v2.0-alpha
# Title: GitHub + HuggingFace Talent Discovery Automation
# ============================================================

import requests
import pandas as pd
from rich.console import Console
from rich.table import Table

console = Console()

# --- Demo Configuration ---
GITHUB_SEARCH = "machine learning engineer ai OR llm OR rag language:python"
HUGGINGFACE_SEARCH = "LLM OR RAG OR LangChain"

# --- GitHub Search Function ---
def search_github(query, max_results=10):
    console.print(f"[bold cyan]🔍 Searching GitHub for:[/bold cyan] {query}")
    url = f"https://api.github.com/search/repositories?q={query}&per_page={max_results}"
    response = requests.get(url)
    data = response.json()
    results = []
    for item in data.get("items", []):
        results.append({
            "source": "GitHub",
            "name": item.get("name"),
            "owner": item.get("owner", {}).get("login"),
            "url": item.get("html_url"),
            "description": item.get("description"),
            "stars": item.get("stargazers_count"),
        })
    return results

# --- Hugging Face Search Function ---
def search_huggingface(query, max_results=10):
    console.print(f"[bold magenta]🤗 Searching HuggingFace for:[/bold magenta] {query}")
    url = f"https://huggingface.co/api/models?search={query}&limit={max_results}"
    response = requests.get(url)
    data = response.json()
    results = []
    for item in data:
        results.append({
            "source": "HuggingFace",
            "name": item.get("modelId"),
            "owner": item.get("author"),
            "url": f"https://huggingface.co/{item.get('modelId')}",
            "description": item.get("pipeline_tag"),
            "stars": item.get("likes"),
        })
    return results

# --- Combine & Display Results ---
def display_results(results):
    table = Table(title="AI Talent Discovery Results", show_lines=True)
    table.add_column("Source", style="cyan", no_wrap=True)
    table.add_column("Name", style="green")
    table.add_column("Owner", style="yellow")




# --- Main Execution ---
if __name__ == "__main__":
    console.rule("[bold blue]AI TALENT ENGINE: Phase 2 Demo[/bold blue]")
    console.print("[bold yellow]⚙️  Starting Phase 2 demo run...[/bold yellow]")

    github_results = search_github(GITHUB_SEARCH)
    huggingface_results = search_huggingface(HUGGINGFACE_SEARCH)
    all_results = github_results + huggingface_results
    display_results(all_results)

    df = pd.DataFrame(all_results)
    df.to_csv("ai_talent_leads.csv", index=False)
    console.print(f"[bold green]✅ Results saved to ai_talent_leads.csv[/bold green]")
