"""
文本处理 Tool - 总结、翻译、代码解释
"""

from langchain.tools import BaseTool

from model_config import get_openai_client, MODEL

client = get_openai_client()


class SummarizeTool(BaseTool):
    """总结文本内容"""

    name: str = "summarize_text"
    description: str = (
        "总结给定的文本内容，提取核心要点。输入需要总结的文本。"
    )

    def _run(self, text: str) -> str:
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": f"请总结以下内容：{text}"}],
                max_tokens=300,
            )
            return (response.choices[0].message.content or "").strip()
        except Exception as e:
            return f"总结失败: {str(e)}"

    async def _arun(self, text: str) -> str:
        return self._run(text)


class TranslateTool(BaseTool):
    """翻译文本"""

    name: str = "translate_text"
    description: str = (
        "将文本翻译成中文。输入需要翻译的外文文本。"
    )

    def _run(self, text: str) -> str:
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": f"请将以下文本翻译成中文：{text}"}],
                max_tokens=500,
            )
            return (response.choices[0].message.content or "").strip()
        except Exception as e:
            return f"翻译失败: {str(e)}"

    async def _arun(self, text: str) -> str:
        return self._run(text)


class ExplainCodeTool(BaseTool):
    """解释代码"""

    name: str = "explain_code"
    description: str = (
        "解释给定的代码片段，说明其功能和逻辑。输入代码文本。"
    )

    def _run(self, code: str) -> str:
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": f"请解释以下代码：{code}"}],
                max_tokens=500,
            )
            return (response.choices[0].message.content or "").strip()
        except Exception as e:
            return f"代码解释失败: {str(e)}"

    async def _arun(self, code: str) -> str:
        return self._run(code)
