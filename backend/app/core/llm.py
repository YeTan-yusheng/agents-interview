from langchain_openai import ChatOpenAI

from app.core.config import settings

_model = None

def get_model() -> ChatOpenAI:
    """模块级单例：全项目共用一个模型客户端（回调体系的入口）。"""
    global _model
    if _model is None:
        _model = ChatOpenAI(
            model=settings.llm_model,
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url,
            temperature=0.7,
        )
    return _model
