"""
麦克风输入处理模块，负责从麦克风捕获音频并进行预处理
"""

import pyaudio
import numpy as np
from config import SAMPLE_RATE, CHANNELS, CHUNK_SIZE, FORMAT


class MicrophoneInput:
    """麦克风输入处理类"""
    
    def __init__(self):
        """初始化麦克风输入处理器"""
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.is_recording = False
    
    def start_recording(self):
        """开始录音"""
        if self.stream is not None:
            self.stop_recording()
        
        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=CHANNELS,
            rate=SAMPLE_RATE,
            input=True,
            frames_per_buffer=CHUNK_SIZE
        )
        self.is_recording = True
        print("开始录音...")
    
    def stop_recording(self):
        """停止录音"""
        if self.stream is not None:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
            self.is_recording = False
            print("停止录音")
    
    def read_chunk(self):
        """读取一个音频块"""
        if not self.is_recording or self.stream is None:
            return None
        
        try:
            data = self.stream.read(CHUNK_SIZE, exception_on_overflow=False)
            return data
        except Exception as e:
            print(f"读取音频时出错: {e}")
            return None
    
    def __del__(self):
        """清理资源"""
        self.stop_recording()
        if self.audio:
            self.audio.terminate()
