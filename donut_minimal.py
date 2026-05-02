"""
DONUT Receipt Parser - Enhanced with English Receipt Model
Uses AdamCodd/donut-receipts-extract for better English receipt performance
"""

import os
import sys
import warnings
from pathlib import Path
import re
import json
import socket

# Suppress warnings
warnings.filterwarnings('ignore')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

print("Loading dependencies...")

# Check PyTorch
try:
    import torch
    print(f"✓ PyTorch {torch.__version__} loaded")
except ImportError:
    print("✗ PyTorch not installed. Run: pip install torch")
    sys.exit(1)

# Check Transformers
try:
    from transformers import DonutProcessor, VisionEncoderDecoderModel
    print("✓ Transformers loaded")
except ImportError:
    print("✗ Transformers not installed. Run: pip install transformers")
    sys.exit(1)

# Check Gradio
try:
    import gradio as gr
    print("✓ Gradio loaded")
except ImportError:
    print("✗ Gradio not installed. Run: pip install gradio")
    sys.exit(1)

try:
    from PIL import Image
    print("✓ Pillow loaded")
except ImportError:
    print("✗ Pillow not installed. Run: pip install pillow")
    sys.exit(1)

print("=" * 60)
print("DONUT Receipt Parser - English Receipt Model")
print("=" * 60)
print(f"Python: {sys.version.split()[0]}")
print(f"Working directory: {os.getcwd()}")
print(f"Device: {'GPU' if torch.cuda.is_available() else 'CPU'}")

# Global variables
processor = None
model = None
device = "cuda" if torch.cuda.is_available() else "cpu"

def load_model():
    """Load DONUT model fine-tuned on English receipts"""
    global processor, model, device

    print("\n" + "=" * 60)
    print("Loading DONUT English Receipt Model...")
    print("=" * 60)

    # Using English receipt-trained model
    model_name = "AdamCodd/donut-receipts-extract"

    print(f"Model: {model_name}")
    print("This model is trained on English receipts (SROIE dataset)")
    print("Should perform better on American receipts like Trader Joe's")

    try:
        print("\nLoading processor...")
        processor = DonutProcessor.from_pretrained(model_name)
        print("✓ Processor loaded")

        print(f"\nLoading model to {device}...")
        print("Note: First run will download ~800MB")

        model = VisionEncoderDecoderModel.from_pretrained(
            model_name,
            device_map=None,
            low_cpu_mem_usage=False,
            torch_dtype=torch.float32
        )

        model = model.to(device)
        model.eval()

        print(f"✓ Model loaded successfully on {device}")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"✗ Error loading model: {e}")
        print("\nTroubleshooting:")
        print("1. Clear cache: rm -rf ~/.cache/huggingface/")
        print("2. Ensure stable internet connection")
        print("3. Check available disk space")
        return False

def clean_tag_content(text):
    """Remove any remaining unclosed tags from text"""
    text = re.sub(r'</?s_[a-z_]+>', '', text)
    return text.strip()

def extract_price_from_text(text):
    """Extract valid price from text, handling malformed data"""
    if text is None:
        return None
    # Prefer a fully formed decimal price
    price_match = re.search(r'\$?\d+\.\d{2}', text)
    if price_match:
        price = price_match.group()
        if not price.startswith('$'):
            price = '$' + price
        return price

    # Fall back to a bare integer (rare in this model's output)
    price_match = re.search(r'\$?\d+', text)
    if price_match:
        price = price_match.group()
        if not price.startswith('$'):
            price = '$' + price
        if '.' not in price:
            price = price + '.00'
        return price

    return None

