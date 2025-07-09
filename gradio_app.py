import gradio as gr
from rag_model import chatbot

# Load model and index ONCE
bot = chatbot("my_resume.pdf")

# Main logic to answer questions
def ask(query):
    return bot.query(query)

# Define Gradio UI
demo = gr.Interface(
    fn=ask,
    inputs=gr.Textbox(label="Ask something based on your resume"),
    outputs="text",
    title="Resume RAG Assistant",
    description="Upload your resume once (internally) and ask anything about it."
)

# Run locally (ignored by HF Spaces)
if __name__ == "__main__":
    demo.launch()
