import os
from langfuse.decorators import observe

# -------------------------------------------------------------
# BƯỚC QUAN TRỌNG: ĐIỀN API KEYS CỦA BẠN VÀO ĐÂY
# Lấy keys từ: http://localhost:3001 -> Settings -> API Keys
# -------------------------------------------------------------
os.environ["LANGFUSE_PUBLIC_KEY"] = "pk-lf-ce5e2400-0d0f-4ae6-8977-cc4ddab36d00"
os.environ["LANGFUSE_SECRET_KEY"] = "sk-lf-4aa5dd1c-8373-4ee3-8284-92f565074884"
os.environ["LANGFUSE_HOST"] = "http://localhost:3001"

@observe()
def fake_llm_call(prompt: str):
    # Langfuse sẽ tự động ghi lại hàm này thành một "trace"
    print(f"Đang xử lý prompt: {prompt}")
    return "Langfuse thực sự rất tuyệt vời!"

if __name__ == "__main__":
    print("Đang gửi fake trace lên Langfuse...")
    fake_llm_call("Xin chào, Langfuse có tuyệt vời không?")
    print("\nĐã gửi Trace lên Langfuse thành công!")
    print("Vui lòng mở http://localhost:3001, vào mục Traces để kiểm tra và chụp Screenshot.")
