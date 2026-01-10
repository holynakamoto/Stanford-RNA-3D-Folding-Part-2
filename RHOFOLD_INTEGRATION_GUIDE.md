# RhoFold Integration Guide - Complete Implementation

## 🎯 **Goal: Achieve 0.35-0.40 TM-Score**

Timeline: 1-2 weeks
Current baseline: 0.15-0.18
Expected improvement: 2-2.5x

---

## 📅 **Week 1: Dataset Preparation & Setup**

### **Day 1-2: Create and Upload Datasets**

#### **Step 1: RhoFold Model Dataset**

```bash
# Run locally
chmod +x create_rhofold_dataset.sh
./create_rhofold_dataset.sh

# Manual steps:
# 1. Download RhoFold weights from GitHub releases
#    Place in: rhofold_kaggle_dataset/RhoFold/pretrained/model.pt
# 2. Upload to Kaggle:
#    https://www.kaggle.com/datasets -> New Dataset
# 3. Name: "rhofold-rna-prediction"
```

#### **Step 2: PDB Structures Dataset**

```bash
# Run locally (requires internet)
python3 create_pdb_dataset.py

# This downloads ~20 representative RNA structures
# Upload to Kaggle: "pdb-rna-structures"
```

#### **Step 3: Offline Python Wheels**

```bash
# Download wheels locally
mkdir python_wheels
cd python_wheels

# Get PyTorch for Linux (Kaggle uses Ubuntu)
pip download torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Get other dependencies
pip download biopython einops fair-esm ml-collections pandas numpy scipy

# Upload to Kaggle: "offline-python-wheels"
```

#### **Step 4: MMseqs2 Binary**

```bash
# Download precompiled binary
wget https://github.com/soedinglab/MMseqs2/releases/download/14-7e284/mmseqs-linux-avx2.tar.gz
tar xvf mmseqs-linux-avx2.tar.gz

# Create dataset with structure:
# mmseqs2_dataset/
# ├── mmseqs2/
# │   └── bin/mmseqs
# └── README.md

# Upload to Kaggle: "mmseqs2-binary"
```

### **Day 3-4: Verify Datasets in Kaggle**

Create test notebook to verify all datasets load:

```python
# Test notebook
import sys
import os

# 1. Check RhoFold
sys.path.append('/kaggle/input/rhofold-rna-prediction/RhoFold')
try:
    import rhofold
    print("✓ RhoFold loaded")
except:
    print("✗ RhoFold failed")

# 2. Check PDB structures
pdb_path = '/kaggle/input/pdb-rna-structures/structures'
num_structures = len(os.listdir(pdb_path))
print(f"✓ Found {num_structures} PDB structures")

# 3. Check wheels
wheels_path = '/kaggle/input/offline-python-wheels'
print(f"✓ Found {len(os.listdir(wheels_path))} wheel files")

# 4. Check MMseqs2
mmseqs_bin = '/kaggle/input/mmseqs2-binary/mmseqs2/bin/mmseqs'
if os.path.exists(mmseqs_bin):
    print("✓ MMseqs2 binary found")
else:
    print("✗ MMseqs2 not found")
```

---

## 📅 **Week 2: Implementation & Testing**

### **Day 5-7: Core Implementation**

Replace prediction cell in `main.ipynb` with RhoFold-based system.

#### **Complete Integration Code**

