from contracts.canonical_people_schema import enforce_canonical
# © 2025 Dave Mendoza, DBA AI Craft, Inc. All rights reserved. Strictly proprietary; no copying, derivative works, reverse engineering, redistribution, or commercial/personal use permitted without written authorization. Governed by Colorado, USA law.
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
df = enforce_canonical(df)
    df.to_csv("ai_talent_leads.csv", index=False)
    console.print(f"[bold green]✅ Results saved to ai_talent_leads.csv[/bold green]")

Proprietary Rights Notice
------------------------
All code, scripts, GitHub repositories, documentation, data, and GPT-integrated components of the AI Talent Engine – Signal Intelligence and Research_First_Sourcer_Automation Python Automation Sourcing Framework are strictly proprietary. All intellectual property rights, copyrights, trademarks, and related rights are exclusively owned by Dave Mendoza, DBA AI Craft, Inc.
No individual or entity may copy, reproduce, distribute, modify, create derivative works, reverse engineer, decompile, or otherwise use any part of this system, software, or associated materials for personal or commercial purposes without explicit written authorization from Dave Mendoza.
All rights reserved. Unauthorized use may result in legal action.
This statement is governed by the laws of the State of Colorado, USA.
