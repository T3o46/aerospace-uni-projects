# Aerospace Engineering University Projects

A collection of university coursework projects spanning 3D aircraft structural CAD modeling, Finite Element Method (FEM) structural analysis and composite redesign, and Python numerical optimisation algorithms.

## Projects

| Folder | Course / Domain | Tools & Stack | Summary |
| :--- | :--- | :--- | :--- |
| [`01-wing-box-cad/`](./01-wing-box-cad/) | Aircraft Structural CAD | SolidWorks (`.SLDASM`, `.SLDPRT`) | 3D CAD assembly of an aircraft wing box section including upper/lower aerodynamic skins, front/rear spars, root rib, and L-bracket joint. |
| [`02-aerospace-structures-fem/`](./02-aerospace-structures-fem/) | Aerospace Structures and Elements (ASE) | Altair HyperMesh, OptiStruct, Tcl, Excel | 3-part FEM structural analysis, metallic sizing, and CFRP composite laminate redesign of a stiffened aircraft wing superpanel. |
| [`03-numerical-optimisation-algorithms/`](./03-numerical-optimisation-algorithms/) | Aerospace Structural Optimisation (ASO) | Python, NumPy, pytest, `uv` | From-scratch Python implementations of Steepest Descent, Strong Wolfe line search, KKT convergence checks, and Powell-damped BFGS constrained SQP. |

## Repository Structure

```text
aerospace-uni-projects/
├── 01-wing-box-cad/
│   ├── Assem1.SLDASM
│   ├── LBracket.SLDPRT
│   ├── RootRib.SLDPRT
│   ├── Shell_Lower.SLDPRT
│   ├── Shell_Upper.SLDPRT
│   ├── SparBack.SLDPRT
│   ├── SparFront.SLDPRT
│   └── README.md
├── 02-aerospace-structures-fem/
│   ├── part1-metallic-baseline/
│   ├── part2-metallic-sizing/
│   ├── part3-composite-redesign/
│   └── README.md
├── 03-numerical-optimisation-algorithms/
│   ├── scripts/
│   ├── src/aso/
│   ├── tests/
│   ├── pyproject.toml
│   ├── uv.lock
│   └── README.md
├── .gitignore
└── README.md
```
