"""
chatbot_google_studio_repl_updated.py
Phiên bản REPL nâng cao: kết hợp tìm kiếm trên nhiều cột (title, content, tags, region)
và chạy liên tục (REPL). Dùng Google Studio AI (Gemini-pro) để trả lời.

Hướng dẫn sử dụng:
1) Cài thư viện:
   pip install pandas rapidfuzz requests

2) Mở file và điền API key vào biến API_KEY bên dưới (thay "YOUR_GOOGLE_API_KEY_HERE").

3) Đặt file CSV `south_vn_travel.csv` trong cùng thư mục (mẫu có sẵn).

4) Chạy:
   python chatbot_google_studio_repl_updated.py

Gõ 'exit' hoặc 'quit' để thoát chương trình.
"""

import time, json
import pandas as pd
from rapidfuzz import process, fuzz
from collections import defaultdict
import requests

# ========== ĐIỀN API KEY Ở ĐÂY ==========
API_KEY = "AIzaSyDjldtlqP2r6MzCc0HJkUvkdJeP2G0H-BA"  # <-- Thay bằng key thật
# =======================================

MODEL = "gemini-2.5-flash"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
CSV_PATH = "./south_vn_travel.csv"

# --- Search ---
def combined_search(query, df, top_k=6):
    """
    Kết hợp fuzzy search trên title, content, tags và boost theo region.
    Trả về danh sách dict: {'index','score','row'} sắp xếp theo score giảm dần.
    """
    titles = df['title'].astype(str).tolist() if 'title' in df.columns else ['']*len(df)
    contents = df['content'].astype(str).tolist() if 'content' in df.columns else ['']*len(df)
    tags = df['tags'].astype(str).tolist() if 'tags' in df.columns else ['']*len(df)
    regions = df['region'].astype(str).tolist() if 'region' in df.columns else ['']*len(df)

    # Compute fuzzy matches for each field (full lists)
    title_matches = process.extract(query, titles, scorer=fuzz.WRatio, limit=len(titles))
    content_matches = process.extract(query, contents, scorer=fuzz.WRatio, limit=len(contents))
    tag_matches = process.extract(query, tags, scorer=fuzz.WRatio, limit=len(tags))

    score_map = defaultdict(float)
    # weights
    w_title, w_content, w_tag, w_region_boost = 0.6, 0.25, 0.15, 25.0

    for text, score, idx in title_matches:
        score_map[idx] += w_title * (score / 100.0)
    for text, score, idx in content_matches:
        score_map[idx] += w_content * (score / 100.0)
    for text, score, idx in tag_matches:
        score_map[idx] += w_tag * (score / 100.0)

    q_lower = query.lower()
    # boost by region mentions in query (exact substring match, case-insensitive)
    for idx, reg in enumerate(regions):
        try:
            if isinstance(reg, str) and reg.strip() and reg.lower() in q_lower:
                score_map[idx] += w_region_boost
        except Exception:
            continue

    # If nothing scored (all zero), fallback to simple region/tag filters or top rows
    if not any(score_map.values()):
        # try region filter: look for any region token in query that matches df['region']
        candidate_idxs = []
        for idx, reg in enumerate(regions):
            if isinstance(reg, str) and reg.strip() and reg.lower() in q_lower:
                candidate_idxs.append(idx)
        if not candidate_idxs:
            # try tag matching via simple substring
            for idx, t in enumerate(tags):
                if isinstance(t, str) and any(tok in q_lower for tok in t.lower().split(',')):
                    candidate_idxs.append(idx)
        if not candidate_idxs:
            candidate_idxs = list(range(min(len(df), top_k)))
        for i in candidate_idxs:
            score_map[i] += 1.0

    # Normalize/convert to 0..100-like scores and sort
    scored = [(idx, val) for idx, val in score_map.items()]
    scored.sort(key=lambda x: x[1], reverse=True)
    results = []
    for idx, raw in scored[:top_k]:
        results.append({
            "index": int(idx),
            "score": float(raw * 100),  # map back to 0..100-ish
            "row": df.iloc[idx].to_dict()
        })
    return results


