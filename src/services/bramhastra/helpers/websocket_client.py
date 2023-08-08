import asyncio
import websockets

async def main():
    async with websockets.connect("ws://localhost:8000/ws") as websocket:
        while True:
            message = input("Enter a message: ")
            await websocket.send(message)
            response = await websocket.recv()
            print(f"Server says: {response}")

asyncio.get_event_loop().run_until_complete(main())