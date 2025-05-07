#   pyinstaller --onefile --windowed ai_assistant.py

import requests
import tkinter as tk
from tkinter import scrolledtext
from tkinter import font
import time
import random
import speech_recognition as sr
import pyttsx3
import threading
from datetime import datetime
import pytz
from config import (
    DEEPSEEKR_API_URL,
    DEEPSEEKR_API_KEY,
    WEATHER_API_URL,
    WEATHER_API_KEY,
    AI_FACES
)

# Khởi tạo engine text-to-speech
engine = pyttsx3.init()
# Thiết lập giọng nói tiếng Anh
voices = engine.getProperty('voices')
for voice in voices:
    if 'english' in voice.name.lower():
        engine.setProperty('voice', voice.id)
        break
engine.setProperty('rate', 150)  # Tốc độ nói

# Khởi tạo recognizer cho speech-to-text
recognizer = sr.Recognizer()

# Hàm gửi câu hỏi đến API DeepSeekr1 và nhận phản hồi
def get_ai_response(user_input):
    """
    Gửi câu hỏi của người dùng đến API DeepSeekr1 và nhận phản hồi
    """
    headers = {
        "Authorization": f"Bearer {DEEPSEEKR_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-r1-distill-llama-70b",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant. Please respond in English."},
            {"role": "user", "content": user_input},
        ],
        "max_tokens": 5685,
        "temperature": 0.6,
        "top_p": 0.95,
        "presence_penalty": 0
    }
    try:
        response = requests.post(DEEPSEEKR_API_URL, headers=headers, json=data)
        response.raise_for_status()
        full_response = response.json().get("choices", [{}])[0].get("message", {}).get("content", "No response available.")
        return full_response
    except Exception as e:
        return f"Sorry, an error occurred: {str(e)}"

# Hàm lấy thông tin thời tiết từ Weather API
def get_weather(city):
    """
    Lấy thông tin thời tiết cho một thành phố cụ thể
    """
    params = {
        "key": WEATHER_API_KEY,
        "q": city
    }
    try:
        response = requests.get(WEATHER_API_URL, params=params)
        response.raise_for_status()  # Kiểm tra lỗi HTTP
        weather_data = response.json()
        condition = weather_data['current']['condition']['text']
        temp_c = weather_data['current']['temp_c']
        feelslike_c = weather_data['current']['feelslike_c']
        humidity = weather_data['current']['humidity']
        wind_kph = weather_data['current']['wind_kph']
        
        # Định dạng thông tin thời tiết gọn gàng hơn
        return (
            f"Weather in {city}:\n"
            f"Condition: {condition}\n"
            f"Temp: {temp_c}°C (Feels: {feelslike_c}°C)\n"
            f"Humidity: {humidity}% | Wind: {wind_kph} km/h"
        )
    except Exception as e:
        return f"Sorry, an error occurred when getting weather information: {str(e)}"

def speak(text):
    """Chuyển văn bản thành giọng nói"""
    engine.say(text)
    engine.runAndWait()

def listen():
    """Lắng nghe và chuyển giọng nói thành văn bản"""
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio, language='en-US')
            return text
        except sr.UnknownValueError:
            return "Could not recognize speech"
        except sr.RequestError:
            return "Error connecting to speech recognition service"

