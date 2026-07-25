from raito.utils.helpers.code_evaluator import CodeEvaluator, EvaluationData


async def test_returns_last_expression():
    result = await CodeEvaluator().evaluate("1 + 1", {})
    assert isinstance(result, EvaluationData)
    assert result.result == "2"
    assert result.error is None


async def test_captures_stdout():
    result = await CodeEvaluator().evaluate("print('hello')\n2 + 3", {})
    assert result.stdout == "hello\n"
    assert result.result == "5"


async def test_uses_provided_context():
    result = await CodeEvaluator().evaluate("x * 2", {"x": 21})
    assert result.result == "42"


async def test_supports_await():
    code = "import asyncio\nawait asyncio.sleep(0)\n99"
    result = await CodeEvaluator().evaluate(code, {})
    assert result.result == "99"
    assert result.error is None


async def test_error_is_captured_in_error_field():
    result = await CodeEvaluator().evaluate("1 / 0", {})
    assert result.result is None
    assert result.error is not None
    assert "ZeroDivisionError" in result.error


async def test_statement_only_code_has_no_result():
    result = await CodeEvaluator().evaluate("y = 5", {})
    assert result.result is None
    assert result.error is None


async def test_empty_code_returns_no_result():
    result = await CodeEvaluator().evaluate("", {})
    assert result.result is None
    assert result.error is None
