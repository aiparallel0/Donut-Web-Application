# -*- coding: utf-8 -*-
"""
Configuration file for DONUT Receipt Parser
Centralized settings for model, inference, and application behavior
"""

import os
from pathlib import Path

# ============================================================================
# PROJECT PATHS
# ============================================================================
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
INPUT_DIR = DATA_DIR / "input"
OUTPUT_DIR = DATA_DIR / "output"
SAMPLES_DIR = DATA_DIR / "samples"
MODELS_DIR = PROJECT_ROOT / "models"
LOGS_DIR = PROJECT_ROOT / "logs"

# Create directories if they don't exist
for directory in [DATA_DIR, INPUT_DIR, OUTPUT_DIR, SAMPLES_DIR, MODELS_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# ============================================================================
# MODEL CONFIGURATION
# ============================================================================
# Primary model (public, no authentication required)
MODEL_NAME = "naver-clova-ix/donut-base-finetuned-cord-v2"
TASK_PROMPT = "<s_cord-v2>"

# Alternative models (uncomment to use)
# MODEL_NAME = "AdamCodd/donut-receipts-extract"  # Requires HuggingFace auth
# TASK_PROMPT = "<s_receipt>"

# Device configuration
DEVICE = "cuda"  # Options: "cuda", "cpu", "auto"
AUTO_DEVICE = True  # Automatically detect best device

# Model cache directory
CACHE_DIR = str(MODELS_DIR)

# ============================================================================
# INFERENCE SETTINGS
# ============================================================================
# Generation parameters
MAX_LENGTH = 512  # Maximum sequence length
NUM_BEAMS = 1  # Number of beams for beam search (1 = greedy)
EARLY_STOPPING = True  # Stop generation when all beams finish
GENERATION_TIMEOUT = 60  # Timeout in seconds (0 = no timeout)

# Batch processing
BATCH_SIZE = 4  # Number of images to process in parallel
MAX_BATCH_SIZE = 8  # Maximum batch size

# ============================================================================
# IMAGE PROCESSING SETTINGS
# ============================================================================
# Image constraints
MAX_IMAGE_SIZE = (1280, 960)  # Maximum image dimensions (width, height)
MIN_IMAGE_SIZE = (100, 100)  # Minimum image dimensions
IMAGE_FORMAT = "RGB"  # Color format for processing
SUPPORTED_FORMATS = [".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"]

# Image preprocessing
RESIZE_STRATEGY = "fit"  # Options: "fit", "crop", "stretch"
MAINTAIN_ASPECT_RATIO = True

# ============================================================================
# OUTPUT SETTINGS
# ============================================================================
# Output formats
SAVE_JSON = True  # Save results as JSON
SAVE_TXT = True  # Save results as formatted text
SAVE_RAW = False  # Save raw model output

# Output formatting
JSON_INDENT = 2  # JSON indentation spaces
JSON_ENSURE_ASCII = False  # Allow unicode in JSON output

# File naming
OUTPUT_TIMESTAMP = True  # Add timestamp to output filenames
OUTPUT_PREFIX = "receipt_"  # Prefix for output files

# ============================================================================
# GRADIO WEB INTERFACE
# ============================================================================
# Server settings
GRADIO_SERVER_NAME = "127.0.0.1"  # Bind address
GRADIO_SERVER_PORT = 7860  # Default port
GRADIO_SHARE = False  # Create public shareable link
GRADIO_DEBUG = False  # Enable debug mode

# Interface settings
SHOW_RAW_OUTPUT = False  # Show raw model output by default
ENABLE_QUEUE = True  # Enable request queuing
MAX_QUEUE_SIZE = 10  # Maximum queued requests

# ============================================================================
# API SETTINGS (for REST API)
# ============================================================================
API_ENABLED = True  # Enable REST API endpoints
API_HOST = "0.0.0.0"  # API bind address
API_PORT = 8000  # API port
API_TITLE = "DONUT Receipt Parser API"
API_VERSION = "1.0.0"
API_DOCS_URL = "/docs"  # Swagger UI documentation URL

# Rate limiting
API_RATE_LIMIT = 100  # Requests per minute per IP
API_MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================
# Logging levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL = "INFO"
LOG_FILE = LOGS_DIR / "donut.log"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Log rotation
LOG_MAX_BYTES = 10 * 1024 * 1024  # 10 MB
LOG_BACKUP_COUNT = 5  # Keep 5 backup log files

# Console logging
LOG_TO_CONSOLE = True
CONSOLE_LOG_LEVEL = "INFO"

# ============================================================================
# PERFORMANCE SETTINGS
# ============================================================================
# Memory management
CLEAR_CACHE_AFTER_INFERENCE = True  # Clear GPU cache after each inference
USE_MIXED_PRECISION = False  # Use FP16 for faster inference (GPU only)

# Threading
NUM_WORKERS = 4  # Number of worker threads for batch processing
PREFETCH_FACTOR = 2  # Number of batches to prefetch

# ============================================================================
# VALIDATION & QUALITY CONTROL
# ============================================================================
# Output validation
VALIDATE_JSON_OUTPUT = True  # Validate JSON structure
MIN_CONFIDENCE_SCORE = 0.0  # Minimum confidence threshold (0-1)

# Receipt validation
VALIDATE_TOTALS = True  # Validate calculated vs reported totals
TOTAL_TOLERANCE = 0.50  # Maximum difference allowed in dollars

# ============================================================================
# ERROR HANDLING
# ============================================================================
# Retry settings
MAX_RETRIES = 3  # Maximum retry attempts on failure
RETRY_DELAY = 1  # Delay between retries in seconds

# Error reporting
DETAILED_ERRORS = True  # Include detailed error messages
SAVE_ERROR_LOGS = True  # Save error logs to file

# ============================================================================
# DEVELOPMENT & DEBUG SETTINGS
# ============================================================================
DEBUG_MODE = False  # Enable debug features
PROFILE_PERFORMANCE = False  # Profile execution time
SAVE_INTERMEDIATE_OUTPUTS = False  # Save preprocessing steps

# Testing
TEST_MODE = False  # Enable test mode (uses smaller models, less strict validation)

# ============================================================================
# ENVIRONMENT OVERRIDES
# ============================================================================
# Override settings with environment variables
if os.getenv("DONUT_MODEL_NAME"):
    MODEL_NAME = os.getenv("DONUT_MODEL_NAME")

if os.getenv("DONUT_DEVICE"):
    DEVICE = os.getenv("DONUT_DEVICE")

if os.getenv("DONUT_DEBUG"):
    DEBUG_MODE = os.getenv("DONUT_DEBUG").lower() == "true"

if os.getenv("DONUT_API_ENABLED"):
    API_ENABLED = os.getenv("DONUT_API_ENABLED").lower() == "true"

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================
def get_config_summary():
    """Return a dictionary of current configuration settings"""
    return {
        "model": {
            "name": MODEL_NAME,
            "task_prompt": TASK_PROMPT,
            "device": DEVICE,
        },
        "inference": {
            "max_length": MAX_LENGTH,
            "num_beams": NUM_BEAMS,
            "batch_size": BATCH_SIZE,
            "timeout": GENERATION_TIMEOUT,
        },
        "paths": {
            "input_dir": str(INPUT_DIR),
            "output_dir": str(OUTPUT_DIR),
            "models_dir": str(MODELS_DIR),
            "logs_dir": str(LOGS_DIR),
        },
        "api": {
            "enabled": API_ENABLED,
            "host": API_HOST,
            "port": API_PORT,
        },
        "gradio": {
            "host": GRADIO_SERVER_NAME,
            "port": GRADIO_SERVER_PORT,
            "share": GRADIO_SHARE,
        }
    }

def print_config():
    """Print current configuration to console"""
    import json
    print("="*60)
    print("DONUT Receipt Parser - Configuration")
    print("="*60)
    print(json.dumps(get_config_summary(), indent=2))
    print("="*60)

# ============================================================================
# VALIDATE CONFIGURATION
# ============================================================================
def validate_config():
    """Validate configuration settings"""
    errors = []

    # Check required directories exist
    if not DATA_DIR.exists():
        errors.append(f"Data directory not found: {DATA_DIR}")

    # Check device settings
    if DEVICE not in ["cuda", "cpu", "auto"]:
        errors.append(f"Invalid device: {DEVICE}. Must be 'cuda', 'cpu', or 'auto'")

    # Check batch size
    if BATCH_SIZE < 1 or BATCH_SIZE > MAX_BATCH_SIZE:
        errors.append(f"Batch size must be between 1 and {MAX_BATCH_SIZE}")

    # Check ports
    if not (1024 <= GRADIO_SERVER_PORT <= 65535):
        errors.append(f"Invalid Gradio port: {GRADIO_SERVER_PORT}")

    if API_ENABLED and not (1024 <= API_PORT <= 65535):
        errors.append(f"Invalid API port: {API_PORT}")

    if errors:
        raise ValueError(f"Configuration validation failed:\n" + "\n".join(f"  - {e}" for e in errors))

    return True

# Validate on import
if not TEST_MODE:
    validate_config()