```python
"""
RHOFOLD + TEMPLATE-BASED RNA STRUCTURE PREDICTION
==================================================
Expected score: 0.35-0.40 (competitive)

Strategy:
1. Short RNAs (<200nt): RhoFold de novo
2. Long RNAs (>200nt): Template search -> RhoFold if no match
3. Ensemble: 5 predictions with variation
"""

import sys
import os
import numpy as np
import pandas as pd
from pathlib import Path
import subprocess
import tempfile
import shutil

# ============================================================================
# SETUP
# ============================================================================

# Install dependencies offline
print("Installing dependencies...")
wheels_path = '/kaggle/input/offline-python-wheels'
subprocess.run([
    sys.executable, '-m', 'pip', 'install', 
    '--no-index', '--find-links', wheels_path,
    'torch', 'biopython', 'einops', 'fair-esm', 'ml-collections'
], check=False, capture_output=True)

# Add RhoFold to path
sys.path.insert(0, '/kaggle/input/rhofold-rna-prediction/RhoFold')

try:
    from rhofold.model.rna_fm import RNA_FM
    from rhofold.model.rhofold import RhoFold
    from rhofold.utils.utils import load_config
    import torch
    from Bio import PDB
    from Bio.PDB import PDBIO
    RHOFOLD_AVAILABLE = True
    print("✓ RhoFold loaded successfully")
except Exception as e:
    print(f"⚠ RhoFold not available: {e}")
    print("  Falling back to physics-based model")
    RHOFOLD_AVAILABLE = False

# ============================================================================
# CONFIGURATION
# ============================================================================

# Paths
RHOFOLD_MODEL = '/kaggle/input/rhofold-rna-prediction/RhoFold/pretrained/model.pt'
PDB_DB_PATH = '/kaggle/input/pdb-rna-structures'
MMSEQS_BIN = '/kaggle/input/mmseqs2-binary/mmseqs2/bin/mmseqs'
WORK_DIR = '/kaggle/working/predictions'
Path(WORK_DIR).mkdir(exist_ok=True)

# Strategy thresholds
SHORT_RNA_THRESHOLD = 200  # Use RhoFold for <200nt
TEMPLATE_IDENTITY_THRESHOLD = 0.30  # Min identity for templates
ENSEMBLE_SIZE = 5

# Device
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"Using device: {DEVICE}")

# ============================================================================
# TEMPLATE SEARCH
# ============================================================================

def create_mmseqs_database():
    """Create MMseqs2 database from PDB sequences (one-time setup)"""
    db_path = f"{WORK_DIR}/pdb_rna_db"
    if os.path.exists(f"{db_path}.dbtype"):
        return db_path
    
    print("Creating MMseqs2 database...")
    fasta_path = f"{PDB_DB_PATH}/rna_sequences.fasta"
    
    cmd = [
        MMSEQS_BIN, 'createdb',
        fasta_path,
        db_path
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return db_path

def find_template(sequence, target_id, db_path):
    """
    Search for template structure using MMseqs2.
    Returns (template_id, identity, alignment) or None.
    """
    # Write query
    query_fasta = f"{WORK_DIR}/{target_id}_query.fasta"
    with open(query_fasta, 'w') as f:
        f.write(f">{target_id}\n{sequence}\n")
    
    # Create query database
    query_db = f"{WORK_DIR}/{target_id}_query"
    subprocess.run([
        MMSEQS_BIN, 'createdb',
        query_fasta, query_db
    ], check=True, capture_output=True)
    
    # Search
    result_db = f"{WORK_DIR}/{target_id}_result"
    tmp_dir = f"{WORK_DIR}/tmp_{target_id}"
    Path(tmp_dir).mkdir(exist_ok=True)
    
    subprocess.run([
        MMSEQS_BIN, 'search',
        query_db, db_path, result_db, tmp_dir,
        '--min-seq-id', str(TEMPLATE_IDENTITY_THRESHOLD),
        '-s', '7.5',  # Sensitivity
        '--max-seqs', '1'  # Top hit only
    ], check=True, capture_output=True)
    
    # Convert to TSV
    result_tsv = f"{WORK_DIR}/{target_id}_result.tsv"
    subprocess.run([
        MMSEQS_BIN, 'convertalis',
        query_db, db_path, result_db, result_tsv,
        '--format-output', 'query,target,pident,alnlen,qstart,qend,tstart,tend'
    ], check=True, capture_output=True)
    
    # Parse results
    try:
        results = pd.read_csv(result_tsv, sep='\t', header=None,
                             names=['query', 'target', 'pident', 'alnlen',
                                   'qstart', 'qend', 'tstart', 'tend'])
        if len(results) > 0:
            top_hit = results.iloc[0]
            template_id = top_hit['target']
            identity = top_hit['pident'] / 100.0
            
            # Cleanup
            shutil.rmtree(tmp_dir, ignore_errors=True)
            
            return template_id, identity, top_hit
    except:
        pass
    
    # Cleanup
    shutil.rmtree(tmp_dir, ignore_errors=True)
    return None

def load_template_coords(template_id):
    """Load C1' coordinates from template PDB"""
    pdb_id = template_id.split('_')[0]
    chain_id = template_id.split('_')[1] if '_' in template_id else 'A'
    
    pdb_file = f"{PDB_DB_PATH}/structures/{pdb_id}.pdb"
    if not os.path.exists(pdb_file):
        return None
    
    parser = PDB.PDBParser(QUIET=True)
    structure = parser.get_structure('template', pdb_file)
    
    coords = []
    for model in structure:
        for chain in model:
            if chain.id != chain_id:
                continue
            for residue in chain:
                if "C1'" in residue:
                    atom = residue["C1'"]
                    coords.append(atom.get_coord())
    
    return np.array(coords) if coords else None

# ============================================================================
# RHOFOLD INFERENCE
# ============================================================================

class RhoFoldPredictor:
    """Wrapper for RhoFold inference"""
    
    def __init__(self, model_path, device='cuda'):
        self.device = device
        print(f"Loading RhoFold model from {model_path}...")
        
        # Load config
        config_path = os.path.join(os.path.dirname(model_path), 'config.yaml')
        if not os.path.exists(config_path):
            # Use default config
            config = self.get_default_config()
        else:
            config = load_config(config_path)
        
        # Load model
        self.model = RhoFold(config).to(device)
        checkpoint = torch.load(model_path, map_location=device)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.model.eval()
        
        print("✓ RhoFold model loaded")
    
    def get_default_config(self):
        """Default config if file not available"""
        from ml_collections import ConfigDict
        config = ConfigDict()
        config.model = ConfigDict()
        config.model.hidden_dim = 384
        config.model.num_layers = 12
        config.model.num_heads = 12
        return config
    
    @torch.no_grad()
    def predict(self, sequence, num_recycles=3, temperature=1.0):
        """
        Predict structure for RNA sequence.
        
        Args:
            sequence: RNA sequence string
            num_recycles: Number of recycling iterations
            temperature: Sampling temperature (higher = more diversity)
        
        Returns:
            coords: (L, 3) numpy array of C1' coordinates
        """
        # Tokenize sequence
        tokens = self.tokenize_sequence(sequence)
        tokens = torch.tensor(tokens).unsqueeze(0).to(self.device)
        
        # Run inference
        outputs = self.model(
            tokens,
            num_recycles=num_recycles,
            temperature=temperature
        )
        
        # Extract coordinates
        coords = outputs['structure'].cpu().numpy()[0]  # (L, 3)
        
        return coords
    
    def tokenize_sequence(self, sequence):
        """Convert sequence to tokens"""
        token_map = {'A': 0, 'C': 1, 'G': 2, 'U': 3}
        return [token_map.get(base, 3) for base in sequence]
    
    def predict_ensemble(self, sequence, num_predictions=5):
        """Generate ensemble of predictions with variation"""
        ensemble = []
        
        # Base prediction
        base_coords = self.predict(sequence, temperature=1.0)
        ensemble.append(base_coords)
        
        # Variations
        temperatures = [0.8, 1.2, 1.4, 1.6]
        for i, temp in enumerate(temperatures[:num_predictions-1]):
            coords = self.predict(sequence, temperature=temp)
            ensemble.append(coords)
        
        return ensemble

# ============================================================================
# FALLBACK: PHYSICS-BASED PREDICTION
# ============================================================================

# [Include your current Nussinov-based predictor here as fallback]
# This runs if RhoFold fails or isn't available

# ============================================================================
# MAIN PREDICTION PIPELINE
# ============================================================================

def predict_rna_structure_rhofold(sequence, target_id, predictor, db_path):
    """
    Main prediction pipeline combining RhoFold and templates.
    
    Strategy:
    1. Short RNAs (<200nt): Use RhoFold
    2. Long RNAs (>200nt): Try template first, then RhoFold
    3. Generate ensemble of 5 predictions
    
    Returns:
        list of (L, 3) coordinate arrays
    """
    seq_len = len(sequence)
    
    # Strategy selection
    if seq_len < SHORT_RNA_THRESHOLD:
        # Short RNA: RhoFold is best
        print(f"  Using RhoFold (length={seq_len})")
        ensemble = predictor.predict_ensemble(sequence, ENSEMBLE_SIZE)
        
    else:
        # Long RNA: Try template first
        print(f"  Searching templates (length={seq_len})...")
        template_result = find_template(sequence, target_id, db_path)
        
        if template_result:
            template_id, identity, alignment = template_result
            print(f"    Found template: {template_id} ({identity:.1%} identity)")
            
            if identity >= TEMPLATE_IDENTITY_THRESHOLD:
                # Use template as base
                template_coords = load_template_coords(template_id)
                
                if template_coords is not None and len(template_coords) > 0:
                    # Generate variations around template
                    ensemble = []
                    base = template_coords
                    
                    # Pad/trim to match sequence length
                    if len(base) < seq_len:
                        # Pad with RhoFold prediction for missing regions
                        rhofold_coords = predictor.predict(sequence)
                        combined = rhofold_coords.copy()
                        combined[:len(base)] = base
                        ensemble.append(combined)
                    elif len(base) > seq_len:
                        # Trim
                        ensemble.append(base[:seq_len])
                    else:
                        ensemble.append(base)
                    
                    # Add variations
                    for i in range(ENSEMBLE_SIZE - 1):
                        noise = np.random.normal(0, 0.5 + i*0.3, base.shape)
                        coords_var = base + noise
                        ensemble.append(coords_var[:seq_len])
                    
                    return ensemble
        
        # Fallback to RhoFold if no template or template failed
        print("    No template found, using RhoFold")
        ensemble = predictor.predict_ensemble(sequence, ENSEMBLE_SIZE)
    
    return ensemble

# ============================================================================
# INFERENCE LOOP
# ============================================================================

if RHOFOLD_AVAILABLE:
    print("\n" + "="*70)
    print("RHOFOLD-BASED PREDICTION SYSTEM")
    print("="*70)
    
    # Initialize
    predictor = RhoFoldPredictor(RHOFOLD_MODEL, DEVICE)
    db_path = create_mmseqs_database()
    
    # Generate predictions
    all_predictions = []
    
    for idx, row in test_sequences.iterrows():
        target_id = row['target_id']
        sequence = row['sequence']
        
        print(f"\n[{idx+1}/{len(test_sequences)}] {target_id} ({len(sequence)}nt)")
        
        try:
            # Get ensemble predictions
            ensemble = predict_rna_structure_rhofold(
                sequence, target_id, predictor, db_path
            )
            
            # Format for submission
            for j, base in enumerate(sequence):
                pred_row = {
                    'ID': f"{target_id}_{j+1}",
                    'resname': base,
                    'resid': j + 1
                }
                
                for pred_num in range(min(5, len(ensemble))):
                    if j < len(ensemble[pred_num]):
                        pred_row[f'x_{pred_num+1}'] = float(ensemble[pred_num][j][0])
                        pred_row[f'y_{pred_num+1}'] = float(ensemble[pred_num][j][1])
                        pred_row[f'z_{pred_num+1}'] = float(ensemble[pred_num][j][2])
                    else:
                        # Fallback to zeros if prediction shorter
                        pred_row[f'x_{pred_num+1}'] = 0.0
                        pred_row[f'y_{pred_num+1}'] = 0.0
                        pred_row[f'z_{pred_num+1}'] = 0.0
                
                all_predictions.append(pred_row)
            
            print(f"  ✓ Generated {len(ensemble)} predictions")
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            print(f"    Falling back to physics-based model")
            
            # [Call your fallback Nussinov predictor here]
    
    # Create submission
    submission_df = pd.DataFrame(all_predictions)
    submission_df.to_csv('submission.csv', index=False)
    
    print("\n" + "="*70)
    print(f"✓ Predictions complete: {len(submission_df)} rows")
    print("="*70)
    
else:
    print("RhoFold not available, using fallback predictor")
    # [Use your current Nussinov-based system]
```

