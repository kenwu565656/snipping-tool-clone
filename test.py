import time
import tkinter as tk
from tkinter import ttk
import pyautogui
import cv2
import numpy as np
from PIL import Image, ImageTk
import multiprocessing as mp

# this class is our snipping tool, it has an gui to handle the user input. We can screen cap in a
# drag area, edit the screenshot by drawing line and recangle, then save the screenshot.
# We can also set some setting such as the drawing color, save location of the screenshot
class SnippingTool:
    def __init__(self):
        # use the following value to save the screen cap status and range
        self.click_x = 0
        self.click_y = 0
        self.release_x = 0
        self.release_y = 0
        self.capping = False
        self.set = False

        # our ui
        self.ui = tk.Tk()
        self.ui.geometry("")
        self.tabControl = ttk.Notebook(self.ui)
        self.tabControl.pack(expand=1, fill="both")

        # the variables in our app setting
        self.delay = tk.IntVar()
        self.delay.set(0)
        self.location_folder = tk.StringVar() #ok
        self.location_folder.set("./")#ok
        self.file_name = tk.StringVar() #ok
        self.file_name.set("output")#ok
        self.save_file_format = tk.StringVar()
        self.save_file_format.set(".png")
        self.rgb_r = tk.IntVar()
        self.rgb_g = tk.IntVar()
        self.rgb_b = tk.IntVar()
        self.rgb_r.set(0)
        self.rgb_g.set(255)
        self.rgb_b.set(0)
        self.draw_line_width = tk.IntVar()
        self.draw_line_width.set(1)
        self.quit_edit_key = tk.StringVar()
        self.quit_edit_key.set('q')
        self.change_draw_line_key = tk.StringVar()
        self.change_draw_line_key.set('l')
        self.change_draw_rec_key = tk.StringVar()
        self.change_draw_rec_key.set('r')

        # the screenshot page
        self.screen_cap_page = ttk.Frame(self.tabControl)
        button_container = tk.Frame(self.screen_cap_page)
        button_container.grid(row=0, column=0)
        self.startButton = tk.Button(button_container, text="New", command=self.start)
        self.startButton.grid(row=0, column=0)
        self.closeButton = tk.Button(button_container, text="Close", command=self.close)
        self.closeButton.grid(row=0, column=1)
        self.editButton = tk.Button(button_container, text="Edit", command=self.edit)
        self.editButton.grid(row=0, column=2)
        self.saveButton = tk.Button(button_container, text="Save", command=self.save)
        self.saveButton.grid(row=0, column=3)
        self.label = tk.Label(self.screen_cap_page)
        self.label.grid(row=1, column=0, columnspan=2)
        self.tabControl.add(self.screen_cap_page, text="Screenshot")

        # the widgets in the recording page
        self.screen_record_page = ttk.Frame(self.tabControl)
        self.start_screen_record_button = tk.Button(self.screen_record_page, text="Start", command=self.start_recording)
        self.end_screen_record_button = tk.Button(self.screen_record_page, text="End", command=self.end_recording)
        self.start_screen_record_button.grid(row=0, column=0)
        self.end_screen_record_button.grid(row=0, column=2)
        self.tabControl.add(self.screen_record_page, text="Screen record")

        # the widgets in the setting page
        self.setting = ttk.Frame(self.tabControl)
        labelframe_for_screen_setting = tk.LabelFrame(self.setting, text="Screen Shot Setting")
        labelframe_for_screen_setting.grid(row=0, column=0)
        tk.Label(labelframe_for_screen_setting, text="Save location").grid(row=0, column=0)
        tk.Entry(labelframe_for_screen_setting, textvariable=self.location_folder).grid(row=0, column=1, columnspan=2)
        tk.Label(labelframe_for_screen_setting, text="Save file name").grid(row=1, column=0)
        tk.Entry(labelframe_for_screen_setting, textvariable=self.file_name).grid(row=1, column=1,columnspan=2)
        tk.Label(labelframe_for_screen_setting, text="Save file format").grid(row=2, column=0)
        tk.Radiobutton(labelframe_for_screen_setting, variable=self.save_file_format, value=".png", text=".png").grid(row=2, column=1)
        tk.Radiobutton(labelframe_for_screen_setting, variable=self.save_file_format, value=".jpg", text=".jpg").grid(row=2,
                                                                                                         column=2)

        labelframe_for_edit_setting = tk.LabelFrame(self.setting, text="Edit Setting")
        labelframe_for_edit_setting.grid(row=1, column=0)

        tk.Scale(labelframe_for_edit_setting, orient=tk.HORIZONTAL, from_=0, to=255, variable=self.rgb_r).grid(row=4, column=1)
        tk.Scale(labelframe_for_edit_setting, orient=tk.HORIZONTAL, from_=0, to=255, variable=self.rgb_g).grid(row=5,
                                                                                                               column=1)
        tk.Scale(labelframe_for_edit_setting, orient=tk.HORIZONTAL, from_=0, to=255, variable=self.rgb_b).grid(row=6,
                                                                                                               column=1)
        tk.Label(labelframe_for_edit_setting, text="Paint width").grid(row=0, column=0)
        tk.Entry(labelframe_for_edit_setting, textvariable=self.draw_line_width).grid(row=0, column=1)
        tk.Label(labelframe_for_edit_setting, text="Close Edit KeyBoard key").grid(row=1, column=0)
        tk.Entry(labelframe_for_edit_setting, textvariable=self.quit_edit_key).grid(row=1, column=1)
        tk.Label(labelframe_for_edit_setting, text="Line Edit Mode KeyBoard key").grid(row=2, column=0)
        tk.Entry(labelframe_for_edit_setting, textvariable=self.change_draw_line_key).grid(row=2, column=1)
        tk.Label(labelframe_for_edit_setting, text="Rec Edit Mode KeyBoard key").grid(row=3, column=0)
        tk.Entry(labelframe_for_edit_setting, textvariable=self.change_draw_rec_key).grid(row=3, column=1)
        tk.Label(labelframe_for_edit_setting, text="Paint color(rgb red)").grid(row=4, column=0)
        tk.Label(labelframe_for_edit_setting, text="Paint color(rgb green)").grid(row=5, column=0)
        tk.Label(labelframe_for_edit_setting, text="Paint color(rgb blue)").grid(row=6, column=0)
        tk.Scale(labelframe_for_edit_setting, orient=tk.HORIZONTAL, from_=0, to=255, variable=self.rgb_r).grid(row=4,
                                                                                                               column=1)
        tk.Scale(labelframe_for_edit_setting, orient=tk.HORIZONTAL, from_=0, to=255, variable=self.rgb_g).grid(row=5,
                                                                                                               column=1)
        tk.Scale(labelframe_for_edit_setting, orient=tk.HORIZONTAL, from_=0, to=255, variable=self.rgb_b).grid(row=6,
                                                                                                               column=1)
        self.tabControl.add(self.setting, text="Setting")

    # this method is called when the user click the new button, then the app will enter a mode that
    # get the screen shot area by first set the ui to full screen and then bind the set_click_x_y and set_release_x_y function to the ui's
    # mouse left click and mouse left release event
    def start(self):
        self.label.config(image='')
        self.ui.attributes('-fullscreen', True)
        self.ui.attributes('-alpha', 0.1)
        self.capping = True
        self.ui.bind("<Button-1>", lambda x: self.set_click_x_y(pyautogui.position().x, pyautogui.position().y))
        self.ui.bind("<ButtonRelease-1>",
                     lambda x: self.set_release_x_y(pyautogui.position().x, pyautogui.position().y))

    def close(self):
        self.ui.destroy()

    # this function will be in set_release_x_y, after the user release the mouse, that means the user
    # has selected the screenshot region, then we can cap the screen and save only the region to self.img
    def screen_cap(self):
        while True:
            if not self.set:
                time.sleep(1)
            else:
                small_x, small_y = min(self.click_x, self.release_x), min(self.click_y, self.release_y)
                big_x, big_y = max(self.click_x, self.release_x), max(self.click_y, self.release_y)
                self.ui.attributes('-alpha', 0)
                cap = pyautogui.screenshot()
                # cv2image = cv2.cvtColor(np.array(self.cap), cv2.COLOR_RGB2BGR)
                # cv2image = cv2image[small_y:big_y, small_x:big_x]
                img = Image.fromarray(np.array(cap)[small_y:big_y, small_x:big_x])
                self.img = np.array(cap)[small_y:big_y, small_x:big_x]

                imgtk = ImageTk.PhotoImage(image=img)
                self.label.imgtk = imgtk
                self.label.configure(image=imgtk)
                break

    # this function will be bind to the ui's mouse left click event in order to set the user's
    # screenshot region
    def set_click_x_y(self, x, y):
        if not self.capping:
            return
        self.click_x, self.click_y = x, y

        print(self.click_x, self.click_y)

    # this function will be bind to the ui's mouse left release event in order to set the user's
    # screenshot region, after the region is set, we call the screen_cap function, after screen cap,
    # set every thing back to normal mode
    def set_release_x_y(self, x, y):
        if not self.capping:
            return
        self.release_x, self.release_y = x, y

        print(self.release_x, self.release_y)
        self.capping = False
        self.set = True

        self.screen_cap()
        self.ui.geometry('')
        self.back_to_normal_mode()

    # this function is used to set the app back to normal mode(not the screen cap mode), i.e.
    # not read the mouse left click and mouse left release any more(bind a useless function to replace)
    def back_to_normal_mode(self):
        self.ui.attributes('-alpha', 1)
        self.ui.attributes('-fullscreen', False)
        self.set = False
        self.ui.bind("<Button-1>", lambda x: print(x))
        self.ui.bind("<ButtonRelease-1>",
                     lambda x: print(x))


    def screen_recording(self):
        resolution = (1920, 1080)
        codec = cv2.VideoWriter_fourcc(*"XVID")
        filename = "Recording.avi"
        fps = 60
        out = cv2.VideoWriter(filename, codec, 20, resolution)

        while True:
            if self.screenRecordingFlat.get() == "pause":
                continue
            img = pyautogui.screenshot()

            frame = np.array(img)
            out.write(frame)
            if self.screenRecordingFlat.get() == "end":
                break
        out.release

    # this function is used to start the screen recording
    def start_recording(self):
        recordingProcess.start()

    # this function is used to end the screen recording
    def end_recording(self):
        recordingProcess.kill()
        print("killed")

    # this function can let the user edit the screenshot image by use an opencv screen
    # the screen is binded by a callback function that draw on the image when the screen read a set
    # of mouse left click and release
    # To close the opencv window when finish edit, press q on keyboard
    def edit(self):
        x_points = []
        y_points = []
        draw = "Line"
        image = cv2.cvtColor(self.img, cv2.COLOR_RGB2BGR)

        def draw_line(event, x, y, t, r):
            image = self.img
            if event == cv2.EVENT_LBUTTONDOWN:
                x_points.append(x)
                y_points.append(y)
            elif event == cv2.EVENT_LBUTTONUP:
                x_points.append(x)
                y_points.append(y)
                if draw == "Line":
                    image = cv2.line(image, (x_points[-2], y_points[-2]), (x_points[-1], y_points[-1]), (self.rgb_r.get(), self.rgb_g.get(), self.rgb_b.get()), self.draw_line_width.get())
                else:
                    image = cv2.rectangle(image, (x_points[-2], y_points[-2]), (x_points[-1], y_points[-1]), (self.rgb_r.get(), self.rgb_g.get(), self.rgb_b.get()), self.draw_line_width.get())
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                cv2.imshow("Edit", image)
        cv2.namedWindow("Edit")
        # cv2.createButton('Line', change_draw, ["REC"], cv2.QT_PUSH_BUTTON, 1)
        cv2.setMouseCallback("Edit", draw_line)
        while True:
            cv2.imshow("Edit", image)
            key = cv2.waitKey(0)
            if key == ord(self.quit_edit_key.get()):
                # image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                imgtk = ImageTk.PhotoImage(image=Image.fromarray(np.array(self.img)))
                self.label.imgtk = imgtk
                self.label.configure(image=imgtk)
                break
            elif key == ord(self.change_draw_line_key.get()):
                draw = "Line"
            elif key == ord(self.change_draw_rec_key.get()):
                draw = "Rec"
        cv2.destroyAllWindows()

    # this function is to save our screen shot
    def save(self):
        cv2image = cv2.cvtColor(self.img, cv2.COLOR_RGB2BGR)
        cv2.imwrite(self.location_folder.get() + self.file_name.get() + '.png', cv2image)

# this function is use to take screen record in a while true loop
# it will be a multiProcessing job, so can be killed by other call(the end button in the ui)
def screen_recording():
    SCREEN_SIZE = tuple(pyautogui.size())
    codec = cv2.VideoWriter_fourcc(*"XVID")
    filename = "Recording.avi"
    fps = 12.0
    out = cv2.VideoWriter(filename, codec, 20, (SCREEN_SIZE))
    record_seconds = 10
    print("start")

    while True:

        img = pyautogui.screenshot()

        frame = np.array(img)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        out.write(frame)
        if cv2.waitKey(1) == ord("q"):
            break
    print("end")
    out.release
    print("end2")


if __name__ == "__main__":
    recordingProcess = mp.Process(target=screen_recording)
    myapp = SnippingTool()
    myapp.ui.mainloop()
    # kill the screen recording when forget to close
    recordingProcess.kill()