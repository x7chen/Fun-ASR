"""
Fun-ASR API 客户端使用示例

展示如何使用 Python 调用 Fun-ASR RESTful API
"""
import requests
from typing import Optional, List


class FunASRClient:
    """Fun-ASR API 客户端"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")
    
    def health_check(self) -> dict:
        """检查服务健康状态"""
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def transcribe(
        self,
        audio_path: str,
        language: Optional[str] = None,
        itn: Optional[bool] = None,
        hotwords: Optional[List[str]] = None,
        return_timestamps: bool = False,
    ) -> dict:
        """
        语音转写
        
        Args:
            audio_path: 音频文件路径
            language: 识别语言
            itn: 是否进行文本逆规整
            hotwords: 热词列表
            return_timestamps: 是否返回时间戳
        
        Returns:
            转写结果
        """
        url = f"{self.base_url}/v1/transcriptions"
        
        data = {}
        if language:
            data["language"] = language
        if itn is not None:
            data["itn"] = itn
        if hotwords:
            data["hotwords"] = ",".join(hotwords)
        if return_timestamps:
            data["return_timestamps"] = True
        
        with open(audio_path, "rb") as f:
            files = {"file": f}
            response = requests.post(url, files=files, data=data)
        
        response.raise_for_status()
        return response.json()
    
    def transcribe_from_url(
        self,
        audio_url: str,
        language: Optional[str] = None,
        itn: Optional[bool] = None,
        hotwords: Optional[List[str]] = None,
        return_timestamps: bool = False,
    ) -> dict:
        """
        从 URL 转写音频
        
        Args:
            audio_url: 音频文件 URL
            language: 识别语言
            itn: 是否进行文本逆规整
            hotwords: 热词列表
            return_timestamps: 是否返回时间戳
        
        Returns:
            转写结果
        """
        url = f"{self.base_url}/v1/transcriptions/url"
        
        params = {"url": audio_url}
        if language:
            params["language"] = language
        if itn is not None:
            params["itn"] = itn
        if hotwords:
            params["hotwords"] = ",".join(hotwords)
        if return_timestamps:
            params["return_timestamps"] = True
        
        response = requests.post(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_models(self) -> dict:
        """获取支持的模型信息"""
        response = requests.get(f"{self.base_url}/v1/models")
        response.raise_for_status()
        return response.json()


def main():
    """使用示例"""
    # 初始化客户端
    client = FunASRClient(base_url="http://localhost:8000")
    
    # 1. 检查服务状态
    print("=== 检查服务状态 ===")
    health = client.health_check()
    print(f"服务状态：{health['status']}")
    print(f"模型已加载：{health['model_loaded']}")
    print(f"设备：{health['device']}")
    print()
    
    # 2. 获取模型信息
    print("=== 支持的模型 ===")
    models = client.get_models()
    for model in models["models"]:
        print(f"模型：{model['name']}")
        print(f"描述：{model['description']}")
        print(f"支持语言：{', '.join(model['languages'][:5])}...")
    print()
    
    # 3. 转写本地音频文件
    print("=== 转写本地音频 ===")
    audio_path = "path/to/your/audio.wav"  # 替换为实际路径
    
    try:
        result = client.transcribe(
            audio_path=audio_path,
            language="中文",
            itn=True,
            hotwords=["开放时间", "预约"],
            return_timestamps=False,
        )
        print(f"识别结果：{result['text']}")
        print(f"处理时间：{result['processing_time']}秒")
        if result.get('duration'):
            print(f"音频时长：{result['duration']}秒")
    except FileNotFoundError:
        print(f"音频文件不存在：{audio_path}")
    except Exception as e:
        print(f"转写失败：{e}")
    print()
    
    # 4. 从 URL 转写音频
    print("=== 从 URL 转写音频 ===")
    audio_url = "https://example.com/audio.mp3"  # 替换为实际 URL
    
    try:
        result = client.transcribe_from_url(
            audio_url=audio_url,
            language="英文",
            itn=True,
        )
        print(f"识别结果：{result['text']}")
    except Exception as e:
        print(f"转写失败：{e}")


if __name__ == "__main__":
    main()
