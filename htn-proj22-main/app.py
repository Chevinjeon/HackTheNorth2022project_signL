import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image
from output import *
import cv2
from threading import Thread
import pyvirtualcam

window = tk.Tk()
settings_window = None
manual_window = None
window.title('SiGnL')

outputs = Output()
output_devices = Output.get_output_devices()
sending = True

window_width = 960
window_height = 540
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()

window.geometry(
    f'{window_width}x{window_height}+{screen_width // 2 - window_width // 2}+{screen_height // 2 - window_height // 2}')
window.resizable(0, 0)

frame = tk.Frame(window).pack()

center_x = int(screen_width / 2 - window_width / 2)
center_y = int(screen_height / 2 - window_height / 2)

canvas = tk.Canvas(frame, bg='black', width=window_width, height=window_height, highlightthickness=0)
canvas.pack()

camera = tk.Label(window, borderwidth=0)
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

bg_img = ImageTk.PhotoImage(Image.open('static/img/background.png').resize((window_width + 10, window_height + 10)))
bg = canvas.create_image(window_width // 2, window_height // 2, image=bg_img)
label = canvas.create_text(window_width // 2, window_height - 100, width=460, anchor='nw', text='', fill='black', font='Calibri 15')


def close():
    global window, sending
    window.destroy()
    sending = False


window.protocol('WM_DELETE_WINDOW', close)


def close_settings():
    global settings_window
    settings_window.destroy()
    settings_window = None


def set_device(variable):
    for od in output_devices:
        if od['name'] == variable:
            outputs.set_output_device(od['index'])
            return


def set_voice(variable):
    outputs.set_gender(variable)


def talk(text):
    outputs.speak(text)


def print_output(text):
    global label
    label = canvas.create_text(window_width // 2 - 245, window_height - 95, width=460, anchor='nw', text=text, fill='black', font='Calibri 11')


def open_settings():
    global settings_window
    if settings_window is None:
        settings_window = tk.Toplevel()
        settings_window.title('SiGnL Settings')
        settings_window['bg'] = '#0f4ebf'
        settings_window.geometry(f'260x180+50+50')
        settings_window.protocol('WM_DELETE_WINDOW', close_settings)

        options1 = []
        variable1 = tk.StringVar(settings_window)
        for od in output_devices:
            options1.append(od['name'])
            if od['index'] == outputs.output_device:
                variable1.set(od['name'])
        dropdown1 = tk.OptionMenu(settings_window, variable1, *options1, command=set_device)
        dropdown1.place(x=20, y=50)

        label1 = tk.Label(settings_window, text='Select Output Device:', bg='#0f4ebf', fg='#fff', font=("Calibri", 14))
        label1.place(x=20, y=20)
        label2 = tk.Label(settings_window, text='Select Gender:', bg='#0f4ebf', fg='#fff', font=("Calibri", 14))
        label2.place(x=20, y=90)
        options2 = ['Male', 'Female']
        variable2 = tk.StringVar(settings_window)
        variable2.set(outputs.gender)
        dropdown2 = tk.OptionMenu(settings_window, variable2, *options2, command=set_voice)
        dropdown2.place(x=20, y=120)

        settings_window.mainloop()


def close_manual():
    global manual_window
    manual_window.destroy()
    manual_window = None


def open_manual():
    global manual_window
    if manual_window is None:
        print_output('I want to sleep')
        speak = Thread(target=talk, args=['Testing'])
        speak.start()
        manual_window = tk.Toplevel()
        manual_window.title('SiGnL Manual')
        manual_window.geometry(f'500x500+100+100')
        manual_window.protocol('WM_DELETE_WINDOW', close_manual)

        chart_img = ImageTk.PhotoImage(Image.open('static/img/manual.png').resize((500, 500)))
        chart_bg = tk.Label(manual_window, image=chart_img)
        chart_bg.pack()

        manual_window.mainloop()


settings_img = ImageTk.PhotoImage(Image.open('static/img/settings.png').resize((40, 40)))
settings = tk.Button(canvas, image=settings_img, highlightthickness=0, borderwidth=0, command=open_settings)
settings.pack()
canvas.create_window(window_width - 20, 20, anchor='ne', window=settings)
manual_img = ImageTk.PhotoImage(Image.open('static/img/book.png').resize((40, 40)))
manual = tk.Button(canvas, image=manual_img, highlightthickness=0, borderwidth=0, command=open_manual)
manual.pack()
canvas.create_window(window_width - 70, 20, anchor='ne', window=manual)


def send_to_virtual_cam():
    cam = pyvirtualcam.Camera(width=1280, height=720, fps=30)
    while sending:
        cv2_image = cv2.cvtColor(cap.read()[1], cv2.COLOR_BGR2RGB)
        cam_frame = np.array(
            Image.fromarray(cv2_image).resize((1280, 960)).crop((0, 120, 1280, 840)))
        cam.send(cam_frame)
        cam.sleep_until_next_frame()


def show_frames():
    cv2_image = cv2.cvtColor(cap.read()[1], cv2.COLOR_BGR2RGB)
    frame_img = ImageTk.PhotoImage(
        Image.fromarray(cv2_image).transpose(Image.Transpose.FLIP_LEFT_RIGHT).resize((496, 372)))
    camera.frame = frame_img
    canvas.create_image(window_width // 2 - 15, window_height // 2 - 35, image=frame_img)
    canvas.tag_raise(bg)
    canvas.tag_raise(label)
    camera.after(10, show_frames)


show_frames()
virtual_cam = Thread(target=send_to_virtual_cam)
virtual_cam.start()

window.mainloop()
