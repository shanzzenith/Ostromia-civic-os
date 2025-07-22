# 🏛️ Ostromia — Civic Operating System Prototype

*A civic-tech experiment in token-driven localism:*  
essay ▸ bonding-curve math ▸ cadCAD simulation ▸ commons-centric governance

🌱 **A city that provides for everybody, because it is created by everybody.**

---

## 📖 Read the article
> **“Ostromia – Building a Civic Operating System in Times of Disruption”**  
> https://www.shanzz.xyz/ostromia-building-a-civic-operating-system-in-times-of-disruption/

## 🔬 Explore the code
| Path | What’s inside |
|------|---------------|
| `/simulation/Ostromia-civic-os-V1.ipynb` | Original 7-day minimal model |
| `/simulation/Ostromia_sim.ipynb` | **NEW**: decay, gold tier & param-sweep |
| `/library/bonding_curve.py` | Re-usable curve math (`price = a·supply + b`) |

---

## ✨ Project highlights
* **Commons as infrastructure** — programmable, adaptive, regenerative  
* **City Points** — participatory currency that turns *care* into *capital*  
* **Token engineering** — bonding curves + cadCAD stress tests  

### New in `v1.1`
| Feature | Implemented |
|---------|-------------|
| Bonding curve mint (A·supply + B) | ✅ |
| **5-day half-life decay** | ✅ |
| **Gold tier bonus (+20 %)** | ✅ |
| **Parameter sweep** (base 10 vs 20) | ✅ |

---

## 🚀 Quick-start

### ▶️ Colab (zero setup)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/YOUR_USERNAME/ostromia-civic-os/blob/main/simulation/Ostromia_sim.ipynb)

### 🖥️ Local
```bash
git clone https://github.com/YOUR_USERNAME/ostromia-civic-os.git
cd ostromia-civic-os
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt          # cadCAD, pandas, matplotlib
python simulation/ostromia_sim.py        # or open the notebook
