"""Download required ML models."""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from transformers import AutoTokenizer
from sentence_transformers import SentenceTransformer
from app.config import settings


def main():
    """Download and cache required models."""
    print("Downloading required ML models...")
    
    # Create cache directory
    cache_dir = Path(settings.MODEL_CACHE_DIR)
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Download transformer tokenizer
        print(f"\n1. Downloading {settings.ML_MODEL_NAME}...")
        tokenizer = AutoTokenizer.from_pretrained(
            settings.ML_MODEL_NAME,
            cache_dir=str(cache_dir)
        )
        print(f"✓ Downloaded {settings.ML_MODEL_NAME}")
        
        # Download sentence transformer for embeddings
        print(f"\n2. Downloading {settings.SENTENCE_TRANSFORMER_MODEL}...")
        model = SentenceTransformer(
            settings.SENTENCE_TRANSFORMER_MODEL,
            cache_folder=str(cache_dir)
        )
        print(f"✓ Downloaded {settings.SENTENCE_TRANSFORMER_MODEL}")
        
        print("\n✓ All models downloaded successfully!")
        print(f"Models cached in: {cache_dir}")
        
        return 0
        
    except Exception as e:
        print(f"\nError downloading models: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

