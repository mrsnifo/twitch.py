---
title: "twitch.py Core Concepts - App, EventSub, and OAuth Explained"
description: "Understand the three core components of twitch.py: the main App class for API calls, EventSub for real-time notifications, and OAuth for authentication. Learn which tool to use for your bot or application."
icon: octicons/question-16
search:
  exclude: true
---

# Concepts

The library is built around three essential components that work together:

- **[App](#app)**
- **[EventSub](#eventsub)** 
- **[OAuth](#oauth)**

## App

The main class that handles API calls and authentication. Manages tokens, provides access to Helix API endpoints, and handles user management. Use this for fetching data from Twitch without real-time events.

## EventSub

Real-time notifications for follows, subs, chat messages, etc. Inherits from App.

**ClientUser**: Single user only. EventSub can only use one access token per connection, so this is for personal tools. Has access to user-specific EventSub subscriptions that ClientApp can't use.

**ClientApp**: Most common. For bots handling multiple users/channels. Uses availability-based shard selection to connect to the first available shard in your conduit.

**MultiShardClientApp**: Production scale. Creates multiple WebSocket connections instead of switching shards. Some larger bots use around 20 shards or less.

## OAuth

Auth-focused tools for token validation, refresh, and revocation. Inherits from App.

Supports **Device Code Flow** - no HTTP server required. Other flows need your own server or third-party service like Supabase etc.

**Architecture**: Use separate apps for web auth and scripts with `user_authorization_grant` EventSub subscription.


## Pick Your Tool

- Just need data? **App**
- Personal tool? **ClientUser**  
- Multi-channel bot? **ClientApp**
- Thousands of channels? **MultiShardClientApp**