def parse_donut_output(raw_output):
    """
    Parse DONUT's raw output from English receipt model.

    The AdamCodd/donut-receipts-extract model emits one <s_menu>...</s_menu>
    block per line item, so we must collect ALL of them rather than only
    the first match.
    """
    print("\n" + "=" * 60)
    print("DEBUG: RAW DONUT OUTPUT ANALYSIS")
    print("=" * 60)

    receipt = {
        'store_info': {},
        'items': [],
        'subtotal': None,
        'total': None,
        'payment': {},
        'metadata': {}
    }

    # Print raw output for debugging
    print("Raw output preview (first 500 chars):")
    print(raw_output[:500])
    print("...")

    # Store name: model uses <s_company> primarily, sometimes <s_store>/<s_storename>
    for tag in ('s_company', 's_store', 's_storename'):
        m = re.search(rf'<{tag}>\s*([^<]+?)\s*</{tag}>', raw_output)
        if m:
            receipt['store_info']['name'] = clean_tag_content(m.group(1))
            break

    # Address
    address_match = re.search(r'<s_address>\s*([^<]+?)\s*</s_address>', raw_output)
    if address_match:
        address_text = clean_tag_content(address_match.group(1))
        receipt['store_info']['address'] = [
            addr.strip() for addr in address_text.split('\n') if addr.strip()
        ]

    # Date
    date_match = re.search(r'<s_date>\s*([^<]+?)\s*</s_date>', raw_output)
    if date_match:
        receipt['store_info']['date'] = clean_tag_content(date_match.group(1))

    # Time (optional)
    time_match = re.search(r'<s_time>\s*([^<]+?)\s*</s_time>', raw_output)
    if time_match:
        receipt['store_info']['time'] = clean_tag_content(time_match.group(1))

    # Phone
    phone_match = re.search(r'<s_phone>\s*([^<]+?)\s*</s_phone>', raw_output)
    if phone_match:
        receipt['store_info']['phone'] = clean_tag_content(phone_match.group(1))

    # Items: each item is wrapped in its own <s_menu>...</s_menu>.
    # Use findall to collect every block, then extract name/price from each.
    menu_blocks = re.findall(r'<s_menu>(.*?)</s_menu>', raw_output, re.DOTALL)
    print(f"\n\U0001F4CB Found {len(menu_blocks)} <s_menu> blocks")

    for block in menu_blocks:
        name_match = re.search(r'<s_nm>\s*([^<]+?)\s*</s_nm>', block, re.DOTALL)
        price_match = re.search(r'<s_price>\s*([^<]+?)\s*</s_price>', block, re.DOTALL)
        cnt_match = re.search(r'<s_cnt>\s*([^<]+?)\s*</s_cnt>', block, re.DOTALL)

        if not name_match:
            continue
        clean_name = clean_tag_content(name_match.group(1))
        if not clean_name:
            continue

        item = {'name': clean_name}
        if price_match:
            clean_price = extract_price_from_text(clean_tag_content(price_match.group(1)))
            if clean_price:
                item['price'] = clean_price
        if cnt_match:
            cnt = clean_tag_content(cnt_match.group(1))
            if cnt:
                item['count'] = cnt
        receipt['items'].append(item)
        print(f"  - {item.get('name')}: {item.get('price', '[no price]')}")

    # Fallback: pair up <s_nm> and <s_price> globally if menu blocks were absent
    if not receipt['items']:
        print("\n⚠ Menu-based parsing found no items, trying global extraction...")

        all_names = re.findall(r'<s_nm>\s*([^<]+?)\s*</s_nm>', raw_output, re.DOTALL)
        all_prices = re.findall(r'<s_price>\s*([^<]+?)\s*</s_price>', raw_output, re.DOTALL)

        print(f"  Found {len(all_names)} names, {len(all_prices)} prices")

        for i, name in enumerate(all_names):
            clean_name = clean_tag_content(name)
            if clean_name and len(clean_name) > 1:
                item = {'name': clean_name}
                if i < len(all_prices):
                    clean_price = extract_price_from_text(clean_tag_content(all_prices[i]))
                    if clean_price:
                        item['price'] = clean_price
                receipt['items'].append(item)

    # Total
    total_match = re.search(r'<s_total>\s*([^<]+?)\s*</s_total>', raw_output)
    if total_match:
        receipt['total'] = extract_price_from_text(clean_tag_content(total_match.group(1)))

    # Subtotal: accept both <s_subtotal> and <s_sub_total>, but require
    # the open and close tags to match.
    subtotal_match = re.search(
        r'<s_subtotal>\s*([^<]+?)\s*</s_subtotal>'
        r'|<s_sub_total>\s*([^<]+?)\s*</s_sub_total>',
        raw_output,
    )
    if subtotal_match:
        sub_text = subtotal_match.group(1) or subtotal_match.group(2)
        receipt['subtotal'] = extract_price_from_text(clean_tag_content(sub_text))

    # Tax
    tax_match = re.search(r'<s_tax>\s*([^<]+?)\s*</s_tax>', raw_output)
    if tax_match:
        receipt['metadata']['tax'] = extract_price_from_text(clean_tag_content(tax_match.group(1)))

    # Discount
    discount_match = re.search(r'<s_discount>\s*([^<]+?)\s*</s_discount>', raw_output)
    if discount_match:
        receipt['metadata']['discount'] = extract_price_from_text(
            clean_tag_content(discount_match.group(1))
        )

    print(f"\n✅ Parsed {len(receipt['items'])} items total")
    print("=" * 60 + "\n")

    return receipt

