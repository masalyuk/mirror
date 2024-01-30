import json

MODEL_FILE_JSON = "models.json"

class ModelCollection:
    def __init__(self):
        with open(MODEL_FILE_JSON, 'r') as f:
            data = json.load(f)
 
        self.models = []
        self.default_settings = {
            "denoise": 0.35,  # Default denoise value
            "lora_model": 1.0,  # Default lora_model value
            "lora_clip": 1.0,  # Default lora_clip value
            "promt": ""  # Default prompt value
        }
        
        for model_data in data.get('models', []):
            name = model_data.get('name')
            settings = model_data.get('settings', {})
            
            # Fill in missing settings with default values
            for key, default_value in self.default_settings.items():
                settings[key] = settings.get(key, default_value)
            
            model = {"name": name, "settings": settings}
            self.models.append(model)
    
    def find_index_by_name(self, name):
        for index, model in enumerate(self.models):
            if model["name"] == name:
                return index
        
        return -1

    def get_model(self, model_name):
        return self.models.get(model_name)
    
    def get_model_names(self):
        return list(self.models.keys())
    
    def get_models(self):
        return self.models