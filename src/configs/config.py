from . import *


system_prompt = "You're a helpful assistant"

IPConfig = ConfigDict()
IPConfig.INFERENCE_SERVER = "http://192.168.1.20"
IPConfig.REDIS = IPConfig.INFERENCE_SERVER.replace("http://","redis://")

URLConfig = ConfigDict()
URLConfig.REDIS_URL = f"{IPConfig.REDIS}:6379/0"

ModelConfig = ConfigDict()
ModelConfig.model_1_name = "microsoft/phi-4"
# ModelConfig.model_1_name = "Qwen/Qwen2-7B-Instruct"
ModelConfig.model_2_name = "meta-llama/Meta-Llama-3.1-8B-Instruct"
ModelConfig.model_3_name = "google/gemma-2-9b-it"
ModelConfig.model_lst = [ModelConfig.model_1_name,
                         ModelConfig.model_2_name,
                         ModelConfig.model_3_name]

class ModelConfigFactory:
    @staticmethod
    def get_config(model_name: str):
        if model_name == ModelConfig.model_1_name:
            return ModelConfigFactory.Model1()
        elif model_name == ModelConfig.model_2_name:
            return ModelConfigFactory.Model2()
        elif model_name == ModelConfig.model_3_name:
            return ModelConfigFactory.Model3()
        else:
            raise ValueError(f"Unknown model: {model_name}")
        
    class Model1:
        MODEL_NAME = ModelConfig.model_1_name
        PORT = 1331
        ENDPOINT = f"{IPConfig.INFERENCE_SERVER}:{PORT}"

    class Model2:
        MODEL_NAME = ModelConfig.model_2_name
        PORT = 1332
        ENDPOINT = f"{IPConfig.INFERENCE_SERVER}:{PORT}"

    class Model3:
        MODEL_NAME = ModelConfig.model_3_name
        PORT = 1333
        ENDPOINT = f"{IPConfig.INFERENCE_SERVER}:{PORT}"


from importlib.resources import files
PATHES = {
    "log": str(files("log")),
    "scripts": str(files("scripts")),
    "configs": str(files("configs")),
    "modules": str(files("modules")),
    "utils": str(files("utils")),
    "unittests": str(files("unittests")),
    "src": str(files("src"))
}