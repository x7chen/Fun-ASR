"""
Fun-ASR RESTful API 服务

提供语音识别的 HTTP 接口服务
"""
import io
import logging
import os
import tempfile
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

import torch
from fastapi import FastAPI, File, Form, HTTPException, UploadFile, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from funasr import AutoModel

from api.config import config
from api.schemas import (
    BatchTranscriptionResult,
    ErrorResponse,
    HealthResponse,
    Timestamp,
    TranscriptionRequest,
    TranscriptionResult,
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 全局模型实例
model = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global model
    
    # 启动时加载模型
    logger.info("正在加载 Fun-ASR 模型...")
    logger.info(f"模型目录：{config.MODEL_DIR}")
    logger.info(f"设备：{config.DEVICE}")
    
    try:
        model_kwargs = config.get_model_kwargs()
        model = AutoModel(**model_kwargs)
        logger.info("模型加载成功!")
    except Exception as e:
        logger.error(f"模型加载失败：{str(e)}")
        raise
    
    yield
    
    # 关闭时清理资源
    logger.info("正在释放模型资源...")
    if model is not None:
        del model
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    logger.info("服务已关闭")


# 创建 FastAPI 应用
app = FastAPI(
    title="Fun-ASR Speech Recognition API",
    description="基于 Fun-ASR 的语音识别 RESTful API 服务，支持多种语言和方言",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def validate_audio_file(file: UploadFile) -> tuple[bytes, str]:
    """验证音频文件"""
    # 检查文件扩展名
    filename = file.filename or ""
    ext = filename.split(".")[-1].lower() if "." in filename else ""
    
    if ext not in config.ALLOWED_AUDIO_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的音频格式：{ext}。支持的格式：{', '.join(config.ALLOWED_AUDIO_EXTENSIONS)}"
        )
    
    # 读取文件内容
    content = file.file.read()
    
    # 检查文件大小
    if len(content) > config.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"文件过大：{len(content) / 1024 / 1024:.2f}MB。最大允许：{config.MAX_FILE_SIZE / 1024 / 1024:.2f}MB"
        )
    
    return content, ext


def transcribe_audio(audio_data: bytes, request: TranscriptionRequest, file_ext: str = "wav") -> TranscriptionResult:
    """执行语音识别"""
    start_time = time.time()

    # 创建临时文件保存音频
    with tempfile.NamedTemporaryFile(
        suffix=f".{file_ext}",
        delete=False
    ) as tmp_file:
        tmp_file.write(audio_data)
        tmp_path = tmp_file.name
    
    try:
        # 获取音频时长
        try:
            import soundfile as sf
            duration = sf.info(tmp_path).duration
        except:
            duration = None
        
        # 检查音频时长
        if duration and duration > config.MAX_AUDIO_DURATION:
            raise HTTPException(
                status_code=400,
                detail=f"音频时长过长：{duration:.2f}秒。最大允许：{config.MAX_AUDIO_DURATION}秒"
            )
        
        # 执行识别
        inference_kwargs = config.get_inference_kwargs(
            language=request.language,
            itn=request.itn,
            hotwords=request.hotwords,
        )
        
        result = model.generate(
            input=[tmp_path],
            **inference_kwargs,
        )
        
        processing_time = time.time() - start_time
        
        # 解析结果
        res = result[0] if result else {}
        text = res.get("text", "")
        text_tn = res.get("text_tn", text)
        
        # 处理时间戳
        timestamps = None
        if request.return_timestamps and "timestamps" in res:
            timestamps = [
                Timestamp(
                    token=ts.get("token", ""),
                    start_time=ts.get("start_time", 0),
                    end_time=ts.get("end_time", 0),
                )
                for ts in res.get("timestamps", [])
            ]
        
        ctc_timestamps = None
        if request.return_timestamps and "ctc_timestamps" in res:
            ctc_timestamps = [
                Timestamp(
                    token=ts.get("token", ""),
                    start_time=ts.get("start_time", 0),
                    end_time=ts.get("end_time", 0),
                )
                for ts in res.get("ctc_timestamps", [])
            ]
        
        return TranscriptionResult(
            text=text,
            text_tn=text_tn,
            language=request.language or config.DEFAULT_LANGUAGE,
            timestamps=timestamps,
            ctc_text=res.get("ctc_text"),
            ctc_timestamps=ctc_timestamps,
            duration=duration,
            processing_time=round(processing_time, 3),
        )
    
    finally:
        # 清理临时文件
        try:
            os.unlink(tmp_path)
        except:
            pass


