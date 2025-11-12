import streamlit as st
import google.generativeai as genai

# --- Cấu hình trang ---
st.set_page_config(page_title="Chatbot du lịch", page_icon="🤖")
st.title("🤖 Chatbot du lịch")

# --- Nhập API key ---
st.sidebar.header("🔐 Cấu hình API")
api_key = st.sidebar.text_input("Nhập Google API key của bạn:", type="password")

# Nếu chưa nhập API key thì dừng chương trình
if not api_key:
    st.warning("⚠️ Vui lòng nhập API key ở thanh bên trái để tiếp tục.")
    st.stop()

# --- Cấu hình Gemini ---
try:
    genai.configure(api_key=api_key)
    model_name = "models/gemini-2.5-flash"
    model = genai.GenerativeModel(model_name)
except Exception as e:
    st.error(f"Lỗi cấu hình API key: {e}")
    st.stop()

# --- Đọc dữ liệu từ file ---
with open("data_txt.txt", "r", encoding="utf-8") as f:
    data = f.read()

# --- Lưu lịch sử chat ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Hiển thị lịch sử chat ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- Ô nhập tin nhắn ---
if prompt := st.chat_input("Nhập câu hỏi của bạn..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # --- Gộp hội thoại ---
    conversation_history = "\n".join(
        [f"{'Người dùng' if m['role']=='user' else 'Trợ lý'}: {m['content']}" for m in st.session_state.messages]
    )

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

    try:
        response = model.generate_content(full_prompt)
        reply = response.text.strip()
    except Exception as e:
        reply = f"❌ Lỗi khi gọi API: {e}"

    with st.chat_message("assistant"):
        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})

# --- Nút reset chat ---
if st.button("🔁 Xóa lịch sử chat"):
    st.session_state.messages = []
    st.rerun()
