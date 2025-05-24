#   pyinstaller --onefile --windowed ai_assistant.py

import requests
import tkinter as tk
from tkinter import scrolledtext
from tkinter import font
import threading
from datetime import datetime
import pytz
from config import (
    DEEPSEEKR_API_URL,
    DEEPSEEKR_API_KEY,
    WEATHER_API_URL,
    WEATHER_API_KEY
)

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
        response = requests.post(DEEPSEEKR_API_URL, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        full_response = response.json().get("choices", [{}])[0].get("message", {}).get("content", "No response available.")
        return full_response
    except requests.exceptions.Timeout:
        return "Sorry, the request timed out. Please try again later."
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
        response = requests.get(WEATHER_API_URL, params=params, timeout=10)
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
    except requests.exceptions.Timeout:
        return "Sorry, the weather request timed out. Please try again later."
    except Exception as e:
        return f"Sorry, an error occurred when getting weather information: {str(e)}"

def create_ui():
    def on_submit(event=None):
        user_input = entry.get()
        if user_input:
            process_input(user_input)
            entry.delete(0, tk.END)

    def process_input(user_input):
        # Hiển thị câu hỏi của người dùng ngay lập tức
        output_area.config(state='normal')
        output_area.insert(tk.END, f"\nYou: {user_input}\n")
        output_area.config(state='disabled')
        output_area.see(tk.END)
        
        # Vô hiệu hóa nút gửi và hiển thị rõ là đang xử lý
        submit_button.config(state='disabled')
        entry.config(state='disabled')
        
        # Xử lý trong luồng riêng biệt
        def background_task():
            if user_input.lower().startswith("weather "):
                # Trích xuất tên thành phố
                if "in" in user_input.lower():
                    city = user_input.lower().split("in")[-1].strip()
                else:
                    city = user_input[8:].strip()
                response = get_weather(city)
            else:
                response = get_ai_response(user_input)
            
            # Cập nhật UI trong luồng chính
            window.after(0, lambda: update_ui(response))
            
        threading.Thread(target=background_task).start()
    
    def update_ui(response):
        # Hiển thị câu trả lời
        output_area.config(state='normal')
        output_area.insert(tk.END, f"AI: {response}\n\n")
        output_area.config(state='disabled')
        output_area.see(tk.END)
        
        # Kích hoạt lại các điều khiển
        submit_button.config(state='normal')
        entry.config(state='normal')
        entry.focus()

    def update_weather():
        city = city_entry.get()
        if city:
            def background_task():
                weather_info = get_weather(city)
                window.after(0, lambda: update_weather_ui(weather_info))
            
            threading.Thread(target=background_task).start()
        
        # Hẹn giờ cập nhật sau 30 phút
        window.after(1800000, update_weather)
    
    def update_weather_ui(weather_info):
        weather_area.config(state='normal')  # Mở khóa để cập nhật
        weather_area.delete(1.0, tk.END)
        weather_area.insert(tk.END, weather_info)
        weather_area.config(state='disabled')  # Khóa lại sau khi cập nhật

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

    window = tk.Tk()
    window.title("AI Thomas")
    
    # Thiết lập kích thước tối thiểu cho cửa sổ
    window.minsize(800, 600)  # Chiều rộng tối thiểu 800px, chiều cao tối thiểu 600px
    window.resizable(True, True)  # Cho phép thay đổi kích thước nhưng không nhỏ hơn minsize

    # Font chữ đẹp
    custom_font = font.Font(family="Helvetica", size=10, weight="bold")
    title_font = font.Font(family="Helvetica", size=16, weight="bold")
    designer_font = font.Font(family="Helvetica", size=8, slant="italic")
    time_font = font.Font(family="Helvetica", size=12, weight="bold")

    # Thêm tiêu đề và dòng thiết kế
    title_label = tk.Label(window, text="AI Thomas", font=title_font, fg="#df0a0a")
    title_label.pack(pady=5)
    
    designer_label = tk.Label(window, text="Designed by Dr.ngominhtu", font=designer_font)
    designer_label.pack(pady=2)

    # Hiển thị thời gian thực
    time_label = tk.Label(window, font=time_font, justify=tk.LEFT)
    time_label.pack(anchor='ne', padx=10, pady=5)
    update_time()

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

    output_area = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, width=60, height=20, font=custom_font)
    output_area.pack(fill='both', expand=True, pady=5)

    # Khởi tạo với một tin nhắn chào mừng
    output_area.config(state='normal')
    output_area.insert(tk.END, "Welcome to AI Thomas! How can I help you today?\n\n")
    output_area.config(state='disabled')

    window.mainloop()

if __name__ == "__main__":
    create_ui()