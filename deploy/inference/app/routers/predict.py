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
    """
    获取客户端真实IP
    兼容:
    1. CDN场景 (CloudFront/其他CDN)
    2. 直接访问场景
    3. 反向代理场景
    """
    # 1. 检查X-Forwarded-For
    if 'X-Forwarded-For' in request.headers:
        ips = [ip.strip() for ip in request.headers['X-Forwarded-For'].split(',')]
        if ips:
            return ips[0]  # 永远取最左侧IP (客户端IP)
    
    # 2. 检查其他可能的头部
    for header in ['X-Real-IP', 'CF-Connecting-IP']:
        if header in request.headers:
            return request.headers[header].strip()
    
    # 3. 降级到直接连接的IP
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
    
    # 使用异步读取文件内容
    file_content = await file.read()  # 异步读取文件内容
    file_size = len(file_content)
    
    # 检查文件大小
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds maximum limit of {MAX_FILE_SIZE/1024/1024}MB"
        )
    
    # 重置文件指针以供后续读取
    file.file.seek(0)

    logger.info(f"File validation passed: {file.filename}, size: {file_size}, type: {file.content_type}")

    # 返回文件大小
    return file_size
    
    


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
        return {
            "timing": {
                "server_receive_time": self.timing["server_receive_time"],
                "server_complete_time": int(time.time() * 1000),
                "client_start_time": self.timing.get("client_start_time")
            }
        }

    def get_detailed_metrics(self):
        detailed_steps = self.steps.copy()
        
        if 'client_start_time' in self.timing:
            # 直接使用服务器接收时间减去客户端开始时间
            upload_time = self.timing['server_receive_time'] - self.timing['client_start_time']
            
            if upload_time < 0:
                logger.warning(f"Negative upload time detected: {upload_time}ms")
                upload_time = 0
                
            detailed_steps['network_upload'] = upload_time
        
        backend_time = self.total()
        total_with_upload = backend_time
        if 'network_upload' in detailed_steps:
            total_with_upload = detailed_steps['network_upload'] + backend_time

        return {
            "total_ms": f"{backend_time:.2f}",
            "total_with_upload": f"{total_with_upload:.2f}",
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
        await validate_file(file)
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
        
        # 返回结果
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
