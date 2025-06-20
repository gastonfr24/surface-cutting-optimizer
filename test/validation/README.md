# 🔬 Industry Validation Suite

This directory contains **industry validation scripts** that compare algorithm performance against real-world manufacturing solutions.

## 📁 Contents

- `test_supervised_validation.py` - Supervised validation against industry benchmarks

## 🎯 Purpose

**Validation ≠ Testing**

| Testing (`test/`) | Validation (`validation/`) |
|-------------------|----------------------------|
| ✅ Unit tests | 🔬 Industry benchmarks |
| ✅ Interface testing | 🏭 Real-world data comparison |
| ✅ Edge cases | 📊 Performance validation |
| ✅ Fast execution | ⏱️ Comprehensive analysis |
| ✅ Code correctness | 💼 Business value |

## 🚀 Usage

```bash
# Run validation suite
python validation/test_supervised_validation.py

# Or with unittest
python -m unittest validation.test_supervised_validation
```

## 📊 What It Validates

1. **Furniture Industry** - Wood cutting optimization
2. **Glass Manufacturing** - Sheet glass cutting
3. **Metal Fabrication** - Steel sheet optimization  
4. **Textile Industry** - Fabric pattern cutting

## ⚠️ Note

These are **validation scripts**, not unit tests. They:
- Take longer to run
- Compare against industry solutions
- Generate detailed reports
- Should be run separately from unit tests 