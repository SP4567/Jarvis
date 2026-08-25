import asyncio
from server.core.orchestrator import orchestrator

async def main():
    queries = [
        'who are you?',
        'what can you do?',
        'hello jarvis how are you?',
        'what is the time right now?',
        'what is 45 times 12?',
        'jarvis open notepad',
        'who is Albert Einstein?',
        'check weather in London',
        'tell me a joke',
        'remind me to prepare presentation',
        'play synthwave on youtube',
        'inspect my screen'
    ]
    for q in queries:
        res = await orchestrator.handle_user_command(q)
        print(f"Q: {q}")
        print(f"A: [{res.get('agent_used')}] {res.get('text')}")
        print("-" * 50)

if __name__ == "__main__":
    asyncio.run(main())
