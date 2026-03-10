"""
Fun-ASR API 配置文件
"""
import os
from typing import Optional


class APIConfig:
    """API 配置类"""
    
    # 模型配置
    MODEL_DIR: str = os.getenv("FUNASR_MODEL_DIR", "FunAudioLLM/Fun-ASR-Nano-2512")
    DEVICE: str = os.getenv("FUNASR_DEVICE", "cpu")  # 默认使用 CPU
    HUB: str = os.getenv("FUNASR_HUB", "ms")  # "ms" for ModelScope, "hf" for Hugging Face
    
    # 服务器配置
    HOST: str = os.getenv("FUNASR_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("FUNASR_PORT", "8000"))
    
    # 识别配置
    DEFAULT_LANGUAGE: str = os.getenv("FUNASR_LANGUAGE", "中文")
    DEFAULT_ITN: bool = os.getenv("FUNASR_ITN", "true").lower() == "true"
    MAX_AUDIO_DURATION: int = int(os.getenv("FUNASR_MAX_DURATION", "300"))  # 最大音频时长 (秒)
    MAX_FILE_SIZE: int = int(os.getenv("FUNASR_MAX_FILE_SIZE", "52428800"))  # 最大文件大小 50MB
    
    # 支持的音频格式
    ALLOWED_AUDIO_EXTENSIONS: set = {"wav", "mp3", "flac", "m4a", "ogg", "webm"}
    
    # 热词配置
    DEFAULT_HOTWORDS: list = []
    
    # VAD 配置
    USE_VAD: bool = os.getenv("FUNASR_USE_VAD", "false").lower() == "true"
    VAD_MODEL: str = os.getenv("FUNASR_VAD_MODEL", "fsmn-vad")
    VAD_MAX_SEGMENT_TIME: int = int(os.getenv("FUNASR_VAD_MAX_SEGMENT", "30000"))  # 毫秒
    
    @classmethod
    def get_model_kwargs(cls) -> dict:
        """获取模型初始化参数"""
        kwargs = {
            "model": cls.MODEL_DIR,
            "trust_remote_code": True,
            "remote_code": "./model.py",
            "device": cls.DEVICE,
            "hub": cls.HUB,
        }
        
        if cls.USE_VAD:
            kwargs.update({
                "vad_model": cls.VAD_MODEL,
                "vad_kwargs": {"max_single_segment_time": cls.VAD_MAX_SEGMENT_TIME},
            })
        
        return kwargs
    
    @classmethod
    def get_inference_kwargs(cls, language: Optional[str] = None, itn: Optional[bool] = None, 
                             hotwords: Optional[list] = None) -> dict:
        """获取推理参数"""
        return {
            "language": language or cls.DEFAULT_LANGUAGE,
            "itn": itn if itn is not None else cls.DEFAULT_ITN,
            "hotwords": hotwords or cls.DEFAULT_HOTWORDS,
            "cache": {},
            "batch_size": 1,
        }


# 创建全局配置实例
config = APIConfig()
