from twitch.oauth import DeviceCodeFlow, Scopes
import asyncio


async def main():
    async with DeviceCodeFlow('CLIENT_ID', 'CLIENT_SECRET') as flow:
        # Request device code with required scopes
        device_code = await flow.request_device_code({Scopes.USER_READ_EMAIL})

        # Display authorization instructions to user
        print(f"Go to: {device_code.verification_uri}")
        print(f"Enter code: {device_code.user_code}")

        # Wait for user to authorize and receive access token
        token = await flow.wait_for_device_token(device_code.device_code)
        print(f"Access token: {token.access_token}")

        # Add user to the flow with tokens for future use
        await flow.add_user(token.access_token, token.refresh_token)


asyncio.run(main())