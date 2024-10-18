import requests
import tkinter as tk
from tkinter import messagebox
import os
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

# 環境変数からSwitchBotのAPIキーとデバイスIDを取得
API_KEY = os.getenv('SWITCHBOT_API_KEY')
DEVICE_ID = os.getenv('DEVICE_ID')

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
def update_weather_info():
    try:
        temperature, humidity = get_temperature_humidity()
        print(f"update_weather_info 温度: {temperature}")
        print(f"update_weather_info 湿度: {humidity}")
        if temperature is not None and humidity is not None:
            temperature_label.config(text=f"気温: {temperature}°C")
            humidity_label.config(text=f"湿度: {humidity}%")
            root.update_idletasks()
        else:
            print("error データが更新されませんでした")
            messagebox.showerror("エラー", "温湿度データの取得に失敗しました")
    except Exception as e:
        print(f"エラー発生: {e}")

# GUIの初期設定
root = tk.Tk()
root.title("温湿度計")
root.geometry("600x500")
root.configure(bg="lightblue")  # ウィンドウ全体の背景色を設定

# ラベルを表示（背景色を設定）
# temperature_label = tk.Label(root, text="気温: 取得中...", font=("Helvetica", 20), fg="white", bg="black", width=15)
temperature_label = tk.Button(root, text="気温: 取得中...", font=("Helvetica", 16), fg="white", bg="black", width=15, height=6)
temperature_label.place(x=200,y=50)

# humidity_label = tk.Label(root, text="湿度: 取得中...", font=("Helvetica", 20), fg="white", bg="black", width=15)
humidity_label = tk.Button(root, text="湿度: 取得中...", font=("Helvetica", 16), fg="white", bg="black", width=15, height=6)
humidity_label.place(x=200,y=100)

# 更新ボタン
update_button = tk.Button(root, text="データ取得", command=update_weather_info)
update_button.place(x=220,y=200)

# 初期化時に温湿度を取得して表示
update_weather_info()

# ウィンドウのループを開始
root.mainloop()