### **Day 8-9: Local Testing**

Test on validation set before Kaggle submission:

```python
# Test on 2-3 validation targets locally
validation_subset = validation_seqs.head(3)

for _, row in validation_subset.iterrows():
    ensemble = predict_rna_structure_rhofold(
        row['sequence'], 
        row['target_id'],
        predictor,
        db_path
    )
    
    # Calculate TM-score against ground truth
    # [Use provided metric from competition]
```

### **Day 10: Runtime Optimization**

```python
# Optimizations for 8-hour limit:

# 1. Batch short RNAs together
short_rnas = [row for _, row in test_sequences.iterrows() 
              if len(row['sequence']) < 100]

# Process in batches
batch_predictions = predictor.predict_batch(
    [r['sequence'] for r in short_rnas],
    batch_size=16
)

# 2. Early stopping for long RNAs
if seq_len > 500:
    # Use faster template search only
    # Or chunk into domains

# 3. Cache template database
# Don't recreate MMseqs DB each time

# 4. Reduce ensemble for very long RNAs
if seq_len > 700:
    ensemble_size = 3  # Instead of 5
```

---

## 📊 **Expected Results**

| Component | Score Contribution | Notes |
|-----------|-------------------|-------|
| **RhoFold (short RNAs)** | 0.25-0.30 | Best for <200nt |
| **Templates (long RNAs)** | +0.05-0.10 | If >30% identity |
| **Ensemble diversity** | +0.02-0.03 | 5 varied predictions |
| **Total Expected** | **0.35-0.40** | 2-2.5x baseline |

