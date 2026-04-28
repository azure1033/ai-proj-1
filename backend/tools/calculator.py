"""
安全计算器 Tool
"""

import re
from langchain.tools import BaseTool


class CalculatorTool(BaseTool):
    """执行数学计算"""

    name: str = "calculator"
    description: str = (
        "执行数学计算。输入数学表达式，如 '2+3*4'、'sqrt(16)'、'sin(0.5)'。"
        "支持基本运算符（+ - * / **）和常用数学函数（sqrt, sin, cos, abs, pow 等）。"
    )

    # 白名单：只允许安全的数学表达式
    _ALLOWED_PATTERN = re.compile(r'^[\d\s+\-*/()**.,eE]+$|^[a-z_][a-z0-9_]*(\([\d\s+\-*/()**.,eE]*\))?$')

    @staticmethod
    def _safe_eval(expression: str) -> str:
        import math

        # 构建安全的命名空间
        safe_names = {
            "abs": abs,
            "round": round,
            "min": min,
            "max": max,
            "pow": pow,
            "sqrt": math.sqrt,
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "pi": math.pi,
            "e": math.e,
            "log": math.log,
            "log10": math.log10,
            "ceil": math.ceil,
            "floor": math.floor,
        }

        try:
            # 只允许安全的函数和操作
            result = eval(expression, {"__builtins__": {}}, safe_names)
            return str(result)
        except Exception as e:
            return f"计算错误: {str(e)}"

    def _run(self, expression: str) -> str:
        expression = expression.strip()
        if not expression:
            return "请输入数学表达式"
        return self._safe_eval(expression)

    async def _arun(self, expression: str) -> str:
        return self._run(expression)
