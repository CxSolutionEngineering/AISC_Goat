"""Pinned open-weight models from several Hugging Face Hub providers.

Demo only. Repo IDs are literal strings so asset discovery picks them up.
"""

from huggingface_hub import hf_hub_download, snapshot_download
from sentence_transformers import SentenceTransformer
from transformers import (
    AutoModelForCausalLM,
    AutoModelForSpeechSeq2Seq,
    AutoProcessor,
    AutoTokenizer,
    pipeline,
)

# --- Chat / reasoning LLMs -------------------------------------------------
QWEN_REPO = "Qwen/Qwen2.5-0.5B-Instruct"                        # Alibaba
MISTRAL_REPO = "mistralai/Mistral-7B-Instruct-v0.2"             # Mistral AI
PHI_REPO = "microsoft/phi-2"                                    # Microsoft
DEEPSEEK_REPO = "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B"     # DeepSeek
GEMMA_REPO = "google/gemma-2-2b-it"                             # Google (gated)

# --- Embeddings / rerankers -----------------------------------------------
BGE_REPO = "BAAI/bge-small-en-v1.5"                             # BAAI
MINILM_REPO = "sentence-transformers/all-MiniLM-L6-v2"          # SBERT

# --- Speech ---------------------------------------------------------------
WHISPER_REPO = "openai/whisper-tiny"                            # OpenAI

# --- Third-party community fine-tune (unvetted provenance, on purpose) ----
COMMUNITY_REPO = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"


def load_qwen():
    tok = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-0.5B-Instruct")
    model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-0.5B-Instruct")
    return model, tok


def load_mistral():
    return AutoModelForCausalLM.from_pretrained(MISTRAL_REPO, device_map="auto")


def load_phi():
    # phi-2 historically shipped custom modeling code
    return AutoModelForCausalLM.from_pretrained(PHI_REPO, trust_remote_code=True)


def load_deepseek():
    return pipeline("text-generation", model="deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B")


def load_gemma():
    return AutoModelForCausalLM.from_pretrained(GEMMA_REPO)


def load_embedder(name: str = BGE_REPO) -> SentenceTransformer:
    return SentenceTransformer("BAAI/bge-small-en-v1.5")


def load_minilm() -> SentenceTransformer:
    return SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


def load_whisper():
    processor = AutoProcessor.from_pretrained("openai/whisper-tiny")
    model = AutoModelForSpeechSeq2Seq.from_pretrained("openai/whisper-tiny")
    return model, processor


def fetch_tinyllama_weights() -> str:
    return snapshot_download("TinyLlama/TinyLlama-1.1B-Chat-v1.0")


def fetch_single_file() -> str:
    # Direct file pull, bypasses from_pretrained's safetensors preference
    return hf_hub_download(repo_id="microsoft/phi-2", filename="config.json")
