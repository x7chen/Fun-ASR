# Fun-ASR RESTful API 使用指南

## 目录

- [快速开始](#快速开始)
- [API 接口](#api-接口)
- [请求参数](#请求参数)
- [响应格式](#响应格式)
- [使用示例](#使用示例)
- [配置说明](#配置说明)

---

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动服务

**Linux/Mac:**
```bash
bash start_api.sh
```

**Windows:**
```bash
start_api.bat
```

**或直接运行:**
```bash
python -m uvicorn api.server:app --host 0.0.0.0 --port 8000
```

### 3. 访问文档

服务启动后，访问以下地址查看 API 文档:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## API 接口

### 健康检查

```http
GET /health
```

检查服务运行状态和模型加载情况。

**响应示例:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "device": "cuda:0",
  "version": "1.0.0"
}
```

---

### 语音转写 (表单参数)

```http
POST /v1/transcriptions
Content-Type: multipart/form-data
```

**参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file | File | 是 | 音频文件 (wav, mp3, flac, m4a, ogg, webm) |
| language | string | 否 | 识别语言 (中文/英文/日文等) |
| itn | boolean | 否 | 是否进行文本逆规整 |
| hotwords | string | 否 | 热词列表，逗号分隔 |
| return_timestamps | boolean | 否 | 是否返回时间戳 |

**cURL 示例:**
```bash
curl -X POST "http://localhost:8000/v1/transcriptions" \
  -F "file=@audio.wav" \
  -F "language=中文" \
  -F "itn=true" \
  -F "hotwords=开放时间，预约"
```

---

### 语音转写 (JSON 参数)

```http
POST /v1/transcriptions/json
Content-Type: multipart/form-data
```

适合需要复杂配置的场景。

**cURL 示例:**
```bash
curl -X POST "http://localhost:8000/v1/transcriptions/json" \
  -F "file=@audio.wav" \
  -F 'request={
    "language": "中文",
    "itn": true,
    "hotwords": ["开放时间", "预约"],
    "return_timestamps": false
  }'
```

---

### 语音转写 (URL 方式)

```http
POST /v1/transcriptions/url?url=<音频 URL>
```

通过音频文件 URL 进行识别。

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
curl -X POST "http://localhost:8000/v1/transcriptions/url?url=https://example.com/audio.wav"
```

---

### 获取模型信息

```http
GET /v1/models
```

获取支持的模型和语言列表。

**响应示例:**
```json
{
  "models": [
    {
      "name": "Fun-ASR-Nano-2512",
      "description": "端到端语音识别大模型，支持 31 种语言",
      "languages": ["中文", "英文", "日文", ...],
      "features": ["7 大方言支持", "26 种地方口音", ...]
    }
  ],
  "current_model": "FunAudioLLM/Fun-ASR-Nano-2512",
  "device": "cuda:0"
}
```

---

## 响应格式

### 成功响应

```json
{
  "text": "识别出的文本内容",
  "text_tn": "规整后的文本",
  "language": "中文",
  "timestamps": null,
  "ctc_text": "CTC 解码结果",
  "duration": 5.2,
  "processing_time": 1.3
}
```

### 带时间戳的响应

```json
{
  "text": "识别出的文本",
  "timestamps": [
    {
      "token": "识",
      "start_time": 0.12,
      "end_time": 0.18
    },
    {
      "token": "别",
      "start_time": 0.18,
      "end_time": 0.24
    }
  ],
  "duration": 5.2,
  "processing_time": 1.3
}
```

### 错误响应

```json
{
  "error": "ValidationError",
  "message": "不支持的音频格式：avi。支持的格式：wav, mp3, flac, m4a, ogg, webm"
}
```

---

## 使用示例

### Python 客户端

```python
import requests

# 上传音频文件
def transcribe_audio(audio_path: str) -> str:
    url = "http://localhost:8000/v1/transcriptions"
    
    with open(audio_path, "rb") as f:
        files = {"file": f}
        data = {
            "language": "中文",
            "itn": "true",
            "hotwords": "开放时间，预约"
        }
        response = requests.post(url, files=files, data=data)
    
    result = response.json()
    return result["text"]

# 使用示例
text = transcribe_audio("audio.wav")
print(f"识别结果：{text}")
```

### JavaScript/Fetch

```javascript
async function transcribeAudio(audioFile) {
  const formData = new FormData();
  formData.append('file', audioFile);
  formData.append('language', '中文');
  formData.append('itn', 'true');
  
  const response = await fetch('http://localhost:8000/v1/transcriptions', {
    method: 'POST',
    body: formData
  });
  
  const result = await response.json();
  return result.text;
}

// 使用示例
const fileInput = document.querySelector('input[type="file"]');
const text = await transcribeAudio(fileInput.files[0]);
console.log(`识别结果：${text}`);
```

### cURL

```bash
# 基本转写
curl -X POST "http://localhost:8000/v1/transcriptions" \
  -F "file=@audio.wav"

# 带参数转写
curl -X POST "http://localhost:8000/v1/transcriptions" \
  -F "file=@audio.wav" \
  -F "language=英文" \
  -F "itn=true"

# 获取时间戳
curl -X POST "http://localhost:8000/v1/transcriptions" \
  -F "file=@audio.wav" \
  -F "return_timestamps=true"
```

---

## 配置说明

### 环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `FUNASR_MODEL_DIR` | FunAudioLLM/Fun-ASR-Nano-2512 | 模型目录 |
| `FUNASR_DEVICE` | cuda:0 | 运行设备 (cuda:0/cpu) |
| `FUNASR_HOST` | 0.0.0.0 | 服务监听地址 |
| `FUNASR_PORT` | 8000 | 服务端口 |
| `FUNASR_LANGUAGE` | 中文 | 默认识别语言 |
| `FUNASR_ITN` | true | 默认是否进行文本逆规整 |
| `FUNASR_MAX_DURATION` | 300 | 最大音频时长 (秒) |
| `FUNASR_MAX_FILE_SIZE` | 52428800 | 最大文件大小 (字节，默认 50MB) |
| `FUNASR_USE_VAD` | false | 是否使用 VAD |
| `FUNASR_VAD_MODEL` | fsmn-vad | VAD 模型名称 |
| `FUNASR_VAD_MAX_SEGMENT` | 30000 | VAD 最大分段时长 (毫秒) |

### 配置示例

```bash
# 使用 CPU 运行
export FUNASR_DEVICE=cpu

# 修改端口
export FUNASR_PORT=8080

# 启用 VAD
export FUNASR_USE_VAD=true

# 启动服务
python -m uvicorn api.server:app --host 0.0.0.0 --port 8080
```

---

## 支持的语言

### Fun-ASR-Nano-2512

- **主要语言**: 中文、英文、日文
- **中文方言**: 吴语、粤语、闽语、客家话、赣语、湘语、晋语
- **地方口音**: 河南、山西、湖北、四川、重庆、云南、贵州、广东、广西等 26 种

### Fun-ASR-MLT-Nano-2512

支持 31 种语言：韩语、越南语、印尼语、泰语、马来语、菲律宾语、阿拉伯语、印地语、保加利亚语、克罗地亚语、捷克语、丹麦语、荷兰语、爱沙尼亚语、芬兰语、希腊语、匈牙利语、爱尔兰语、拉脱维亚语、立陶宛语、马耳他语、波兰语、葡萄牙语、罗马尼亚语、斯洛伐克语、斯洛文尼亚语、瑞典语等。

---

## 性能优化建议

1. **使用 GPU**: 确保安装 CUDA 并设置 `FUNASR_DEVICE=cuda:0`
2. **启用 VAD**: 对于长音频，启用 VAD 可以提升识别准确率
3. **批量处理**: 对于多个音频文件，建议使用并发请求
4. **热词优化**: 针对特定领域添加热词可以提升专业术语识别率

---

## 故障排查

### 模型加载失败

检查网络连接，确保能够访问 ModelScope 或 HuggingFace 下载模型。

### CUDA out of memory

- 减小并发请求数
- 使用 CPU 模式：`export FUNASR_DEVICE=cpu`
- 使用更小的模型

### 音频文件过大

- 检查 `FUNASR_MAX_FILE_SIZE` 配置
- 压缩音频文件或分段处理
