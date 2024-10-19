import requests
import tkinter as tk
from tkinter import messagebox
import io
import os
from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image, ImageTk

# グローバル変数
temperature = None
humidity = None

# 環境ファイルからSwitchBotのAPIキーとデバイスIDを取得
load_dotenv()
API_KEY = os.getenv('SWITCHBOT_API_KEY')
DEVICE_ID = os.getenv('DEVICE_ID')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
WINDOW_WIDTH = int(os.getenv('WINDOW_WIDTH'))
WINDOW_HEIGHT = int(os.getenv('WINDOW_HEIGHT'))
UPDATE_INTERVAL = int(os.getenv('UPDATE_INTERVAL')) or 3600
AGE = int(os.getenv('AGE'))
GENDER = os.getenv('GENDER')

# OpenAIクライアントの初期化
client = OpenAI(api_key=OPENAI_API_KEY)

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
def update_temperature_humidity():
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
    root.after(UPDATE_INTERVAL * 1000, update_temperature_humidity)

# ChatGPTから画像を取得する関数
def get_image_from_url(image_url):
    response = requests.get(image_url)
    image_data = response.content
    image = Image.open(io.BytesIO(image_data))
    return image

# ChatGPTから服装とアドバイスを取得
def get_clothing_advice(preference, style, physical):
    print(f'get_clothing_advice START');

    prompt = f"""
    私は{AGE}歳、{GENDER}です。{preference}が好きで、{style}スタイルを好みます。体質は{physical}です。
    現在の気温{temperature}°C、湿度{humidity}%。この条件に合う服装のアドバイスを100文字以内でお願いします
    """

    response_advice = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "あなたはファッションの専門家"},
            {"role": "user", "content": prompt},
        ]
    )
    
    # 回答を取得
    advice = response_advice.choices[0].message.content
    print(f'アドバイス: {advice}');

    prompt = f"""
    {advice}
    ここより先に記載した文章に適合する服装の画像を生成してください。
    年齢は{AGE}歳、性別は{GENDER}、1人の人物が服を着た実写風でカラーでお願いします。
    テキスト情報は画像に出力しないでください
    """

    response_image = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1,
    )
    image_url = response_image.data[0].url
    image = get_image_from_url(image_url)
    print(f'服装の画像URL: {image_url}');

    print(f'get_clothing_advice END');
    return image, advice

# 服装を取得
def update_clothing():
    try:
        message_label.config(text="データ取得中...", fg="cyan")
        root.update()
        preference = "カジュアル"
        style = "ゆったりめ"
        physical = "普通"
        image, advice = get_clothing_advice(preference, style, physical)
        if image is not None and advice is not None:
            image = image.resize((300, 300), Image.BILINEAR)    #中程度品質の圧縮、速度も速い
            image_tk = ImageTk.PhotoImage(image)
            image_label.config(image=image_tk)
            image_label.image = image_tk
            advice_label.config(text=f"{advice}")
            message_label.config(text="服装の取得OK", fg="blue")
            root.update()
        else:
            print("update_clothing error")
            message_label.config(text="服装の取得NG", fg="red")

    except Exception as e:
        print(f"update_clothing Exception error: {e}")

# モニター中央の座標をウィンドウサイズを考慮して取得
def get_window_coordinate():
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x_coordinate = (screen_width // 2) - (WINDOW_WIDTH // 2)
    y_coordinate = (screen_height // 2) - (WINDOW_HEIGHT // 2)
    return x_coordinate, y_coordinate

# GUIの初期設定
root = tk.Tk()
root.title("今日の服をAIに聞く")

# ウィンドウ表示位置を取得
x_coordinate, y_coordinate = get_window_coordinate()

root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x_coordinate}+{y_coordinate}")
root.configure(bg="gray")
# background = tk.PhotoImage(file="bg_image.png")
# bg = tk.Label(root, image=background)
# bg.pack(fill="x")

# 画面に表示する項目
message_label = tk.Label(root, text=".", font=("Helvetica", 16), bg="gray")
message_label.place(x=WINDOW_WIDTH // 2,y=10, anchor="center")

temperature_label = tk.Label(root, text="気温: 取得中...", font=("Helvetica", 20), fg="white", width=15)
temperature_label.place(x=WINDOW_WIDTH // 2,y=50, anchor="center")

humidity_label = tk.Label(root, text="湿度: 取得中...", font=("Helvetica", 20), fg="white", width=15)
humidity_label.place(x=WINDOW_WIDTH // 2,y=75, anchor="center")

update_button = tk.Button(root, text="気温・温度を取得", command=update_temperature_humidity, font=("Helvetica", 16), width=12, height=2)
update_button.place(x=WINDOW_WIDTH // 2,y=120, anchor="center")

update_clothing_button = tk.Button(root, text="服装を取得", command=update_clothing, font=("Helvetica", 16), width=12, height=2)
update_clothing_button.place(x=WINDOW_WIDTH // 2,y=175, anchor="center")

image_label = tk.Label(root, bg="gray")
image_label.place(x=WINDOW_WIDTH // 2, y=360, anchor="center")

advice_label = tk.Label(root, text="", font=("Helvetica", 16), fg="white", bg="gray", width=60, wraplength=550)
advice_label.place(x=WINDOW_WIDTH // 2,y=550, anchor="center")

# 初期化時に気温・温度を表示
update_temperature_humidity()

root.mainloop()