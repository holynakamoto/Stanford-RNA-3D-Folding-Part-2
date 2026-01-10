# Dataset Upload Guide for Kaggle

## ✅ **Datasets Ready to Upload**

You now have **2 of 4** datasets prepared locally and ready for upload!

---

## 📦 **Dataset 1: RhoFold Model (Ready to Upload)**

**Location**: `/Users/nickmoore/kagglecomp/rhofold_kaggle_dataset/`
**Size**: 582MB
**Contents**:
- ✅ RhoFold repository (Python package)
- ✅ Pretrained model weights (497MB)
- ✅ Inference scripts
- ✅ Metadata and documentation

### **Upload Steps**:

1. **Go to Kaggle Datasets**: https://www.kaggle.com/datasets

2. **Click "New Dataset"**

3. **Upload the folder**:
   - Drag and drop: `rhofold_kaggle_dataset/`
   - Or click "Upload" and select the folder

4. **Set metadata**:
   - **Title**: `RhoFold RNA Structure Prediction`
   - **Subtitle**: `Pretrained deep learning model for RNA 3D folding`
   - **Description**: Copy from `rhofold_kaggle_dataset/README.md`

5. **Settings**:
   - **Visibility**: Public (so you can use it in competition)
   - **License**: Apache 2.0

6. **Click "Create"**

7. **Copy the dataset path** (will look like):
   - `yourusername/rhofold-rna-prediction`

---

## 📦 **Dataset 2: PDB RNA Structures (Ready to Upload)**

**Location**: `/Users/nickmoore/kagglecomp/pdb_rna_dataset/`
**Size**: 5.3MB
**Contents**:
- ✅ 12 PDB structure files
- ✅ 79 RNA chains extracted
- ✅ Sequences (11-1005 nucleotides)
- ✅ CSV index and FASTA format

### **Upload Steps**:

Same as above, but with:
- **Folder**: `pdb_rna_dataset/`
- **Title**: `PDB RNA Structures Database`
- **Subtitle**: `Representative RNA structures for template-based modeling`
- **Dataset path**: `yourusername/pdb-rna-structures`

---

## 📦 **Dataset 3: PyTorch Offline Wheels (Need to Get)**

**Size**: ~2GB
**Options**:

### **Option A: Use Existing Kaggle Dataset (Recommended)**

Search on Kaggle for:
- "pytorch wheels offline"
- "wheels for all"
- "pytorch cpu linux"

Popular datasets:
- `masoudmzb/wheels-for-all`
- `pytorch/pytorch`
- Various user-uploaded wheel collections

**What you need**:
- `torch` (CPU version for Linux)
- `torchvision`
- `biopython`
- `einops`
- `fair-esm` (optional, for better embeddings)
- `ml-collections`

### **Option B: Create Your Own**

```bash
# On a Linux machine or Docker container
mkdir pytorch_wheels
cd pytorch_wheels

# Download PyTorch CPU (smaller, works on Kaggle)
pip download torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Download other dependencies
pip download biopython einops fair-esm ml-collections pandas numpy scipy

# Upload to Kaggle as "pytorch-offline-wheels"
```

### **Option C: Skip for Now (Use Fallback Model)**

If PyTorch installation is problematic, the integration code will automatically fall back to your current Nussinov-based predictor.

---

## 📦 **Dataset 4: MMseqs2 Binary (Need to Get)**

**Size**: ~100MB
**Options**:

### **Option A: Use Existing Kaggle Dataset (Recommended)**

Search on Kaggle for:
- "mmseqs2 binary"
- "mmseqs2 linux"

### **Option B: Download and Upload**

```bash
# Download precompiled binary
cd /Users/nickmoore/kagglecomp
mkdir mmseqs2_dataset
cd mmseqs2_dataset

wget https://github.com/soedinglab/MMseqs2/releases/download/14-7e284/mmseqs-linux-avx2.tar.gz
tar xvf mmseqs-linux-avx2.tar.gz

# Create metadata
cat > dataset-metadata.json <<EOF
{
  "title": "MMseqs2 Sequence Search",
  "id": "yourusername/mmseqs2-binary",
  "licenses": [{"name": "GPL-3.0"}]
}
EOF

# Upload to Kaggle as "mmseqs2-binary"
```

### **Option C: Skip Template Search**

