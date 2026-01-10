# Hybrid RNA Structure Prediction Approach

## Overview

Combining the sophisticated secondary structure prediction and template matching from the new code with the corrected energy minimization and conservative noise from our fixed approach.

## Key Components

### 1. **Nussinov Secondary Structure Prediction**
- Uses dynamic programming to predict base pairing
- More accurate than simple heuristic pairing
- O(n³) complexity but still fast enough

### 2. **Template-Based Modeling**
- Searches training data for similar sequences (>40% identity)
- Uses actual structure as starting point
- Significantly better for homologous sequences

### 3. **Multiple Strategy Ensemble**
- Strategy 1: SS-guided (2 models)
- Strategy 2: Template-based (1 model if match found)
- Strategy 3: Extended random walk (2 models)

### 4. **Conservative Energy Minimization**
- Apply to all strategies
- 50 iterations with backbone + base pairing constraints
- Small noise [0, 0.5, 1, 1.5, 2]Å

## Integration Plan

### For `main.ipynb` (Kaggle Submission)

**Challenge**: Need to keep it self-contained and fast (<15 minutes)

**Solution**: Simplified hybrid
1. Use Nussinov for secondary structure (fast: O(n³) ≈ 0.1s for 100nt)
2. Skip template matching (requires training data access)
3. Build SS-guided structure
4. Apply energy minimization with base pairing constraints
5. Generate 5 conformations with small noise

### For `src/` System (Local Development)

**Advantage**: Can use full training dataset and more compute

**Solution**: Full hybrid
1. Nussinov secondary structure
2. Template matching from train_labels.csv
3. Multiple strategies
4. Energy minimization
5. Ensemble selection based on diversity

## Expected Performance

### Current Corrected Approach
- Score: ~0.12-0.15
- Fast: ~5-10 minutes
- No training data needed

### Hybrid Approach (Kaggle)
- Score: ~0.15-0.18 (10-20% better)
- Fast: ~10-15 minutes
- Uses SS prediction

### Full Hybrid (Local)
- Score: ~0.18-0.22 (20-50% better)
- Slower: ~30-60 minutes
- Uses training data templates

## Complexity Trade-offs

| Feature | Time Cost | Score Gain | Worth It? |
|---------|-----------|------------|-----------|
| Nussinov SS | +0.1s/seq | +0.02-0.03 | ✅ YES |
| Template match | +5s/seq | +0.03-0.05 | ⚠️ Maybe (if >40% match) |
| Energy min 50 iter | +0.5s/seq | +0.01-0.02 | ✅ YES |
| Multiple strategies | +10s/seq | +0.02-0.04 | ⚠️ Depends on time limit |

## Recommendation

### For Immediate Submission (Today)
Use **simplified hybrid in main.ipynb**:
- Add Nussinov
- Keep corrected energy minimization
- Skip template matching (no training data)
- Stay under 15 min runtime

### For Best Score (This Week)
Create **full hybrid notebook**:
- Add Nussinov
- Add template matching with training data
- Multiple strategies
- May take 30-60 min (acceptable if allowed)

## Code Structure

```python
# 1. Predict secondary structure
pairs = nussinov_fold(sequence)

# 2. Check for template (if training data available)
if has_training_data:
    template = find_best_template(sequence, train_seqs)
    if template_similarity > 0.4:
        coords_base = build_from_template(template)
    else:
        coords_base = build_ss_guided(sequence, pairs)
else:
    coords_base = build_ss_guided(sequence, pairs)

# 3. Energy minimize with constraints
coords_base = energy_minimize(coords_base, pairs, 50)

# 4. Generate ensemble with small noise
for conf_num in range(1, 6):
    noise_scale = NOISE_SCALES[conf_num - 1]  # [0, 0.5, 1, 1.5, 2]
    coords_conf = coords_base + np.random.normal(0, noise_scale, coords_base.shape)
    coords_conf = energy_minimize(coords_conf, pairs, 10)  # Quick refinement
    ensemble.append(coords_conf)
```

## Files to Create

1. **main_hybrid.ipynb** - Simplified hybrid for Kaggle (fast)
2. **main_full_hybrid.ipynb** - Full hybrid with training data (best score)
3. **src/structure/nussinov.py** - Secondary structure prediction
4. **src/structure/templates.py** - Template matching
5. **test_hybrid.py** - Local testing script

## Next Steps

1. **Test locally**: Validate Nussinov + energy min gives better scores
2. **Profile runtime**: Ensure stays under 15 minutes on Kaggle
3. **Ablation study**: Test each component's contribution
4. **Submit**: Try simplified hybrid first, then full if time allows