@app.get("/", tags=["Root"])
async def root():
    """根路径"""
    return {
        "message": "Fun-ASR Speech Recognition API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """健康检查接口"""
    return HealthResponse(
        status="healthy",
        model_loaded=model is not None,
        device=config.DEVICE,
        version="1.0.0",
    )


@app.post(
    "/v1/transcriptions",
    response_model=TranscriptionResult,
    responses={
        200: {"model": TranscriptionResult},
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
    tags=["Transcription"]
)
async def transcribe(
    file: UploadFile = File(..., description="音频文件 (支持 wav, mp3, flac, m4a, ogg, webm)"),
    language: Optional[str] = Form(None, description="识别语言"),
    itn: Optional[bool] = Form(None, description="是否进行文本逆规整"),
    hotwords: Optional[str] = Form(None, description="热词列表，逗号分隔"),
    return_timestamps: Optional[bool] = Form(False, description="是否返回时间戳"),
):
    """
    语音转写接口
    
    上传音频文件进行语音识别，返回识别结果文本。
    
    **参数说明:**
    - `file`: 音频文件 (必填)
    - `language`: 识别语言 (可选，默认使用配置中的语言)
    - `itn`: 是否进行文本逆规整 (可选)
    - `hotwords`: 热词列表，逗号分隔 (可选)
    - `return_timestamps`: 是否返回时间戳信息 (可选)
    
    **支持的语言:**
    - Fun-ASR-Nano: 中文、英文、日文 (中文支持 7 大方言和 26 种地方口音)
    - Fun-ASR-MLT-Nano: 31 种语言 (韩语、越南语、印尼语、泰语等)
    """
    try:
        # 验证文件
        audio_data, ext = validate_audio_file(file)

        # 解析热词
        hotwords_list = []
        if hotwords:
            hotwords_list = [h.strip() for h in hotwords.split(",") if h.strip()]

        # 创建请求对象
        request = TranscriptionRequest(
            language=language,
            itn=itn,
            hotwords=hotwords_list,
            return_timestamps=return_timestamps,
        )

        # 执行识别
        result = transcribe_audio(audio_data, request, ext)

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"识别失败：{str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"识别失败：{str(e)}"
        )


@app.post(
    "/v1/transcriptions/json",
    response_model=TranscriptionResult,
    responses={
        200: {"model": TranscriptionResult},
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
    tags=["Transcription"]
)
async def transcribe_json(
    request: TranscriptionRequest,
    file: UploadFile = File(..., description="音频文件"),
):
    """
    语音转写接口 (JSON 参数)

    使用 JSON 格式传递参数，适合需要复杂配置的场景。
    """
    try:
        # 验证文件
        audio_data, ext = validate_audio_file(file)

        # 执行识别
        result = transcribe_audio(audio_data, request, ext)

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"识别失败：{str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"识别失败：{str(e)}"
        )


@app.post(
    "/v1/transcriptions/url",
    response_model=TranscriptionResult,
    responses={
        200: {"model": TranscriptionResult},
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
    tags=["Transcription"]
)
async def transcribe_url(
    url: str = Query(..., description="音频文件 URL"),
    language: Optional[str] = Query(None, description="识别语言"),
    itn: Optional[bool] = Query(None, description="是否进行文本逆规整"),
    hotwords: Optional[str] = Query(None, description="热词列表，逗号分隔"),
    return_timestamps: Optional[bool] = Query(False, description="是否返回时间戳"),
):
    """
    语音转写接口 (URL 方式)
    
    通过音频文件 URL 进行语音识别。
    """
    import requests
    
    try:
        # 下载音频文件
        logger.info(f"正在下载音频：{url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        audio_data = response.content
        
        # 从 URL 获取文件扩展名
        ext = url.split(".")[-1].lower() if "." in url else "wav"
        if ext not in config.ALLOWED_AUDIO_EXTENSIONS:
            ext = "wav"

        # 解析热词
        hotwords_list = []
        if hotwords:
            hotwords_list = [h.strip() for h in hotwords.split(",") if h.strip()]

        # 创建请求对象
        request = TranscriptionRequest(
            language=language,
            itn=itn,
            hotwords=hotwords_list,
            return_timestamps=return_timestamps,
        )

        # 执行识别
        result = transcribe_audio(audio_data, request, ext)

        return result

    except requests.RequestException as e:
        raise HTTPException(
            status_code=400,
            detail=f"无法下载音频文件：{str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"识别失败：{str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"识别失败：{str(e)}"
        )


@app.get("/v1/models", tags=["Models"])
async def list_models():
    """获取支持的模型和语言信息"""
    return {
        "models": [
            {
                "name": "Fun-ASR-Nano-2512",
                "description": "端到端语音识别大模型，支持 31 种语言",
                "languages": [
                    "中文", "英文", "日文",
                    "粤语", "韩语", "越南语", "印尼语", "泰语", 
                    "马来语", "菲律宾语", "阿拉伯语", "印地语",
                    "保加利亚语", "克罗地亚语", "捷克语", "丹麦语",
                    "荷兰语", "爱沙尼亚语", "芬兰语", "希腊语",
                    "匈牙利语", "爱尔兰语", "拉脱维亚语", "立陶宛语",
                    "马耳他语", "波兰语", "葡萄牙语", "罗马尼亚语",
                    "斯洛伐克语", "斯洛文尼亚语", "瑞典语"
                ],
                "features": [
                    "7 大方言支持",
                    "26 种地方口音",
                    "音乐背景歌词识别",
                    "低延迟实时转写"
                ]
            }
        ],
        "current_model": config.MODEL_DIR,
        "device": config.DEVICE,
    }


# 错误处理器
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTPError",
            "message": exc.detail,
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    logger.error(f"未处理的异常：{str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "InternalServerError",
            "message": "服务器内部错误",
            "detail": str(exc),
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"启动 Fun-ASR API 服务：{config.HOST}:{config.PORT}")
    uvicorn.run(
        "api.server:app",
        host=config.HOST,
        port=config.PORT,
        reload=False,
        workers=1,
    )
