#!/bin/bash
# Fun-ASR API 启动脚本

# 设置环境变量 (可选)
# export FUNASR_MODEL_DIR="FunAudioLLM/Fun-ASR-Nano-2512"
# export FUNASR_DEVICE="cuda:0"
# export FUNASR_HOST="0.0.0.0"
# export FUNASR_PORT="8000"
# export FUNASR_LANGUAGE="中文"
# export FUNASR_USE_VAD="false"

# 启动服务
python -m uvicorn api.server:app --host 0.0.0.0 --port 8000 --workers 1
