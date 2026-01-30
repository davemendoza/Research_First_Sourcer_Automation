#========================================================================
# AI TALENT ENGINE – SIGNAL INTELLIGENCE
# Proprietary and Confidential
# © 2025–2026 L. David Mendoza. All Rights Reserved.
#========================================================================
# This file contains proprietary intellectual property and trade secrets of
# L. David Mendoza and is part of the AI Talent Engine – Signal Intelligence system.
#
# Unauthorized access, use, copying, modification, distribution, disclosure,
# reverse engineering, or derivative use, in whole or in part, is strictly
# prohibited without prior written authorization.
#========================================================================
from __future__ import annotations

from pathlib import Path
from typing import List

import pandas as pd

try:
    from langchain.schema import Document
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain_community.vectorstores import FAISS
    from langchain_openai import OpenAIEmbeddings
except Exception as exc:  # pragma: no cover - dependency enforced at runtime
    raise RuntimeError("LangChain dependencies are required for Phase 10") from exc

import qa_gate


REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_people_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def _documents_from_df(df: pd.DataFrame) -> List[Document]:
    docs: List[Document] = []
    for idx, row in df.iterrows():
        text = row.to_json()
        docs.append(Document(page_content=text, metadata={"row_index": int(idx)}))
    return docs


def build_vector_store(
    people_csv: Path,
    gold_standard_xlsx: Path,
    run_manifest_json: Path,
    vector_dir: Path,
) -> None:
    if not qa_gate.should_initialize_components(), str(gold_standard_xlsx), str(run_manifest_json)]):
        raise RuntimeError("RAG inputs must be people.FULL.csv, gold_standard.xlsx, run_manifest.json only.")

    df = _load_people_csv(people_csv)
    docs = _documents_from_df(df)
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    split_docs = splitter.split_documents(docs)
    embeddings = OpenAIEmbeddings()
    vector = FAISS.from_documents(split_docs, embeddings)
    vector.save_local(str(vector_dir))
