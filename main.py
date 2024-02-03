import os

from workflow import Workflow
from mirror import Mirror
from syncer import *

# General settings
LOCAL_COMFYUI = False

# IP Settings
LOCAL_URL = "127.0.0.1:8188"
REMOTE_URL = "188.250.58.205:40440"
COMFYUI_URl = LOCAL_URL  if LOCAL_COMFYUI else REMOTE_URL

#SYNCER SETTINGS
REMOTE_IP_SSH = "188.250.58.205"
REMOTE_PORT_SSH = 40441
USER = 'root'

REMOTE_IN = '/workspace/files/in/in.jpg'
REMOT_OUT = '/workspace/files/out/out.jpg'

# PATH
SAVE_CAMERA_IMAGE_PATH = '.\\files\\in\\in.jpg'
SHOW_IMAGE_PATH = '.\\files\\out\\out.jpg'

# WORKFLOW Settings
COMFYUI_WF = 'mirror_api.json'

# Style settings
KEEP_AGE_TIME_SEC = 5
KEEP_BACKGROUND_TIME_SEC = 60
KEEP_MODEL_TIME_SEC = 60

# for ComfyUI better to specify absolute path
WF_IN  = os.path.abspath(SAVE_CAMERA_IMAGE_PATH)  if LOCAL_COMFYUI else REMOTE_IN
WF_OUT = os.path.abspath(SHOW_IMAGE_PATH)         if LOCAL_COMFYUI else REMOT_OUT

def main():
    with open(COMFYUI_WF) as flow_file:
        syncer = None
        if LOCAL_COMFYUI is False:
            syncer = Syncer(REMOTE_IP_SSH, REMOTE_PORT_SSH, local_in=SAVE_CAMERA_IMAGE_PATH, local_out=SHOW_IMAGE_PATH, remote_in=REMOTE_IN, remote_out=REMOT_OUT, user=USER)

        wf = Workflow(flow_file, COMFYUI_URl)
        wf.init_save_img_node(save_path=WF_OUT, jpg_quality=100, png_compression=1, img_format=".jpg")
        wf.init_load_img_node(load_path=WF_IN)
        #wf.upscale_x(1)

        mirror = Mirror(wf, SAVE_CAMERA_IMAGE_PATH, SHOW_IMAGE_PATH, local_run=LOCAL_COMFYUI, syncer=syncer)

        mirror.set_keep_model_time(KEEP_MODEL_TIME_SEC)
        mirror.set_keep_age_time(KEEP_AGE_TIME_SEC)
        mirror.set_keep_background_time(KEEP_BACKGROUND_TIME_SEC)

        mirror.run()

main()