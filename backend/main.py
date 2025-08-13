# backend/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any

# 👇 从你的模块中导入已经编译好的 app
from Graph.CompileGraph import app as rag_app
from Graph.GraphState import GraphState

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

#app = FastAPI()
app = FastAPI(title="Adaptive RAG API")

# ✅ 正确配置 CORS：允许 localhost 和 127.0.0.1
origins = [
    "http://localhost:3000",
    "http://localhost:5173",  # 👈 很多时候 Vite 会用这个
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 允许的前端地址
    allow_credentials=True,
    allow_methods=["*"],    # 允许所有方法（GET, POST, etc.）
    allow_headers=["*"],    # 允许所有头部
)

class QuestionRequest(BaseModel):
    question: str

@app.post("/chat")
async def chat(request: QuestionRequest):
    try:
        print(f"📥 收到问题: {request.question}")  # 👈 打印输入
        result = rag_app.invoke({"question": request.question})
        print(f"✅ 调用成功，结果: {result}")     # 👈 打印输出
        return {
            "messages": [
                {"type": "user", "content": request.question},
                {"type": "ai", "content": result.get("generation", "No answer")}
            ],
            "source_documents": result.get("documents", [])
        }
    except Exception as e:
        print(f"❌ 错误详情: {type(e).__name__}: {e}")  # 👈 打印错误
        import traceback
        traceback.print_exc()  # 👈 打印完整堆栈
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health():
    return {"status": "ok"}