"""
音频输出处理模块，负责播放音频
"""

import os
import tempfile
import sounddevice as sd
import soundfile as sf


class AudioOutput:
    """音频输出处理类"""
    
    def __init__(self):
        """初始化音频输出处理器"""
        self.temp_dir = tempfile.mkdtemp()
    
    def play_audio(self, audio_data, sample_rate=24000):
        """
        播放音频数据
        
        Args:
            audio_data (bytes): 音频数据
            sample_rate (int): 采样率
        """
        try:
            # 创建临时文件
            temp_file = os.path.join(self.temp_dir, "temp_audio.mp3")
            
            # 写入音频数据
            with open(temp_file, 'wb') as f:
                f.write(audio_data)
            
            # 读取并播放音频
            data, samplerate = sf.read(temp_file)
            sd.play(data, samplerate)
            sd.wait()  # 等待音频播放完成
            
            # 删除临时文件
            try:
                os.remove(temp_file)
            except:
                pass
                
            return True
        except Exception as e:
            print(f"播放音频时出错: {e}")
            return False
    
    def __del__(self):
        """清理资源"""
        try:
            # 清理临时目录
            for file in os.listdir(self.temp_dir):
                os.remove(os.path.join(self.temp_dir, file))
            os.rmdir(self.temp_dir)
        except:
            pass
