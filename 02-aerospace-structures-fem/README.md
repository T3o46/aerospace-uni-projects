# Aerospace Structures and Elements (ASE) — FEM Superpanel Analysis & Redesign

A three-part Finite Element Method (FEM) structural analysis, sizing, and composite redesign project for the **Aerospace Structures and Elements (ASE)** course, built in **Altair HyperMesh** and solved with **Altair OptiStruct**.

## Structural Model Overview

The model represents a stiffened aircraft wing superpanel consisting of:
- **10 skin panels** (`CQUAD4` shell elements)
- **9 stringers** (`CBAR` beam elements) combining **T-section** and **Omega/HAT-section** profiles
- **2 spar caps** (`CROD` elements)
- **Load introduction** via an `RBE3` rigid body element and `SPC` boundary conditions

---

## Project Parts

### Part 1 — Metallic Baseline Analysis (`part1-metallic-baseline/`)
- **Material**: Aluminum alloy (`MAT1`, $E_{\text{avg}} = 71{,}531.88\text{ MPa}$, $E_{\text{B-basis}} = 65{,}210.67\text{ MPa}$, $\nu = 0.34$, $\sigma_y = 490\text{ MPa}$, $\sigma_u = 530\text{ MPa}$).
- **Baseline Geometry**: Uniform $4.0\text{ mm}$ skin (`PSHELL`), T-stringers ($70 \times 40\text{ mm}$, flange $3.0\text{ mm}$, web $2.0\text{ mm}$), and HAT/Omega stringers ($h = 29\text{ mm}$, $t = 2.5\text{ mm}$).
- **Analyses Performed** (Load Cases `LC1` and `LC3`):
  - **Strength analysis**: Element-level von Mises / strength reserve factors (`RFstrength`).
  - **Panel buckling**: Combined biaxial compression and shear buckling (`RF_panelbuckl`, `k_biax`, `k_shear`).
  - **Column buckling**: Combined skin-stringer column buckling (`RF_columnbuckl_comb`, crippling stress $\sigma_{\text{crip}}$, slenderness $\lambda$).
- **Key Finding**: Baseline skin + stringer mass is **16.89 kg**, but stability checks reveal buckling deficits (`RF < 1.0` in panel and column buckling), motivating structural sizing in Part 2.

### Part 2 — Metallic Structural Sizing (`part2-metallic-sizing/`)
- **Objective**: Iteratively resize the metallic superpanel (`ASE_TEST2`–`ASE_TEST7`) under load cases `LC1` and `LC2` to satisfy all strength and buckling reserve-factor requirements within the **19.52 kg** skin + stringer mass budget.
- **Design Updates**: Adjusted skin panel thicknesses (e.g., increasing panel 1 to $4.9\text{ mm}$) and stringer cross-section dimensions (e.g., T-stringer web height $40\text{ mm} \rightarrow 48\text{ mm}$, HAT/Omega height $29\text{ mm} \rightarrow 32\text{ mm}$).

### Part 3 — CFRP Composite Laminate Redesign (`part3-composite-redesign/`)
- **Material**: Replaced aluminum with **M21/IMA** carbon-fiber reinforced polymer (`MAT8`, $E_{11} = 129{,}036\text{ MPa}$, $E_{22} = 9{,}903.6\text{ MPa}$, $G_{12} = 6{,}484.32\text{ MPa}$, $\nu_{12} = 0.32$, $\rho = 1.58 \times 10^{-9}\text{ t/mm}^3$).
- **Composite Layup & Stiffeners**:
  - Symmetric 16-ply `[45₂/-45₂/0₂/90₂]s` `PCOMP` skin laminate ($0.4\text{ mm/ply}$, $6.4\text{ mm}$ total thickness).
  - Homogenized composite T-section ($70 \times 44 \times 4.0 \times 4.0\text{ mm}$) and Omega/HAT-section ($30 \times 4.0 \times 30 \times 10\text{ mm}$) stringers.
- **Analyses Performed** (Load Cases `LC1` and `LC2`):
  - **Classical Laminate Theory (CLT)**: Computed the **ABD stiffness matrix** of the T-stringer flange laminate.
  - **Ply-by-Ply Strength (Puck Failure)**: Evaluated fiber failure (`RF_FF`) and inter-fiber failure (`RF_IFF`, modes A/B/C) across all layers.
  - **Composite Panel Buckling**: Minimum `RF_panelbuckl = 1.145` (LC2, panel 9).
  - **Composite Column Buckling**: Minimum `RF_columnbuckl_comb = 1.239` (LC1, column 2).
- **Result**: Achieved a fully feasible design with a skin + stringer mass of **15.74 kg** — a **6.8% weight reduction** compared to the unfeasible metallic baseline, with all reserve factors $> 1.0$.

---

## File Types

- `.fem` — Altair OptiStruct solver input decks
- `.hm` — Altair HyperMesh model databases
- `.tcl` — HyperMesh automation macro (`command1.tcl`)
- `.csv` / `.xlsx` — Extracted stress/strain exports, analytical post-processing workbooks, and submission reserve-factor sheets
- `.h3d` / `.op2` / `.pch` / `.mvw` / `.out` / `.stat` — OptiStruct binary/ASCII result and HyperView session files
