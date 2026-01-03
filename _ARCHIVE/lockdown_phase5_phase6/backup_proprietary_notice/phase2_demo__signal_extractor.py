from contracts.canonical_people_schema import enforce_canonical
# ==============================================
# AI TALENT ENGINE – Phase 3.3 (Demo-Proof Build)
# ==============================================

import os
import pandas as pd
from rich.console import Console
from rich.table import Table

console = Console()

# Absolute paths (permanent fix)
BASE_DIR = "/Users/davemendoza/Desktop/Research_First_Sourcer_Automation/phase2_demo"
CSV_PATH = os.path.join(BASE_DIR, "ai_talent_leads.csv")
OUTPUT_PATH = os.path.join(BASE_DIR, "ranked_talent_signals.csv")

# ==============================================
# Load Data (PERMANENT FIX)
# ==============================================
def load_data(file_path=CSV_PATH):
    console.print("[bold cyan]Loading dataset...[/bold cyan]")
    try:
        df = pd.read_csv(file_path)
        console.print(f"[green]Loaded {len(df)} rows[/green]")
        return df
    except FileNotFoundError:
        console.print(f"[red]CSV not found at: {file_path}[/red]")
        return pd.DataFrame()

# ==============================================
# Signal Extraction
# ==============================================
def extract_signals(df):
    console.print("[bold yellow]Extracting signals...[/bold yellow]")

    # --- Role detection ---
    def detect_role(name, desc=""):
        text = f"{name} {desc}".lower()
        if "research" in text or "scientist" in text:
            return "Researcher"
        elif "engineer" in text or "developer" in text:
            return "Engineer"
        else:
            return "Contributor"

    # --- Focus area detection ---
    def detect_focus(desc):
        desc = str(desc).lower()
        # RAG exhaustive variants
        rag_terms = [
            "rag", "retrieval augmented generation", "retrieval-augmented generation",
            "retrievalaugmented", "retrieval ag", "retrievalag",
            "r-a-g", "r a g", "retrieval pipeline", "retrieval system",
            "retrieval workflow", "llm retrieval", "semantic retrieval",
            "hybrid retrieval", "vector-search retrieval"
        ]
        if any(term in desc for term in rag_terms):
            return "RAG"

        if "langchain" in desc:
            return "LangChain"
        if "llm" in desc:
            return "LLM"
        if "rlhf" in desc:
            return "RLHF"

        return "General AI"

    # ==============================
    # Apply detection
    # ==============================
    df["role"] = df.apply(lambda x: detect_role(x.get("name", ""), x.get("description", "")), axis=1)
    df["focus_area"] = df["description"].apply(detect_focus)

    # ==============================
    # Core signal strength score
    # ==============================
    df["signal_strength"] = df["stars"].fillna(0).astype(float) * 0.6
    df["signal_strength"] += df["role"].apply(lambda r: 40 if r == "Engineer" else 30 if r == "Researcher" else 20)

    # ==============================
    # 1–10 ranking
    # ==============================
    df = df.sort_values("signal_strength", ascending=False).reset_index(drop=True)
    df["rank_1_10"] = df.index + 1

    # ==============================
    # Tier assignment
    # ==============================
    def assign_tier(score):
        if score >= 500:
            return "🧠 Foundation AI"
        elif score >= 200:
            return "⚙️ Advanced AI"
        elif score >= 80:
            return "💡 Emerging AI"
        return "👥 General Contributor"

    df["tier"] = df["signal_strength"].apply(assign_tier)

    # ==============================
    # Initialize the enriched signal columns (all zero for now)
    # ==============================
    signal_columns = [
        "LLM_Signal",
        "RAG_Signal",
        "VectorDB_Signal",
        "RLHF_Signal",
        "AI_Infrastructure_Signal",
        "Machine_Learning_Infrastructure_Signal",
        "Inference_and_Model_Serving_Signal",
        "Research_Signal"
    ]
    for col in signal_columns:
        df[col] = 0

    console.print("[green]Signals extracted and enriched[/green]")
    return df

# ==============================================
# Save Output
# ==============================================
def save_ranked(df, output=OUTPUT_PATH):
df = enforce_canonical(df)
    df.to_csv(output, index=False)
    console.print(f"[bold green]Saved ranked signals to {output}[/bold green]")

# ==============================================
# Summary Table
# ==============================================
def display_summary(df, top_n=15):
    if df.empty:
        return

    console.print("[bold cyan]Top ranked AI talent[/bold cyan]")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Name", style="cyan")
    table.add_column("Tier", style="green")
    table.add_column("Rank", style="yellow")
    table.add_column("Signal", style="white")

    for _, row in df.head(top_n).iterrows():
        table.add_row(
            str(row["name"]),
            str(row["tier"]),
            str(row["rank_1_10"]),
            f"{row['signal_strength']:.1f}"
        )
    console.print(table)

# ==============================================
# Excel Preview Table
# ==============================================
def display_excel_preview(df, rows=8):
    if df.empty:
        return

    console.print("\n[bold cyan]Excel-Style Preview of Enriched Output[/bold cyan]")

    preview_cols = [
        "name", "tier", "rank_1_10", "signal_strength",
        "LLM_Signal", "RAG_Signal", "VectorDB_Signal", "RLHF_Signal",
        "AI_Infrastructure_Signal", "Machine_Learning_Infrastructure_Signal",
        "Inference_and_Model_Serving_Signal", "Research_Signal",
    ]

    preview_cols = [c for c in preview_cols if c in df.columns]

    table = Table(show_header=True, header_style="bold magenta", show_lines=False)
    for col in preview_cols:
        table.add_column(col, style="cyan", overflow="fold")

    for _, row in df.head(rows).iterrows():
        table.add_row(*(str(row.get(col, "")) for col in preview_cols))

    console.print(table)

# ==============================================
# Main
# ==============================================
if __name__ == "__main__":
    console.rule("[bold blue]AI TALENT ENGINE – Phase 3.3[/bold blue]")
    data = load_data()
    if not data.empty:
        ranked = extract_signals(data)
        save_ranked(ranked)
        display_summary(ranked)
        display_excel_preview(ranked)
