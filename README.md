# Profanity Alert Plugin

A Modmail plugin that monitors profanity usage in threads and sends alerts based on whether the message came from staff or customers.

## Features

- **Staff Profanity Detection**: When staff members use profanity in a thread, an alert is sent to a designated channel
- **Customer Profanity Detection**: When customers use profanity, an alert is sent to a channel and pings a role with blacklist permissions
- **Customizable Word List**: Add or remove words from the profanity filter
- **Configurable Roles**: Define which roles are considered "staff"

## Installation

### GitHub Repository Setup

1. Create a new repository on GitHub (can be private if you have GITHUB_TOKEN configured)
2. Create the following folder structure:

```
profanity_alert/
  └── profanity_alert.py
```

3. Upload the plugin code to `profanity_alert/profanity_alert.py`

### Installing the Plugin

Load the plugin using the Modmail bot:

```
?plugins add <your-github-username>/profanity_alert
```

Or if using a different branch:

```
?plugins add <your-github-username>/profanity_alert@branch-name
```

## Configuration

### Initial Setup

1. **Set Staff Alert Channel** (where staff profanity alerts go):
   ```
   ?profanityalert staffchannel #staff-alerts
   ```

2. **Set Customer Alert Channel** (where customer profanity alerts go):
   ```
   ?profanityalert customerchannel #customer-alerts
   ```

3. **Set Blacklist Role** (role to ping when customers swear):
   ```
   ?profanityalert blacklistrole @Moderator
   ```

4. **Set Staff Roles** (which roles count as staff):
   ```
   ?profanityalert staffroles @Staff @Moderator @Admin
   ```

### Commands

All commands require administrator permissions.

| Command | Description | Usage |
|---------|-------------|-------|
| `?profanityalert staffchannel` | Set/clear staff alert channel | `?pa staffchannel #channel` |
| `?profanityalert customerchannel` | Set/clear customer alert channel | `?pa customerchannel #channel` |
| `?profanityalert blacklistrole` | Set/clear blacklist role | `?pa blacklistrole @role` |
| `?profanityalert staffroles` | Set staff roles | `?pa staffroles @role1 @role2` |
| `?profanityalert addword` | Add word to filter | `?pa addword badword` |
| `?profanityalert removeword` | Remove word from filter | `?pa removeword word` |
| `?profanityalert config` | Show current settings | `?pa config` |

**Note:** `?pa` can be used as a shortcut for `?profanityalert`

## How It Works

1. The plugin monitors all messages sent in Modmail threads
2. When a message contains profanity, it checks if the sender is staff or a customer
3. **Staff profanity**: Sends an alert to the staff alert channel with details about who said what
4. **Customer profanity**: Sends an alert to the customer alert channel and pings the blacklist role

### Alert Format

**Staff Alert Example:**
```
⚠️ Staff Profanity Detected
Staff Member: @JohnDoe (123456789)
Thread: #ticket-username
Words Detected: damn, shit
Message: [first 1000 characters of the message]
```

**Customer Alert Example:**
```
@Moderator
⚠️ Customer Profanity Detected
User: @Customer (987654321)
Thread: #ticket-customer
Words Detected: fuck
Message: [first 1000 characters of the message]
```

## Default Profanity List

The plugin comes with a basic profanity filter. You can customize it by adding or removing words using the `addword` and `removeword` commands.

## Notes

- Bot messages are ignored
- Only works in Modmail threads (not regular channels)
- Profanity detection is case-insensitive
- Word boundary detection prevents false positives (e.g., "grass" won't trigger "ass")

## Support

If you encounter issues, check:
1. The bot has permission to send messages in your alert channels
2. Staff roles are correctly configured
3. The plugin is properly loaded (`?plugins loaded`)

For bugs or feature requests, open an issue on the GitHub repository.
