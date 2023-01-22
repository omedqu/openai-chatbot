import os
import configparser
import openai
import tkinter as tk
from tkinter import Text, filedialog, Menu, font, simpledialog, messagebox

import requests

model_engine = "text-davinci-003"

directory = os.path.join(os.path.expanduser("~"), "Documents", "uqs_userdata")
if not os.path.exists(directory):
    os.makedirs(directory)

config = configparser.ConfigParser()
config_path = os.path.join(directory, "ccb_config.ini")
config.read(config_path)

print("config_path: ", config_path)
if not os.path.exists(config_path):
    print("Creating configuration file")
    config["Style"] = {"current_style": "dark"}
    config["Language"] = {"current_language": "Deutsch"}
    with open(config_path, "w") as config_file:
        config.write(config_file)
else:
    print("Configuration file already exists")

config.read(config_path)


if not os.path.exists(config_path):
    config["Style"] = {"current_style": "dark"}
    config["Language"] = {"current_language": "Deutsch"}
    with open(config_path, "w") as config_file:
        config.write(config_file)

root = tk.Tk()
menu = Menu(root)
menu.configure(bg="Black")
root.config(menu=menu)


def check_file_exists(file_path):
    if os.path.exists(file_path):
        return True
    else:
        return False


def download_icon(file_path):
    url = 'https://zap1015869-1.plesk06.zap-webspace.com/icon.ico'
    r = requests.get(url)
    with open(file_path, 'wb') as f:
        f.write(r.content)


def main(file_path):
    if check_file_exists(file_path):
        print('chatbot_icon.ico already exists in the given path.')
    else:
        download_icon(file_path)
        print('chatbot_icon.ico downloaded successfully.')


icon_path = os.path.join(directory, "chatbot_icon.ico")
main(icon_path)

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width / 16)
y = (screen_height / 16)

root.iconbitmap(icon_path)
root.title("Coding Chatbot © 2023 UQ (Powered by OpenAI)")
root.geometry("%dx%d+%d+%d" % (480, 869, x, y))
root.resizable(False, False)
root.configure(background="dimgray")


prompt = tk.Text(root, height=5, wrap='char')
prompt.configure(background="white", foreground="black", font=("Calibri", 14))
prompt.grid(row=2, sticky='s')
prompt.config(width=480, wrap="word")

response_text = Text(root, height=31, state='disabled', wrap='word')
response_text.configure(background="gainsboro", foreground="black", font=("Calibri", 14))
response_text.grid(row=1, sticky='n')
response_text.config(width=480, wrap="word")

previous_prompts_responses = []

frame = tk.Frame(root)
frame.grid(row=3, sticky='s')

defined_width = 470

def copy_latest_response():
    latest_response = previous_prompts_responses[-1][1]
    root.clipboard_clear()
    root.clipboard_append(latest_response)


copy_latest_response_button = tk.Button(root, text="Copy last response", command=copy_latest_response,
                                        bg="gainsboro", fg="black", width="59", font=("Calibri", 12),
                                        highlightcolor="white")
copy_latest_response_button.grid(row=3, column=0, sticky='w')


def change_menu_label(label):
    edit_menu.entryconfigure(0, label=label)


def insert_line_break_at_width(event):
    text = event.widget
    last_line = text.get("end-1c linestart", "end-1c lineend")
    font_info = font.Font(font=text['font'])
    last_line_width = font_info.measure(last_line)
    if last_line_width >= defined_width:
        text.insert(tk.END, "\n")


def clear_conversation():
    response_text.config(state='normal')
    response_text.delete("1.0", tk.END)
    response_text.config(state='disabled')
    previous_prompts_responses.clear()


