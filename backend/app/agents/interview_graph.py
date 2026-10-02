import logging
from typing import TypedDict
from langgraph.graph import END, START, StateGraph

from app.core.config import settings
from app.core.llm import client
from app.exceptions import llmError

logger = logging.getLogger(__name__)

# 面试官
SYSTEM_PROMPT = (
    "你是一位资深的技术面试官，正在进行一场多轮技术面试。"
    "根据对话历史和候选人的最新回答继续面试："
    "回答含糊或浅显就追问细节，回答扎实就换角度深入或提出新问题。"
    "只输出面试官的下一句话，不要解释，不要复述候选人的回答。"
)

# 评分官
SCORER_PROMPT = (
    "你是一位严格但客观的面试评估官。"
    "根据整场面试对话，给候选人一段 150 字以内的总评："
    "指出表现最好的地方、最薄弱的地方，以及一条最优先的改进建议。"
    "只输出总评正文，不要客套开头。"
)


class InterviewTurnState(TypedDict):
    history: list[dict]  # LLM 方言的历史（assistant/user 已映射好）
    answer: str  # 候选人本次回答
    round_no: int  # 本答是第几轮
    max_rounds: int
    follow_up: str  # 面试官的追问（ask_llm 节点产出）
    finished: bool  # 是否结束（finish 节点产出）
    evaluation: str  # 整场结束后的总评


async def ask_llm(state: InterviewTurnState) -> dict:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *state["history"],
        {"role": "user", "content": state["answer"]},
    ]
    try:
        resp = await client.chat.completions.create(
            model=settings.llm_model,
            messages=messages,
            temperature=0.7,
        )
    except Exception as exc:
        raise llmError() from exc

    return {"follow_up": (resp.choices[0].message.content or "").strip()}


def finish(state: InterviewTurnState) -> dict:
    return {"finished": True}


def route_by_round(state: InterviewTurnState) -> str:
    return "ask_llm" if state["round_no"] < state["max_rounds"] else "finish"


async def generate_evaluation(messages: list[dict]) -> str:
    """能力函数：给一份完整对话，返回总评文本。与图无关，谁都能调。"""
    try:
        resp = await client.chat.completions.create(
            model=settings.llm_model,
            messages=[{"role": "system", "content": SCORER_PROMPT}, *messages],
            temperature=0.3,
        )
    except Exception as exc:
        raise llmError() from exc

    return (resp.choices[0].message.content or "").strip()


async def score(state: InterviewTurnState) -> dict:
    """适配器：从 state 取材料、拼完整对话，能力交给 generate_evaluation。"""
    messages = [*state["history"],{"role":"user","content":state["answer"]}]
    return {"evaluation": await generate_evaluation(messages)}


def build_turn_graph():
    graph = StateGraph(InterviewTurnState)
    graph.add_node("ask_llm", ask_llm)
    graph.add_node("finish", finish)
    graph.add_node("score", score)
    graph.add_conditional_edges(
        START,
        route_by_round,
        {"ask_llm": "ask_llm", "finish": "finish"}
    )
    graph.add_edge("ask_llm", END)
    graph.add_edge("finish", "score")
    graph.add_edge("score", END)
    return graph


turn_graph = build_turn_graph().compile()
