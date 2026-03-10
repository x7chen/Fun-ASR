@echo off
REM Fun-ASR API 启动脚本 (Windows)

REM 设置环境变量 (可选)
REM set FUNASR_MODEL_DIR=FunAudioLLM/Fun-ASR-Nano-2512
REM set FUNASR_DEVICE=cuda:0
REM set FUNASR_HOST=0.0.0.0
REM set FUNASR_PORT=8000
REM set FUNASR_LANGUAGE=中文
REM set FUNASR_USE_VAD=false

REM 启动服务
python -m uvicorn api.server:app --host 0.0.0.0 --port 8000 --workers 1
