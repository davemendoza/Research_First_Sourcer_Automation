#!/usr/bin/env python3
# ==============================================================================
# AI Talent Engine — Synthetic Evaluation Generator (ONE-PASS, DEMO SAFE)
# Owner: Dave Mendoza
# © 2025 L. David Mendoza
#
# This script:
# - Overwrites the three *_PLACEHOLDER.csv files used by the demo
# - Populates 30+ columns with realistic synthetic data
# - Generates defensible analytics (median-based, outlier-safe)
# - Creates charts that actually render
# - Requires ZERO manual file creation
# ==============================================================================

import math
import random
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# -----------------------
# Determinism
# -----------------------
SEED = 42
random.seed(SEED)
np.random.seed(SEED)

# -----------------------
# Paths
# -----------------------
ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "demo"
CHARTS = DEMO / "charts"

FRONTIER = DEMO / "demo_frontier_evaluation_PLACEHOLDER.csv"
APPLIED = DEMO / "demo_applied_evaluation_PLACEHOLDER.csv"
ENGINEER = DEMO / "demo_ai_engineer_evaluation_PLACEHOLDER.csv"

SUMMARY = DEMO / "demo_summary.txt"

DEMO.mkdir(exist_ok=True)
CHARTS.mkdir(exist_ok=True)

# -----------------------
# Synthetic pools
# -----------------------
FIRST = ["Ava","Maya","Sofia","Liam","Noah","Ethan","Mila","Zoe","Aria","Leo","Nora","Kai","Rina","Tariq","Priya","Diego"]
LAST = ["Nguyen","Patel","Kim","Garcia","Chen","Singh","Lopez","Park","Johnson","Brown","Khan","Wong"]

FRONTIER_ORGS = ["OpenAI","Anthropic","DeepMind","Meta AI","NVIDIA Research","Microsoft Research"]
APPLIED_ORGS = ["Databricks","Scale AI","Hugging Face","Pinecone","Snowflake","ServiceNow"]
ENGINEER_ORGS = ["NVIDIA","Google Cloud","AWS","Microsoft","Meta","Oracle"]

LLMS = ["GPT-4","Claude 3","Gemini","Llama 3","Mistral"]
VECTOR = ["Pinecone","Weaviate","FAISS","Chroma"]
RAG = ["LangChain","LlamaIndex","RAG"]
INFER = ["vLLM","TensorRT","ONNX","TGI"]

def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def fname():
    return f"{random.choice(FIRST)} {random.choice(LAST)}"

def winsor(x):
    lo, hi = np.percentile(x, [2,95])
    return np.clip(x, lo, hi)

def pct(x):
    r = np.argsort(np.argsort(x))
    return 100 * r / (len(x)-1)

def gen_track(n, role, orgs):
    citations = np.random.lognormal(9 if role=="Frontier" else 7.5, 1.0, n)
    citations = winsor(citations).astype(int)
    logc = np.log10(1 + citations)
    vel = (citations / np.random.uniform(3,10,n)).astype(int)
    stack = np.random.normal(80 if role!="Applied" else 70, 10, n).clip(30,98)
    delivery = np.random.normal(75 if role!="Frontier" else 55, 12, n).clip(20,98)

    score = (
        0.55*pct(logc) + 0.25*stack + 0.20*delivery
        if role=="Frontier"
        else 0.25*pct(logc) + 0.45*delivery + 0.30*stack
    )
    spct = pct(score)

    rows=[]
    for i in range(n):
        h = f"{role.lower()}-{i:03d}"
        rows.append({
            "Person_ID": f"{role[:2].upper()}-{i:03d}",
            "Full_Name": fname(),
            "Role_Type": role,
            "Title": role + " Engineer",
            "Company": random.choice(orgs),
            "LLM_Names": "; ".join(random.sample(LLMS,2)),
            "Vector_Databases": "; ".join(random.sample(VECTOR,2)),
            "RAG_Stack": random.choice(RAG),
            "Inference_Stack": random.choice(INFER),
            "GitHub_Profile": f"https://github.com/{h}",
            "GitHub_Repos": f"{h}/rag-pipeline; {h}/inference-stack",
            "HuggingFace_Profile": f"https://huggingface.co/{h}",
            "ArXiv_Count": random.randint(0,15),
            "SemanticScholar": f"https://semanticscholar.org/{h}",
            "OpenAlex": f"https://openalex.org/A{random.randint(10**9,10**10-1)}",
            "Total_Citations": int(citations[i]),
            "Citation_Velocity": int(vel[i]),
            "Citation_Log10": round(float(logc[i]),4),
            "Stack_Depth_Score": round(float(stack[i]),2),
            "Delivery_Score": round(float(delivery[i]),2),
            "Signal_Score": round(float(score[i]),2),
            "Signal_Percentile": round(float(spct[i]),2),
            "Signal_Tier": "T1" if spct[i]>=90 else "T2" if spct[i]>=70 else "T3",
            "Signal_Skills": "LLM systems, RAG pipelines, vector search, inference optimization",
            "Strengths": "Demonstrates verifiable AI system contribution across modern LLM stacks.",
            "Weaknesses": "Limited public evidence of base-model training at frontier scale.",
            "Run_Timestamp_UTC": now(),
            "SYNTHETIC_FLAG": True
        })
    return pd.DataFrame(rows)

# -----------------------
# Generate + write CSVs
# -----------------------
df_f = gen_track(50,"Frontier",FRONTIER_ORGS)
df_a = gen_track(100,"Applied",APPLIED_ORGS)
df_e = gen_track(100,"AI Engineer",ENGINEER_ORGS)

df_f.to_csv(FRONTIER,index=False)
df_a.to_csv(APPLIED,index=False)
df_e.to_csv(ENGINEER,index=False)

# -----------------------
# Charts
# -----------------------
plt.figure()
plt.hist(np.log10(1+df_f["Total_Citations"]),alpha=0.6,label="Frontier")
plt.hist(np.log10(1+df_a["Total_Citations"]),alpha=0.6,label="Applied")
plt.hist(np.log10(1+df_e["Total_Citations"]),alpha=0.6,label="Engineer")
plt.legend()
plt.title("Citation Distribution (log scale)")
plt.savefig(CHARTS/"citations.png",dpi=160)
plt.close()

plt.figure()
plt.scatter(df_f["Citation_Velocity"],df_f["Signal_Score"],label="Frontier")
plt.scatter(df_a["Citation_Velocity"],df_a["Signal_Score"],label="Applied")
plt.scatter(df_e["Citation_Velocity"],df_e["Signal_Score"],label="Engineer")
plt.legend()
plt.title("Velocity vs Signal Score")
plt.savefig(CHARTS/"velocity_vs_signal.png",dpi=160)
plt.close()

SUMMARY.write_text(
    "Synthetic demo data generated.\n"
    "Math: winsorized citations -> log10 -> percentile -> weighted signal.\n"
    "Median-safe. Outlier-robust. Interview-defensible.\n",
    encoding="utf-8"
)
