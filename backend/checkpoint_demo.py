import asyncio
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from app.agents.interview_graph import build_turn_graph


async def main():
    async with AsyncSqliteSaver.from_conn_string("checkpoints.db") as saver:
        demo_graph = build_turn_graph().compile(checkpointer=saver)
        config = {"configurable": {"thread_id": "demo-1"}}

        snap = await demo_graph.aget_state(config)
        if snap.values:
            print("发现上次会话的 checkpoint，直接续（跳过全量初始化）")
        else:
            print("全新 thread，先做全量首调")
            s1 = await demo_graph.ainvoke({
                "history": [{"role": "assistant", "content": "介绍一个你最有挑战的项目"}],
                "answer": "我做了一个面试系统，用 LangGraph 编排多个 Agent……",
                "round_no": 1, "max_rounds": 3,
                "follow_up": "", "finished": False, "evaluation": "",
            }, config=config)
            print("第 1 次追问：", s1["follow_up"][:60], "...\n")

        # 增量续聊：round_no / history 全从 checkpoint 来
        s2 = await demo_graph.ainvoke(
            {"answer": "数据库层我选了异步驱动，避开了同步阻塞……"},
            config=config,
        )
        print("续聊追问：", s2["follow_up"][:60], "...\n")
        print("当前 round_no =", (await demo_graph.aget_state(config)).values["round_no"])


if __name__ == "__main__":
    asyncio.run(main())
