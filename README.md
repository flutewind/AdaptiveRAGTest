# RAG测试程序

这是一个基于Retrieval-Augmented Generation (RAG)架构的前后端测试程序，后端使用了国内的TONGYI和Moonshot模型替代OpenAI模型，前端用React构建。  
后端原文参考 https://langchain-ai.github.io/langgraph/tutorials/rag/langgraph_adaptive_rag/ ，由于原文使用OpenAI的大模型，国内不能访问，因此尝试使用国内的模型代替。


## 项目概述

此项目旨在展示如何将检索增强生成(RAG)技术与国内AI模型结合使用。通过本项目，用户能够体验到利用本地化模型进行文本生成的能力，以及其在实际应用中的潜力。

## 目录结构

AdaptiveRAGTest  
├──backend/  
│   ├──main.py             #后端程序入口  
├──CreateIndex/            #创建本地或Internet的网页索引，使用了阿里通义的模型  
├──frontend/               #前端React程序  
│   ├──src/  
│   ├──├──App.tsx          #问答页面  
├──Graph/                  #工作流  
├──moonshot/               #使用月之暗面的免费模型实现问题路由、检索、幻觉、评分、重写的功能  
├──TavilySearch/           #网页搜索工具  
├──tongyi/                 #使用阿里通义的模型实现问题路由、检索、幻觉、评分、重写的功能  
├──utils/                  #提供了一个模型工厂，单例，用以限制调用频率  


## 环境配置

后端启动： uvicorn backend.main:app --reload --port 8000  
前端启动：   
cd frontend  
npm run dev  
启动后访问 http://localhost:5173/ 进行问答测试。