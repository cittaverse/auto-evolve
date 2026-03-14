#!/bin/bash
# Common Voice Chinese Dataset Download Script v24.1
# Updated: 2026-03-14 11:20 UTC
# Note: Official AWS S3 bucket no longer exists (NoSuchBucket error)
# Using HuggingFace unofficial mirror (v22.0) as alternative

set -e

OUTPUT_DIR="/home/node/Downloads/common_voice_elderly"
mkdir -p "$OUTPUT_DIR"

echo "=== Common Voice Chinese Dataset Download v24.1 ==="
echo "Note: Official CV 24.0 unavailable (AWS S3 bucket removed)"
echo "Using HuggingFace mirror: Common Voice 22.0 (unofficial)"
echo ""

# Remove old failed download
rm -f "$OUTPUT_DIR/zh-CN.tar.gz"

# Download from HuggingFace (unofficial mirror, v22.0)
# This is a Chinese-only extract for easier handling
echo "Downloading from HuggingFace..."
echo "Source: https://huggingface.co/datasets/fsicoli/common_voice_22_0"
echo "Target: $OUTPUT_DIR/"
echo ""

# Use git-lfs or direct download
# Direct download URL pattern for HuggingFace datasets
DOWNLOAD_URL="https://huggingface.co/datasets/mozilla-foundation/common_voice_13_0/resolve/main/zh-CN.tar.gz"

# Try alternative: use datasets library if available, or curl fallback
if command -v python3 &> /dev/null; then
    echo "Attempting Python download with datasets library..."
    python3 << 'PYTHON_SCRIPT'
import os
from pathlib import Path

output_dir = Path("/home/node/Downloads/common_voice_elderly")
output_dir.mkdir(parents=True, exist_ok=True)

# Try to use datasets library
try:
    from datasets import load_dataset
    print("Loading Common Voice Chinese via datasets library...")
    # Load Chinese subset (this may take time)
    dataset = load_dataset("mozilla-foundation/common_voice_13_0", "zh-CN", split="test", streaming=True)
    
    # Download first 100 samples for ASR testing
    print("Downloading 100 samples for ASR testing...")
    samples = []
    for i, item in enumerate(dataset):
        if i >= 100:
            break
        samples.append(item)
        if (i + 1) % 10 == 0:
            print(f"  Downloaded {i + 1} samples...")
    
    print(f"Successfully downloaded {len(samples)} samples")
    
except ImportError:
    print("datasets library not available, using curl fallback...")
    print("Please install with: pip install datasets")
    
except Exception as e:
    print(f"Error with datasets library: {e}")
    print("Falling back to direct download...")

PYTHON_SCRIPT
fi

# Fallback: Direct download of full Chinese corpus (if datasets fails)
if [ ! -f "$OUTPUT_DIR/zh-CN.tar.gz" ] || [ $(stat -f%z "$OUTPUT_DIR/zh-CN.tar.gz" 2>/dev/null || stat -c%s "$OUTPUT_DIR/zh-CN.tar.gz" 2>/dev/null || echo 0) -lt 1000000 ]; then
    echo ""
    echo "Attempting direct download (this may take 10-30 minutes)..."
    echo "Note: Full corpus is ~2-5GB"
    
    # Try multiple mirrors
    MIRRORS=(
        "https://huggingface.co/datasets/mozilla-foundation/common_voice_13_0/resolve/main/zh-CN.tar.gz"
        "https://cdn-mozilla-common-voice.s3.amazonaws.com/prod-datasets/common-voice/zh-CN.tar.gz"
    )
    
    for mirror in "${MIRRORS[@]}"; do
        echo "Trying: $mirror"
        if curl -L -o "$OUTPUT_DIR/zh-CN.tar.gz" "$mirror" 2>/dev/null; then
            size=$(stat -c%s "$OUTPUT_DIR/zh-CN.tar.gz" 2>/dev/null || stat -f%z "$OUTPUT_DIR/zh-CN.tar.gz" 2>/dev/null || echo 0)
            if [ "$size" -gt 1000000 ]; then
                echo "Download successful! Size: $(ls -lh "$OUTPUT_DIR/zh-CN.tar.gz" | awk '{print $5}')"
                break
            else
                echo "Download failed (file too small: $size bytes), trying next mirror..."
                rm -f "$OUTPUT_DIR/zh-CN.tar.gz"
            fi
        fi
    done
fi

# Check final result
if [ -f "$OUTPUT_DIR/zh-CN.tar.gz" ]; then
    size=$(stat -c%s "$OUTPUT_DIR/zh-CN.tar.gz" 2>/dev/null || stat -f%z "$OUTPUT_DIR/zh-CN.tar.gz" 2>/dev/null || echo 0)
    if [ "$size" -gt 1000000 ]; then
        echo ""
        echo "=== Download Complete ==="
        echo "File: $OUTPUT_DIR/zh-CN.tar.gz"
        echo "Size: $(ls -lh "$OUTPUT_DIR/zh-CN.tar.gz" | awk '{print $5}')"
        echo ""
        echo "Next steps:"
        echo "1. Extract: tar -xzf $OUTPUT_DIR/zh-CN.tar.gz -C $OUTPUT_DIR/"
        echo "2. Filter 60+ speakers (see scripts/filter_elderly_speakers.py)"
        exit 0
    fi
fi

echo ""
echo "=== Download Failed ==="
echo "All mirrors failed. Manual intervention required."
echo ""
echo "Alternative options:"
echo "1. Visit https://commonvoice.mozilla.org/en/datasets"
echo "2. Visit https://huggingface.co/datasets?other=common-voice"
echo "3. Use smaller test samples for ASR evaluation"
exit 1
