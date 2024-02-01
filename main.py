import os

from workflow import Workflow
from mirror import Mirror
from syncer import *

# General settings
LOCAL_COMFYUI = True

# IP Settings
LOCAL_URL = "127.0.0.1:8188"
REMOTE_URL = "65.109.73.2:7830"
COMFYUI_URl = LOCAL_URL

#SYNCER SETTINGS
REMOTE_IP_SSH = "65.109.73.2"
REMOTE_PORT_SSH = 7838
USER = 'root'

REMOTE_IN = '/workspace/files/in/in.jpg'
REMOT_OUT = '/workspace/files/out/out.jpg'

# PATH
SAVE_CAMERA_IMAGE_PATH = 'files\\in\\in.jpg'
SHOW_IMAGE_PATH = 'files\\out\\out.jpg'

# WORKFLOW Settings
COMFYUI_WF = 'mirror_api.json'

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
        wf.upscale_x(1)

        mirror = Mirror(wf, SAVE_CAMERA_IMAGE_PATH, SHOW_IMAGE_PATH, local_run=LOCAL_COMFYUI, syncer=syncer)
        mirror.run()

main()