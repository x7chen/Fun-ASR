# Fun-ASR RESTful API 调用说明

## 目录

- [服务地址](#服务地址)
- [快速开始](#快速开始)
- [API 接口详解](#api-接口详解)
- [代码示例](#代码示例)
- [常见问题](#常见问题)

---

## 服务地址

| 环境 | 地址 |
|------|------|
| 本地服务 | http://localhost:8000 |
| API 文档 | http://localhost:8000/docs |
| ReDoc 文档 | http://localhost:8000/redoc |

---

## 快速开始

### 1. 启动服务

```bash
# Windows
start_api.bat

# Linux/Mac
bash start_api.sh

# 或直接运行
python -m uvicorn api.server:app --host 0.0.0.0 --port 8000
```

### 2. 检查服务状态

```bash
curl http://localhost:8000/health
```

**响应示例:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "device": "cpu",
  "version": "1.0.0"
}
```

### 3. 调用转写接口

```bash
curl -X POST "http://localhost:8000/v1/transcriptions" \
  -F "file=@audio.mp3" \
  -F "language=中文"
```

---

## API 接口详解

### 1. 健康检查

**接口:** `GET /health`

**说明:** 检查服务运行状态

**响应:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "device": "cpu",
  "version": "1.0.0"
}
```

---

### 2. 语音转写（表单参数）

**接口:** `POST /v1/transcriptions`

**Content-Type:** `multipart/form-data`

**参数:**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| file | File | 是 | - | 音频文件，支持 wav, mp3, flac, m4a, ogg, webm |
| language | string | 否 | 中文 | 识别语言：中文/英文/日文/粤语/韩语等 |
| itn | boolean | 否 | true | 是否进行文本逆规整（数字、日期等格式化） |
| hotwords | string | 否 | - | 热词列表，逗号分隔，如："开放，预约，时间" |
| return_timestamps | boolean | 否 | false | 是否返回时间戳信息 |

**cURL 示例:**
```bash
curl -X POST "http://localhost:8000/v1/transcriptions" \
  -F "file=@meeting.wav" \
  -F "language=中文" \
  -F "itn=true" \
  -F "hotwords=张三，李四，项目预算" \
  -F "return_timestamps=false"
```

**成功响应:**
```json
{
  "text": "开饭时间早上九点至下午五点。",
  "text_tn": "开饭时间早上九点至下午五点",
  "language": "中文",
  "timestamps": null,
  "ctc_text": "开饭时间早上九点至下午五点",
  "ctc_timestamps": null,
  "duration": 5.62,
  "processing_time": 2.58
}
```

**带时间戳响应:**
```json
{
  "text": "你好世界",
  "timestamps": [
    {"token": "你", "start_time": 0.12, "end_time": 0.24},
    {"token": "好", "start_time": 0.24, "end_time": 0.36},
    {"token": "世", "start_time": 0.36, "end_time": 0.48},
    {"token": "界", "start_time": 0.48, "end_time": 0.60}
  ],
  "duration": 1.5,
  "processing_time": 1.2
}
```

---

### 3. 语音转写（JSON 参数）

**接口:** `POST /v1/transcriptions/json`

**说明:** 使用 JSON 格式传递参数，适合复杂配置场景

**参数:**

| 参数 | 类型 | 说明 |
|------|------|------|
| request | JSON | 转写配置对象 |
| file | File | 音频文件 |

**cURL 示例:**
```bash
curl -X POST "http://localhost:8000/v1/transcriptions/json" \
  -F 'request={
    "language": "英文",
    "itn": true,
    "hotwords": ["AI", "Machine Learning"],
    "return_timestamps": true
  }' \
  -F "file=@english.wav"
```

---

### 4. 语音转写（URL 方式）

**接口:** `POST /v1/transcriptions/url`

**参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| url | string | 是 | 音频文件 URL |
| language | string | 否 | 识别语言 |
| itn | boolean | 否 | 是否进行文本逆规整 |
| hotwords | string | 否 | 热词列表，逗号分隔 |
| return_timestamps | boolean | 否 | 是否返回时间戳 |

**cURL 示例:**
```bash
curl -X POST "http://localhost:8000/v1/transcriptions/url?url=https://example.com/audio.wav" \
  -F "language=中文"
```

---

### 5. 获取模型信息

**接口:** `GET /v1/models`

**响应:**
```json
{
  "models": [
    {
      "name": "Fun-ASR-Nano-2512",
      "description": "端到端语音识别大模型，支持 31 种语言",
      "languages": ["中文", "英文", "日文", "粤语", "韩语", ...],
      "features": ["7 大方言支持", "26 种地方口音", "音乐背景歌词识别", "低延迟实时转写"]
    }
  ],
  "current_model": "FunAudioLLM/Fun-ASR-Nano-2512",
  "device": "cpu"
}
```

---

## 代码示例

### Python

#### 基础示例

```python
import requests

def transcribe_audio(file_path, language="中文"):
    """语音转写基础函数"""
    url = "http://localhost:8000/v1/transcriptions"
    
    with open(file_path, "rb") as f:
        files = {"file": f}
        data = {"language": language}
        response = requests.post(url, files=files, data=data)
    
    if response.status_code == 200:
        result = response.json()
        return result["text"]
    else:
        raise Exception(f"转写失败：{response.text}")

# 使用示例
text = transcribe_audio("audio.wav")
print(f"识别结果：{text}")
```

#### 完整示例（带错误处理）

```python
import requests
from typing import Optional, List

class FunASRClient:
    """Fun-ASR API 客户端"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")
    
    def health_check(self) -> dict:
        """检查服务状态"""
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def transcribe(
        self,
        audio_path: str,
        language: str = "中文",
        itn: bool = True,
        hotwords: Optional[List[str]] = None,
        return_timestamps: bool = False
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
            转写结果字典
        """
        url = f"{self.base_url}/v1/transcriptions"
        
        data = {
            "language": language,
            "itn": str(itn).lower(),
            "return_timestamps": str(return_timestamps).lower()
        }
        
        if hotwords:
            data["hotwords"] = ",".join(hotwords)
        
        with open(audio_path, "rb") as f:
            files = {"file": f}
            response = requests.post(url, files=files, data=data)
        
        response.raise_for_status()
        return response.json()
    
    def transcribe_from_url(
        self,
        audio_url: str,
        language: str = "中文"
    ) -> dict:
        """从 URL 转写音频"""
        url = f"{self.base_url}/v1/transcriptions/url"
        params = {"url": audio_url, "language": language}
        response = requests.post(url, params=params)
        response.raise_for_status()
        return response.json()


# 使用示例
if __name__ == "__main__":
    client = FunASRClient()
    
    # 检查服务
    health = client.health_check()
    print(f"服务状态：{health['status']}")
    
    # 转写音频
    result = client.transcribe(
        "meeting.wav",
        language="中文",
        hotwords=["张三", "李四", "项目预算"],
        return_timestamps=True
    )
    
    print(f"识别结果：{result['text']}")
    print(f"音频时长：{result['duration']:.2f}秒")
    print(f"处理时间：{result['processing_time']:.2f}秒")
    
    if result.get('timestamps'):
        print("\n时间戳:")
        for ts in result['timestamps'][:5]:  # 显示前 5 个
            print(f"  {ts['token']}: {ts['start_time']:.2f}s - {ts['end_time']:.2f}s")
```

#### 批量处理示例

```python
import requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

def transcribe_single_file(args):
    """处理单个文件"""
    file_path, output_dir = args
    
    url = "http://localhost:8000/v1/transcriptions"
    
    with open(file_path, "rb") as f:
        response = requests.post(url, files={"file": f}, data={"language": "中文"})
    
    if response.status_code == 200:
        result = response.json()
        # 保存结果
        output_file = Path(output_dir) / f"{file_path.stem}.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(result["text"])
        return file_path.name, result["text"], "success"
    else:
        return file_path.name, None, "failed"

def batch_transcribe(audio_folder: str, output_folder: str, max_workers: int = 4):
    """批量转写音频文件"""
    audio_files = list(Path(audio_folder).glob("*.wav"))
    audio_files.extend(Path(audio_folder).glob("*.mp3"))
    
    Path(output_folder).mkdir(parents=True, exist_ok=True)
    
    args_list = [(f, output_folder) for f in audio_files]
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(transcribe_single_file, args_list))
    
    # 统计结果
    success = sum(1 for _, _, status in results if status == "success")
    print(f"处理完成：成功 {success}/{len(results)}")
    
    return results

# 使用示例
# batch_transcribe("audio_files", "transcription_results")
```

---

### JavaScript / Node.js

#### 基础示例

```javascript
const FormData = require('form-data');
const fs = require('fs');
const axios = require('axios');

async function transcribeAudio(filePath) {
    const form = new FormData();
    form.append('file', fs.createReadStream(filePath));
    form.append('language', '中文');
    
    try {
        const response = await axios.post(
            'http://localhost:8000/v1/transcriptions',
            form,
            { headers: form.getHeaders() }
        );
        return response.data.text;
    } catch (error) {
        console.error('转写失败:', error.message);
        throw error;
    }
}

// 使用示例
transcribeAudio('audio.wav').then(text => {
    console.log('识别结果:', text);
});
```

#### 浏览器示例

```javascript
async function transcribeAudioFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('language', '中文');
    formData.append('itn', 'true');
    
    try {
        const response = await fetch('http://localhost:8000/v1/transcriptions', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        return result.text;
    } catch (error) {
        console.error('转写失败:', error);
        throw error;
    }
}

// HTML 文件输入监听
document.getElementById('audioInput').addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (file) {
        const text = await transcribeAudioFile(file);
        document.getElementById('result').textContent = text;
    }
});
```

---

### cURL

```bash
# 基础转写
curl -X POST "http://localhost:8000/v1/transcriptions" \
  -F "file=@audio.wav"

# 指定语言
curl -X POST "http://localhost:8000/v1/transcriptions" \
  -F "file=@audio.wav" \
  -F "language=英文"

# 使用热词
curl -X POST "http://localhost:8000/v1/transcriptions" \
  -F "file=@audio.wav" \
  -F "language=中文" \
  -F "hotwords=张三，李四，项目预算"

# 获取时间戳
curl -X POST "http://localhost:8000/v1/transcriptions" \
  -F "file=@audio.wav" \
  -F "return_timestamps=true"

# 从 URL 转写
curl -X POST "http://localhost:8000/v1/transcriptions/url?url=https://example.com/audio.wav"
```

---

### Java (OkHttp)

```java
import okhttp3.*;
import java.io.File;
import java.io.IOException;

public class FunASRClient {
    private static final String BASE_URL = "http://localhost:8000";
    private final OkHttpClient client = new OkHttpClient();
    
    public String transcribe(File audioFile) throws IOException {
        RequestBody requestBody = new MultipartBody.Builder()
            .setType(MultipartBody.FORM)
            .addFormDataPart("file", audioFile.getName(),
                RequestBody.create(audioFile, MediaType.parse("audio/wav")))
            .addFormDataPart("language", "中文")
            .build();
        
        Request request = new Request.Builder()
            .url(BASE_URL + "/v1/transcriptions")
            .post(requestBody)
            .build();
        
        try (Response response = client.newCall(request).execute()) {
            if (!response.isSuccessful()) {
                throw new IOException("转写失败: " + response.message());
            }
            
            String responseBody = response.body().string();
            // 使用 JSON 库解析结果
            return extractTextFromJson(responseBody);
        }
    }
    
    private String extractTextFromJson(String json) {
        // 使用 Gson 或 Jackson 解析 JSON
        // 这里简化处理
        return json.split("\"text\":\"")[1].split("\"")[0];
    }
    
    public static void main(String[] args) throws IOException {
        FunASRClient client = new FunASRClient();
        File audioFile = new File("audio.wav");
        String text = client.transcribe(audioFile);
        System.out.println("识别结果: " + text);
    }
}
```

---

### Go

```go
package main

import (
    "bytes"
    "encoding/json"
    "fmt"
    "io"
    "mime/multipart"
    "net/http"
    "os"
)

type TranscriptionResult struct {
    Text           string  `json:"text"`
    TextTn         string  `json:"text_tn"`
    Language       string  `json:"language"`
    Duration       float64 `json:"duration"`
    ProcessingTime float64 `json:"processing_time"`
}

func transcribe(filePath string) (*TranscriptionResult, error) {
    file, err := os.Open(filePath)
    if err != nil {
        return nil, err
    }
    defer file.Close()

    body := &bytes.Buffer{}
    writer := multipart.NewWriter(body)

    part, err := writer.CreateFormFile("file", filePath)
    if err != nil {
        return nil, err
    }
    _, err = io.Copy(part, file)
    if err != nil {
        return nil, err
    }

    writer.WriteField("language", "中文")
    writer.Close()

    resp, err := http.Post("http://localhost:8000/v1/transcriptions", 
        writer.FormDataContentType(), body)
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()

    respBody, err := io.ReadAll(resp.Body)
    if err != nil {
        return nil, err
    }

    var result TranscriptionResult
    err = json.Unmarshal(respBody, &result)
    if err != nil {
        return nil, err
    }

    return &result, nil
}

func main() {
    result, err := transcribe("audio.wav")
    if err != nil {
        fmt.Println("错误:", err)
        return
    }
    fmt.Println("识别结果:", result.Text)
}
```

---

## 常见问题

### 1. 服务启动失败

**问题:** `ModuleNotFoundError: No module named 'fastapi'`

**解决:**
```bash
pip install -r requirements.txt
```

### 2. CUDA 不可用

**问题:** `Torch not compiled with CUDA enabled`

**解决:** 使用 CPU 模式（默认配置）
```bash
# 或使用环境变量
set FUNASR_DEVICE=cpu
```

### 3. 文件上传失败

**问题:** `curl: (26) Failed to open/read local data from file`

**解决:** 确保文件路径正确，使用绝对路径
```bash
# 错误
-F "file=@audio.wav"

# 正确
-F "file=@D:\path\to\audio.wav"
```

### 4. 响应乱码

**问题:** 中文显示为乱码

**解决:** 确保终端使用 UTF-8 编码
```bash
# Windows
chcp 65001
```

### 5. 请求超时

**问题:** 长音频处理超时

**解决:** 
- 增加超时时间
- 启用 VAD 分段处理
- 设置 `FUNASR_USE_VAD=true`

### 6. 内存不足

**问题:** 处理大文件时内存溢出

**解决:**
- 减小并发请求数
- 分割长音频文件
- 使用 CPU 模式

---

## 支持的语言

### Fun-ASR-Nano-2512

| 语言类别 | 支持语言 |
|----------|----------|
| 主要语言 | 中文、英文、日文 |
| 中文方言 | 吴语、粤语、闽语、客家话、赣语、湘语、晋语 |
| 地方口音 | 河南、山西、湖北、四川、重庆、云南、贵州、广东、广西等 26 种 |

### Fun-ASR-MLT-Nano-2512

支持 31 种语言：韩语、越南语、印尼语、泰语、马来语、菲律宾语、阿拉伯语、印地语、保加利亚语、克罗地亚语、捷克语、丹麦语、荷兰语、爱沙尼亚语、芬兰语、希腊语、匈牙利语、爱尔兰语、拉脱维亚语、立陶宛语、马耳他语、波兰语、葡萄牙语、罗马尼亚语、斯洛伐克语、斯洛文尼亚语、瑞典语。

---

## 性能参考

| 音频时长 | CPU 处理时间 | GPU 处理时间 |
|----------|-------------|-------------|
| 5 秒 | ~2-3 秒 | ~0.5-1 秒 |
| 30 秒 | ~10-15 秒 | ~3-5 秒 |
| 60 秒 | ~20-30 秒 | ~6-10 秒 |

*实际性能取决于硬件配置和音频质量*

---

## 联系与支持

如有问题，请查看:
- API 文档：http://localhost:8000/docs
- 项目文档：./api/README.md
