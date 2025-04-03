"""
日志配置模块，提供统一的日志设置
"""

import logging
import os
from datetime import datetime

# 创建logs目录（如果不存在）
logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

# 创建日志文件名，包含日期
log_file = os.path.join(logs_dir, f'voice_processor_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')

# 配置根日志记录器
def setup_logger():
    """设置并返回配置好的日志记录器"""
    # 创建日志记录器
    logger = logging.getLogger('voice_processor')
    logger.setLevel(logging.DEBUG)
    
    # 创建文件处理器
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # 创建格式化器
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # 添加处理器到日志记录器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# 获取日志记录器实例
logger = setup_logger()