def create_ui():
    def on_submit(event=None):
        user_input = entry.get()
        if user_input:
            process_input(user_input)
            entry.delete(0, tk.END)

    def process_input(user_input):
        if user_input.lower().startswith("weather "):
            city = user_input.split("in")[-1].strip()
            response = get_weather(city)
        else:
            response = get_ai_response(user_input)
        
        output_area.insert(tk.END, f"\nYou: {user_input}\nAI: {response}\n")
        output_area.see(tk.END)
        
        # Phát âm thanh phản hồi
        threading.Thread(target=speak, args=(response,)).start()

    def update_status(message):
        status_label.config(text=message)
        window.after(2000, lambda: status_label.config(text=""))  # Xóa tin nhắn sau 2 giây

    def start_listening():
        def listen_thread():
            update_status("Listening...")
            voice_input = listen()
            if voice_input:
                update_status("Voice recognized!")
                entry.delete(0, tk.END)
                entry.insert(0, voice_input)
                process_input(voice_input)
            else:
                update_status("Could not recognize speech")
        
        threading.Thread(target=listen_thread).start()

    def update_weather():
        city = city_entry.get()
        if city:
            weather_info = get_weather(city)
            weather_area.config(state='normal')  # Mở khóa để cập nhật
            weather_area.delete(1.0, tk.END)
            weather_area.insert(tk.END, weather_info)
            weather_area.config(state='disabled')  # Khóa lại sau khi cập nhật
        window.after(1800000, update_weather)  # Cập nhật mỗi 30 phút

    def save_city():
        update_weather()  # Cập nhật thông tin thời tiết ngay khi lưu

    def update_time():
        # Lấy múi giờ Việt Nam
        vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')
        now = datetime.now(vn_tz)
        
        # Định dạng thời gian
        current_time = now.strftime("%H:%M:%S")
        current_date = now.strftime("%A, %d/%m/%Y")  # Thứ, ngày/tháng/năm
        
        # Cập nhật label
        time_label.config(text=f"{current_time}\n{current_date}")
        window.after(1000, update_time)  # Cập nhật mỗi giây

    def update_ai_face():
        ai_face = random.choice(AI_FACES)
        ai_face_label.config(text=ai_face)
        window.after(5000, update_ai_face)  # Cập nhật biểu cảm mỗi 5 giây

    window = tk.Tk()
    window.title("AI Assistant")
    
    # Thiết lập kích thước tối thiểu cho cửa sổ
    window.minsize(800, 600)  # Chiều rộng tối thiểu 800px, chiều cao tối thiểu 600px
    
    # Ngăn không cho thay đổi kích thước cửa sổ
    window.resizable(True, True)  # Cho phép thay đổi kích thước nhưng không nhỏ hơn minsize

    # Font chữ đẹp
    custom_font = font.Font(family="Helvetica", size=10, weight="bold")
    title_font = font.Font(family="Helvetica", size=16, weight="bold")
    designer_font = font.Font(family="Helvetica", size=8, slant="italic")
    time_font = font.Font(family="Helvetica", size=12, weight="bold")

    # Thêm tiêu đề và dòng thiết kế
    title_label = tk.Label(window, text="AI Thomas", font=title_font, fg="#0066cc")
    title_label.pack(pady=5)
    
    designer_label = tk.Label(window, text="Designed by Dr.ngominhtu", font=designer_font)
    designer_label.pack(pady=2)

    # Hiển thị thời gian thực
    time_label = tk.Label(window, font=time_font, justify=tk.LEFT)
    time_label.pack(anchor='ne', padx=10, pady=5)
    update_time()

    # Khung cho khuôn mặt AI
    ai_face_frame = tk.Frame(window)
    ai_face_frame.pack(side=tk.LEFT, padx=10, pady=10, anchor='nw')

    ai_face_label = tk.Label(ai_face_frame, text="", font=("Courier", 20), width=10, height=2)
    ai_face_label.pack()
    update_ai_face()

    # Thêm khung cho voice chat và trạng thái
    voice_frame = tk.Frame(ai_face_frame)
    voice_frame.pack(pady=10, fill='x')

    # Thêm nút voice chat
    voice_button = tk.Button(voice_frame, text="🎤", font=("Arial", 20), command=start_listening, width=3)
    voice_button.pack(side=tk.LEFT, padx=5)

    # Thêm ô hiển thị trạng thái
    status_label = tk.Label(voice_frame, text="", font=("Helvetica", 10), fg="#666666", width=20)
    status_label.pack(side=tk.LEFT, padx=5)

    # Khung chính cho nội dung
    main_frame = tk.Frame(window)
    main_frame.pack(side=tk.LEFT, fill='both', expand=True, padx=10, pady=10)

    # Khung cho thời tiết
    weather_frame = tk.Frame(main_frame)
    weather_frame.pack(fill='x', pady=5)

    city_label = tk.Label(weather_frame, text="Enter city name:", font=custom_font, width=15)
    city_label.pack(side=tk.LEFT)

    city_entry = tk.Entry(weather_frame, width=30, font=custom_font)
    city_entry.pack(side=tk.LEFT, padx=5)

    save_button = tk.Button(weather_frame, text="Save", command=save_city, font=custom_font, width=8)
    save_button.pack(side=tk.LEFT)

    # Khung hiển thị thời tiết với kích thước cố định
    weather_area = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, width=40, height=5, font=custom_font)
    weather_area.pack(pady=5, fill='x')
    weather_area.config(state='disabled')  # Khóa không cho chỉnh sửa

    # Khung cho chat
    chat_frame = tk.Frame(main_frame)
    chat_frame.pack(fill='x', pady=5)

    entry = tk.Entry(chat_frame, width=50, font=custom_font)
    entry.pack(side=tk.LEFT, padx=5, fill='x', expand=True)
    entry.bind("<Return>", on_submit)

    submit_button = tk.Button(chat_frame, text="Send", command=on_submit, font=custom_font, width=8)
    submit_button.pack(side=tk.LEFT)

    output_area = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, width=60, height=10, font=custom_font)
    output_area.pack(fill='both', expand=True, pady=5)

    window.mainloop()

if __name__ == "__main__":
    create_ui()