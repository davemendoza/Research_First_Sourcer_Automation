"""
EXECUTION_CORE/determinative_skill_resolver.py
============================================================
DETERMINATIVE SKILL AREAS RESOLVER (Sample.xlsx Gold Standard)

Maintainer: L. David Mendoza © 2026
Version: v1.0.0 (Autogen rebuild, best-in-class)

Mission:
Populate the Sample.xlsx-style determinative skill areas field using evidence only.

Outputs (row fields, if present/desired by caller):
- Determinative_Skill_Areas
- Field_Level_Provenance_JSON (augmented, if present)

Canonical determinative skill areas (exact strings):
- multimodal fusion (vision + text + audio)
- Mixture-of-Experts routing and expert load balancing
- distributed training (NCCL/DeepSpeed/FSDP)
- base-model architecture & scaling
- kernel-level inference optimization (Triton/CUDA)
- quantization (GPTQ/AWQ/GGUF, INT4/INT8)

Contract:
- resolve_determinative_skill_areas(row: dict) -> list[str]
- apply_determinative_skill_areas(rows: list[dict], out_field: str="Determinative_Skill_Areas") -> list[dict]

Safety:
- Evidence-only. No fabrication.
- Deterministic. Pure functions on provided row data.
- No network calls.

Validation:
python3 -m py_compile EXECUTION_CORE/_AUTOGEN_STAGING/determinative_skill_resolver.py

Git:
git add EXECUTION_CORE/determinative_skill_resolver.py
git commit -m "Add determinative skill areas resolver (Sample.xlsx gold standard)"
git push
"""
from __future__ import annotations
import json
import re
from typing import Any, Dict, Iterable, List, Tuple
_VERSION = 'v1.0.0'

def _norm(s: str) -> str:
    s = (s or '').strip().lower()
    s = _WS_RE.sub(' ', s)
    return s

def _safe_str(v: Any) -> str:
    if v is None:
        return ''
    try:
        return str(v)
    except Exception:
        return ''

def _collect_evidence_text(row: Dict[str, Any]) -> str:
    """
    Conservative: only uses existing row fields. If the pipeline supplies rich fields
    (READMEs, repo descriptions, abstracts), this becomes very strong.
    """
    preferred_keys = ['GitHub_Repo_Evidence_Why', 'Repo_Topics_Keywords', 'Downstream_Adoption_Signal', 'Open_Source_Impact_Note', 'OSS_Evidence', 'OSS_Signals', 'GitHub_Notes', 'Repo_Notes', 'Repo_Descriptions', 'Repo_Readme_Text', 'Repo_README_Text', 'Repo_Text', 'Repo_Evidence_Text', 'Repo_Evidence', 'GitHub_Profile_Bio', 'GitHub_Profile_Name', 'GitHub_Profile_Company', 'GitHub_Profile_Location', 'GitHub_Profile_Blog', 'Scholar_Abstracts', 'Paper_Abstracts', 'Publication_Abstracts', 'Publications_Text', 'Citations_Text', 'Influence_Evidence', 'Research_Notes', 'Summary', 'Experience', 'Skills', 'Skills2', 'Headline', 'Title', 'Prior_Titles', 'Strengths']
    parts: List[str] = []
    for k in preferred_keys:
        if k in row and row.get(k):
            parts.append(_safe_str(row.get(k)))
    for k, v in row.items():
        if k in preferred_keys:
            continue
        if isinstance(v, str) and v.strip():
            if k.endswith('_JSON') or k.endswith('_json'):
                continue
            parts.append(v)
    return _norm(' \n '.join(parts))

def _has_any(text: str, needles: Iterable[str]) -> bool:
    return any((n in text for n in needles))

def _detect_multimodal(text: str) -> Tuple[bool, List[str]]:
    """
    Requires multimodal evidence beyond generic "multimodal".
    """
    reasons: List[str] = []
    hard = ['vision-language', 'vision language', 'vision+language', 'vlm', 'vqa', 'image caption', 'image-caption', 'clip ', 'openclip', 'siglip', 'blip', 'llava', 'flamingo', 'kosmos', 'paligemma', 'qwen-vl', 'gemini vision', 'gpt-4o', 'audio-to-text', 'speech-to-text', 'asr', 'whisper', 'wav2vec', 'tacotron', 'tts', 'speech synthesis', 'audio encoder', 'audio decoder', 'multimodal transformer', 'cross-attention', 'cross attention', 'late fusion', 'early fusion']
    gate = ['vision', 'image', 'audio', 'speech', 'video', 'text', 'language']
    if _has_any(text, hard) and _has_any(text, gate):
        reasons.append('found multimodal model or modality-fusion indicators')
        return (True, reasons)
    modalities = 0
    for m in ('vision', 'image', 'audio', 'speech', 'video'):
        if m in text:
            modalities += 1
    if modalities >= 2 and 'fusion' in text:
        reasons.append('found 2+ modalities plus fusion')
        return (True, reasons)
    return (False, reasons)

