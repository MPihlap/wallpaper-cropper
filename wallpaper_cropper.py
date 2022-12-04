#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging

import cv2
import yaml


class Screen():
    def __init__(self, name, resolution, rotation=0, trackbar_window = None, max_x = 1920, max_y = 1080) -> None:
        self.name = name
        self.resolution = resolution
        self.rotation = rotation
        self.ratio = resolution[0]/resolution[1]
        self.trackbar_window = trackbar_window if trackbar_window is not None else self.name

        self.max_x = max_x
        self.max_y = max_y
        self.x_pos = 0
        self.y_pos = 0
        self.scaler = 1

        self.__trackbar_setup()


    def update_x(self, value):
        self.x_pos = value


    def update_y(self, value):
        self.y_pos = value


    def update_scaler(self, value):
        self.scaler = value/1000


    def __trackbar_setup(self):
        cv2.createTrackbar(f"{self.name}_x_pos", f"{self.trackbar_window}", 0, self.max_x, self.update_x)
        cv2.createTrackbar(f"{self.name}_y_pos", f"{self.trackbar_window}", 0, self.max_y, self.update_y)
        cv2.createTrackbar(f"{self.name}_scaler", f"{self.trackbar_window}", 0, 1000, self.update_scaler)




class ScreenCropper():
    def __init__(self, source_img, screens, preview_resolution=(1280, 720)) -> None:
        # Create a named window and name it 'Output'
        self.window_name = "Wallpaper Cropper"
        self.img = cv2.imread(source_img)
        cv2.namedWindow(self.window_name)
        self.colours = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
        self.preview_resolution = preview_resolution

        self.screens = []
        for screen in screens:
            self.screens.append(Screen(screen["screen"],
            (screen["resolution"]["x"], screen["resolution"]["y"]),
            screen["rotation"], self.window_name,
            self.img.shape[0], self.img.shape[1]))


    def update(self):
        temp_img = self.img.copy()
        for i, screen in enumerate(self.screens):
            x_len = int(screen.scaler*self.img.shape[1])
            y_len = int(screen.scaler*self.img.shape[0])
            if screen.rotation == 90: # TODO: Implement proper rotation handling
                x_len = int(screen.scaler*self.img.shape[0])
                y_len = int(screen.scaler*self.img.shape[1])
            temp_img = cv2.rectangle(temp_img, (screen.x_pos, screen.y_pos), (screen.x_pos + x_len, screen.y_pos + y_len), self.colours[i], 1)
            temp_img = cv2.putText(temp_img, screen.name, (screen.x_pos, screen.y_pos), cv2.FONT_HERSHEY_SIMPLEX, 1, self.colours[i], 1)
        img_preview = cv2.resize(temp_img, self.preview_resolution)
        cv2.imshow(self.window_name, img_preview)

    def save_images(self):
        for screen in self.screens:
            x_len = int(screen.scaler*self.img.shape[1])
            y_len = int(screen.scaler*self.img.shape[0])
            if screen.rotation == 90: # TODO: Implement proper rotation handling
                x_len = int(screen.scaler*self.img.shape[0])
                y_len = int(screen.scaler*self.img.shape[1])
            cropped_img = self.img[screen.y_pos:screen.y_pos + y_len, screen.x_pos:screen.x_pos + x_len]
            if screen.rotation == 90:
                cropped_img = cv2.resize(cropped_img, list(reversed(screen.resolution)))
            else:
                cropped_img = cv2.resize(cropped_img, screen.resolution)

            cv2.imwrite(f"{screen.name}.png", cropped_img)



def set_loglevel(loglevel):
    if loglevel == "DEBUG":
        logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("mod_updater_debug.log", mode="w"),
            logging.StreamHandler()
        ])
    elif loglevel == "INFO":
        logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    else:
        error = ValueError(f"Incorrect debug level specified in yaml: {loglevel}. Please choose either DEBUG or INFO")
        logging.exception(error)
        input("Press ENTER to exit")
        exit(1)

def main():


    try:
        with open("config.yaml", "r") as stream:
            try:
                params = yaml.safe_load(stream) # Throws yaml parse error
            except yaml.YAMLError as exc:
                raise yaml.YAMLError("Unable to parse yaml. Check your syntax.")
    except FileNotFoundError as e:
        logging.exception(e)
        logging.error("Please make sure the mod_updater_config.yaml file is in the same folder as the mod_updater.exe")
        input("Press ENTER to exit")
        exit(1)

    global_params = params["global"]
    screen_params = params["screens"]
    logging.debug(params)

    sc = ScreenCropper(global_params["input_file"], screen_params)

    while True:

        sc.update()

        # Quit the program when 'q' is pressed
        if (cv2.waitKey(1) & 0xFF) == ord('q'):
            break
    sc.save_images()
    # Close any windows associated with OpenCV GUI
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()