import pytest

from stepproof.models import SimulatedModel
from stepproof.problems import Problem, generate
from stepproof.stats import bootstrap_ci, paired_bootstrap
from stepproof.verifier import verify


def evaluate_problem(expr, answer, steps=()):
    return Problem("t", "test", "test", "evaluate", "", expr, answer, list(steps))


def solve_problem(eq, answer, steps=()):
    return Problem("t", "test", "test", "solve", "", eq, answer, list(steps))


def test_benchmark_size_and_reference_solutions_verify():
    problems = generate()
    assert len(problems) >= 500
    for p in problems[::13]:
        v = verify(p, p.reference_steps, p.answer)
        assert v.final_correct and v.process_correct, p.id


def test_arithmetic_slip_is_located():
    p = evaluate_problem("(1/2 + 1/3)*6", "5")
    v = verify(p, ["(5/6)*6", "6"], "6")
    assert not v.final_correct
    assert v.first_error_step == 1
    assert v.first_error_type == "arithmetic_slip"


def test_misapplied_rule_product_rule():
    p = evaluate_problem("Derivative(x**2*sin(x), x)", "2*x*sin(x) + x**2*cos(x)")
    v = verify(p, ["2*x*cos(x)"], "2*x*cos(x)")
    assert v.first_error_step == 0
    assert v.first_error_type == "misapplied_rule"


def test_invalid_algebra_sign_error():
    p = evaluate_problem("(x + 2)**2 - (x - 3)**2", "10*x - 5")
    v = verify(p, ["(x**2 + 4*x + 4) - (x**2 - 6*x + 9)", "-2*x - 5"], "-2*x - 5")
    assert v.first_error_step == 1
    assert v.first_error_type == "invalid_algebra"


def test_error_propagation_is_not_double_counted():
    p = evaluate_problem("2 + 3*4", "14")
    v = verify(p, ["2 + 13", "15"], "15")
    assert [s.status for s in v.steps] == ["error", "propagated"]


def test_solve_lost_root_is_invalid_algebra():
    p = solve_problem("x**2 - 5*x + 6 = 0", "2, 3")
    v = verify(p, ["x - 2 = 0"], "2")
    assert v.first_error_type == "invalid_algebra"
    assert not v.final_correct


def test_solve_constant_error_is_arithmetic():
    p = solve_problem("3*x + 4 = 19", "5")
    v = verify(p, ["3*x = 16", "x = 16/3"], "16/3")
    assert v.first_error_step == 0
    assert v.first_error_type == "arithmetic_slip"


def test_unjustified_leap_and_lucky_guess():
    p = solve_problem("3*x + 4 = 19", "5")
    v = verify(p, ["3*x = 16"], "5")    # wrong step, then asserts the right answer anyway
    assert v.final_correct and not v.process_correct and v.lucky_guess
    assert any(s.error_type == "unjustified_leap" for s in v.steps)


def test_unparseable_step():
    p = evaluate_problem("2 + 2", "4")
    v = verify(p, ["two plus two is four"], "4")
    assert v.first_error_type == "parse_error"


def test_simulated_model_injects_detectable_errors():
    problems = generate(per_template=5)
    model = SimulatedModel("probe", {"arithmetic_slip": 1.0})
    for p in problems:
        sol = model.solve(p)
        if sol.injected:
            v = verify(p, sol.steps, sol.final_answer)
            assert v.first_error_step == sol.injected["step"], p.id


def test_bootstrap_ci_contains_mean():
    mean, lo, hi = bootstrap_ci([1, 0, 1, 1, 0, 1, 1, 1])
    assert lo <= mean <= hi


def test_paired_bootstrap_detects_clear_difference():
    a = [1] * 90 + [0] * 10
    b = [1] * 50 + [0] * 50
    res = paired_bootstrap(a, b)
    assert res["diff"] == pytest.approx(0.4)
    assert res["significant"]
