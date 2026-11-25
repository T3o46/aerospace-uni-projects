# Aerospace Structural Optimisation (ASO) — Numerical Optimisation Algorithms

A Python package (`aso`) implementing gradient-based numerical optimisation algorithms from scratch using NumPy for the **Aerospace Structural Optimisation (ASO)** course.

## Architecture

- [`src/aso/optimiser.py`](./src/aso/optimiser.py) — `Optimiser` class containing convergence checks, line search, Steepest Descent, and constrained SQP.
- [`src/aso/optimisation_problem.py`](./src/aso/optimisation_problem.py) — `OptimisationProblem` wrapper supporting analytic or central finite-difference gradients, inequality/equality constraints, box bounds, and Lagrangian evaluation.
- [`src/aso/problem_factory.py`](./src/aso/problem_factory.py) — `ProblemFactory` suite of benchmark test problems (Rosenbrock, Sphere, Booth, Matyas, Himmelblau, Easom, McCormick, Rastrigin, Ackley, and constrained variants).
- [`src/aso/optimisation_result.py`](./src/aso/optimisation_result.py) — Result container for optimisation callbacks.
- [`tests/test_optimiser.py`](./tests/test_optimiser.py) — Pytest benchmark suite for each project milestone.

## Implemented Algorithms

1. **Rosenbrock Objective & Analytic Gradient** (`ProblemFactory.rosenbrock`)
   Implemented the 2D Rosenbrock function and its exact analytic gradient.
2. **First-Order KKT Convergence Criterion** (`Optimiser.converged`)
   Checks Lagrangian gradient stationarity ($\|\nabla_x \mathcal{L}\|_\infty \le \text{tol}$), primal feasibility for inequality ($g \le \text{tol}$) and equality ($|h| \le \text{tol}$) constraints, dual feasibility ($\lambda_i \ge -\text{tol}$), and complementary slackness ($|\lambda_i g_i| \le \text{tol}$).
3. **Strong Wolfe Line Search** (`Optimiser.line_search`)
   Bracketing/bisection line search on the Lagrangian merit function enforcing the sufficient decrease condition ($m_1 = 0.01$) and the strong curvature condition ($m_2 = 0.90$).
4. **Steepest Descent** (`Optimiser.steepest_descent`)
   Unconstrained gradient descent using Strong Wolfe line search and in-place design-variable updates.
5. **Constrained Sequential Quadratic Programming (SQP)** (`Optimiser.sqp_constrained`)
   Active-set KKT linear system solver with:
   - **Powell-damped BFGS** Hessian approximation update to maintain positive definiteness,
   - **Strong Wolfe line search** along the SQP step direction,
   - **Box-constraint projection** (`np.clip`) and **gradient masking** at active variable bounds.

> **Note**: Template stubs for `mma` (Project 3), `conjugate_gradients`, and `sqp_unconstrained` are present in `Optimiser` and not yet implemented.

## Benchmark Results

Verified with `pytest` (**14/14 tests passing** across `project_1` and `project_2`):

- **Project 1 (`STEEPEST_DESCENT`)**: Converges on all 7 unconstrained benchmarks (Rosenbrock, Sphere, Booth, Matyas, Himmelblau, Easom, McCormick) within the 100,000-iteration limit (e.g., 11,663 iterations on Rosenbrock; 1–32 iterations on the remaining functions).
- **Project 2 (`SQP`)**: Converges on all 7 constrained benchmarks in **1–17 iterations** (e.g., 8 iterations on constrained Rosenbrock).

## Setup & Running Tests

Using [`uv`](https://docs.astral.sh/uv/):

```bash
uv venv
uv sync
```

Run the implemented test suites:

```bash
# Project 1: Unconstrained Steepest Descent
uv run pytest -m project_1

# Project 2: Constrained SQP
uv run pytest -m project_2
```
