import asyncio

from adapter.rest.server import start_web_server

async def main():
    await start_web_server()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
