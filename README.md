# DONUT Receipt Parser - Web Application

A Gradio-based web application for parsing receipts using the DONUT model fine-tuned on English receipts.

## Features

- **OCR-free document understanding** using the DONUT transformer model
- **English receipt optimization** using the AdamCodd/donut-receipts-extract model
- **Structured data extraction**: Store info, items, prices, totals
- **JSON export** for easy integration
- **Web interface** powered by Gradio
- **Automatic validation** of extracted totals

## Model

This application uses [AdamCodd/donut-receipts-extract](https://huggingface.co/AdamCodd/donut-receipts-extract), a DONUT model fine-tuned on the SROIE English receipt dataset for better performance on American receipts.

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python3 donut_minimal.py
```

The web interface will launch automatically on an available port (default: 7860).

## Usage

1. Open the web interface in your browser
2. Upload a receipt image (JPG, PNG, etc.)
3. Click "Parse Receipt"
4. View the extracted information in formatted and JSON formats

## System Requirements

- Python 3.8+
- 4GB+ RAM (8GB+ recommended)
- ~2GB disk space for model and dependencies
- GPU recommended but not required (CPU inference supported)

## Technical Details

- **Framework**: PyTorch, Transformers, Gradio
- **Model**: Vision Encoder-Decoder architecture
- **Task prompt**: `<s_receipt>`
- **Output format**: Structured JSON with store info, items, and totals

## Testing

Run the test script to verify the setup:
```bash
python3 test_fix.py
```

## Troubleshooting

### Model download fails
- Ensure stable internet connection
- Check available disk space (>2GB required)
- Clear HuggingFace cache: `rm -rf ~/.cache/huggingface/`

### Out of memory errors
- Close other applications
- The application will use CPU if GPU is unavailable
- Consider using a machine with more RAM

### Port already in use
- The application automatically finds an available port
- Check the console output for the actual port being used

## License

This project uses the DONUT model and is subject to its license terms. See the official [DONUT repository](https://github.com/clovaai/donut) for details.

## Credits

- DONUT model: [Clova AI Research](https://github.com/clovaai/donut)
- Fine-tuned model: [AdamCodd](https://huggingface.co/AdamCodd/donut-receipts-extract)
- Framework: Hugging Face Transformers, Gradio