def _detect_moe(text: str) -> Tuple[bool, List[str]]:
    reasons: List[str] = []
    moe_terms = ['mixture of experts', 'mixture-of-experts', 'moe', 'switch transformer', 'expert routing', 'expert router', 'routing', 'top-k gating', 'top k gating', 'capacity factor', 'expert capacity', 'load balancing', 'auxiliary loss', 'router z-loss', 'router z loss', 'expert parallel', 'expert-parallel', 'gshard', 'mesh-tensorflow', 'deepseek-moe', 'mixtral', 'dbrx']
    gate = ['router', 'routing', 'load balancing', 'capacity', 'expert', 'gating', 'top-k', 'top k']
    if _has_any(text, moe_terms) and _has_any(text, gate):
        reasons.append('found MoE and routing/load-balancing indicators')
        return (True, reasons)
    return (False, reasons)

def _detect_distributed_training(text: str) -> Tuple[bool, List[str]]:
    reasons: List[str] = []
    terms = ['nccl', 'deepspeed', 'fsdp', 'fully sharded data parallel', 'ddp', 'distributed data parallel', 'torchrun', 'torch.distributed', 'allreduce', 'all-reduce', 'ring allreduce', 'pipeline parallel', 'tensor parallel', 'sequence parallel', 'sharded optimizer', 'zero-1', 'zero-2', 'zero-3', 'zeRO', 'megatron', 'megatron-lm', 'slurm', 'mpi', 'horovod', 'collectives', 'gloo', 'rdma', 'infiniband']
    gate = ['distributed', 'training', 'pretrain', 'pre-training', 'train', 'fine-tune', 'finetune', 'scale', 'cluster', 'multi-gpu', 'multi gpu', 'multi-node', 'multi node']
    if _has_any(text, terms) and _has_any(text, gate):
        reasons.append('found NCCL/DeepSpeed/FSDP or distributed training primitives')
        return (True, reasons)
    return (False, reasons)

def _detect_base_model_arch_scaling(text: str) -> Tuple[bool, List[str]]:
    reasons: List[str] = []
    terms = ['transformer architecture', 'decoder-only', 'encoder-decoder', 'attention mechanism', 'multi-head attention', 'mha', 'gqa', 'mqa', 'swa', 'rotary embedding', 'rope', 'alibi', 'flashattention', 'flash attention', 'paged attention', 'kv cache', 'context length', 'sequence length', 'positional encoding', 'scaling laws', 'chinchilla', 'kaplan', 'parameter count', 'b parameters', 'billion parameters', 'trillion parameters', 'pretraining', 'pre-training', 'tokenizer', 'bpe', 'sentencepiece', 'data mixture', 'deduplication', 'curriculum', 'training recipe', 'optimizer', 'adamw', 'bf16', 'fp16', 'gradient checkpointing', 'activation checkpointing', 'model parallel', 'pipeline parallel', 'tensor parallel']
    gate = ['pretrain', 'pre-training', 'pretraining', 'base model', 'foundation model', 'language model', 'llm', 'scaling', 'architecture', 'train']
    if _has_any(text, terms) and _has_any(text, gate):
        reasons.append('found architecture/scaling signals tied to base-model work')
        return (True, reasons)
    return (False, reasons)

def _detect_kernel_inference_opt(text: str) -> Tuple[bool, List[str]]:
    reasons: List[str] = []
    terms = ['triton', 'cuda', 'cutlass', 'cublas', 'cudnn', 'tensorcore', 'tensor core', 'kernel fusion', 'fusion', 'custom kernel', 'ptx', 'nvcc', 'warp', 'shared memory', 'memory coalescing', 'latency', 'throughput', 'tensorRT', 'tensorrt-llm', 'onnxruntime', 'onnx runtime', 'xla', 'jax pjit', 'inductor', 'torch.compile', 'flashattention', 'flash attention', 'paged attention', 'kv-cache', 'kv cache', 'speculative decoding', 'continuous batching', 'vllm', 'tgi', 'trt-llm', 'llama.cpp', 'ggml', 'gguf']
    gate = ['inference', 'serving', 'decode', 'generation', 'kernel', 'optimiz', 'latency', 'throughput', 'cuda', 'triton']
    if _has_any(text, terms) and _has_any(text, gate):
        reasons.append('found Triton/CUDA or kernel-level inference optimization indicators')
        return (True, reasons)
    return (False, reasons)

