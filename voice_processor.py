"""
主程序，协调麦克风输入、Transcribe转录和Polly语音合成
"""

import time
import signal
import sys
import numpy as np
from audio_helpers.mic_input import MicrophoneInput
from audio_helpers.audio_output import AudioOutput
from aws_services.transcribe_client import TranscribeClient
from aws_services.polly_client import PollyClient


class VoiceProcessor:
    """语音处理器类，协调整个流程"""
    
    def __init__(self):
        """初始化语音处理器"""
        self.mic_input = MicrophoneInput()
        self.audio_output = AudioOutput()
        self.transcribe_client = TranscribeClient()
        self.polly_client = PollyClient()
        self.running = False
    
    def start(self):
        """启动语音处理"""
        self.running = True
        
        # 注册信号处理器，以便优雅地退出
        signal.signal(signal.SIGINT, self._signal_handler)
        
        print("=== AWS语音处理POC ===")
        print("按Ctrl+C停止程序")
        
        while self.running:
            try:
                # 开始录音和转录
                print("\n准备好了吗？开始说话...")
                self.mic_input.start_recording()
                self.transcribe_client.start_streaming()
                
                # 处理音频块
                silence_counter = 0
                max_silence = 50  # 约5秒的静音
                while silence_counter < max_silence and self.running:
                    audio_chunk = self.mic_input.read_chunk()
                    
                    if audio_chunk:
                        # 检查是否为静音
                        if self._is_silence(audio_chunk):
                            silence_counter += 1
                        else:
                            silence_counter = 0
                        
                        # 发送到Transcribe
                        self.transcribe_client.send_audio_chunk(audio_chunk)
                    
                    time.sleep(0.01)
                
                # 停止录音和转录
                self.mic_input.stop_recording()
                transcript, language = self.transcribe_client.stop_streaming()
                
                # 如果有转录结果，则使用Polly合成语音
                if transcript and self.running:
                    print(f"\n转录结果 ({language if language else 'en-US'}): {transcript}")
                    
                    # 合成语音
                    print("正在合成语音...")
                    audio_data = self.polly_client.synthesize_speech(transcript, language if language else 'en-US')
                    
                    if audio_data:
                        # 播放合成的语音
                        print("播放合成的语音...")
                        self.audio_output.play_audio(audio_data)
                    else:
                        print("语音合成失败")
                else:
                    print("未检测到语音或转录失败")
                
                if self.running:
                    # 询问是否继续
                    print("\n按Enter继续，或按Ctrl+C退出")
                    input()
                
            except Exception as e:
                print(f"处理过程中出错: {e}")
                import traceback
                traceback.print_exc()
                self.running = False
    
    def _is_silence(self, audio_chunk, threshold=500):
        """
        检测音频块是否为静音
        
        Args:
            audio_chunk (bytes): 音频数据
            threshold (int): 静音阈值
        
        Returns:
            bool: 如果是静音则返回True
        """
        # 将字节转换为16位整数数组
        audio_array = np.frombuffer(audio_chunk, dtype=np.int16)
        
        # 计算音量
        volume = np.abs(audio_array).mean()
        
        return volume < threshold
    
    def _signal_handler(self, sig, frame):
        """处理Ctrl+C信号"""
        print("\n正在停止程序...")
        self.running = False
        self.mic_input.stop_recording()
        sys.exit(0)


if __name__ == "__main__":
    processor = VoiceProcessor()
    processor.start()
