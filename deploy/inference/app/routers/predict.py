# deploy/inference/app/routers/predict.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from ...core.exceptions import PreprocessError, InferenceError
from ...utils.audio_utils import load_audio, resample_audio
from ..dependencies import predictor, preprocessor, config

router = APIRouter()

@router.post("/predict")
async def predict(file: UploadFile = File(...)):
    """
    音频分类预测接口
    """
    try:
        # 读取音频文件
        contents = await file.read()
        audio_data, orig_sr = load_audio(contents)
        
        # 重采样到目标采样率
        target_sr = config['preprocess']['sample_rate']
        if orig_sr != target_sr:
            audio_data = resample_audio(audio_data, orig_sr, target_sr)
        
        # 预处理
        input_tensor = preprocessor(audio_data)
        
        # 推理
        result = predictor.predict(input_tensor)
        
        return JSONResponse({
            "status": "success",
            "result": result
        })
        
    except PreprocessError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except InferenceError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")