def validate_and_enhance_receipt(receipt_data, image=None):
    """Validate and enhance receipt data"""
    def normalize_price(price_str):
        if not price_str:
            return None
        price_str = str(price_str).strip()
        nums = re.findall(r'\d+\.\d{2}|\d+', price_str)
        if nums:
            price_val = nums[0]
            if '.' not in price_val:
                price_val = f"{price_val}.00"
            return f"${price_val}" if not price_val.startswith('$') else price_val
        return price_str

    # Normalize prices
    if receipt_data.get('subtotal'):
        receipt_data['subtotal'] = normalize_price(receipt_data['subtotal'])

    if receipt_data.get('total'):
        receipt_data['total'] = normalize_price(receipt_data['total'])

    if receipt_data.get('metadata'):
        if receipt_data['metadata'].get('tax'):
            receipt_data['metadata']['tax'] = normalize_price(receipt_data['metadata']['tax'])
        if receipt_data['metadata'].get('discount'):
            receipt_data['metadata']['discount'] = normalize_price(receipt_data['metadata']['discount'])

    for item in receipt_data.get('items', []):
        if item.get('price'):
            item['price'] = normalize_price(item['price'])

    # Remove duplicates
    seen_items = set()
    unique_items = []
    for item in receipt_data.get('items', []):
        item_key = f"{item.get('name', '')}_{item.get('price', '')}"
        if item_key not in seen_items:
            seen_items.add(item_key)
            unique_items.append(item)
    receipt_data['items'] = unique_items

    # Calculate and validate totals
    if receipt_data.get('items'):
        calculated_total = 0.0
        for item in receipt_data['items']:
            price_str = item.get('price', '0')
            try:
                price = float(re.sub(r'[^\d.]', '', price_str))
                calculated_total += price
            except Exception:
                pass

        receipt_data['calculated_subtotal'] = f"${calculated_total:.2f}"

        if receipt_data.get('subtotal'):
            try:
                reported = float(re.sub(r'[^\d.]', '', receipt_data['subtotal']))
                diff = abs(calculated_total - reported)
                if diff > 0.50:
                    receipt_data['validation_warning'] = (
                        f"Item total (${calculated_total:.2f}) differs from "
                        f"subtotal ({receipt_data['subtotal']})"
                    )
            except Exception:
                pass
        elif receipt_data.get('total'):
            try:
                reported = float(re.sub(r'[^\d.]', '', receipt_data['total']))
                diff = abs(calculated_total - reported)
                if diff > 0.50:
                    receipt_data['validation_warning'] = (
                        f"Item total (${calculated_total:.2f}) differs from "
                        f"total ({receipt_data['total']})"
                    )
            except Exception:
                pass

    return receipt_data

