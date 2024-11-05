# routers/predict.py
from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from fastapi.responses import JSONResponse
from ...core.exceptions import PreprocessError, InferenceError
from ...utils.audio_utils import load_audio, resample_audio
from ..dependencies import predictor, preprocessor, config
import time
import logging

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

class StepTimer:
    def __init__(self):
        self.start_time = time.time()
        self.steps = {}
        self.current_step_start = self.start_time

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
            "total_ms": f"{self.total():.2f}",
            "steps": {k: f"{v:.2f}ms" for k, v in self.steps.items()}
        }

@router.post("/predict")
async def predict(request: Request, file: UploadFile = File(...)):  # 修改了参数顺序
    """音频分类预测接口"""
    timer = StepTimer()
    file_size = 0
    
    # 获取请求相关信息
    client_ip = get_client_ip(request)
    user_agent = request.headers.get('User-Agent', 'Unknown')
    request_id = request.headers.get('X-Request-ID', '')
    
    try:
        # 读取音频文件
        contents = await file.read()
        file_size = len(contents)
        timer.step("file_upload")
        
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
        inference_time = timer.step("inference")
        
        # 记录性能日志
        perf_report = timer.get_report()
        logger.info(
            f"Prediction completed:\n"
            f"Request ID: {request_id}\n"
            f"Client IP: {client_ip}\n"
            f"User Agent: {user_agent}\n"
            f"File size: {file_size/1024:.2f}KB\n"
            f"Original SR: {orig_sr}Hz\n"
            f"CloudFront-Viewer-Country: {request.headers.get('CloudFront-Viewer-Country', 'Unknown')}\n"
            f"Performance metrics:\n"
            f"{perf_report}"
        )
        
        return JSONResponse({
            "status": "success",
            "result": result,
            "metrics": {
                "processing_time": perf_report
            }
        })
        
    except PreprocessError as e:
        logger.error(
            f"Preprocessing error after {timer.total():.2f}ms: {str(e)}\n"
            f"Client IP: {client_ip}\n"
            f"Request ID: {request_id}"
        )
        raise HTTPException(status_code=400, detail=str(e))
    except InferenceError as e:
        logger.error(
            f"Inference error after {timer.total():.2f}ms: {str(e)}\n"
            f"Client IP: {client_ip}\n"
            f"Request ID: {request_id}"
        )
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(
            f"Internal error after {timer.total():.2f}ms: {str(e)}\n"
            f"Client IP: {client_ip}\n"
            f"Request ID: {request_id}"
        )
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")