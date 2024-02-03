import time

import cv2
import screeninfo

from model import ModelCollection

class MirrorStyle:
    def __init__(self, workflow, keep_age_sec=5, keep_background_sec=60, keep_model_sec=20):
        self.wf = workflow

        self.model_collection = ModelCollection()
        self.models = self.model_collection.get_models()
        self.model_name = self.models[0]["name"]

        self.default_promt = "masterpice, good quality"
        self.AGES = ['teenager', 'young adult', 'mature individual', 'senior citizen', 'elderly person']
        self.age = self.AGES[0]

        self.BACKGROUNDS = ['space ship', 'pool', 'forest', 'mount', 'church', 'dungeon', 'beach', 'jungle']
        self.background =  self.BACKGROUNDS[0]

        cur_time = time.time()
        self.keep_time = {"age": keep_age_sec, "back": keep_background_sec, "model": keep_model_sec}
        self.last_change_time = {"age": cur_time, "back": cur_time, "model": cur_time - keep_model_sec - 2}
    
    def change_keep_time(self, param, dur):
         self.keep_time[param] = dur

    # change to next background
    def change_background(self):
        if self.does_need_change("back"):
            current_index = self.BACKGROUNDS.index(self.background)
            next_index = (current_index + 1) % len( self.BACKGROUNDS)
            self.background = self.BACKGROUNDS[next_index]

    # change to next age
    def change_age(self):
        if self.does_need_change("age"):    
            current_index = self.AGES.index(self.age)
            next_index = (current_index + 1) % len( self.AGES)
            self.age = self.AGES[next_index]

    # promt related functions
    def apply_description(self, additional=None):
        res_promt = self.age + ", " + self.background + ", " + self.default_promt
        if additional is not None:
            res_promt += ", " + additional

        print(res_promt)
        self.wf.init_promt_pos_node(res_promt)

    def does_need_change(self, param):
        end_time = time.time()
        if end_time - self.last_change_time[param] > self.keep_time[param]:
            self.last_change_time[param] = end_time
            return True
        return False

    def change_model(self):
        if self.does_need_change("model"):

            current_index = self.model_collection.find_index_by_name(self.model_name) 
            next_index = (current_index + 1) % len(self.models)

            self.model_name = self.models[next_index]["name"]
            
            settings = self.models[next_index]["settings"]
        
            self.wf.init_ksampler_node(steps=4, denoise=settings["denoise"], cfg=1.7)
            self.wf.init_lora_loader_node(strength_model=settings["lora_model"], strength_clip=settings["lora_clip"])
            self.wf.init_checkpoint_loader_node(self.model_name)
    
class Mirror:
    # Initialize the camera (0 is the default camera)
    def __init__(self, workflow, in_img, out_img, syncer=None, screen_dev_id=0, webcam_dev_id=0, local_run=True):
        self.local_run = local_run
        self.syncer = syncer
        self.in_img = in_img
        self.out_img = out_img
        self.wf = workflow
        self.style = MirrorStyle(self.wf)

        self.screen_dev_id = screen_dev_id # to show image
        self.webcam = cv2.VideoCapture(webcam_dev_id)
        # Check if the webcam is opened correctly
        if not self.webcam.isOpened():
            raise IOError("Cannot open webcam")

    def set_keep_age_time(self, dur):
        self.style.change_keep_time("age", dur)
    
    def set_keep_background_time(self, dur):
        self.style.change_keep_time("back", dur)

    def set_keep_model_time(self, dur):
        self.style.change_keep_time("model", dur)

    # image related functions
    @staticmethod
    def add_text_to_image(image, text, position=None, font=cv2.FONT_HERSHEY_SIMPLEX, font_scale=1, font_color=(0, 255, 0), font_thickness=2):
        # If position is not provided, set the default position to top-right corner
        if position is None:
            text_size, _ = cv2.getTextSize(text, font, font_scale, font_thickness)
            image_height, image_width, _ = image.shape
            position = (image_width - text_size[0] - 10, text_size[1] + 10)

        # Add the text to the image
        cv2.putText(image, text, position, font, font_scale, font_color, font_thickness)

        return image


    def show_image(self, img_path, model_name=None):
        screen = screeninfo.get_monitors()[self.screen_dev_id]
        window_name = 'mirror'
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

        cv2.moveWindow(window_name, screen.x - 1, screen.y - 1)
        cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN,
                            cv2.WINDOW_FULLSCREEN)
        
        (img_path)
        img = cv2.imread(img_path)

        if img is not None:
            if model_name is not None:
                img = self.add_text_to_image(img, model_name)
            cv2.imshow(window_name, img)
            cv2.waitKey(1)

    def take_photo(self, save_path): 
        ret, frame = self.webcam.read()
        cv2.imwrite(save_path, frame)

    def send_photo_to_remote_server(self):
        self.syncer.send_to_remote()

    def reflect(self):
        self.take_photo(self.in_img)

        if self.local_run is False:
            self.send_photo_to_remote_server()
            
        #start process and wait result
        img = self.wf.send_and_wait_result()

        if self.local_run is False:
            self.syncer.copy_to_local()
        self.show_image(self.out_img, self.style.model_name)

    def run(self):

        while True:
            self.style.change_model()
            # change only if needed
            self.style.change_age()
            self.style.change_background()
            self.style.apply_description()

            self.reflect()


            
