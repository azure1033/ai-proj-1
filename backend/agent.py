"""
Agent 模式核心模块

提供:
- create_agent_executor(): 创建 Tool-Calling Agent
- run_agent(): 执行 Agent 并提取结果和步骤

兼容 LangChain 1.x create_agent API
"""

from langchain.agents import create_agent

from model_config import get_langchain_llm
from tools import get_all_tools

# Agent 配置
MAX_ITERATIONS = 5
MAX_EXECUTION_TIME = 30  # 秒

# Agent 系统提示词
AGENT_SYSTEM_PROMPT = """你是一个智能助手，可以使用工具来回答用户问题。

核心原则：根据用户问题的性质，自主决定是直接回答还是调用工具。

何时直接回答（不调用工具）：
- 你知道答案的常识问题（如 "什么是Python"、"1+1等于几"）
- 简单的文本翻译（如 "翻译hello world"）
- 代码解释（如 "解释这段代码"）
- 总结文本（如 "总结这段内容"）
- 任何不需要实时数据即可回答的问题

何时调用工具：
- get_weather: 用户问天气、温度、穿衣建议等
- web_search: 用户问最新信息、新闻、产品发布时间等超过你知识截止日期的问题
- calculator: 需要精确数学计算
- 其他工具按需使用

回答要求：
1. 简洁有用，不要重复工具已经返回的信息
2. 优先使用工具获取实时信息，而非依赖训练数据

如果工具返回的消息以 [服务提示:] 开头，说明该功能暂时不可用。
请勿直接向用户展示技术细节。你应该：
1. 用友好简洁的语言告知用户该功能暂不可用
2. 如果问题可以用你的训练知识回答，请基于已有知识提供帮助
3. 如果完全无法回答，礼貌地说明原因并提供替代建议
"""


def _create_agent_executor():
    """创建 Agent (LangChain 1.x create_agent API)

    返回 CompiledStateGraph，通过 invoke/stream 调用
    """
    llm = get_langchain_llm()
    tools = get_all_tools()

    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=AGENT_SYSTEM_PROMPT,
    )

    return agent


def run_agent(query: str) -> dict:
    """执行 Agent 并返回结果

    Args:
        query: 用户查询

    Returns:
        dict: {
            "response": str,   # 最终回答
            "steps": [         # Agent 中间步骤
                {
                    "thought": str,
                    "tool": str,
                    "tool_input": str,
                    "observation": str,
                }
            ]
        }
    """
    agent = _create_agent_executor()

    try:
        result = agent.invoke(
            {"messages": [{"role": "user", "content": query}]},
            config={"recursion_limit": MAX_ITERATIONS * 2 + 1},
        )

        # 从消息列表中提取最终回答和中间步骤
        messages = result.get("messages", [])
        final_response = ""
        steps = []

        for msg in messages:
            msg_type = getattr(msg, "type", "")

            if msg_type == "ai":
                # AI 消息：可能包含 tool_calls
                content = getattr(msg, "content", "")
                tool_calls = getattr(msg, "tool_calls", None) or []

                if tool_calls:
                    for tc in tool_calls:
                        steps.append({
                            "thought": content or "调用工具...",
                            "tool": tc.get("name", "unknown"),
                            "tool_input": str(tc.get("args", {})),
                            "observation": "",
                        })
                elif content and not steps:
                    final_response = content
                elif content:
                    final_response = content

            elif msg_type == "tool":
                # 工具返回：绑定到最近一步
                if steps:
                    steps[-1]["observation"] = str(getattr(msg, "content", ""))[:500]

        # 如果最后没有提取到 final_response，使用最后一条 AI 消息
        if not final_response:
            for msg in reversed(messages):
                if getattr(msg, "type", "") == "ai":
                    content = getattr(msg, "content", "")
                    if content and not getattr(msg, "tool_calls", None):
                        final_response = content
                        break

        if not final_response:
            final_response = "抱歉，无法完成您的请求。请简化问题后重试。"

        return {
            "response": final_response,
            "steps": steps,
        }

    except Exception as e:
        error_msg = str(e)
        return {
            "response": f"抱歉，处理您的请求时遇到问题：{error_msg}",
            "steps": [],
        }
