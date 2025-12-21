#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_synthetic_evaluations.py
AI Talent Engine — Research_First_Sourcer_Automation
Author: L. David Mendoza © 2025
Purpose: One-pass generator for demo evaluation CSVs.
"""

import os
import math
import random
import pandas as pd
import numpy as np
from datetime import datetime

DEMO_DIR = "demo"
os.makedirs(DEMO_DIR, exist_ok=True)

FILES = {
    "ai_engineer": os.path.join(DEMO_DIR, "demo_ai_engineer_evaluation_PLACEHOLDER.csv"),
    "applied": os.path.join(DEMO_DIR, "demo_applied_evaluation_PLACEHOLDER.csv"),
    "frontier": os.path.join(DEMO_DIR, "demo_frontier_evaluation_PLACEHOLDER.csv"),
}

COLUMNS = [
    "Person_ID", "Full_Name", "Title", "Company", "Role_Type", "SYNTHETIC_FLAG",
    "Company_Type", "Company_Tier", "Ecosystem",
    "Total_Citations", "Citations_Last_5Y", "Citation_Velocity", "H_Index", "OpenAlex_Works_Count",
    "Log_Citation_Score", "Normalized_Influence", "Percentile", "Influence_Tier",
    "LLM_Names", "VectorDBs", "RAG_Frameworks", "Inference_Engines",
    "Fine_Tuning_Methods", "GPU_Stack",
    "GitHub_Profile", "GitHub_Repos_Count", "HuggingFace_Models_Count",
    "ArXiv_Papers_Count", "SemanticScholar_Profile", "Google_Scholar_Profile",
    "Personal_Site", "Overall_Fit_Score", "Signal_Strength",
    "Generated_Timestamp"
]

COMPANY_SETS = {
    "frontier": [
        ("OpenAI", "Frontier Lab", "T1", "OpenAI-like"),
        ("Anthropic", "Frontier Lab", "T1", "Anthropic-like"),
        ("DeepMind", "Frontier Lab", "T1", "Google-like"),
        ("Mistral AI", "Startup", "T2", "Mistral-like"),
        ("Cohere", "Startup", "T2", "Cohere-like"),
        ("xAI", "Startup", "T2", "xAI-like"),
    ],
    "applied": [
        ("Scale AI", "Startup", "T2", "Applied-Infra"),
        ("Databricks", "Hyperscaler", "T2", "Infra-like"),
        ("Adept AI", "Startup", "T3", "Multimodal-like"),
        ("Runway ML", "Startup", "T3", "Creative-AI"),
        ("Character AI", "Startup", "T3", "Chat-AI"),
        ("Hugging Face", "Open Source", "T2", "Community"),
    ],
    "ai_engineer": [
        ("NVIDIA", "Hyperscaler", "T1", "Infra-like"),
        ("Meta AI", "Hyperscaler", "T1", "Meta-like"),
        ("Microsoft AI", "Hyperscaler", "T1", "Azure-like"),
        ("Amazon AGI", "Hyperscaler", "T1", "AWS-like"),
        ("Apple AIML", "Corporate", "T2", "Apple-like"),
        ("OpenAI", "Frontier Lab", "T1", "OpenAI-like"),
    ]
}

LLM_LIST = ["GPT-4", "Claude 3", "LLaMA 3", "Gemini 2", "Mistral 7B", "Mixtral", "Command-R+", "Falcon 180B"]
VDB_LIST = ["FAISS", "Weaviate", "Pinecone", "Milvus", "Chroma"]
RAG_LIST = ["LangChain", "LlamaIndex", "Haystack"]
INFER_LIST = ["vLLM", "TensorRT-LLM", "ONNX Runtime", "Triton"]
FT_LIST = ["LoRA", "QLoRA", "Full Fine-Tuning", "PEFT"]
GPU_LIST = ["A100", "H100", "MI300X", "RTX 6000", "TPU v5e"]

def fake_name():
    first = random.choice(
        ["Alice","Brian","Carla","David","Evelyn","Felix","Grace","Hassan","Ivy","Jun","Kai","Lina",
         "Mateo","Nora","Omar","Priya","Quinn","Ravi","Sofia","Theo","Uma","Viktor","Willow","Yara","Zane"])
    last = random.choice(
        ["Nguyen","Lee","Patel","Garcia","Khan","Smith","Chen","Brown","Takahashi","Silva","Lopez","Ivanov",
         "Martinez","Kim","Singh","Andersson","Wang","Miller"])
    return f"{first} {last}"

def influence_tier(p):
    return "T1" if p >= 90 else ("T2" if p >= 70 else "T3")

def normalized_influence(values):
    median = np.median(values)
    return [min(round(v/median,3),10) for v in values]

def generate_dataset(category, n=25):
    rows=[]
    for i in range(1,n+1):
        cid=f"{category.upper()}_{i:03d}"
        name=fake_name()
        title=random.choice(["Research Scientist","ML Engineer","Applied Scientist","AI Systems Engineer",
                             "Data Scientist","Inference Engineer","RLHF Engineer","LLM Engineer"])
        company,ctype,tier,eco=random.choice(COMPANY_SETS[category])
        total=int(np.random.lognormal(4.3,0.8))
        recent=int(total*random.uniform(0.2,0.5))
        h_idx=int(math.sqrt(total)/random.uniform(1.2,2.0))
        velocity=recent/total
        works=random.randint(10,120)
        log_cit=round(math.log10(total+1),3)
        norm_val=total**0.35/100
        rows.append([cid,name,title,company,category.capitalize(),True,ctype,tier,eco,total,recent,
                     round(velocity,3),h_idx,works,log_cit,norm_val,0,"T3",
                     random.sample(LLM_LIST,2),random.choice(VDB_LIST),random.choice(RAG_LIST),
                     random.choice(INFER_LIST),random.choice(FT_LIST),random.choice(GPU_LIST),
                     f"https://github.com/{name.replace(' ','').lower()}",
                     random.randint(5,150),random.randint(0,10),random.randint(0,20),
                     f"https://semanticscholar.org/{name.replace(' ','').lower()}",
                     f"https://scholar.google.com/{name.replace(' ','').lower()}",
                     f"https://{name.split()[0].lower()}.ai",0.0,random.choice(["High","Medium","Low"]),
                     datetime.now().isoformat()])
    df=pd.DataFrame(rows,columns=COLUMNS)
    df["Normalized_Influence"]=normalized_influence(df["Total_Citations"])
    df["Percentile"]=df["Total_Citations"].rank(pct=True)*100
    df["Influence_Tier"]=df["Percentile"].apply(influence_tier)
    df["Overall_Fit_Score"]=round(
        0.5*df["Normalized_Influence"]+
        0.3*(df["Citation_Velocity"]*10)+
        0.2*(df["H_Index"]/df["H_Index"].max()*10),2)
    return df

if __name__=="__main__":
    random.seed(42); np.random.seed(42)
    for cat in FILES.keys():
        df=generate_dataset(cat,25)
        df.to_csv(FILES[cat],index=False)
        print(f"[✓] Generated {FILES[cat]} ({len(df)} rows, {len(df.columns)} cols)")
    print("All synthetic evaluation datasets successfully generated and schema-complete.")
