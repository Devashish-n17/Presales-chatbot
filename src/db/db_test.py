from api1.db.db_conversations import store_conversation, get_last_conversations

store_conversation("What is AI?", "AI stands for Artificial Intelligence.")
store_conversation("Tell me about OpenAI.", "OpenAI is a leading AI research company.")

conversations = get_last_conversations(5)

for convo in conversations:
    print(f"🗨️ Q: {convo[0]}")
    print(f"🤖 A: {convo[1]}")
    print(f"🕒 Time: {convo[2]}")
    print("-" * 30)
