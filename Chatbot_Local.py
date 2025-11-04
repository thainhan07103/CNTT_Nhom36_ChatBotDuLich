#AIzaSyDjldtlqP2r6MzCc0HJkUvkdJeP2G0H-BA  models/gemini-live-2.5-flash-preview
import google.generativeai as genai
import pandas as pd


# --- Cấu hình API key ---
genai.configure(api_key="AIzaSyDjldtlqP2r6MzCc0HJkUvkdJeP2G0H-BA")

# --- Xem model hợp lệ (nên dùng cái mới nhất) ---
# Ví dụ: models/gemini-1.5-flash hoặc models/gemini-1.5-pro
model_name = "gemini-2.0-flash"  # hoặc "gemini-1.5-pro"

# --- Tạo model ---
model = genai.GenerativeModel(model_name)

# --- Đọc dữ liệu từ file txt ---
with open("data.csv", "r", encoding="utf-8") as f:
    data = pd.read_csv(f)

# --- Vòng chat ---
print("🤖 Chatbot sẵn sàng! (gõ 'exit' để thoát)\n")

while True:
    question = input("🧠 Bạn: ")
    if question.lower() in ["exit", "quit"]:
        break

    prompt = f"""
Dưới đây là dữ liệu tham khảo:

{data}

Hãy trả lời câu hỏi của người dùng dựa trên dữ liệu trên.
Nếu không có thông tin trong dữ liệu, hãy nói 'Không tìm thấy thông tin trong dữ liệu.' 
Câu hỏi: {question}
"""

    # --- Gọi model ---
    response = model.generate_content(prompt)

    # --- In kết quả ---
    print("🤖 Chatbot:", response.text)
    print()
