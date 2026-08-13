import anthropic

MODEL = "claude-opus-5"
MAX_TOKENS = 4096


class ChatSession:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.history: list[dict] = []

    def send_message(self, text: str):
        self.history.append({"role": "user", "content": text})
        full_response = ""

        with self.client.messages.stream(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            messages=self.history,
        ) as stream:
            for chunk in stream.text_stream:
                full_response += chunk
                yield chunk

        self.history.append({"role": "assistant", "content": full_response})

    def clear(self):
        self.history = []
