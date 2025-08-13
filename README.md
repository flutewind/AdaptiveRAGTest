# RAG测试程序

这是一个基于Retrieval-Augmented Generation (RAG)架构的前后端测试程序，后端使用了国内的TONGYI和Moonshot模型替代OpenAI模型，并且前端是用React构建的。

## 项目概述

此项目旨在展示如何将检索增强生成(RAG)技术与国内AI模型结合使用。通过本项目，用户能够体验到利用本地化模型进行文本生成的能力，以及其在实际应用中的潜力。

## 目录结构

ag-test/
├── backend/
│   ├── app.py                # 后端主程序入口
│   ├── models/               # 存放使用的模型配置及权重
│   ├── utils/                # 工具函数库
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/       # React组件
│   │   ├── App.js            # 主应用组件
│   │   └── index.js          # React应用入口
├── README.md                 # 项目说明文档
└── requirements.txt          # Python依赖包列表


## 环境配置