def save_conversation():
    conversation = response_text.get("1.0", 'end-1c')
    filename = filedialog.asksaveasfilename(title=textsaveconv, defaultextension=".txt",
                                            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
    with open(filename, "w") as f:
        f.write(conversation)


def save_api_key(api_key):
    config = configparser.ConfigParser()
    config['API'] = {'key': api_key}
    with open(config_path, 'w') as configfile:
        config.write(configfile)

def load_api_key():
    config = configparser.ConfigParser()
    try:
        config.read(config_path)
        api_key = config['API']['key']
    except:
        api_key = "empty"
        config['API'] = {'key': api_key}
        with open(config_path, 'w') as configfile:
            config.write(configfile)
    return api_key


api_key = load_api_key()
openai.api_key = api_key

def change_apikey():
    new_api_key = simpledialog.askstring("Change API key", "Enter the new API key:")
    if new_api_key:
        openai.api_key = new_api_key  # Update the API key
        save_api_key(new_api_key)  # Save the new API key to the config file
        messagebox.showinfo("API key changed", "API key changed to: " + new_api_key)
    else:
        messagebox.showwarning("Cancelled", "API key change cancelled")


def reply_to_conversation(event):
    if event.state & 0x0001:  # Shift-Taste gedrückt
        prompt.insert(tk.END, "")
    else:
        try:
            current_prompt = prompt.get("1.0", 'end-1c')
            prompt.delete("1.0", tk.END)
            shortened_prompt = current_prompt
            if len(current_prompt) > 100:
                shortened_prompt = current_prompt[:100] + '...\n'

            full_prompt = ""
            if len(previous_prompts_responses) > 0:
                for previous_prompt_response in previous_prompts_responses:
                    full_prompt += previous_prompt_response[0] + "\n" + previous_prompt_response[1] + "\n"
            full_prompt += current_prompt
            print(full_prompt)

            if len(full_prompt) > 4000:
                full_prompt = full_prompt[-4000:]

            response_text.config(state='normal')
            response_text.insert(tk.END, "Me:\n" + shortened_prompt)
            response_text.config(state='disabled')
            response_text.yview_moveto(1.0)

            completion = openai.Completion.create(
                engine=model_engine,
                prompt=full_prompt,
                max_tokens=1024,
                n=1,
                stop=None,
                temperature=1,
            )
            response = completion.choices[0].text
            response_formatted = ""
            current_line = ""
            for word in response.split():
                if len(current_line) + len(word) > 58:
                    response_formatted += current_line + "\n"
                    current_line = ""
                current_line += word + " "
            response_formatted += current_line

            response_text.config(state='normal')
            response_text.insert(tk.END, '\nBot:\n' + response_formatted + "\n\n")
            response_text.config(state='disabled')
            response_text.yview_moveto(1.0)

            previous_prompts_responses.append((current_prompt, response))
        except Exception as e:
            response_text.config(state='normal')
            response_text.insert(tk.END, "Error: " + str(e))
            response_text.config(state='disabled')


def change_style_bright():
    root.configure(bg="dimgray")
    copy_latest_response_button.configure(bg="gainsboro", fg="black")
    prompt.configure(bg="white", fg="black")
    response_text.configure(bg="gainsboro", fg="black")
    with open(config_path, 'w') as configfile:
        config.write(configfile)


def change_style_dark():
    root.configure(bg="black")
    copy_latest_response_button.configure(bg="black", fg="white")
    prompt.configure(bg="black", fg="white")
    response_text.configure(bg="black", fg="white")
    with open(config_path, 'w') as configfile:
        config.write(configfile)


edit_menu = Menu(menu)
edit_menu.configure(tearoff=0)
menu.add_cascade(label="Edit", menu=edit_menu)
edit_menu.add_command(label="Copy latest response", command=copy_latest_response)
edit_menu.add_command(label="Clear conversation", command=clear_conversation)
edit_menu.add_command(label="Save conversation", command=save_conversation)
edit_menu.add_command(label="Change API-Key", command=change_apikey)
edit_menu.add_command(label="Exit", command=root.destroy)


style_menu = Menu(menu)
style_menu.configure(tearoff=0)
menu.add_cascade(label="Style", menu=style_menu)
style_menu.add_command(label="Bright", command=change_style_bright)
style_menu.add_command(label="Dark", command=change_style_dark)


prompt.bind("<Key>", insert_line_break_at_width)
root.bind('<Return>', reply_to_conversation)

root.mainloop()
