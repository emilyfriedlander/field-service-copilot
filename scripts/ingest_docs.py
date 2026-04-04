"""
Ingest HVAC educational documents into ChromaDB.

Usage:
    python3 scripts/ingest_docs.py                    # ingest data/hvac_education/
    python3 scripts/ingest_docs.py --reset            # wipe and re-ingest
    python3 scripts/ingest_docs.py --dir path/to/docs # custom directory

To add real-world sources, drop .md or converted PDF files into
data/hvac_education/ and re-run this script.

Recommended real sources to add:
    - EPA 608 study guide PDFs (esco.org, reftechhvac.com) → convert with pdfplumber
    - Carrier/Trane/Lennox service bulletins (from manufacturer portals) → save as .md
    - NATE study materials (northamerica-tech-excellence.com)
    - HVAC School tech tips (hvacrschool.com/tech-tips) → fetch with requests + BeautifulSoup
    - ACCA Manual J/S/D summaries (acca.org)
"""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from retriever import ingest_directory

DEFAULT_DIR = Path(__file__).parent.parent / "data" / "hvac_education"


def main():
    parser = argparse.ArgumentParser(description="Ingest HVAC education docs into ChromaDB")
    parser.add_argument("--dir",   type=Path, default=DEFAULT_DIR)
    parser.add_argument("--reset", action="store_true", help="Wipe existing collection and re-ingest")
    args = parser.parse_args()

    print(f"Ingesting documents from: {args.dir}")
    if args.reset:
        print("  --reset: existing collection will be wiped")

    count = ingest_directory(args.dir, reset=args.reset)
    print(f"Done. {count} new chunks added to ChromaDB.")


if __name__ == "__main__":
    main()
