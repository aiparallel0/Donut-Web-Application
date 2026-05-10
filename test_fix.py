"""Smoke test for DONUT receipt parser setup.

Verifies that the AdamCodd/donut-receipts-extract model loads with the same
flags donut_minimal.py uses, lands on real (non-meta) tensors, and that the
parser regexes extract a known-good receipt from a synthetic raw sequence.

Usage:
    python3 test_fix.py

Exits 0 on success, 1 on the first failure.
"""

from __future__ import annotations

import re
import sys

MODEL_NAME = "AdamCodd/donut-receipts-extract"
TASK_PROMPT = "<s_receipt>"


def test_imports() -> None:
    print("[1/4] Imports...")
    import torch  # noqa: F401
    from transformers import DonutProcessor, VisionEncoderDecoderModel  # noqa: F401
    from PIL import Image  # noqa: F401
    import gradio  # noqa: F401
    print("      ok")


def test_parser_regexes() -> None:
    """Replicate donut_minimal's regex contract on a synthetic sequence.

    Imported lazily because importing donut_minimal triggers a model download.
    """
    print("[2/4] Parser regexes...")
    raw = (
        "<s_company>Trader Joe's</s_company>"
        "<s_date>2024-11-02</s_date>"
        "<s_menu><s_nm>Bananas</s_nm><s_price>1.99</s_price></s_menu>"
        "<s_menu><s_nm>Almond Butter</s_nm><s_price>7.49</s_price></s_menu>"
        "<s_subtotal>9.48</s_subtotal><s_total>10.21</s_total>"
    )
    company = re.search(r"<s_company>\s*([^<]+?)\s*</s_company>", raw)
    menu_blocks = re.findall(r"<s_menu>(.*?)</s_menu>", raw, re.DOTALL)
    total = re.search(r"<s_total>\s*([^<]+?)\s*</s_total>", raw)
    assert company and company.group(1) == "Trader Joe's", company
    assert len(menu_blocks) == 2, menu_blocks
    assert total and total.group(1) == "10.21", total
    print("      ok")


def test_model_load() -> None:
    print("[3/4] Model load (downloads ~800MB on first run)...")
    import torch
    from transformers import DonutProcessor, VisionEncoderDecoderModel

    device = "cuda" if torch.cuda.is_available() else "cpu"
    DonutProcessor.from_pretrained(MODEL_NAME)
    model = VisionEncoderDecoderModel.from_pretrained(
        MODEL_NAME,
        device_map=None,
        low_cpu_mem_usage=False,
        torch_dtype=torch.float32,
    ).to(device)
    model.eval()

    first_param = next(model.parameters())
    if first_param.is_meta:
        raise RuntimeError("Model parameters are still on meta device")
    print(f"      ok (device={first_param.device})")


def test_task_prompt_token() -> None:
    print("[4/4] Task prompt tokenises...")
    from transformers import DonutProcessor
    proc = DonutProcessor.from_pretrained(MODEL_NAME)
    ids = proc.tokenizer(TASK_PROMPT, add_special_tokens=False, return_tensors="pt").input_ids
    assert ids.numel() > 0, "task prompt produced no tokens"
    print("      ok")


def main() -> int:
    try:
        test_imports()
        test_parser_regexes()
        test_model_load()
        test_task_prompt_token()
    except AssertionError as exc:
        print(f"FAIL: assertion: {exc}")
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"FAIL: {type(exc).__name__}: {exc}")
        return 1
    print("\nAll checks passed. Run: python3 donut_minimal.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
