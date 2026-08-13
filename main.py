import os
import sys
from dotenv import load_dotenv
from chat import ChatSession

load_dotenv()


def main():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not set.")
        print("Copy .env.example to .env and add your API key.")
        sys.exit(1)

    session = ChatSession(api_key)
    print("Claude CLI Chatbot  (type 'exit' to quit, '/clear' to reset history)\n")

    while True:
        try:
            user_input = input("> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nBye!")
            break

        if not user_input:
            continue

        if user_input.lower() in ("exit", "quit"):
            print("Bye!")
            break

        if user_input == "/clear":
            session.clear()
            print("History cleared.\n")
            continue

        print()
        for chunk in session.send_message(user_input):
            print(chunk, end="", flush=True)
        print("\n")


if __name__ == "__main__":
    main()
