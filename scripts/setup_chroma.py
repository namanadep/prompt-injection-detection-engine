"""Initialize ChromaDB with seed data."""
import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.database.chroma_client import chroma_client
from app.config import settings


def main():
    """Load known attacks into ChromaDB."""
    print("Initializing ChromaDB with seed data...")
    
    # Load known attacks
    attacks_file = Path(settings.KNOWN_ATTACKS_FILE)
    if not attacks_file.exists():
        print(f"Error: Attacks file not found at {attacks_file}")
        return 1
    
    try:
        with open(attacks_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            attacks = data.get('attacks', [])
        
        if not attacks:
            print("Warning: No attacks found in data file")
            return 1
        
        print(f"Loading {len(attacks)} known attacks...")
        
        # Reset collection if requested
        import sys
        if '--reset' in sys.argv:
            print("Resetting ChromaDB collection...")
            chroma_client.reset()
        
        # Add attacks
        chroma_client.add_attacks(attacks)
        
        # Verify
        count = chroma_client.get_count()
        print(f"✓ Successfully loaded {count} attacks into ChromaDB")
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

