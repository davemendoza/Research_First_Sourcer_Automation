#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Talent Engine – Full Analytics Generator (Corrected)
Author: L. David Mendoza © 2025
"""

import os, math, random, numpy as np, pandas as pd
from datetime import datetime
random.seed(42); np.random.seed(42)

DEMO_DIR="demo"
os.makedirs(DEMO_DIR,exist_ok=True)

FILES={
 "ai_engineer":f"{DEMO_DIR}/demo_ai_engineer_evaluation_PLACEHOLDER.csv",
 "applied":f"{DEMO_DIR}/demo_applied_evaluation_PLACEHOLDER.csv",
 "frontier":f"{DEMO_DIR}/demo_frontier_evaluation_PLACEHOLDER.csv"
}

COMPANY_SETS={
 "frontier":[("OpenAI","Frontier Lab","T1","openai.com"),("Anthropic","Frontier Lab","T1","anthropic.com"),
             ("DeepMind","Frontier Lab","T1","deepmind.com"),("Mistral AI","Startup","T2","mistral.ai"),
             ("Cohere","Startup","T2","cohere.ai")],
 "applied":[("Databricks","Hyperscaler","T2","databricks.com"),("Scale AI","Startup","T2","scale.com"),
            ("Runway","Startup","T3","runwayml.com"),("Adept","Startup","T3","adept.ai"),
            ("Hugging Face","Open Source","T2","huggingface.co")],
 "ai_engineer":[("NVIDIA","Hyperscaler","T1","nvidia.com"),("Meta AI","Hyperscaler","T1","meta.com"),
                ("Microsoft AI","Hyperscaler","T1","microsoft.com"),("Apple AIML","Corporate","T2","apple.com"),
                ("Amazon AGI","Hyperscaler","T1","amazon.com")]
}

LLM_LIST=["GPT-4","Claude 3","LLaMA 3","Gemini 2","Mistral 7B","Mixtral"]
VDB_LIST=["FAISS","Weaviate","Pinecone","Milvus","Chroma"]
RAG_LIST=["LangChain","LlamaIndex","Haystack"]
INFER_LIST=["vLLM","TensorRT-LLM","ONNX Runtime","Triton"]
FT_LIST=["LoRA","QLoRA","Full Fine-Tuning","PEFT"]
GPU_LIST=["A100","H100","MI300X","TPU v5e"]

def fake_name():
    fn=random.choice(["Alice","Brian","Carla","David","Evelyn","Felix","Grace","Hassan","Ivy","Jun","Kai",
                      "Lina","Mateo","Nora","Omar","Priya","Quinn","Ravi","Sofia","Theo","Uma","Viktor",
                      "Willow","Yara","Zane"])
    ln=random.choice(["Nguyen","Lee","Patel","Garcia","Khan","Smith","Chen","Brown","Takahashi","Silva",
                      "Lopez","Ivanov","Martinez","Kim","Singh","Andersson","Wang","Miller"])
    return fn,ln,f"{fn} {ln}"

def influence_tier(p):
    return "T1" if p>=90 else ("T2" if p>=70 else "T3")

def generate(category,n=50):
    rows=[]
    for _ in range(n):
        fn,ln,name=fake_name()
        company,ctype,tier,domain=random.choice(COMPANY_SETS[category])
        title=random.choice(["Research Scientist","ML Engineer","Applied Scientist","AI Systems Engineer","RLHF Engineer"])
        level=random.choice(["Senior","Staff","Principal"])
        corp_email=f"{fn.lower()}.{ln.lower()}@{domain}"
        pers_email=f"{fn.lower()}.research@proton.me"
        linked=f"https://linkedin.com/in/{fn.lower()}-{ln.lower()}-{random.randint(100,999)}"
        port=f"https://{fn.lower()}{ln.lower()}.ai"
        gh=f"https://github.com/{fn.lower()}{ln.lower()}"
        scholar=f"https://scholar.google.com/{fn.lower()}{ln.lower()}"
        semsch=f"https://semanticscholar.org/{fn.lower()}{ln.lower()}"
        rows.append([
            category.capitalize(),name,company,"",title,level,corp_email,pers_email,linked,port,
            scholar,semsch,gh,"AI Systems",
            random.choice(LLM_LIST),random.choice(VDB_LIST),random.choice(RAG_LIST),random.choice(INFER_LIST),
            random.choice(GPU_LIST),random.choice(FT_LIST),"Multimodal Fusion","Alignment",
            "; ".join([f"Scaling {random.choice(LLM_LIST)} Models","Mixture-of-Experts Optimization"]),
            "; ".join(["ICLR 2024 Tutorial","NeurIPS 2023 Talk"]),
            random.choice(["Best Paper","Spotlight","Keynote"]),"Workshop on Safe LLMs",
            "",random.choice(["Distributed Training","RLHF Reward Modeling"]),
            "Limited Dataset Diversity",f"https://{domain}/research",f"https://{domain}/publications",
            f"https://{fn.lower()}.ai/blog",0,0,0,0,0,0,"T3",7
        ])
    df=pd.DataFrame(rows,columns=[
        "AI_Classification","Full_Name","Company","Team_or_Lab","Title","Seniority_Level",
        "Corporate_Email","Personal_Email","LinkedIn_URL","Portfolio_URL","Google_Scholar_URL",
        "Semantic_Scholar_URL","GitHub_URL","Primary_Specialties","LLM_Names","VectorDB_Tech",
        "RAG_Details","Inference_Stack","GPU_Infra_Signals","RLHF_Eval_Signals","Multimodal_Signals",
        "Research_Areas","Top_Papers_or_Blogposts","Conference_Presentations","Awards_Luminary_Signals",
        "Panel_Talks_Workshops","Citation_Trajectory","Strengths","Weaknesses","Corporate_Profile_URL",
        "Publications_Page_URL","Blog_Post_URLs","Citation_Velocity_Score","Collaboration_Count",
        "Cross_Lab_Cluster_ID","Recent_Papers_24mo","Citation_Growth_Rate","Influence_Rank_Change",
        "Influence_Tier","Phase"
    ])
    # ----- analytics -----
    n=len(df)
    df["Total_Citations"]=np.random.lognormal(4.4,0.8,n).astype(int)
    df["Citations_Last_5Y"]=(df["Total_Citations"]*np.random.uniform(0.25,0.55,n)).astype(int)
    df["Citation_Velocity"]=df["Citations_Last_5Y"]/df["Total_Citations"]
    df["H_Index"]=(np.sqrt(df["Total_Citations"])/np.random.uniform(1.2,2.0,n)).astype(int)
    med=np.median(df["Total_Citations"])
    df["Log_Citation_Score"]=np.log10(df["Total_Citations"]+1)
    df["Normalized_Influence"]=df["Total_Citations"]/med
    df["Percentile"]=df["Total_Citations"].rank(pct=True)*100
    df["Influence_Tier"]=df["Percentile"].apply(influence_tier)
    df["Citation_Velocity_Score"]=df["Citation_Velocity"]*10
    df["Collaboration_Count"]=np.random.poisson(8,n)
    df["Cross_Lab_Cluster_ID"]=[f"CL{random.randint(100,999)}" for _ in range(n)]
    df["Recent_Papers_24mo"]=(df["Citations_Last_5Y"]/400).astype(int)
    df["Citation_Growth_Rate"]=np.random.normal(1.0,0.2,n)*df["Citation_Velocity"]
    df["Influence_Rank_Change"]=np.random.randint(-3,4,n)
    df["Overall_Fit_Score"]=0.5*df["Normalized_Influence"]+0.3*(df["Citation_Velocity_Score"]/10)+0.2*(df["H_Index"]/df["H_Index"].max()*10)
    return df

for key,path in FILES.items():
    df=generate(key,50)
    df.to_csv(path,index=False)
    print(f"[✓] {path} written ({len(df)} rows × {len(df.columns)} cols)")
print("All 3 analytics-ready CSVs generated successfully.")
