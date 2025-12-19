import asyncio
import os
from interpreter import interpret_task
from dotenv import load_dotenv

# Load env to ensure we pick up changes if any


async def main():
    print("Testing interpreter...")
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or "your_" in api_key:
        print("WARNING: GEMINI_API_KEY is not set or is numeric/default. Verification will fail or rely on mocks.")
        print(f"Current Key: {api_key}")
    
    test_inputs = [
        "Buy groceries",
        "go out with the dog"
    ]

    for text in test_inputs:
        print(f"\nInput: '{text}'")
        try:
            result = await interpret_task(text)
            print("Result:", result.model_dump_json(indent=2))
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
