import streamlit as st
import json
from chat import main, web_search

st.title("Presales Chatbot")
st.write("Ask me anything!")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

use_web_search = st.toggle("Use Google Search for latest data")

if prompt := st.chat_input("Type your question here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()

if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    last_prompt = st.session_state.messages[-1]["content"]

    with st.spinner("Generating Response..."):
        try:
            answer, sources = main(last_prompt)

            if answer.strip() == "Match Not Found." or not answer.strip():
                st.session_state.messages.append({"role": "assistant", "content": "No Documents Available."})
            else:
                formatted_message = f"**Answer:** {answer}\n\n"

                if use_web_search:
                    raw_results = web_search(last_prompt)
                    parsed_results = json.loads(raw_results)

                    search_results_text = "\n\n**Latest Web Search Results:**\n"
                    for res in parsed_results:
                        search_results_text += f"- [{res['Title']}]({res['Link']})\n"

                    formatted_message += search_results_text

                st.session_state.messages.append({"role": "assistant", "content": formatted_message})
        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.session_state.messages.append({"role": "assistant", "content": "Sorry, an error occurred while processing your request."})

    st.rerun()
