import streamlit as st
import google.generativeai as genai

# --- Cấu hình API key ---
genai.configure(api_key="AIzaSyCOlUN4DdFZj2QKhOe7UKJwJirTaqlehCw")

# --- Khai báo model ---
model_name = "models/gemini-2.5-flash"  # hoặc "gemini-2.0-flash"
model = genai.GenerativeModel(model_name)

# --- Đọc dữ liệu từ file ---
with open("data_txt.txt", "r", encoding="utf-8") as f:
    data = f.read()

# --- Giao diện Streamlit ---
st.set_page_config(page_title="Chatbot du lịch", page_icon="🤖")
st.title("🤖 Chatbot du lịch")

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

    # --- Gộp lịch sử hội thoại để model nhớ ngữ cảnh ---
    conversation_history = ""
    for m in st.session_state.messages:
        role = "Người dùng" if m["role"] == "user" else "Trợ lý"
        conversation_history += f"{role}: {m['content']}\n"

    # --- Tạo prompt đầy đủ ---
    full_prompt = f"""
Bạn là trợ lý du lịch chuyên nghiệp.

Dưới đây là dữ liệu du lịch:
{data}

Hội thoại trước đó:
{conversation_history}

Trả lời câu hỏi mới nhất của người dùng một cách rõ ràng, dễ đọc.
- Nếu liệt kê địa điểm, hãy xuống dòng và dùng dấu • hoặc số thứ tự.
- Không cần mở đầu bằng 'Dưới đây là...' hay 'Theo dữ liệu...'.
- Giữ câu ngắn gọn, thân thiện, có thể ví dụ nếu cần.

Câu hỏi mới nhất: {prompt}
"""

    # --- Gọi Gemini ---
    response = model.generate_content(full_prompt)
    reply = response.text.strip()

    # --- Hiển thị phản hồi ---
    with st.chat_message("assistant"):
        st.markdown(reply)

    # --- Lưu phản hồi vào session ---
    st.session_state.messages.append({"role": "assistant", "content": reply})

# --- Nút reset chat ---
if st.button("🔁 Xóa lịch sử chat"):
    st.session_state.messages = []
    st.rerun()