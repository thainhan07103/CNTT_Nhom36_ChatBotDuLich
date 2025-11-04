import streamlit as st
import google.generativeai as genai
import pandas as pd

# --- Cấu hình API key ---
genai.configure(api_key="AIzaSyDjldtlqP2r6MzCc0HJkUvkdJeP2G0H-BA")

# --- Khai báo model ---
model_name = "models/gemini-2.0-flash"  # hoặc "gemini-2.0-flash"
model = genai.GenerativeModel(model_name)

# --- Đọc dữ liệu từ file ---
with open("data.csv", "r", encoding="utf-8") as f:
    data = pd.read_csv(f)

# --- Giao diện Streamlit ---
st.set_page_config(page_title="Chatbot Gemini", page_icon="🤖")
st.title("🤖 Chatbot Gemini (Streamlit)")
st.caption("Dữ liệu được nạp từ file `data.csv`")

# --- Lưu lịch sử chat ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Hiển thị lịch sử chat ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- Ô nhập tin nhắn ---
if prompt := st.chat_input("Nhập câu hỏi của bạn..."):
    # Lưu tin nhắn người dùng
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # --- Tạo prompt cho model ---
    full_prompt = f"""
Dưới đây là dữ liệu tham khảo:

{data}

Hãy trả lời câu hỏi của người dùng dựa trên dữ liệu trên.
Nếu không có thông tin trong dữ liệu, hãy nói 'Không tìm thấy thông tin trong dữ liệu.' 
Câu hỏi: {prompt}
"""

    # --- Gọi Gemini ---
    response = model.generate_content(full_prompt)
    reply = response.text

    # Hiển thị phản hồi
    with st.chat_message("assistant"):
        st.markdown(reply)

    # Lưu phản hồi vào session
    st.session_state.messages.append({"role": "assistant", "content": reply})

# --- Nút reset chat ---
if st.button("🔁 Xóa lịch sử chat"):
    st.session_state.messages = []
    st.experimental_rerun()
