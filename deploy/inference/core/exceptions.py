class InferenceError(Exception):
    """推理过程中的错误"""
    pass

class PreprocessError(Exception):
    """预处理过程中的错误"""
    pass

class ModelLoadError(Exception):
    """模型加载错误"""
    pass