# -*- coding: utf-8 -*-
"""
Unit tests for model loading functionality
"""

import unittest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import torch
from transformers import DonutProcessor, VisionEncoderDecoderModel


class TestModelLoader(unittest.TestCase):
    """Test model loading and initialization"""

    @classmethod
    def setUpClass(cls):
        """Load model once for all tests"""
        import config
        cls.model_name = config.MODEL_NAME
        cls.device = "cpu"  # Use CPU for tests

    def test_model_loading(self):
        """Test if model loads successfully"""
        try:
            model = VisionEncoderDecoderModel.from_pretrained(
                self.model_name,
                device_map=None,
                low_cpu_mem_usage=False,
                torch_dtype=torch.float32
            )
            self.assertIsNotNone(model)
        except Exception as e:
            self.fail(f"Model loading failed: {e}")

    def test_processor_loading(self):
        """Test if processor loads successfully"""
        try:
            processor = DonutProcessor.from_pretrained(self.model_name)
            self.assertIsNotNone(processor)
        except Exception as e:
            self.fail(f"Processor loading failed: {e}")

    def test_device_assignment(self):
        """Test if model can be moved to device"""
        try:
            model = VisionEncoderDecoderModel.from_pretrained(
                self.model_name,
                device_map=None,
                low_cpu_mem_usage=False,
                torch_dtype=torch.float32
            )
            model = model.to(self.device)
            model.eval()

            # Check if model is on correct device
            first_param_device = next(model.parameters()).device.type
            self.assertEqual(first_param_device, self.device)
        except Exception as e:
            self.fail(f"Device assignment failed: {e}")

    def test_meta_tensor_fix(self):
        """Test that model doesn't have meta tensors"""
        try:
            model = VisionEncoderDecoderModel.from_pretrained(
                self.model_name,
                device_map=None,
                low_cpu_mem_usage=False,
                torch_dtype=torch.float32
            )
            model = model.to(self.device)

            # Check that parameters are not meta tensors
            for param in model.parameters():
                self.assertFalse(param.is_meta, "Model has meta tensors")
                break  # Check first parameter only
        except Exception as e:
            self.fail(f"Meta tensor check failed: {e}")


if __name__ == "__main__":
    unittest.main()