def format_structured_output(receipt_data):
    """Format structured receipt data for display"""
    output = []

    output.append("╔" + "═" * 58 + "╗")
    output.append("║" + " " * 16 + "\U0001F9FE RECEIPT ANALYSIS" + " " * 22 + "║")
    output.append("╚" + "═" * 58 + "╝")
    output.append("")

    if receipt_data.get('validation_warning'):
        output.append("⚠️  " + receipt_data['validation_warning'])
        output.append("")

    # Store Information
    if receipt_data.get('store_info'):
        output.append("┌─ STORE INFORMATION ─────────────────────────────────────┐")
        store = receipt_data['store_info']

        if store.get('name'):
            output.append(f"│ Store: {store['name']:<49}│")

        if store.get('address'):
            for addr in store['address'][:3]:
                if len(addr) > 55:
                    addr = addr[:52] + "..."
                output.append(f"│ {addr:<55}│")

        if store.get('phone'):
            output.append(f"│ Phone: {store['phone']:<49}│")

        if store.get('date'):
            output.append(f"│ Date: {store['date']:<50}│")

        if store.get('time'):
            output.append(f"│ Time: {store['time']:<50}│")

        output.append("└" + "─" * 58 + "┘")
        output.append("")

    # Items
    if receipt_data.get('items'):
        output.append("┌─ ITEMS PURCHASED ──────────────────────────────────────┐")
        output.append("│ #  Item Name                                    Price    │")
        output.append("├" + "─" * 58 + "┤")

        for idx, item in enumerate(receipt_data['items'], 1):
            name = item.get('name', 'Unknown Item')
            price = item.get('price', '[N/A]')

            if len(name) > 42:
                name = name[:39] + "..."

            price_display = price if price else "  [N/A]"

            output.append(f"│{idx:3}. {name:<43} {price_display:>8} │")

        output.append("└" + "─" * 58 + "┘")
        output.append("")

    # Totals
    output.append("┌─ TOTALS ────────────────────────────────────────────────┐")

    if receipt_data.get('calculated_subtotal'):
        output.append(f"│ Items Sum:                                    {receipt_data['calculated_subtotal']:>10} │")

    if receipt_data.get('subtotal'):
        label = "Subtotal:" if not receipt_data.get('calculated_subtotal') else "Receipt Subtotal:"
        output.append(f"│ {label:<45} {receipt_data['subtotal']:>10} │")

    if receipt_data.get('metadata', {}).get('tax'):
        output.append(f"│ Tax:                                          {receipt_data['metadata']['tax']:>10} │")

    if receipt_data.get('metadata', {}).get('discount'):
        output.append(f"│ Discount:                                     {receipt_data['metadata']['discount']:>10} │")

    if receipt_data.get('total'):
        output.append(f"│ TOTAL:                                        {receipt_data['total']:>10} │")

    output.append("└" + "─" * 58 + "┘")
    output.append("")

    return "\n".join(output)

def parse_receipt(image):
    """Parse receipt image and extract information"""
    global processor, model, device

    if model is None or processor is None:
        print("Model not loaded, loading now...")
        if not load_model():
            return {"error": "Failed to load model"}

    try:
        print("\nProcessing receipt...")

        if isinstance(image, str):
            image = Image.open(image).convert("RGB")
        elif not isinstance(image, Image.Image):
            image = Image.fromarray(image).convert("RGB")

        # NOTE: This model uses <s_receipt> as task prompt (V2)
        task_prompt = "<s_receipt>"

        decoder_input_ids = processor.tokenizer(
            task_prompt,
            add_special_tokens=False,
            return_tensors="pt"
        ).input_ids.to(device)

        pixel_values = processor(
            image,
            return_tensors="pt"
        ).pixel_values.to(device)

        print("Generating predictions...")
        with torch.no_grad():
            outputs = model.generate(
                pixel_values,
                decoder_input_ids=decoder_input_ids,
                max_length=model.decoder.config.max_position_embeddings,
                pad_token_id=processor.tokenizer.pad_token_id,
                eos_token_id=processor.tokenizer.eos_token_id,
                use_cache=True,
                bad_words_ids=[[processor.tokenizer.unk_token_id]],
                return_dict_in_generate=True,
                num_beams=1,
            )

        sequence = processor.batch_decode(outputs.sequences)[0]
        sequence = sequence.replace(processor.tokenizer.eos_token, "").replace(processor.tokenizer.pad_token, "")
        sequence = sequence.replace(task_prompt, "")

        print("✓ Receipt parsed successfully")

        structured_data = parse_donut_output(sequence)
        structured_data = validate_and_enhance_receipt(structured_data, image)
        structured_data['raw_output'] = sequence

        return structured_data

    except Exception as e:
        error_msg = f"Processing error: {str(e)}"
        print(f"✗ {error_msg}")
        import traceback
        traceback.print_exc()
        return {"error": error_msg}

