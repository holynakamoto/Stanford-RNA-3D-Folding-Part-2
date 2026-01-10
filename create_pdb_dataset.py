#!/usr/bin/env python3
"""
Create PDB RNA structures dataset for template-based modeling
Downloads representative RNA structures from PDB for Kaggle
"""

import os
import gzip
import requests
from pathlib import Path
from Bio import PDB
from Bio.PDB import PDBIO
import pandas as pd
from tqdm import tqdm

DATASET_DIR = "pdb_rna_dataset"
PDB_DIR = f"{DATASET_DIR}/structures"
Path(PDB_DIR).mkdir(parents=True, exist_ok=True)

# Representative RNA structures (high quality, diverse)
# Add more PDB IDs as needed
RNA_PDB_IDS = [
    # Transfer RNAs
    "1EHZ", "6TNA", "1I9V",
    # Ribosomal RNAs
    "4V9F", "4V9D", "4YBB",
    # Riboswitches
    "2GDI", "3FU2", "4L81",
    # Ribozymes
    "1Y26", "2OIU", "3R1C",
    # Other functional RNAs
    "1AJU", "2F88", "3DIL",
]

def download_pdb_structure(pdb_id):
    """Download PDB structure from RCSB"""
    url = f"https://files.rcsb.org/download/{pdb_id}.pdb.gz"
    output_path = f"{PDB_DIR}/{pdb_id}.pdb"
    
    if os.path.exists(output_path):
        print(f"  {pdb_id} already exists")
        return True
    
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            # Decompress
            content = gzip.decompress(response.content).decode('utf-8')
            
            with open(output_path, 'w') as f:
                f.write(content)
            
            print(f"  ✓ Downloaded {pdb_id}")
            return True
        else:
            print(f"  ✗ Failed to download {pdb_id}: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ✗ Error downloading {pdb_id}: {e}")
        return False

def extract_rna_chains(pdb_file):
    """Extract RNA chains and their sequences"""
    parser = PDB.PDBParser(QUIET=True)
    structure = parser.get_structure('RNA', pdb_file)
    
    rna_chains = []
    for model in structure:
        for chain in model:
            # Check if chain contains RNA residues
            residues = list(chain.get_residues())
            if not residues:
                continue
            
            # Check for RNA nucleotides
            rna_residues = ['A', 'C', 'G', 'U', 'DA', 'DC', 'DG', 'DT']
            is_rna = any(res.get_resname().strip() in rna_residues 
                        for res in residues)
            
            if is_rna:
                sequence = ''
                for res in residues:
                    resname = res.get_resname().strip()
                    # Map to standard bases
                    base_map = {
                        'A': 'A', 'C': 'C', 'G': 'G', 'U': 'U',
                        'DA': 'A', 'DC': 'C', 'DG': 'G', 'DT': 'U'
                    }
                    sequence += base_map.get(resname, 'N')
                
                if sequence:
                    rna_chains.append({
                        'pdb_id': os.path.basename(pdb_file).replace('.pdb', ''),
                        'chain_id': chain.id,
                        'sequence': sequence,
                        'length': len(sequence)
                    })
    
    return rna_chains

def main():
    print("=== Creating PDB RNA Structures Dataset ===\n")
    
    # 1. Download structures
    print("Downloading PDB structures...")
    for pdb_id in tqdm(RNA_PDB_IDS):
        download_pdb_structure(pdb_id)
    
    # 2. Extract RNA chains and sequences
    print("\nExtracting RNA chains...")
    all_chains = []
    for pdb_file in Path(PDB_DIR).glob("*.pdb"):
        chains = extract_rna_chains(str(pdb_file))
        all_chains.extend(chains)
    
    # 3. Create index file
    df = pd.DataFrame(all_chains)
    df.to_csv(f"{DATASET_DIR}/rna_sequences.csv", index=False)
    print(f"\nExtracted {len(all_chains)} RNA chains")
    print(f"Total sequences: {len(df)}")
    print(f"Length range: {df['length'].min()}-{df['length'].max()} nt")
    
    # 4. Create FASTA file for MMseqs2
    print("\nCreating FASTA file...")
    with open(f"{DATASET_DIR}/rna_sequences.fasta", 'w') as f:
        for _, row in df.iterrows():
            f.write(f">{row['pdb_id']}_{row['chain_id']}\n")
            f.write(f"{row['sequence']}\n")
    
    # 5. Create metadata
    with open(f"{DATASET_DIR}/dataset-metadata.json", 'w') as f:
        f.write('''{
  "title": "PDB RNA Structures Database",
  "id": "yourusername/pdb-rna-structures",
  "licenses": [{"name": "CC0-1.0"}],
  "resources": [
    {
      "path": "structures/",
      "description": "PDB structure files for RNA templates"
    },
    {
      "path": "rna_sequences.csv",
      "description": "Index of RNA chains and sequences"
    }
  ]
}''')
    
    # 6. Create README
    with open(f"{DATASET_DIR}/README.md", 'w') as f:
        f.write(f'''# PDB RNA Structures Database

Representative RNA structures from Protein Data Bank for template-based modeling.

## Contents
- `structures/`: {len(RNA_PDB_IDS)} PDB files
- `rna_sequences.csv`: Index of {len(all_chains)} RNA chains
- `rna_sequences.fasta`: Sequences in FASTA format

## Statistics
- Total structures: {len(RNA_PDB_IDS)}
- Total RNA chains: {len(all_chains)}
- Length range: {df['length'].min()}-{df['length'].max()} nucleotides

## Usage

```python
import pandas as pd
from Bio import PDB

# Load index
index = pd.read_csv('/kaggle/input/pdb-rna-structures/rna_sequences.csv')

# Find template by similarity
target_seq = "GGCGUAGUCC"
# ... implement sequence search ...

# Load structure
parser = PDB.PDBParser()
structure = parser.get_structure(
    'template',
    '/kaggle/input/pdb-rna-structures/structures/1EHZ.pdb'
)
```

## License
CC0 1.0 Universal (Public Domain)
''')
    
    print(f"\n=== Dataset Complete ===")
    print(f"Location: {os.path.abspath(DATASET_DIR)}")
    print(f"\nNext steps:")
    print(f"1. Upload to Kaggle: https://www.kaggle.com/datasets")
    print(f"2. Add to your competition notebook")
    print(f"3. Use with MMseqs2 for template search")

if __name__ == "__main__":
    # Check dependencies
    try:
        import Bio
        import requests
        import tqdm
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Install with: pip install biopython requests tqdm")
        exit(1)
    
    main()