---

## 🚨 **Common Issues & Solutions**

### **Issue: RhoFold Model Not Loading**
```python
# Solution: Verify checkpoint format
checkpoint = torch.load(RHOFOLD_MODEL, map_location='cpu')
print(checkpoint.keys())  # Should have 'model_state_dict'

# If different format, adapt loading code
```

### **Issue: Out of Memory on GPU**
```python
# Solution: Reduce batch size or use CPU
DEVICE = 'cpu'  # Slower but works
# Or process shorter sequences on GPU, longer on CPU
```

### **Issue: MMseqs2 Timeout**
```python
# Solution: Reduce sensitivity or pre-filter
# Use smaller PDB database (only high-quality structures)
# Or skip template search for very long RNAs
```

### **Issue: Exceeding 8-hour Runtime**
```python
# Solution: Profile and optimize
import time

start = time.time()
# ... prediction ...
elapsed = time.time() - start
print(f"Time per RNA: {elapsed:.1f}s")

# If >30s per RNA, optimize:
# - Reduce num_recycles in RhoFold
# - Skip template search for short RNAs
# - Use CPU for some targets
```

---

## 📚 **Additional Resources**

- **RhoFold Paper**: https://www.biorxiv.org/content/10.1101/2022.05.20.492757v1
- **RhoFold GitHub**: https://github.com/ml4bio/RhoFold
- **MMseqs2 User Guide**: https://github.com/soedinglab/MMseqs2/wiki
- **Competition Discussion**: Kaggle forums for latest tips

---

## ✅ **Validation Checklist**

Before final submission:

- [ ] All datasets added to Kaggle notebook
- [ ] RhoFold model loads successfully
- [ ] Template search works on sample sequence
- [ ] Predictions generated for all test sequences
- [ ] Output format matches sample_submission.csv
- [ ] Runtime < 8 hours on Kaggle
- [ ] Validation score > 0.30 locally
- [ ] Fallback works if RhoFold fails

---

## 🎯 **Success Criteria**

- **Week 1 End**: All datasets uploaded and verified
- **Week 2 Mid**: Local validation score > 0.30
- **Week 2 End**: Kaggle submission scoring 0.35-0.40

---

## 🚀 **Next Steps**

1. **Day 1-2**: Run dataset creation scripts
2. **Day 3**: Upload datasets to Kaggle
3. **Day 4**: Verify with test notebook
4. **Day 5-7**: Implement integration code
5. **Day 8-9**: Test locally on validation set
6. **Day 10**: Optimize and submit to Kaggle

Let me know when you complete each phase and I'll help troubleshoot!
