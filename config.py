import ollama


def chat(prompt, model="qwen2.5:14b", temperature=0.7):

    response = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": temperature},
    )

    return response["message"]["content"]
