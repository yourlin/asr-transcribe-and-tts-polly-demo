"""
AWS Polly客户端模块，负责与AWS Polly服务交互
支持自动识别文本语言，默认使用中文语音
"""

import re
import traceback

import boto3

from config import POLLY_OUTPUT_FORMAT, POLLY_REGION, POLLY_VOICE_ID, PREFERRED_LANGUAGE


class PollyClient:
    """AWS Polly客户端类"""

    def __init__(self):
        """初始化Polly客户端"""
        self.client = boto3.client("polly", region_name=POLLY_REGION)
        self.comprehend = boto3.client("comprehend", region_name=POLLY_REGION)
        # 默认语言设置为中文
        self.default_language = PREFERRED_LANGUAGE

    def detect_language(self, text):
        """
        使用AWS Comprehend检测文本语言

        Args:
            text (str): 要检测的文本

        Returns:
            str: 语言代码，例如'en-US'、'zh-CN'等
        """
        try:
            if not text or len(text.strip()) == 0:
                return self.default_language

            # 调用Comprehend API
            response = self.comprehend.detect_dominant_language(Text=text)

            # 获取置信度最高的语言
            languages = response.get("Languages", [])
            if languages:
                dominant_language = max(languages, key=lambda x: x["Score"])
                lang_code = dominant_language["LanguageCode"]

                # 将语言代码映射到Polly支持的格式
                lang_mapping = {
                    "zh": "zh-CN",
                    "en": "en-US",
                    "ja": "ja-JP",
                    "ko": "ko-KR",
                    "fr": "fr-FR",
                    "de": "de-DE",
                    "es": "es-ES",
                }

                return lang_mapping.get(lang_code, self.default_language)
            else:
                return self.default_language
        except Exception as e:
            print(f"检测语言时出错: {e}")
            traceback.print_exc()
            return self.default_language  # 默认返回中文

    def synthesize_speech(self, text, language_code=None):
        """
        将文本转换为语音，如果未提供语言代码，则自动检测

        Args:
            text (str): 要转换的文本
            language_code (str, optional): 语言代码，例如'en-US'、'zh-CN'等

        Returns:
            bytes: 音频数据
        """
        try:
            # 如果未提供语言代码，则自动检测
            if not language_code:
                language_code = self.detect_language(text)
                print(f"自动检测到的语言: {language_code}")

            # 确定使用的语音ID
            voice_id = POLLY_VOICE_ID.get(
                language_code, POLLY_VOICE_ID.get(self.default_language)
            )

            # 检查语言和文本是否匹配
            # 例如，如果检测到英语但使用中文语音，可能需要调整
            if language_code == "en-US" and self._contains_chinese(text):
                print("警告: 检测到英语语言代码，但文本包含中文字符。使用中文语音。")
                language_code = "zh-CN"
                voice_id = POLLY_VOICE_ID.get("zh-CN")

            print(f"使用语音ID: {voice_id} 合成语言: {language_code}")

            # 调用Polly API
            response = self.client.synthesize_speech(
                Text=text,
                OutputFormat=POLLY_OUTPUT_FORMAT,
                VoiceId=voice_id,
                Engine="neural",  # 使用神经引擎获得更好的语音质量
            )

            # 返回音频数据
            if "AudioStream" in response:
                return response["AudioStream"].read()
            else:
                print("Polly API未返回音频流")
                return None
        except Exception as e:
            print(f"合成语音时出错: {e}")
            traceback.print_exc()
            return None

    def _contains_chinese(self, text):
        """
        检查文本是否包含中文字符

        Args:
            text (str): 要检查的文本

        Returns:
            bool: 如果包含中文字符则返回True
        """
        # 中文字符的Unicode范围
        chinese_pattern = re.compile(r"[\u4e00-\u9fff]")
        return bool(chinese_pattern.search(text))
