# -*- coding: utf-8 -*-
"""
Unit tests for configuration
"""

import unittest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import config


class TestConfiguration(unittest.TestCase):
    """Test configuration settings"""

    def test_paths_exist(self):
        """Test that required directories exist"""
        self.assertTrue(config.DATA_DIR.exists())
        self.assertTrue(config.INPUT_DIR.exists())
        self.assertTrue(config.OUTPUT_DIR.exists())
        self.assertTrue(config.MODELS_DIR.exists())
        self.assertTrue(config.LOGS_DIR.exists())

    def test_model_config(self):
        """Test model configuration is valid"""
        self.assertIsNotNone(config.MODEL_NAME)
        self.assertIsNotNone(config.TASK_PROMPT)
        self.assertIn(config.DEVICE, ["cuda", "cpu", "auto"])

    def test_batch_size(self):
        """Test batch size is valid"""
        self.assertGreater(config.BATCH_SIZE, 0)
        self.assertLessEqual(config.BATCH_SIZE, config.MAX_BATCH_SIZE)

    def test_port_numbers(self):
        """Test port numbers are in valid range"""
        self.assertGreaterEqual(config.GRADIO_SERVER_PORT, 1024)
        self.assertLessEqual(config.GRADIO_SERVER_PORT, 65535)

        if config.API_ENABLED:
            self.assertGreaterEqual(config.API_PORT, 1024)
            self.assertLessEqual(config.API_PORT, 65535)

    def test_supported_formats(self):
        """Test supported image formats list"""
        self.assertGreater(len(config.SUPPORTED_FORMATS), 0)
        for fmt in config.SUPPORTED_FORMATS:
            self.assertTrue(fmt.startswith('.'))

    def test_config_summary(self):
        """Test config summary function"""
        summary = config.get_config_summary()
        self.assertIsInstance(summary, dict)
        self.assertIn("model", summary)
        self.assertIn("inference", summary)
        self.assertIn("paths", summary)

    def test_config_validation(self):
        """Test configuration validation"""
        try:
            config.validate_config()
        except ValueError as e:
            self.fail(f"Configuration validation failed: {e}")


if __name__ == "__main__":
    unittest.main()
