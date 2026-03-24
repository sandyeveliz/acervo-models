"""
Prepare and upload model to Hugging Face.

Usage:
    python hf_upload/prepare_and_upload.py              # Just prepare files
    python hf_upload/prepare_and_upload.py --upload      # Prepare + upload
    python hf_upload/prepare_and_upload.py --upload --include-gguf   # Include GGUF files
    python hf_upload/prepare_and_upload.py --upload --include-data   # Include training data
"""

import argparse
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
HF_DIR = PROJECT_ROOT / "hf_upload"
LORA_DIR = PROJECT_ROOT / "02_training" / "outputs" / "s1_sft_v2" / "final_lora"
GGUF_DIR = PROJECT_ROOT / "02_training" / "outputs" / "s1_sft_v2" / "gguf_gguf"
TRAINING_DATA = PROJECT_ROOT / "training_data"

REPO_ID = "SandyVeliz/acervo-extractor-qwen3.5-9b"

# Files to copy from the LoRA output
LORA_FILES = [
    "adapter_config.json",
    "adapter_model.safetensors",
    "tokenizer.json",
    "tokenizer_config.json",
    "chat_template.jinja",
    "processor_config.json",
    "special_tokens_map.json",
]

# Training data files to include (optional)
DATA_FILES = [
    "s1_extraction.jsonl",
    "s1_suplementary_training.jsonl",
    "s1_stress_test.jsonl",
]


def prepare(include_gguf: bool = False, include_data: bool = False):
    """Copy model files to hf_upload/ directory."""
    if not LORA_DIR.exists():
        print(f"ERROR: LoRA not found at {LORA_DIR}")
        print("Run the training notebook first.")
        return False

    # Copy LoRA files
    copied = 0
    for fname in LORA_FILES:
        src = LORA_DIR / fname
        dst = HF_DIR / fname
        if src.exists():
            shutil.copy2(src, dst)
            size_mb = src.stat().st_size / 1e6
            print(f"  {fname} ({size_mb:.1f} MB)")
            copied += 1

    print(f"\nCopied {copied} LoRA files to hf_upload/")

    # Copy GGUF if requested
    if include_gguf and GGUF_DIR.exists():
        gguf_out = HF_DIR / "gguf"
        gguf_out.mkdir(exist_ok=True)
        for f in GGUF_DIR.glob("*.gguf"):
            shutil.copy2(f, gguf_out / f.name)
            size_gb = f.stat().st_size / 1e9
            print(f"  gguf/{f.name} ({size_gb:.1f} GB)")
        print("GGUF files copied.")
    elif include_gguf:
        print(f"WARNING: GGUF not found at {GGUF_DIR}")

    # Copy training data if requested
    if include_data:
        data_out = HF_DIR / "training_data"
        data_out.mkdir(exist_ok=True)
        for fname in DATA_FILES:
            src = TRAINING_DATA / fname
            if src.exists():
                shutil.copy2(src, data_out / fname)
                size_kb = src.stat().st_size / 1e3
                print(f"  training_data/{fname} ({size_kb:.0f} KB)")
        print("Training data copied.")

    # List final contents
    print(f"\nhf_upload/ contents:")
    for f in sorted(HF_DIR.rglob("*")):
        if f.is_file() and f.name != "prepare_and_upload.py":
            rel = f.relative_to(HF_DIR)
            size = f.stat().st_size
            if size > 1e9:
                print(f"  {rel} ({size/1e9:.1f} GB)")
            elif size > 1e6:
                print(f"  {rel} ({size/1e6:.1f} MB)")
            else:
                print(f"  {rel} ({size/1e3:.0f} KB)")

    return True


def upload():
    """Upload hf_upload/ to Hugging Face."""
    try:
        from huggingface_hub import HfApi
    except ImportError:
        print("ERROR: pip install huggingface_hub")
        return

    api = HfApi()

    # Check auth
    try:
        info = api.whoami()
        print(f"Authenticated as: {info['name']}")
    except Exception:
        print("ERROR: Run 'huggingface-cli login' first")
        return

    # Create repo if needed
    api.create_repo(REPO_ID, exist_ok=True, repo_type="model")
    print(f"Repo: https://huggingface.co/{REPO_ID}")

    # Upload all files except this script
    api.upload_folder(
        folder_path=str(HF_DIR),
        repo_id=REPO_ID,
        ignore_patterns=["prepare_and_upload.py", "__pycache__", "*.pyc"],
    )
    print(f"\nUploaded to https://huggingface.co/{REPO_ID}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prepare and upload model to HF")
    parser.add_argument("--upload", action="store_true", help="Upload after preparing")
    parser.add_argument("--include-gguf", action="store_true", help="Include GGUF files")
    parser.add_argument("--include-data", action="store_true", help="Include training data")
    args = parser.parse_args()

    print("=== Preparing HF upload ===\n")
    ok = prepare(include_gguf=args.include_gguf, include_data=args.include_data)

    if ok and args.upload:
        print("\n=== Uploading to Hugging Face ===\n")
        upload()
    elif ok:
        print("\nDry run complete. Add --upload to push to HF.")