# --- Prompt builder ---
def build_prompt(question, hits, include_history=None):
    context_parts = []
    for i, h in enumerate(hits, start=1):
        r = h["row"]
        context_parts.append(
            f"{i}. {r.get('title')} ({r.get('region')}): {r.get('short_description')} -- {r.get('address')}"
        )
    context_text = "\n".join(context_parts)
    history_text = ""
    if include_history:
        history_text = "\n\nLịch sử (ngắn):\n" + "\n".join(include_history[-6:])
    prompt = (
        f"Dưới đây là thông tin tham khảo về du lịch miền Nam Việt Nam:\n{context_text}\n"
        f"{history_text}\n\nHỏi: {question}\nTrả lời ngắn gọn bằng tiếng Việt, nêu tên địa điểm, 1 câu mô tả và địa chỉ. Nếu không đủ thông tin, ghi 'Không đủ thông tin'."
    )
    return prompt


# --- API call ---
def ask_gemini(prompt):
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": API_KEY,
    }
    body = {"contents": [{"parts": [{"text": prompt}]}]}
    resp = requests.post(URL, headers=headers, json=body, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        return json.dumps(data, ensure_ascii=False, indent=2)


# --- Main REPL ---
def load_data(path=CSV_PATH):
    try:
        return pd.read_csv(path)
    except FileNotFoundError:
        print(f"⚠️ Không tìm thấy {path}. Hãy đặt file CSV cùng thư mục.")
        raise

def main():
    if "YOUR_GOOGLE_API_KEY_HERE" in API_KEY or not API_KEY.strip():
        print("⚠️ Bạn chưa điền API key! Mở file và điền key vào biến API_KEY.")
        return

    try:
        df = load_data()
    except FileNotFoundError:
        return

    print(f"✅ Đã tải {len(df)} địa điểm từ {CSV_PATH}.")
    print("Gõ 'exit' hoặc 'quit' để thoát.\n")

    history = []

    while True:
        try:
            question = input("Bạn hỏi: ").strip()
            if not question:
                print("Nhập câu hỏi (không để trống) hoặc 'exit' để thoát.")
                continue
            if question.lower() in ("exit", "quit"):
                print("Thoát chương trình. Bye!")
                break

            # Use combined_search (many fields)
            hits = combined_search(question, df, top_k=6)

            # If user mentions a region explicitly, ensure we include all rows from that region (no duplicates)
            q_lower = question.lower()
            # Try match common variants for 'Cần Thơ' etc.
            for region in df['region'].unique():
                try:
                    if isinstance(region, str) and region.strip() and region.lower() in q_lower:
                        region_rows = df[df['region'].str.lower().str.contains(region.lower(), na=False)]
                        extra = []
                        for i, row in region_rows.iterrows():
                            if not any(h['index'] == i for h in hits):
                                extra.append({"index": int(i), "score": 90.0, "row": row.to_dict()})
                        # prepend region-specific results so they appear first
                        hits = extra + hits
                except Exception:
                    continue

            # Build prompt with top 3 context rows
            prompt = build_prompt(question, hits[:3], include_history=history)

            print("\n--- Prompt (preview) ---")
            print(prompt if len(prompt) < 1200 else prompt[:1200] + "\n...[truncated]")

            try:
                answer = ask_gemini(prompt)
            except requests.exceptions.RequestException as e:
                print(f"⚠️ Lỗi khi gọi API: {e}")
                print("Thử lại sau 2s...")
                time.sleep(2)
                continue

            print("\n💬 AI trả lời:")
            print("-" * 60)
            print(answer)
            print("-" * 60)

            history.append(f"Q: {question}")
            history.append(f"A: {answer[:200]}")
            if len(history) > 40:
                history = history[-40:]

        except KeyboardInterrupt:
            print("\nNhận SIGINT — thoát chương trình. Bye!")
            break
        except Exception as e:
            print(f"⚠️ Lỗi không mong muốn: {e}")
            time.sleep(0.5)
            continue


if __name__ == "__main__":
    main()
