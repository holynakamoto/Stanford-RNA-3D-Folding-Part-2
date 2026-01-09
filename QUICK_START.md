# Quick Start Guide - RNA Structure Prediction with Diversity Diagnostics

## 🎯 TL;DR - 3 Commands You Need

```bash
# 1. Test diversity (2 seconds)
python3 test_diversity.py

# 2. Diagnose your data (5 minutes)
python3 run_inference_and_build_submission.py --diagnose

# 3. Generate submission (full run)
python3 run_inference_and_build_submission.py
```

## ✅ Current Status

**All systems operational!** Your model now generates diverse conformations:
- 28-30Å average pairwise RMSD ✅
- 1.6-1.8x expected RMSD scales ✅
- No centering artifacts ✅
- Fast local validation ✅

## 📊 Expected Output

When you run diagnostics, you should see:

```
Diversity diagnostics for target_id (5 conformations)
  conf 0 → RMSD to base = 0.000 Å
  conf 1 → RMSD to base = 8.837 Å     ← Target: ~5Å
  conf 2 → RMSD to base = 18.015 Å    ← Target: ~10Å
  conf 3 → RMSD to base = 27.783 Å    ← Target: ~15Å
  conf 4 → RMSD to base = 34.359 Å    ← Target: ~20Å
  Average pairwise RMSD = 29.106 Å    ← Should be > 10Å
```

**This is GOOD!** Ratios slightly > 1.0 mean strong diversity.

## 🚨 When to Worry

❌ Average pairwise RMSD < 5Å → Conformations too similar  
❌ RMSD ratios < 0.3 → Noise suppressed by centering/refinement  
❌ All conformations identical → Check config.noise_scales

## ⚙️ Configuration

Current settings (in `src/config.py`):
- `noise_scales = [0.0, 5.0, 10.0, 15.0, 20.0]` ✅
- `max_refinement_steps = 0` ✅
- Centering disabled by default ✅

## 🎓 Iteration Workflow

1. **Test locally** → `python3 test_diversity.py` (2s)
2. **Tweak config** → Edit `src/config.py` if needed
3. **Validate** → `python3 run_inference_and_build_submission.py --diagnose` (5min)
4. **Submit** → Upload `submission.csv` to Kaggle
5. **Monitor score** → Diversity should improve performance

## 📖 Full Documentation

See `DIAGNOSTICS_README.md` for:
- Detailed usage instructions
- Troubleshooting guide
- Alternative configurations
- Advanced features (Kabsch alignment, etc.)

## 💡 Pro Tips

- Run `test_diversity.py` after any config changes
- Use `--diagnose` before generating full submission
- Don't re-enable centering unless necessary
- Keep `max_refinement_steps = 0` for best diversity
- Average pairwise RMSD of 15-30Å is ideal

## 🎉 You're Ready!

All 7 action items completed. Your pipeline now:
- Generates diverse conformations ✅
- Validates locally in seconds ✅
- No more Kaggle waiting ✅

**Go forth and submit!** 🚀
