# HuggingFace Model Authentication Guide

## Issue: Gated Model Access

The `AdamCodd/donut-receipts-extract` model is **gated** on HuggingFace, which means it requires authentication and possibly approval to access.

### Error Message:
```
401 Client Error: Unauthorized
Access to model AdamCodd/donut-receipts-extract is restricted.
You must have access to it and be authenticated to access it. Please log in.
```

---

## Solution 1: Use Public Model (Default - No Authentication Required)

The application now uses `naver-clova-ix/donut-base-finetuned-cord-v2` by default, which is:
- ✅ Publicly accessible (no authentication needed)
- ✅ Trained on CORD v2 receipt dataset
- ✅ Works well for English receipts
- ✅ Actively maintained by Naver Clova AI

**No action needed** - Just run the application:
```bash
python donut_minimal.py
```

---

## Solution 2: Use AdamCodd Model (Requires Authentication)

If you specifically want to use the AdamCodd model, you need to authenticate with HuggingFace:

### Step 1: Create HuggingFace Account
1. Go to https://huggingface.co/join
2. Create a free account

### Step 2: Request Model Access
1. Visit https://huggingface.co/AdamCodd/donut-receipts-extract
2. Click "Request Access" button
3. Wait for approval (may take a few hours to days)

### Step 3: Get Access Token
1. Go to https://huggingface.co/settings/tokens
2. Click "New token"
3. Give it a name (e.g., "donut-app")
4. Select "Read" permission
5. Click "Generate"
6. Copy the token (starts with `hf_...`)

### Step 4: Authenticate

**Option A: Login via CLI (Recommended)**
```bash
pip install huggingface_hub
huggingface-cli login
# Paste your token when prompted
```

**Option B: Use Environment Variable**
```bash
# Windows
set HF_TOKEN=hf_your_token_here

# Linux/Mac
export HF_TOKEN=hf_your_token_here
```

**Option C: Use Token in Code**
Edit `donut_minimal.py` and add:
```python
from huggingface_hub import login
login(token="hf_your_token_here")
```

### Step 5: Change Model in Code
Edit `donut_minimal.py`, line ~72:
```python
# Change from:
model_name = "naver-clova-ix/donut-base-finetuned-cord-v2"

# To:
model_name = "AdamCodd/donut-receipts-extract"
```

Also change the task prompt on line ~428:
```python
# Change from:
task_prompt = "<s_cord-v2>"

# To:
task_prompt = "<s_receipt>"
```

---

## Comparison: Public vs Gated Models

### naver-clova-ix/donut-base-finetuned-cord-v2 (Default)
- ✅ No authentication required
- ✅ Publicly accessible
- ✅ Trained on CORD v2 dataset
- ✅ Well-documented
- ✅ Actively maintained
- ⚠️ General receipt model

### AdamCodd/donut-receipts-extract (Optional)
- ❌ Requires authentication
- ❌ Gated access
- ✅ Trained on SROIE dataset
- ✅ Optimized for English receipts
- ⚠️ May have better performance on specific receipt types

---

## Other Alternative Models (Public - No Auth Required)

If you want to try other models without authentication:

### 1. **naver-clova-ix/donut-base** (Base model)
```python
model_name = "naver-clova-ix/donut-base"
task_prompt = "<s_docvqa>"
```

### 2. **naver-clova-ix/donut-base-finetuned-docvqa** (Document Q&A)
```python
model_name = "naver-clova-ix/donut-base-finetuned-docvqa"
task_prompt = "<s_docvqa>"
```

### 3. **to-be/donut-base-finetuned-invoices** (Invoices)
```python
model_name = "to-be/donut-base-finetuned-invoices"
task_prompt = "<s_invoice>"
```

---

## Troubleshooting Authentication

### Error: "Token is invalid"
- Generate a new token at https://huggingface.co/settings/tokens
- Make sure to copy the entire token (starts with `hf_`)

### Error: "Access still denied after login"
- Check if you've been approved for gated model access
- Visit the model page to see approval status
- Some models require manual approval by the model owner

### Error: "huggingface-cli command not found"
```bash
pip install huggingface_hub
```

---

## Current Configuration

**Model Used:** `naver-clova-ix/donut-base-finetuned-cord-v2`
**Task Prompt:** `<s_cord-v2>`
**Authentication:** Not required ✅

To use a different model, edit:
- `donut_minimal.py` - Line ~72 (model_name)
- `donut_minimal.py` - Line ~428 (task_prompt)
- `diagnose.py` - Line ~72 (model_name)

---

## Quick Reference

```bash
# Install HuggingFace CLI
pip install huggingface_hub

# Login
huggingface-cli login

# Check login status
huggingface-cli whoami

# Logout
huggingface-cli logout
```

---

**Last Updated:** 2025-11-11
**Issue:** Gated model access resolved by using public model
**Status:** Working ✅
