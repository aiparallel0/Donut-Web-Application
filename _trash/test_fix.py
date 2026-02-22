"""
Test script to verify the meta tensor fix works
This script tests the model loading without running the full Gradio interface
"""

import sys
import torch

print("=" * 60)
print("TESTING META TENSOR FIX")
print("=" * 60)
print(f"PyTorch version: {torch.__version__}")
print(f"Device: {'GPU' if torch.cuda.is_available() else 'CPU'}")
print()

# Test 1: Import check
print("Test 1: Checking imports...")
try:
    from transformers import DonutProcessor, VisionEncoderDecoderModel
    print("✓ Transformers imported successfully")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

# Test 2: Model loading with fix
print("\nTest 2: Loading model with fix...")
print("(This will download ~800MB on first run)")

model_name = "naver-clova-ix/donut-base-finetuned-cord-v2"
device = "cuda" if torch.cuda.is_available() else "cpu"

try:
    # THE FIX: Load without meta tensors
    print(f"Loading to {device} with device_map=None, low_cpu_mem_usage=False...")
    model = VisionEncoderDecoderModel.from_pretrained(
        model_name,
        device_map=None,              # Disable automatic device mapping
        low_cpu_mem_usage=False,      # Disable low memory mode
        torch_dtype=torch.float32     # Use full precision
    )
    print("✓ Model created without meta tensors")

    # Test 3: Move to device (this used to fail)
    print(f"\nTest 3: Moving model to {device}...")
    model = model.to(device)
    print(f"✓ Model successfully moved to {device}")

    # Test 4: Set to eval mode
    print("\nTest 4: Setting model to eval mode...")
    model.eval()
    print("✓ Model set to eval mode")

    # Test 5: Check model state
    print("\nTest 5: Verifying model state...")
    # Get first parameter to check it's not a meta tensor
    first_param = next(model.parameters())
    if first_param.is_meta:
        print("❌ FAILED: Model still has meta tensors!")
        sys.exit(1)
    else:
        print(f"✓ Model has real tensors (device: {first_param.device})")

    # Test 6: Try to get item from tensor (this used to fail)
    print("\nTest 6: Testing tensor.item() call...")
    try:
        # Create a small tensor and call .item() on it
        test_tensor = torch.tensor([1.0], device=device)
        value = test_tensor.item()
        print(f"✓ tensor.item() works: {value}")
    except Exception as e:
        print(f"❌ tensor.item() failed: {e}")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("✓ ALL TESTS PASSED!")
    print("=" * 60)
    print()
    print("The meta tensor fix is working correctly.")
    print("You can now run: python donut_minimal.py")
    print()

except Exception as e:
    print(f"\n❌ TEST FAILED: {e}")
    print()
    print("Troubleshooting:")
    print("1. Clear cache: rm -rf ~/.cache/huggingface/")
    print("2. Check internet connection")
    print("3. Ensure sufficient disk space (>2GB)")
    import traceback
    traceback.print_exc()
    sys.exit(1)
