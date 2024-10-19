import requests
import tkinter as tk
from tkinter import messagebox
import os
from dotenv import load_dotenv

# 環境ファイルからSwitchBotのAPIキーとデバイスIDを取得
load_dotenv()
API_KEY = os.getenv('SWITCHBOT_API_KEY')
DEVICE_ID = os.getenv('DEVICE_ID')
UPDATE_INTERVAL = int(os.getenv('UPDATE_INTERVAL')) or 300

# 温湿度計から温度と気温を取得
def get_temperature_humidity():
    url = f'https://api.switch-bot.com/v1.0/devices/{DEVICE_ID}/status'
    headers = {
        'Authorization': f'Bearer {API_KEY}',
    }

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            temperature = data['body']['temperature']
            humidity = data['body']['humidity']
            return temperature, humidity
        else:
            print(f"error status_code: {response.status_code}")
            return None, None
    except Exception as e:
        print(f"error Exception: {e}")
        return None, None

# 温湿度データを取得して表示する関数
def update_info():
    try:
        message_label.config(text="データ取得中...", fg="cyan")
        root.update()
        temperature, humidity = get_temperature_humidity()
        print(f"データ取得OK 温度: {temperature}, 湿度: {humidity}")
        if temperature is not None and humidity is not None:
            temperature_label.config(text=f"気温: {temperature}°C")
            humidity_label.config(text=f"湿度: {humidity}%")
            message_label.config(text="データ取得OK", fg="blue")
            root.update()
        else:
            print("error データ取得NG")
            message_label.config(text="データ取得NG", fg="red")

    except Exception as e:
        print(f"エラー発生: {e}")

    # 定期的に関数を呼び出す afterメソッドはミリ秒
    root.after(UPDATE_INTERVAL * 1000, update_info)

# GUIの初期設定
root = tk.Tk()
root.title("温湿度計")

# ウィンドウサイズ
window_width = 586
window_height = 329

# モニターのサイズから中央の座標を取得
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x_coordinate = (screen_width // 2) - (window_width // 2)    # モニター中央から左にウィンドウの半分を移動させた位置
y_coordinate = (screen_height // 2) - (window_height // 2)  # モニター中央から上にウィンドウの半分を移動させた位置

root.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")
root.configure(bg="gray")

# ラベルを表示
message_label = tk.Label(root, text=".", font=("Helvetica", 16), bg="gray")
message_label.place(x=240,y=10)

temperature_label = tk.Label(root, text="気温: 取得中...", font=("Helvetica", 20), fg="white", width=15)
temperature_label.place(x=200,y=50)

humidity_label = tk.Label(root, text="湿度: 取得中...", font=("Helvetica", 20), fg="white", width=15)
humidity_label.place(x=200,y=100)

# 更新ボタン
update_button = tk.Button(root, text="データ取得", command=update_info)
update_button.place(x=245,y=200)

# 初期化時に温湿度を取得して表示
update_info()

# ウィンドウのループを開始
root.mainloop()