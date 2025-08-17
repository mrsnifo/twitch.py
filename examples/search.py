from twitch import App
import asyncio


async def main():
    async with App('CLIENT_ID', 'CLIENT_SECRET') as app:
        # Search for channels matching query, limit results to 30 max.
        results = await app.application.search_channels('gaming', limit=30)

        # Display each channel result
        for result in results:
            print(result)

asyncio.run(main())