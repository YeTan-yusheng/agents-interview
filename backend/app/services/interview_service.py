import logging
import time
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.interview_graph import get_turn_graph, generate_evaluation
from app.exceptions import InterviewNotFoundError, InterviewCloseError
from app.models.interview import Interview, Message, STATUS_COMPLETED, STATUS_ONGOING
from app.core.llm import get_model
from app.core.config import settings
from app.exceptions import llmError

logger = logging.getLogger(__name__)

ROLE_INTERVIEWER = "interviewer"
ROLE_CANDIDATE = "candidate"

SYSTEM_PROMPT = (
    "你是一位资深的技术面试官，正在进行一场多轮技术面试。"
    "根据对话历史和候选人的最新回答继续面试："
    "回答含糊或浅显就追问细节，回答扎实就换角度深入或提出新问题。"
    "只输出面试官的下一句话，不要解释，不要复述候选人的回答。"
)

MAX_HISTORY = 20

_ROLE_BY_HISTORY = {"assistant": ROLE_INTERVIEWER, "user": ROLE_CANDIDATE}


def sync_projection(db: AsyncSession, interview: Interview, history: list[dict]) -> None:
    """投影对账：以 checkpoint 的 history 为准，DB 缺几行补几行（幂等）"""
    for i in range(len(interview.messages), len(history)):
        m = history[i]
        db.add(Message(interview_id=interview.id, role=_ROLE_BY_HISTORY[m["role"]], content=m["content"]))


async def start_interview(db: AsyncSession, user_id: int, topic: str) -> Interview:
    interview = Interview(user_id=user_id, topic=topic)
    db.add(interview)
    await db.flush()

    question = await generate_question(topic)

    graph = get_turn_graph()
    await graph.ainvoke({
        "history": [{"role": "assistant", "content": question}],
        "answer": "",
        "round_no": 0,
        "max_rounds": settings.max_rounds,
        "follow_up": "",
        "finished": False,
        "evaluation": "",
    }, config={"configurable": {"thread_id": str(interview.id)}})

    message = Message(interview_id=interview.id, role=ROLE_INTERVIEWER, content=question)
    db.add(message)

    await db.commit()
    await db.refresh(interview, attribute_names=["messages", "created_at"])

    logger.info("面试开始 id=%s user_id=%s topic=%s", interview.id, user_id, topic)
    return interview


async def get_interview(db: AsyncSession, interview_id: int, user_id: int) -> Interview:
    interview = await db.scalar(
        select(Interview)
        .options(selectinload(Interview.messages))
        .where(
            Interview.id == interview_id,
            Interview.user_id == user_id,
        )
    )
    if not interview:
        raise InterviewNotFoundError()
    return interview


async def list_interviews(db: AsyncSession, user_id: int) -> list[Interview]:
    interviews = await db.execute(
        select(Interview)
        .options(selectinload(Interview.messages))
        .where(Interview.user_id == user_id)
    )

    interviews_list = interviews.scalars().all()
    return interviews_list


async def generate_question(topic: str) -> str:
    start = time.perf_counter()

    try:
        resp = await get_model().ainvoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=f"应聘方向：{topic}"),
        ])
    except Exception as exc:
        logger.error("LLM 调用失败 topic=%s error=%s", topic, exc)
        raise llmError() from exc

    duration_ms = (time.perf_counter() - start) * 1000
    question =( resp.content or "").strip()

    return question.strip()


async def answer_interview(db: AsyncSession, interview_id: int, user_id: int, content: str) -> Interview:
    interview = await get_interview(db, interview_id, user_id)
    if interview.status != STATUS_ONGOING:
        logger.warning("拒绝回答，面试已经结束 id=%s", interview_id)
        raise InterviewCloseError()

    graph = get_turn_graph()
    cfg = {"configurable": {"thread_id": str(interview_id)}}

    snap = await graph.aget_state(cfg)
    if not snap.values:
        history = [
            {"role": "assistant" if i.role == ROLE_INTERVIEWER else "user", "content": i.content} for i in
            interview.messages[-MAX_HISTORY:]
        ]

        round_no = sum(1 for i in interview.messages if i.role == ROLE_CANDIDATE)
        await graph.ainvoke({
            "history": history, "answer": "",
            "round_no": round_no, "max_rounds": settings.max_rounds,
            "follow_up": "", "finished": False, "evaluation": "",
        }, config=cfg)

    state = await graph.ainvoke({"answer": content, }, config=cfg)

    sync_projection(db, interview, state["history"])

    if state["finished"]:
        interview.status = STATUS_COMPLETED
        interview.evaluation = state["evaluation"]

    await db.commit()
    await db.refresh(interview, attribute_names=["messages"])
    logger.info("回答处理完成 id=%s finished=%s", interview_id, state["finished"])
    return interview


async def finish_interview(db: AsyncSession, interview_id: int, user_id: int) -> Interview:
    interview = await get_interview(db, interview_id, user_id)
    if interview.status != STATUS_ONGOING:
        logger.warning("面试已经结束 id=%s", interview_id)
        raise InterviewCloseError()

    history = [
        {"role": "assistant" if i.role == ROLE_INTERVIEWER else "user", "content": i.content}
        for i in interview.messages[-MAX_HISTORY:]
    ]

    interview.status = STATUS_COMPLETED
    interview.evaluation = await generate_evaluation(history)

    await db.commit()
    await db.refresh(interview, attribute_names=["messages"])
    logger.info("面试完成 id=%s user_id=%s evaluation=%s", interview_id, user_id, interview.evaluation)
    return interview
