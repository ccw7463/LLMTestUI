from . import *


SYSTEM_PROMPT = "You're a helpful assistant"

IPConfig = ConfigDict()
IPConfig.INFERENCE_SERVER = "http://192.168.1.20"
IPConfig.REDIS = IPConfig.INFERENCE_SERVER.replace("http://","redis://")

URLConfig = ConfigDict()
URLConfig.REDIS_URL = f"{IPConfig.REDIS}:6379/0"

ModelConfig = ConfigDict()
ModelConfig.MODEL_1_NAME = "Qwen/Qwen2-7B-Instruct"
ModelConfig.MODEL_2_NAME = "meta-llama/Meta-Llama-3.1-8B-Instruct"
ModelConfig.MODEL_3_NAME = "google/gemma-2-9b-it"
ModelConfig.MODEL_LST = [ModelConfig.MODEL_1_NAME,
                         ModelConfig.MODEL_2_NAME,
                         ModelConfig.MODEL_3_NAME]

class ModelConfigFactory:
    @staticmethod
    def get_config(model_name: str):
        if model_name == ModelConfig.MODEL_1_NAME:
            return ModelConfigFactory.Model1()
        elif model_name == ModelConfig.MODEL_2_NAME:
            return ModelConfigFactory.Model2()
        elif model_name == ModelConfig.MODEL_3_NAME:
            return ModelConfigFactory.Model3()
        else:
            raise ValueError(f"Unknown model: {model_name}")
        
    class Model1:
        MODEL_NAME = ModelConfig.MODEL_1_NAME
        PORT = 1331
        ENDPOINT = f"{IPConfig.INFERENCE_SERVER}:{PORT}"

    class Model2:
        MODEL_NAME = ModelConfig.MODEL_2_NAME
        PORT = 1332
        ENDPOINT = f"{IPConfig.INFERENCE_SERVER}:{PORT}"

    class Model3:
        MODEL_NAME = ModelConfig.MODEL_3_NAME
        PORT = 1333
        ENDPOINT = f"{IPConfig.INFERENCE_SERVER}:{PORT}"