If MMseqs2 is too complex, you can modify the integration code to use only RhoFold (no template search). This will still give good results for short RNAs.

---

## 🎯 **Upload Priority**

| Priority | Dataset | Status | Impact | Effort |
|----------|---------|--------|--------|--------|
| **1. HIGH** | RhoFold Model | ✅ Ready | Very High | 5 min upload |
| **2. MEDIUM** | PyTorch Wheels | ⏳ Find/Create | High | 10 min (find) or 1 hour (create) |
| **3. MEDIUM** | PDB Structures | ✅ Ready | Medium | 2 min upload |
| **4. LOW** | MMseqs2 Binary | ⏳ Find/Create | Medium | 5 min (find) or 15 min (create) |

---

## ⚡ **Quick Start: Upload Now**

### **Step 1: Upload RhoFold (5 minutes)**

1. Go to: https://www.kaggle.com/datasets
2. Click "New Dataset"
3. Upload: `rhofold_kaggle_dataset/`
4. Title: "RhoFold RNA Structure Prediction"
5. Public, Apache 2.0
6. Create

### **Step 2: Upload PDB Structures (2 minutes)**

1. Click "New Dataset" again
2. Upload: `pdb_rna_dataset/`
3. Title: "PDB RNA Structures Database"
4. Public, CC0 1.0
5. Create

### **Step 3: Find PyTorch Wheels (10 minutes)**

1. Search Kaggle: "wheels for all"
2. Add to your notebook later

### **Step 4: Find MMseqs2 (5 minutes)**

1. Search Kaggle: "mmseqs2 binary"
2. Or skip for initial testing

---

## 📝 **After Upload: Update Your Notebook**

Once datasets are uploaded, you'll add them to your competition notebook:

```python
# In Kaggle notebook: Add Data -> Search for your datasets
# They'll be available at:
/kaggle/input/rhofold-rna-prediction/
/kaggle/input/pdb-rna-structures/
/kaggle/input/wheels-for-all/  # or whatever you name it
/kaggle/input/mmseqs2-binary/
```

Then follow the integration code in `RHOFOLD_INTEGRATION_GUIDE.md`.

---

## 🎉 **Current Progress**

```
✅ RhoFold model prepared (582MB)
✅ PDB structures prepared (5.3MB)
⏳ PyTorch wheels (find existing dataset)
⏳ MMseqs2 binary (find existing dataset)
⏳ Upload to Kaggle
⏳ Add to competition notebook
⏳ Run integration code
⏳ Submit and score!
```

**You're ~40% done with dataset prep!**

---

## 💡 **Pro Tips**

1. **Start with RhoFold + PDB**: Upload these two first. They're the most important.

2. **Use existing wheel datasets**: Searching Kaggle is faster than creating your own.

3. **Test incrementally**: Upload datasets one at a time, test each in a notebook.

4. **Make datasets public**: Required to use them in competitions.

5. **Note dataset paths**: You'll need these exact paths in your integration code.

---

## 🚀 **Next Steps**

**Right now**:
1. Upload `rhofold_kaggle_dataset/` to Kaggle
2. Upload `pdb_rna_dataset/` to Kaggle
3. Search for existing PyTorch wheels dataset
4. Search for existing MMseqs2 dataset

**After uploads complete**:
1. Create test notebook to verify datasets load
2. Follow integration guide: `RHOFOLD_INTEGRATION_GUIDE.md`
3. Test on validation set
4. Submit to competition

---

## ❓ **Troubleshooting**

### **Upload fails (file too large)**
- Check internet connection
- Try smaller batches
- Compress large files

### **Can't find PyTorch wheels**
- Search: "pytorch cpu linux wheels"
- Use torch installation guide for Kaggle
- Or use pip install in notebook (slower)

### **Dataset not showing in notebook**
- Make sure it's public
- Refresh the "Add Data" search
- Check dataset name/spelling

---

## ✅ **Success Checklist**

- [ ] Uploaded RhoFold dataset to Kaggle
- [ ] Uploaded PDB structures dataset to Kaggle
- [ ] Found or uploaded PyTorch wheels dataset
- [ ] Found or uploaded MMseqs2 dataset
- [ ] Tested datasets load in notebook
- [ ] Ready to integrate into competition notebook

---

**Ready to upload? Start with RhoFold!** 🚀
