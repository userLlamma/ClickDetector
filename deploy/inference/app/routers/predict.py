# routers/predict.py
from fastapi import APIRouter, UploadFile, File, HTTPException, Request, Form
from fastapi.responses import JSONResponse
from ...core.exceptions import PreprocessError, InferenceError
from ...utils.audio_utils import load_audio, resample_audio
from ..dependencies import predictor, preprocessor, config
import time
import logging
from typing import Optional

logger = logging.getLogger(__name__)
router = APIRouter()

def get_client_ip(request: Request) -> str:
    """获取客户端真实IP"""
    ip_headers = [
        'CF-Connecting-IP',
        'X-Forwarded-For',
        'X-Real-IP',
    ]
    
    for header in ip_headers:
        if header in request.headers:
            if header == 'X-Forwarded-For':
                return request.headers[header].split(',')[0].strip()
            return request.headers[header]
            
    return request.client.host

# 定义常量
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_AUDIO_TYPES = [
    'audio/wav',
    'audio/x-wav',
    'audio/mpeg',
    'audio/mp3'
]

async def validate_file(file: UploadFile):
    """验证上传文件"""
    # 检查文件类型
    if file.content_type not in ALLOWED_AUDIO_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file.content_type} not allowed. Allowed types: {ALLOWED_AUDIO_TYPES}"
        )
    
    # 获取文件大小（不读取文件内容）
    file_size = 0
    async for chunk in file.file:
        file_size += len(chunk)
        if file_size > MAX_FILE_SIZE:
            await file.file.seek(0)  # 重置文件指针
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds maximum limit of {MAX_FILE_SIZE/1024/1024}MB"
            )
    
    await file.file.seek(0)  # 重置文件指针以供后续读取
    
    logger.info(f"File validation passed: {file.filename}, size: {file_size}, type: {file.content_type}")


class StepTimer:
    def __init__(self):
        self.start_time = time.time()
        self.steps = {}
        self.current_step_start = self.start_time
        self.timing = {
            "server_receive_time": int(self.start_time * 1000)
        }

    def step(self, name: str):
        now = time.time()
        duration = (now - self.current_step_start) * 1000
        self.steps[name] = duration
        self.current_step_start = now
        return duration

    def total(self):
        return (time.time() - self.start_time) * 1000

    def get_report(self):
        # API返回只包含计算时间所需的timing信息
        return {
            "timing": {
                "server_receive_time": self.timing["server_receive_time"],
                "server_complete_time": int(time.time() * 1000),
                "client_start_time": self.timing.get("client_start_time")
            }
        }

    def get_detailed_metrics(self):
        # 计算真实的文件上传时间
        detailed_steps = self.steps.copy()
        if 'client_start_time' in self.timing:
            upload_time = self.timing['server_receive_time'] - self.timing['client_start_time']
            detailed_steps['network_upload'] = upload_time  # 真实的网络传输时间

        # 返回详细的性能指标，用于日志记录
        return {
            "total_ms": f"{self.total():.2f}",
            "total_with_upload": f"{(upload_time + self.total()):.2f}" if 'client_start_time' in self.timing else "unknown",
            "steps": {k: f"{v:.2f}ms" for k, v in detailed_steps.items()}
        }

@router.post("/predict")
async def predict(
    request: Request, 
    file: UploadFile = File(...),
    client_start_time: Optional[str] = Form(None),
):
    """音频分类预测接口"""
    timer = StepTimer()
    file_size = 0
    
    # 获取请求相关信息
    client_ip = get_client_ip(request)
    request_id = request.headers.get('X-Request-ID', '')
    
    try:
        # 记录客户端开始时间
        if client_start_time:
            timer.timing["client_start_time"] = int(client_start_time)
        
        # 文件验证
        validate_file(file)
        timer.step("file_validation")
        
        # 读取音频文件
        contents = await file.read()
        file_size = len(contents)
        timer.step("file_read")
        
        # 加载音频
        audio_data, orig_sr = load_audio(contents)
        timer.step("audio_load")
        
        # 重采样到目标采样率
        target_sr = config['preprocess']['sample_rate']
        if orig_sr != target_sr:
            audio_data = resample_audio(audio_data, orig_sr, target_sr)
        timer.step("resample")
        
        # 预处理
        input_tensor = preprocessor(audio_data)
        timer.step("preprocess")
        
        # 推理
        result = predictor.predict(input_tensor)
        timer.step("inference")
        
        # 获取详细性能指标
        detailed_metrics = timer.get_detailed_metrics()
        
        # 记录详细日志
        log_message = (
            f"Prediction completed - "
            f"Request ID: {request_id}, "
            f"Client IP: {client_ip}, "
            f"File size: {file_size/1024:.2f}KB, "
            f"Original SR: {orig_sr}Hz, "
            f"Backend processing time: {detailed_metrics['total_ms']}ms, "
        )
        
        if 'client_start_time' in timer.timing:
            log_message += f"Total time including upload: {detailed_metrics['total_with_upload']}ms, "
            
        log_message += f"Steps: {detailed_metrics['steps']}"
        
        logger.info(log_message)
        
        # API只返回简化的timing信息
        return JSONResponse({
            "status": "success",
            "result": result,
            "metrics": timer.get_report()
        })
        
    except (PreprocessError, InferenceError, Exception) as e:
        error_time = timer.total()
        error_type = type(e).__name__
        status_code = 400 if isinstance(e, PreprocessError) else 500
        
        logger.error(
            f"{error_type} after {error_time:.2f}ms - "
            f"Error: {str(e)}, "
            f"Client IP: {client_ip}, "
            f"Request ID: {request_id}, "
            f"Steps completed: {timer.steps}"
        )
        
        if isinstance(e, Exception) and not isinstance(e, (PreprocessError, InferenceError)):
            detail = f"Internal server error: {str(e)}"
        else:
            detail = str(e)
            
        raise HTTPException(status_code=status_code, detail=detail)