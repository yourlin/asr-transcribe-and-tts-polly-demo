"""
AWS Transcribe客户端模块，负责与AWS Transcribe服务交互
使用Amazon Transcribe Streaming SDK
"""

import asyncio
import queue
import threading
import traceback
from config import TRANSCRIBE_REGION, LANGUAGE_OPTIONS, PREFERRED_LANGUAGE, IDENTIFY_LANGUAGE

from amazon_transcribe.client import TranscribeStreamingClient
from amazon_transcribe.handlers import TranscriptResultStreamHandler
from amazon_transcribe.model import TranscriptEvent


class TranscribeHandler(TranscriptResultStreamHandler):
    """处理Transcribe转录结果的处理器"""
    
    def __init__(self, output_stream, callback=None):
        """
        初始化处理器
        
        Args:
            output_stream: Transcribe输出流
            callback: 接收转录结果的回调函数
        """
        super().__init__(output_stream)
        self.transcript_result = ""
        self.identified_language = None
        self.is_final = False
        self.callback = callback
    
    async def handle_transcript_event(self, transcript_event: TranscriptEvent):
        """处理转录事件"""
        results = transcript_event.transcript.results
        
        for result in results:
            # 检查是否有语言识别结果
            if hasattr(result, 'language_identification') and result.language_identification:
                languages = result.language_identification.languages
                if languages and len(languages) > 0:
                    # 获取置信度最高的语言
                    top_language = max(languages, key=lambda x: x.score)
                    self.identified_language = top_language.language_code
                    print(f"识别到的语言: {self.identified_language}")
            
            # 获取转录文本
            for alt in result.alternatives:
                transcript = alt.transcript
                
                # 检查是否是最终结果
                if not result.is_partial:
                    self.transcript_result = transcript
                    self.is_final = True
                    print(f"最终转录结果: {transcript}")
                    
                    # 调用回调函数
                    if self.callback:
                        self.callback(transcript, self.identified_language)
                else:
                    print(f"部分转录结果: {transcript}")


class TranscribeClient:
    """AWS Transcribe客户端类"""
    
    def __init__(self):
        """初始化Transcribe客户端"""
        self.client = None
        self.stream = None
        self.handler = None
        self.audio_queue = None
        self.stream_thread = None
        self.stop_thread = False
        self.transcript_result = ""
        self.identified_language = None
    
    async def _mic_stream(self):
        """
        从音频队列中获取音频数据
        
        Yields:
            tuple: (音频数据, 状态)
        """
        loop = asyncio.get_event_loop()
        
        while not self.stop_thread:
            try:
                if not self.audio_queue.empty():
                    audio_chunk = self.audio_queue.get()
                    if audio_chunk:
                        yield audio_chunk, None
                    self.audio_queue.task_done()
                else:
                    await asyncio.sleep(0.01)
            except Exception as e:
                print(f"从音频队列获取数据时出错: {e}")
                break
    
    async def _write_chunks(self):
        """将音频块发送到Transcribe流"""
        try:
            async for chunk, status in self._mic_stream():
                await self.stream.input_stream.send_audio_event(audio_chunk=chunk)
            
            # 结束流
            await self.stream.input_stream.end_stream()
        except Exception as e:
            print(f"发送音频数据时出错: {e}")
            traceback.print_exc()
    
    async def _run_transcription(self):
        """运行转录流程"""
        try:
            # 创建客户端
            self.client = TranscribeStreamingClient(region=TRANSCRIBE_REGION)
            
            # 启动转录流
            # 根据最新的SDK版本调整参数
            params = {
                "language_code": PREFERRED_LANGUAGE,  # 默认使用中文
                "media_sample_rate_hz": 16000,
                "media_encoding": "pcm",
            }
            
            # 添加可选参数
            if hasattr(self.client, 'start_stream_transcription') and callable(getattr(self.client, 'start_stream_transcription')):
                # 检查方法签名以确定支持的参数
                import inspect
                sig = inspect.signature(self.client.start_stream_transcription)
                param_names = [param for param in sig.parameters]
                
                # 添加稳定性参数（如果支持）
                if 'enable_partial_results_stabilization' in param_names:
                    params["enable_partial_results_stabilization"] = True
                if 'partial_results_stability' in param_names:
                    params["partial_results_stability"] = "low"
                
                # 添加语言识别参数（如果支持）
                if IDENTIFY_LANGUAGE:
                    if 'identify_language' in param_names:
                        params["identify_language"] = True
                        if 'language_options' in param_names:
                            params["language_options"] = LANGUAGE_OPTIONS
                    elif 'preferred_language' in param_names:
                        params["preferred_language"] = PREFERRED_LANGUAGE
                        if 'language_options' in param_names:
                            params["language_options"] = LANGUAGE_OPTIONS
                        if 'show_language_identification' in param_names:
                            params["show_language_identification"] = True
            
            print(f"使用以下参数启动转录: {params}")
            self.stream = await self.client.start_stream_transcription(**params)
            
            # 创建处理器
            self.handler = TranscribeHandler(
                self.stream.output_stream,
                callback=self._on_transcription_result
            )
            
            # 运行转录和处理
            await asyncio.gather(self._write_chunks(), self.handler.handle_events())
        except Exception as e:
            print(f"运行转录时出错: {e}")
            traceback.print_exc()
    
    def _on_transcription_result(self, transcript, language):
        """转录结果回调"""
        self.transcript_result = transcript
        self.identified_language = language
    
    def _transcription_thread(self):
        """转录线程函数"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(self._run_transcription())
        except Exception as e:
            print(f"转录线程出错: {e}")
            traceback.print_exc()
        finally:
            loop.close()
    
    def start_streaming(self):
        """开始流式转录"""
        # 重置状态
        self.transcript_result = ""
        self.identified_language = None
        self.stop_thread = False
        self.audio_queue = queue.Queue()
        
        # 启动转录线程
        self.stream_thread = threading.Thread(target=self._transcription_thread)
        self.stream_thread.daemon = True
        self.stream_thread.start()
    
    def send_audio_chunk(self, audio_chunk):
        """发送音频块到Transcribe服务"""
        if not self.stream_thread or not self.stream_thread.is_alive() or not self.audio_queue:
            return False
        
        # 将音频块放入队列
        self.audio_queue.put(audio_chunk)
        return True
    
    def stop_streaming(self):
        """停止流式转录"""
        self.stop_thread = True
        
        # 等待转录线程结束
        if self.stream_thread and self.stream_thread.is_alive():
            self.stream_thread.join(timeout=5)
        
        return self.transcript_result, self.identified_language