def gradio_interface(image, show_raw):
    """Gradio interface wrapper"""
    if image is None:
        return "Please upload an image", "", ""

    result = parse_receipt(image)

    if "error" in result:
        return f"✗ Error: {result['error']}", "", ""

    formatted = format_structured_output(result)

    json_data = {k: v for k, v in result.items() if k != 'raw_output'}
    json_output = json.dumps(json_data, indent=2, ensure_ascii=False)

    raw = ""
    if show_raw and 'raw_output' in result:
        raw = "=" * 60 + "\n"
        raw += "RAW DONUT OUTPUT:\n"
        raw += "=" * 60 + "\n"
        raw += result['raw_output']
        raw += "\n" + "=" * 60

    return formatted, json_output, raw

print("\nPreloading model...")
if load_model():
    print("\n✓ Ready to process receipts!")
else:
    print("\n⚠ Model will load when you process first image")

print("\n" + "=" * 60)
print("Starting web interface...")
print("=" * 60)

with gr.Blocks(title="\U0001F9FE DONUT Receipt Parser") as demo:
    gr.Markdown("""
    # \U0001F9FE DONUT Receipt Parser - English Receipt Model
    Upload a receipt image to extract structured information.

    **Model:** AdamCodd/donut-receipts-extract (trained on English receipts)

    **Features:**
    - Fine-tuned on SROIE English receipt dataset
    - Better performance on American receipts
    - Organized sections (Store, Items, Totals)
    - JSON export for integration
    - Validation of totals
    """)

    with gr.Row():
        with gr.Column():
            image_input = gr.Image(type="pil", label="Upload Receipt Image")
            show_raw = gr.Checkbox(label="Show raw DONUT output (for debugging)", value=False)
            process_btn = gr.Button("Parse Receipt", variant="primary")

        with gr.Column():
            formatted_output = gr.Textbox(label="\U0001F4C4 Formatted Receipt", lines=25, max_lines=30)

    with gr.Row():
        json_output = gr.Textbox(label="\U0001F4CB JSON Output (for integration)", lines=15)

    with gr.Row():
        raw_output = gr.Textbox(label="\U0001F50D Raw DONUT Output (debug)", lines=10, visible=True)

    process_btn.click(
        fn=gradio_interface,
        inputs=[image_input, show_raw],
        outputs=[formatted_output, json_output, raw_output]
    )

    gr.Markdown("""
    ---
    **Note:** First processing may take longer due to model initialization.
    This model is trained on English receipts and should work better with American formats.
    """)

if __name__ == "__main__":
    def find_free_port(start_port=7860, max_attempts=10):
        """Find an available port starting from start_port"""
        for port in range(start_port, start_port + max_attempts):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('127.0.0.1', port))
                    return port
            except OSError:
                continue
        return None

    port = find_free_port()
    if port is None:
        print("❌ Could not find available port. Please close other applications.")
        sys.exit(1)

    print(f"\n\U0001F680 Launching on http://127.0.0.1:{port}")
    demo.launch(
        server_name="127.0.0.1",
        server_port=port,
        share=False,
        show_error=True
    )
