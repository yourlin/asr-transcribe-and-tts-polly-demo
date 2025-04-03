# AWS Voice Processing POC

这个项目是一个概念验证(POC)，展示如何使用AWS服务进行实时语音处理。项目使用AWS Transcribe进行流式语音转文本，并使用AWS Polly将文本转换回语音。

## 功能特点

- 从麦克风捕获实时语音输入
- 使用AWS Transcribe流式API进行实时语音转文本
- 自动识别说话人的语言（语言识别功能）
- 使用AWS Polly将转录文本转换为语音输出
- 无需在代码中硬编码AWS凭证（使用本地配置或IAM角色）

## 技术栈

- Python 3.8+
- boto3 (AWS SDK for Python)
- PyAudio (用于麦克风输入)
- AWS Transcribe
- AWS Polly

## 前提条件

1. 安装AWS CLI并配置凭证
2. Python 3.8或更高版本
3. 可用的麦克风设备
4. 适当的AWS IAM权限:
   - `transcribe:StartStreamTranscription`
   - `transcribe:StartStreamTranscriptionWebSocket`
   - `polly:SynthesizeSpeech`

## 安装

```bash
# 克隆仓库
git clone https://github.com/yourusername/aws-voice-processing-poc.git
cd aws-voice-processing-poc

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # 在Windows上使用: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

## 使用方法

1. 确保您的AWS凭证已正确配置（通过AWS CLI或环境变量）
2. 运行主程序:

```bash
python voice_processor.py
```

3. 对着麦克风说话
4. 程序将实时转录您的语音，并在您停止说话后通过扬声器播放转录后的文本

## 项目结构

```
aws-voice-processing-poc/
├── README.md                 # 项目文档
├── requirements.txt          # 项目依赖
├── voice_processor.py        # 主程序
├── audio_helpers/
│   ├── __init__.py
│   ├── mic_input.py          # 麦克风输入处理
│   └── audio_output.py       # 音频输出处理
└── aws_services/
    ├── __init__.py
    ├── transcribe_client.py  # AWS Transcribe客户端
    └── polly_client.py       # AWS Polly客户端
```

## 配置选项

可以通过修改`config.py`文件来调整以下配置:

- 音频采样率
- 音频格式
- Transcribe语言识别设置
- Polly语音选项

## 安全注意事项

- 本项目不在代码中包含AWS凭证
- 使用AWS最佳实践进行身份验证（本地配置文件或IAM角色）
- 确保IAM权限遵循最小权限原则

## 许可证

[MIT](LICENSE)

## 贡献

欢迎提交问题和拉取请求!
