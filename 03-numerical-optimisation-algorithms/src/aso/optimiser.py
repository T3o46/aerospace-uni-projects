"""
optimiser
=========

Defines the Optimiser class.
"""

import logging
from time import perf_counter as timer
from typing import Any, Callable, Literal

import numpy as np
from numpy.typing import NDArray

from aso.logging import format_array_for_logging
from aso.optimisation_problem import OptimisationProblem
from aso.optimisation_result import OptimisationResult

logger = logging.getLogger(__name__)


class Optimiser:
    """
    Contains various optimisation algorithms to solve an `OptimisationProblem`.

    Attributes
    ----------
    problem : OptimisationProblem
        The optimisation problem to be solved.
    x : np.ndarray
        Current design variable values.
    n : int
        Number of design variables.
    lm : np.ndarray
        Current Lagrange multipliers.
    """

    def __init__(
        self,
        problem: OptimisationProblem,
        x: NDArray,
        lm: NDArray | None = None,
    ) -> None:
        """Initialize an `Optimiser` instance.

        Parameters
        ----------
        problem : OptimisationProblem
            Optimisation problem to solve.
        x : np.ndarray
            Initial design variables.
        lm : np.ndarray, optional
            Initial Lagrange multipliers.

        Notes
        -----
        The given array of design variables will be modified in place.
        Hence, the optimiser does currently not reuturn the optimised
        design variables but only the number of outer-loop iterations.
        This behavior may change in future versions.
        """
        self.problem = problem
        self.x = x
        self.n = x.size

        # Check and, if necessary, initialise the Lagrange multipliers:
        if lm is None:
            self.lm = np.zeros(problem.m + problem.me)
        elif lm.size != problem.m + problem.me:
            raise ValueError(
                "The number of Lagrange multipliers must match the number of constraints."
            )
        else:
            self.lm = lm

    def optimise(
        self,
        algorithm: Literal[
            "SQP",
            "MMA",
            "STEEPEST_DESCENT",
            "CONJUGATE_GRADIENTS",
        ] = "SQP",
        iteration_limit: int = 1000,
        callback: Callable[[OptimisationResult], None] | None = None,
    ) -> int:
        """
        Distinguish constrained and unconstrained optimization problems
        and call an appropriate optimisation function.

        Parameters
        ----------
        algorithm : str, default: "SQP"
            Algorithm to use.
        iteration_limit : int, default: 1000
            Maximum number of outer-loop iterations.
        callback : callable, optional
            Callback function to collect (intermediate) optimization results.

        Returns
        -------
        iteration : int
            Number of performed iterations, -1 if `iteration >
            iteration_limit`.

        Raises
        ------
        ValueError
            If `algorithm` is unknown or not suitable for constrained
            optimisation.
        """

        start = timer()

        if self.problem.constrained:
            match algorithm:
                case "SQP":
                    iteration = self.sqp_constrained(
                        iteration_limit=iteration_limit,
                        callback=callback,
                    )
                case "MMA":
                    iteration = self.mma()
                case _:
                    raise ValueError(
                        "Algorithm unknown or not suitable for constrained optimisation."
                    )
        else:
            match algorithm:
                case "STEEPEST_DESCENT":
                    iteration = self.steepest_descent(
                        iteration_limit=iteration_limit,
                    )
                case "CONJUGATE_GRADIENTS":
                    iteration = self.conjugate_gradients(
                        iteration_limit=iteration_limit,
                    )
                case "SQP":
                    iteration = self.sqp_unconstrained(
                        iteration_limit=iteration_limit,
                        callback=callback,
                    )
                case _:
                    raise ValueError(
                        "Algorithm unknown or not suitable for unconstrained optimisation."
                    )

        end = timer()
        elapsed_ms = round((end - start) * 1000, 3)

        if iteration == -1:
            logger.info(
                f"Algorithm {algorithm} failed to converge in {elapsed_ms} ms after {iteration} "
                f"iterations. Consider using another algorithm or increasing the iteration limit.",
            )
        else:
            logger.info(
                f"Algorithm {algorithm} converged in {elapsed_ms} ms after {iteration} "
                f"iterations. Optimised design variables: {format_array_for_logging(self.x)}",
            )

        return iteration

    def steepest_descent(
        self,
        iteration_limit: int = 1000,
    ) -> int:
        """Steepest-descent algorithm for unconstrained optimisation.

        Parameters
        ----------
        iteration_limit : int, default: 1000
            Maximum number of outer loop iterations.

        Returns
        -------
        int
            Number of performed iterations, -1 if `iteration >
            iteration_limit`.
        """
        iteration = 0
        while iteration < iteration_limit:
            if self.converged(self.problem.compute_grad_objective(self.x)):
                return iteration
            direction = -self.problem.compute_grad_objective(self.x)
            step_size = self.line_search(direction)
            self.x += step_size * direction
            iteration += 1
        return -1

    def conjugate_gradients(
        self,
        iteration_limit: int = 1000,
        beta_formula: Literal[
            "FLETCHER-REEVES",
            "POLAK-RIBIERE",
            "HESTENES-STIEFEL",
            "DAI-YUAN",
        ] = "FLETCHER-REEVES",
    ) -> int:
        """Conjugate-gradient algorithm for unconstrained optimisation.

        Parameters
        ----------
        iteration_limit : int, default: 1000
            Maximum number of outer-loop iterations.
        beta_formula : str, : optional
            Heuristic formula for computing the conjugation factor beta.

        Returns
        -------
        int
            Number of performed iterations, -1 if `iteration >
            iteration_limit`.
        """
        ...

    def sqp_unconstrained(
        self,
        iteration_limit: int = 1000,
        callback: Callable[[OptimisationResult], None] | None = None,
    ) -> int:
        """SQP algorithm for unconstrained optimisation.

        Parameters
        ----------
        iteration_limit : int, default: 1000
            Maximum number of outer-loop iterations.
        callback : str, optional
            Callback function to collect intermediate results.

        Returns
        -------
        int
            Number of performed iterations, -1 if `iteration >
            iteration_limit`.
        """
        ...

    def sqp_constrained(
        self,
        iteration_limit: int = 1000,
        working_set: list[int] | None = None,
        working_set_size: int | None = None,
        callback: Callable[[OptimisationResult], None] | None = None,
    ) -> int:
        """
        SQP algorithm with an active-set strategy for constrained
        optimisation.

        Parameters `m_w` and `working_set` are currently ignored.

        Parameters
        ----------
        iteration_limit : int, default: 1000
            Maximum number of outer-loop iterations.
        working_set : list of int, optional
            Initial working set.
        working_set_size : int, optional
            Size of the working set (ignored if `working_set` is provided).
        callback : callable, optional
            Callback function to collect intermediate results.

        Returns
        -------
        int
            Number of performed iterations, -1 if `iteration >
            iteration_limit`.

        Raises
        ------
        ValueError
            If the size of the working set is too large or too small.

        References
        ----------
        .. [1] K. Schittkowski, "An Active Set Strategy for Solving Optimization Problems with up to 200,000,000 Nonlinear Constraints." Accessed: May 25, 2025. [Online]. Available: https://klaus-schittkowski.de/SC_NLPQLB.pdf
        .. [2] J. Nocedal and S. J. Wright, Numerical Optimization. Springer New York, 2006. doi: https://doi.org/10.1007/978-0-387-40065-5.
        """
        iteration = 0
        n,m,me = self.n, self.problem.m, self.problem.me
        # Step 0: Initialise x^0
        V = np.eye(n)
        grad_f = self.problem.compute_grad_objective(self.x)
        c = self.problem.compute_constraints(self.x)
        A = self.problem.compute_grad_constraints(self.x)
        active = np.nonzero(c[:m] >= 0)[0].tolist() + list(range(m, m + me))

        while iteration < iteration_limit:

            # Step 2: Solve SQP at x^i
            if not active:
                p_x = np.linalg.solve(V, -grad_f)
                self.lm[:] = 0
            else:
                A_active = A[active, :]
                k = len(active)
                KKT_matrix = np.block([[V, A_active.T], [A_active, np.zeros((k, k))]])
                rhs = np.concatenate([-grad_f, -c[active]])
                solution = np.linalg.solve(KKT_matrix, rhs)
                p_x = solution[:n]
                self.lm[:] = 0
                self.lm[active] = solution[n:]

            # Step 3: Update iterate x^i+1   
            alpha = self.line_search(p_x)
            x_old = self.x.copy()
            self.x += alpha * p_x
            if self.problem.lb is not None and self.problem.ub is not None:
                np.clip(self.x, self.problem.lb, self.problem.ub, out=self.x)
            
            # Step 4: Compute new gradient and constraints for x^i+1
            grad_f_new = self.problem.compute_grad_objective(self.x)
            c = self.problem.compute_constraints(self.x)
            A_new = self.problem.compute_grad_constraints(self.x)

            # new lag 
            grad_l_new = grad_f_new + A_new.T @ self.lm
            if self.problem.lb is not None and self.problem.ub is not None:
                for i in range(self.x.size):
                    if self.x[i] <= self.problem.lb[i] and grad_l_new[i] > 0:
                        grad_l_new[i] = 0
                    if self.x[i] >= self.problem.ub[i] and grad_l_new[i] < 0:
                        grad_l_new[i] = 0

            if self.converged(grad_l_new, c):
                return iteration

            # Step 5: BFGS update p and y for x^i+1
            p = self.x - x_old
            if not np.allclose(p, 0):
                y = (grad_f_new + A_new.T @ self.lm) - (grad_f + A.T @ self.lm)
                Vp = V @ p
                q = p @ Vp
                c_curve = p @ y
                if c_curve < 0.2 * q:
                    theta = 0.8 * q / (q - c_curve)
                    y = theta * y + (1 - theta) * Vp
                V -= np.outer(Vp, Vp) / q - np.outer(y, y) / (p @ y)
            
            # Step 6: Update active set
            grad_f = grad_f_new
            A = A_new
            active = np.nonzero(c[:m] >= 0)[0].tolist() + list(range(m, m + me))
            x_old = self.x.copy()
            iteration += 1
        return -1

    def mma(
        self,
        iteration_limit: int = 1000,
        callback: Callable[[OptimisationResult], None] | None = None,
    ) -> int:
        """
        MMA algorithm for constrained optimisation.

        Parameters
        ----------
        iteration_limit : int, default: 1000
            Maximum number of outer-loop iterations.
        callback : callable, optional
            Callback function to collect intermediate results.
        """
        ...

    def converged(
        self,
        gradient: NDArray,
        constraints: NDArray | None = None,
        gradient_tol: float = 1e-5,
        constraint_tol: float = 1e-5,
        complementarity_tol: float = 1e-3,
    ) -> bool:
        """
        Check convergence according to the first-order necessary (KKT)
        conditions assuming LICQ.

        See, for example, Theorem 12.1 in [1]_.

        Parameters
        ----------
        gradient : np.ndarray
            Current gradient of the Lagrange function with respect to
            the design variables.
        constraints : np.ndarray, optional
            Current constraint values.
        gradient_tol : float, default: 1e-5
            Tolerance applied to each component of the gradient.
        constraint_tol : float, default: 1e-5
            Tolerance applied to each constraint.
        complementarity_tol : float, default: 1e-5
            Tolerance applied to each complementarity condition.

        References
        ----------
        .. [1] J. Nocedal and S. J. Wright, Numerical Optimization. Springer New York, 2006. doi: https://doi.org/10.1007/978-0-387-40065-5.
        """
        if np.max(np.abs(gradient)) > gradient_tol:
            return False
        if constraints is not None:
            m = self.problem.m
            g = constraints[:m]
            h = constraints[m:]
            lm_i = self.lm[:m]
            if np.any(g > constraint_tol):
                return False
            if np.any(np.abs(h) > constraint_tol):
                return False
            if np.any(lm_i < -complementarity_tol):
                return False
            if np.any(np.abs(lm_i * g) > complementarity_tol):
                return False
        return True

    def line_search(
        self,
        direction: NDArray,
        alpha_ini: float = 1,
        alpha_min: float = 1e-6,
        alpha_max: float = 1,
        algorithm: Literal[
            "WOLFE",
            "STRONG_WOLFE",
            "GOLDSTEIN-PRICE",
        ] = "STRONG_WOLFE",
        m1: float = 0.01,
        m2: float = 0.90,
        callback: Callable[[OptimisationResult], Any] | None = None,
        callback_iteration: int | None = None,
    ) -> float:
        """
        Perform a line search and returns an approximately optimal step size.

        Parameters
        ----------
        direction : np.ndarray
            Search direction.
        alpha_ini : float
            Initial step size.
        alpha_min : float, optional
            Minimum step size.
        alpha_max : float
            Maximum step size.
        algorithm : str, optional
            Line search algorithm to use.
        m1 : float, optional
            Parameter for the sufficient decrease condition.
        m2 : float, optional
            Parameter for the curvature condition.
        callback : callable, optional
            Callback function for collecting intermediate results.
        callback_iteration : int, optional
            Iteration number for the callback function.

        Returns
        -------
        float
            Approximately optimal step size.
        """
        phi_0 = self.problem.compute_lagrange_function(self.x, self.lm)
        phi_grad_0 = self.problem.compute_grad_lagrange_function(self.x, self.lm) @ direction
        alpha = alpha_ini
        while alpha_max - alpha_min > 1e-6:
            phi_x = self.problem.compute_lagrange_function(self.x + alpha * direction, self.lm)
            phi_grad_x = self.problem.compute_grad_lagrange_function(self.x + alpha * direction, self.lm) @ direction
            if phi_x <= phi_0 + m1 * alpha * phi_grad_0 and abs(phi_grad_x) <= m2 * abs(phi_grad_0):
                break
            elif phi_x > phi_0 + m1 * alpha * phi_grad_0:
                alpha_max = alpha
                alpha = (alpha_max + alpha_min)/2
            elif abs(phi_grad_x) > m2 * abs(phi_grad_0):
                if phi_grad_x < 0:
                    alpha_min = alpha
                    if alpha_max != float("inf"):
                        alpha = (alpha_max + alpha_min)/2
                    else:
                        alpha += alpha_ini
                else:
                    alpha_max = alpha
                    alpha = (alpha_max + alpha_min)/2
        return alpha