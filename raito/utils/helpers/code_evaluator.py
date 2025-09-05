from __future__ import annotations

import ast
import sys
import traceback
from collections.abc import Awaitable, Callable, Generator
from contextlib import contextmanager, redirect_stdout
from dataclasses import dataclass
from io import StringIO
from typing import Any


@dataclass
class EvaluationData:
    stdout: str | None = None
    result: str | None = None
    error: str | None = None


class CodeEvaluator:
    @contextmanager
    def _capture_output(self) -> Generator[StringIO, Any, None]:
        old_stdout = sys.stdout
        buf = StringIO()
        try:
            with redirect_stdout(buf):
                yield buf
        finally:
            sys.stdout = old_stdout

    def _wrap_code(self, code: str) -> ast.Module:
        module = ast.parse(code, mode="exec")
        body = module.body or [ast.Pass()]

        if isinstance(body[-1], ast.Expr):
            body[-1] = ast.Return(value=body[-1].value)

        func_def = ast.AsyncFunctionDef(
            name="__eval_func",
            args=ast.arguments(
                posonlyargs=[],
                args=[],
                defaults=[],
                kwonlyargs=[],
                kw_defaults=[],
            ),
            body=body,
        )

        wrapped_module = ast.Module(body=[func_def])
        ast.fix_missing_locations(wrapped_module)
        return wrapped_module

    async def evaluate(self, code: str, context: dict[str, Any]) -> EvaluationData:
        try:
            wrapped_module = self._wrap_code(code)
            compiled_code = compile(wrapped_module, "<raito_eval>", "exec")

            exec_locals: dict[str, Any] = {}
            with self._capture_output() as output:
                exec(compiled_code, context, exec_locals)
                eval_func: Callable[[], Awaitable[Any]] = exec_locals["__eval_func"]
                result = await eval_func()

            return EvaluationData(
                stdout=output.getvalue(),
                result=str(result) if result is not None else None,
            )
        except Exception:  # noqa: BLE001
            return EvaluationData(error=traceback.format_exc())
