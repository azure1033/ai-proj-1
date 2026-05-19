"""
安全计算器 Tool — 基于 AST 的数学表达式求值
"""

import ast
import math
import operator

from langchain.tools import BaseTool

# 安全函数白名单
_SAFE_FUNCTIONS: dict = {
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

# 安全运算符白名单
_SAFE_OPS: dict = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _safe_eval_ast(node: ast.AST) -> float:
    """递归求值 AST 节点，仅允许白名单操作"""
    if isinstance(node, ast.Constant):
        return float(node.value)

    if isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type not in _SAFE_OPS:
            raise ValueError(f"不允许的运算符: {op_type.__name__}")
        left = _safe_eval_ast(node.left)
        right = _safe_eval_ast(node.right)
        return _SAFE_OPS[op_type](left, right)

    if isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type not in _SAFE_OPS:
            raise ValueError(f"不允许的一元运算符: {op_type.__name__}")
        operand = _safe_eval_ast(node.operand)
        return _SAFE_OPS[op_type](operand)

    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise ValueError("不支持嵌套函数调用")
        func_name = node.func.id
        if func_name not in _SAFE_FUNCTIONS:
            raise ValueError(f"不允许的函数: {func_name}")
        if len(node.args) != 1:
            raise ValueError(f"函数 {func_name} 仅支持单参数")
        arg = _safe_eval_ast(node.args[0])
        return _SAFE_FUNCTIONS[func_name](arg)

    if isinstance(node, ast.Name):
        name = node.id
        if name not in _SAFE_FUNCTIONS:
            raise ValueError(f"未知标识符: {name}")
        return _SAFE_FUNCTIONS[name]

    raise ValueError(f"不支持的表达式类型: {type(node).__name__}")


class CalculatorTool(BaseTool):
    """执行数学计算"""

    name: str = "calculator"
    description: str = (
        "执行数学计算。输入数学表达式，如 '2+3*4'、'sqrt(16)'、'sin(0.5)'。"
        "支持基本运算符（+ - * / **）和常用数学函数（sqrt, sin, cos, abs, pow 等）。"
    )

    def _run(self, expression: str) -> str:
        expression = expression.strip()
        if not expression:
            return "请输入数学表达式"
        try:
            tree = ast.parse(expression, mode="eval")
            result = _safe_eval_ast(tree.body)
            # 防止极端情况（极大值/极小值）
            if abs(result) > 1e308:
                return "计算结果溢出"
            # 整数去尾
            if isinstance(result, float) and result == int(result) and not math.isinf(result):
                result = int(result)
            return str(result)
        except SyntaxError:
            return "计算错误: 表达式语法无效"
        except (ValueError, ZeroDivisionError) as e:
            return f"计算错误: {e}"
        except Exception as e:
            return f"计算错误: {str(e)}"

    async def _arun(self, expression: str) -> str:
        return self._run(expression)