def _detect_quantization(text: str) -> Tuple[bool, List[str]]:
    reasons: List[str] = []
    terms = ['gptq', 'awq', 'gguf', 'ggml', 'int4', 'int8', '4-bit', '4 bit', '8-bit', '8 bit', 'bitsandbytes', 'bnb', 'quantization', 'quantize', 'nf4', 'fp8', 'ptq', 'qat', 'post-training quantization', 'quantization-aware training', 'k-bit', 'kbit']
    gate = ['quant', 'int4', 'int8', 'low precision', 'compression', 'memory', 'inference', 'latency']
    if _has_any(text, terms) and _has_any(text, gate):
        reasons.append('found GPTQ/AWQ/GGUF or INT4/INT8 quantization indicators')
        return (True, reasons)
    return (False, reasons)

def resolve_determinative_skill_areas(row: Dict[str, Any]) -> List[str]:
    text = _collect_evidence_text(row)
    out: List[str] = []
    reasons_map: Dict[str, List[str]] = {}
    mm, r = _detect_multimodal(text)
    if mm:
        out.append('multimodal fusion (vision + text + audio)')
        reasons_map['multimodal fusion (vision + text + audio)'] = r
    moe, r = _detect_moe(text)
    if moe:
        out.append('Mixture-of-Experts routing and expert load balancing')
        reasons_map['Mixture-of-Experts routing and expert load balancing'] = r
    dist, r = _detect_distributed_training(text)
    if dist:
        out.append('distributed training (NCCL/DeepSpeed/FSDP)')
        reasons_map['distributed training (NCCL/DeepSpeed/FSDP)'] = r
    base, r = _detect_base_model_arch_scaling(text)
    if base:
        out.append('base-model architecture & scaling')
        reasons_map['base-model architecture & scaling'] = r
    kern, r = _detect_kernel_inference_opt(text)
    if kern:
        out.append('kernel-level inference optimization (Triton/CUDA)')
        reasons_map['kernel-level inference optimization (Triton/CUDA)'] = r
    quant, r = _detect_quantization(text)
    if quant:
        out.append('quantization (GPTQ/AWQ/GGUF, INT4/INT8)')
        reasons_map['quantization (GPTQ/AWQ/GGUF, INT4/INT8)'] = r
    canonical_order = ['multimodal fusion (vision + text + audio)', 'Mixture-of-Experts routing and expert load balancing', 'distributed training (NCCL/DeepSpeed/FSDP)', 'base-model architecture & scaling', 'kernel-level inference optimization (Triton/CUDA)', 'quantization (GPTQ/AWQ/GGUF, INT4/INT8)']
    out = [x for x in canonical_order if x in out]
    if 'Field_Level_Provenance_JSON' in row:
        _augment_provenance(row, 'Determinative_Skill_Areas', out, reasons_map)
    return out

def _augment_provenance(row: Dict[str, Any], field: str, value: Any, reasons_map: Dict[str, Any]) -> None:
    raw = _safe_str(row.get('Field_Level_Provenance_JSON', '')).strip()
    obj: Dict[str, Any] = {}
    if raw:
        try:
            obj = json.loads(raw)
            if not isinstance(obj, dict):
                obj = {}
        except Exception:
            obj = {}
    obj.setdefault(field, {})
    obj[field] = {'version': _VERSION, 'evidence_basis': 'row_text_fields_only', 'value': value, 'reasons': reasons_map}
    row['Field_Level_Provenance_JSON'] = json.dumps(obj, sort_keys=True)

def apply_determinative_skill_areas(rows: List[Dict[str, Any]], out_field: str='Determinative_Skill_Areas') -> List[Dict[str, Any]]:
    for r in rows:
        areas = resolve_determinative_skill_areas(r)
        r[out_field] = '; '.join(areas) if areas else r.get(out_field, '')
    return rows
__all__ = ['resolve_determinative_skill_areas', 'apply_determinative_skill_areas']

def _cli_main():
    _WS_RE = re.compile('\\s+', re.UNICODE)
if __name__ == '__main__':
    _cli_main()
