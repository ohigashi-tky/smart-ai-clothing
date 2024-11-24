import requests
import customtkinter as ctk
from customtkinter import CTkImage
import io
import os
from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image

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
UPDATE_INTERVAL = int(os.getenv('UPDATE_INTERVAL')) or 600
AGE = int(os.getenv('AGE'))
GENDER = os.getenv('GENDER')
PREFERENCE=os.getenv('PREFERENCE')
STYLE=os.getenv('STYLE')
PHYSICAL=os.getenv('PHYSICAL')

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
        message_label.configure(text="データ取得中...", text_color="cyan")
        root.update()
        temperature, humidity = get_temperature_humidity()
        print(f"データ取得OK 温度: {temperature}, 湿度: {humidity}")
        if temperature is not None and humidity is not None:
            temperature_label.configure(text=f"気温: {temperature}°C")
            humidity_label.configure(text=f"湿度: {humidity}%")
            message_label.configure(text="データ取得OK", text_color="blue")
            root.update()
        else:
            print("error データ取得NG")
            message_label.configure(text="データ取得NG", text_color="red")

    except Exception as e:
        print(f"エラー発生: {e}")

    # 定期的に関数を呼び出す afterメソッドはミリ秒
    root.after(UPDATE_INTERVAL * 1000, update_temperature_humidity)

# ChatGPTから画像を取得する関数
def get_image_from_url(image_url):
    response = requests.get(image_url)
    image_data = response.content
    image = Image.open(io.BytesIO(image_data))
    image = CTkImage(light_image=image, dark_image=image, size=(300, 300))
    return image

# ChatGPTから服装とアドバイスを取得
def get_clothing_advice():
    print(f'get_clothing_advice START');

    prompt = f"""
    これから記載する条件に合う服装のアドバイスを100文字以内でお願いします。
    私は{AGE}歳、{GENDER}です。{PREFERENCE}が好きで、{STYLE}スタイルを好みます。体質は{PHYSICAL}です。
    気温は{temperature}°C、湿度は{humidity}%。靴は単色、上下の服は2色以上。
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
    アドバイスに沿った服装の画像を実写風カラーで生成してください。
    1人の日本人{GENDER}、年齢は{AGE}歳です。
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

    print(f'get_clothing_advice END');
    return image, advice

# 服装を取得
def update_clothing():
    try:
        message_label.configure(text="データ取得中...", text_color="cyan")
        root.update()
        image, advice = get_clothing_advice()
        if image is not None and advice is not None:
            # image = image.resize((300, 300), Image.BILINEAR)    #中程度品質の圧縮、速度も速い
            image_label.configure(image=image)
            image_label.image = image
            advice_label.configure(text=f"{advice}")
            message_label.configure(text="服装の取得OK", text_color="blue")
            root.update()
        else:
            print("update_clothing error")
            message_label.configure(text="服装の取得NG", text_color="red")

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
root = ctk.CTk()
root.title("今日の服をAIに聞く")

# ウィンドウ表示位置を取得
x_coordinate, y_coordinate = get_window_coordinate()
root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x_coordinate}+{y_coordinate}")
root.configure(fg_color="gray")

# 表示項目
message_label = ctk.CTkLabel(root, text=".", font=("Helvetica", 14), text_color="white", fg_color="transparent")
message_label.place(x=WINDOW_WIDTH // 2,y=10, anchor="center")

temperature_label = ctk.CTkLabel(
    root, text="気温: 更新中...",
    font=("Helvetica", 24),
    text_color="white",
    anchor="center",
    fg_color="black",
    width=170,
    height=35
)
temperature_label.place(x=WINDOW_WIDTH // 2, y=45, anchor="center")

humidity_label = ctk.CTkLabel(
    root,
    text="湿度: 更新中...",
    font=("Helvetica", 24),
    text_color="white",
    anchor="center",
    fg_color="black",
    width=170,
    height=35
)
humidity_label.place(x=WINDOW_WIDTH // 2, y=75, anchor="center")

update_clothing_button = ctk.CTkButton(
    root,
    text="おすすめの服装",
    command=update_clothing,
    font=("Helvetica", 18),
    width=150,
    height=40,
    corner_radius=5
)
update_clothing_button.place(x=WINDOW_WIDTH // 2,y=125, anchor="center")

image_label = ctk.CTkLabel(root, text="")
image_label.place(x=WINDOW_WIDTH // 2, y=310, anchor="center")

advice_label = ctk.CTkLabel(
    root,
    text="",
    font=("Helvetica", 16),
    text_color="white",
    fg_color="transparent",
    width=60,
    wraplength=550
)
advice_label.place(x=WINDOW_WIDTH // 2,y=505, anchor="center")

# 初期化時に気温・温度を表示
update_temperature_humidity()

root.mainloop()