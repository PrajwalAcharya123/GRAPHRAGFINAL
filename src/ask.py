# src/ask.py
from query_pipeline import ask_question

def main():
    print("💬 Ask questions (type 'exit' to stop):")

    while True:
        q = input("\n👉 ")

        if q.lower() == "exit":
            print("👋 Exiting...")
            break

        try:
            ask_question(q)
        except Exception as e:
            print("❌ Error:", e)


if __name__ == "__main__":
    main()