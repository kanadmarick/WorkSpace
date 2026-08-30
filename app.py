import os

import gradio as gr
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


MODEL_ID = "Qwen/Qwen2.5-0.5B-Instruct"

tokenizer = None
model = None


def load_model():
    global model, tokenizer

    if model is not None and tokenizer is not None:
        return

    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
    )
    model.to("cuda" if torch.cuda.is_available() else "cpu")
    model.eval()


def respond(message, history, max_tokens, temperature, top_p):
    try:
        load_model()
        messages = history + [{"role": "user", "content": message}]
        prompt = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        generation_args = {
            "max_new_tokens": int(max_tokens),
            "pad_token_id": tokenizer.eos_token_id,
        }
        if temperature > 0:
            generation_args.update(
                do_sample=True,
                temperature=float(temperature),
                top_p=float(top_p),
            )

        with torch.inference_mode():
            output = model.generate(**inputs, **generation_args)

        response_tokens = output[0][inputs.input_ids.shape[1] :]
        response = tokenizer.decode(response_tokens, skip_special_tokens=True)
        return history + [
            {"role": "user", "content": message},
            {"role": "assistant", "content": response},
        ]
    except Exception as error:
        return history + [
            {"role": "user", "content": message},
            {"role": "assistant", "content": f"Model error: {error}"},
        ]


with gr.Blocks(title="Hugging Face Inference Playground") as demo:
    gr.Markdown("# Hugging Face Inference Playground\n`Qwen/Qwen2.5-0.5B-Instruct`")
    chatbot = gr.Chatbot(height=500)
    with gr.Row():
        message = gr.Textbox(placeholder="Ask the model anything...", scale=5)
        send = gr.Button("Send", variant="primary", scale=1)
    with gr.Row():
        max_tokens = gr.Slider(32, 1024, value=256, step=32, label="Max tokens")
        temperature = gr.Slider(0, 1.5, value=0.7, step=0.1, label="Temperature")
        top_p = gr.Slider(0.1, 1, value=0.9, step=0.05, label="Top-p")
    clear = gr.Button("Clear")

    inputs = [message, chatbot, max_tokens, temperature, top_p]
    message.submit(respond, inputs, chatbot).then(lambda: "", None, message)
    send.click(respond, inputs, chatbot).then(lambda: "", None, message)
    clear.click(lambda: [], None, chatbot)


if __name__ == "__main__":
    demo.launch(
        server_name=os.getenv("HOST", "127.0.0.1"),
        server_port=int(os.getenv("PORT", "7860")),
    )