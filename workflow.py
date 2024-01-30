import json
import websocket
import urllib.request
import urllib.parse
import uuid
import time

# JSON Field NAME
_INPUTS_ = "inputs"
_CLASS_TYPE_ = "class_type"
_META_ = "_meta"
_TITLE_ = "title"
# WORKFLOW TYPES
_KSAMPLER_        = "KSampler"
_PROMT_           = "CLIPTextEncode"
_SAVE_IMG_        = "SaveImagetoPath"
_LOAD_IMG_        = "LoadWebcamImage"
_UPSCALE_         = "ImageUpscaleWithModel"
_VAE_DECODE_      = "VAEDecode"
_LORA_LOAD_       = "LoraLoader"
_CHECK_POINT_LOAD = "CheckpointLoaderSimple"

class Workflow:
    def __init__(self, file, server_addr):
        self.wf = json.load(file)
        self.server_address = server_addr
        self.ws = websocket.WebSocket()

        client_id = str(uuid.uuid4())
        self.ws.connect("ws://{}/ws?clientId={}".format(self.server_address, client_id))

    def queue_prompt(self):
        p = {"prompt": self.wf}
        data = json.dumps(p).encode('utf-8')
        req =  urllib.request.Request("http://{}/prompt".format(self.server_address), data=data)
        return json.loads(urllib.request.urlopen(req).read())

    def get_work_flow(self):
        return self.wf

    def get_history(self, prompt_id):
        with urllib.request.urlopen("http://{}/history/{}".format(self.server_address, prompt_id)) as response:
            return json.loads(response.read())

    def send_and_wait_result(self):
        prompt_id = self.queue_prompt()['prompt_id']
        while True:
            if self.get_history(prompt_id).get(prompt_id) is not None:
                break
            time.sleep(0.01)# to release port
 

    def get_node_number(self, type, title=None):
        for key, value in self.wf.items():
            if value[_CLASS_TYPE_] == type:
                if title is not None:
                    if value[_META_][_TITLE_] == title:
                        return key
                else:
                    return key

        print("Not found:" + type)
        return None
        
    def get_node_inputs(self, type, title=None):
        for key, value in self.wf.items():
            if value[_CLASS_TYPE_] == type:
                if title is not None:
                    if value[_META_][_TITLE_] == title:
                        return value[_INPUTS_]
                else:
                    return value[_INPUTS_]

        print("Not found:" + type)
        return None
    
    def remove_node(self, type, title=None):
        for key, value in self.wf.items():
            if value[_CLASS_TYPE_] == type:
                if title is not None:
                    if value[_META_][_TITLE_] == title:
                        del self.wf[key]
                        break
                else:
                    del self.wf[key]
                    break

    def upscale_x(self, time_upscale=2):
        if time_upscale == 1: # disable upscale
            self.remove_node(_UPSCALE_)
            save_img_key = self.get_node_number(_SAVE_IMG_)
            vae_decode_key = self.get_node_number(_VAE_DECODE_)
            self.get_node_inputs(_SAVE_IMG_)["image"][0] = vae_decode_key


    def init_save_img_node(self, save_path, img_format=".jpg", jpg_quality=70, png_compression=5):
        node = self.get_node_inputs(_SAVE_IMG_)
        node["path"] = save_path
        node["image_format"] = img_format
        node["jpg_quality"] = 70
        node["png_compression"] = 5
    
    def init_load_img_node(self, load_path):
        node = self.get_node_inputs(_LOAD_IMG_)
        node["image_path"] = load_path

    def init_ksampler_node(self, seed=753, steps=4, cfg=1.3, denoise=0.39):
        node = self.get_node_inputs(_KSAMPLER_)
        node["seed"] = seed
        node["steps"] = steps
        node["cfg"] = cfg
        node["denoise"] = denoise

    def init_promt_pos_node(self, txt):
        node = self.get_node_inputs(_PROMT_, "Positive promt")
        node["text"] = txt

    def init_promt_neg_node(self, txt):
        node = self.get_node_inputs(_PROMT_, "Negative promt")
        node["text"] = txt

    def init_lora_loader_node(self, strength_model, strength_clip):
        node = self.get_node_inputs(_LORA_LOAD_)
        node["strength_model"] = strength_model 
        node["strength_clip"] = strength_clip
    
    def init_checkpoint_loader_node(self, ckpt_name):
        node = self.get_node_inputs(_CHECK_POINT_LOAD)
        node["ckpt_name"] = ckpt_name