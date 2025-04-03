"""
配置文件，包含项目的各种设置
"""

# 音频配置
SAMPLE_RATE = 16000  # 采样率 (Hz)
CHANNELS = 1  # 单声道
CHUNK_SIZE = 1024  # 每个音频块的大小
FORMAT = 'pcm'  # 音频格式

# AWS Transcribe配置
TRANSCRIBE_REGION = 'us-east-1'  # AWS区域
PREFERRED_LANGUAGE = 'zh-CN'  # 首选语言（中文）
LANGUAGE_OPTIONS = ['zh-CN', 'en-US', 'ja-JP', 'ko-KR', 'fr-FR', 'de-DE', 'es-ES']  # 支持的语言
IDENTIFY_LANGUAGE = True  # 是否自动识别语言

# AWS Polly配置
POLLY_REGION = 'us-east-1'  # AWS区域
POLLY_VOICE_ID = {
    'zh-CN': 'Zhiyu',
    'en-US': 'Joanna',
    'ja-JP': 'Takumi',
    'ko-KR': 'Seoyeon',
    'fr-FR': 'Léa',
    'de-DE': 'Vicki',
    'es-ES': 'Lucia'
}  # 各语言的默认语音
POLLY_OUTPUT_FORMAT = 'mp3'  # 输出格式
