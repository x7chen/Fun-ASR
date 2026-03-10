"""
Fun-ASR API 数据模型定义
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class TranscriptionRequest(BaseModel):
    """语音转写请求模型"""
    
    language: Optional[str] = Field(
        default=None,
        description="识别语言，如：中文、英文、日文等"
    )
    itn: Optional[bool] = Field(
        default=None,
        description="是否进行文本逆规整 (Inverse Text Normalization)"
    )
    hotwords: Optional[List[str]] = Field(
        default=[],
        description="热词列表，用于提升特定词汇的识别准确率"
    )
    return_timestamps: Optional[bool] = Field(
        default=False,
        description="是否返回时间戳信息"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "language": "中文",
                "itn": True,
                "hotwords": ["开放时间", "预约"],
                "return_timestamps": False
            }
        }


class Timestamp(BaseModel):
    """时间戳信息"""
    
    token: str = Field(..., description="识别出的文本片段")
    start_time: float = Field(..., description="开始时间 (秒)")
    end_time: float = Field(..., description="结束时间 (秒)")
    confidence: Optional[float] = Field(None, description="置信度")


class TranscriptionResult(BaseModel):
    """转写结果模型"""
    
    text: str = Field(..., description="识别出的文本")
    text_tn: Optional[str] = Field(None, description="规整后的文本")
    language: Optional[str] = Field(None, description="识别语言")
    timestamps: Optional[List[Timestamp]] = Field(None, description="时间戳列表")
    ctc_text: Optional[str] = Field(None, description="CTC 解码结果")
    ctc_timestamps: Optional[List[Timestamp]] = Field(None, description="CTC 时间戳")
    duration: Optional[float] = Field(None, description="音频时长 (秒)")
    processing_time: Optional[float] = Field(None, description="处理时间 (秒)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "你好，这里是 Fun-ASR 语音识别服务",
                "text_tn": "你好，这里是 Fun-ASR 语音识别服务",
                "language": "中文",
                "timestamps": None,
                "duration": 5.2,
                "processing_time": 1.3
            }
        }


class HealthResponse(BaseModel):
    """健康检查响应"""
    
    status: str = Field(..., description="服务状态")
    model_loaded: bool = Field(..., description="模型是否已加载")
    device: str = Field(..., description="运行设备")
    version: str = Field(..., description="API 版本")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "model_loaded": True,
                "device": "cuda:0",
                "version": "1.0.0"
            }
        }


class ErrorResponse(BaseModel):
    """错误响应模型"""
    
    error: str = Field(..., description="错误类型")
    message: str = Field(..., description="错误信息")
    detail: Optional[Any] = Field(None, description="详细错误信息")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "ValidationError",
                "message": "音频文件格式不支持",
                "detail": None
            }
        }


class BatchTranscriptionRequest(BaseModel):
    """批量转写请求模型"""
    
    audio_files: List[str] = Field(..., description="音频文件路径列表")
    language: Optional[str] = Field(default=None, description="识别语言")
    itn: Optional[bool] = Field(default=None, description="是否进行文本逆规整")
    hotwords: Optional[List[str]] = Field(default=[], description="热词列表")
    
    class Config:
        json_schema_extra = {
            "example": {
                "audio_files": ["/path/to/audio1.wav", "/path/to/audio2.wav"],
                "language": "中文",
                "itn": True,
                "hotwords": []
            }
        }


class BatchTranscriptionResult(BaseModel):
    """批量转写结果模型"""
    
    results: List[TranscriptionResult] = Field(..., description="转写结果列表")
    total: int = Field(..., description="总处理数")
    success: int = Field(..., description="成功数")
    failed: int = Field(..., description="失败数")
    
    class Config:
        json_schema_extra = {
            "example": {
                "results": [],
                "total": 2,
                "success": 2,
                "failed": 0
            }
        }
