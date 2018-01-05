# colloquium-reminder
App to automatize the colloquium tasks of DICE group.

## Key files

*email_pwd.txt* contains the email password for user *dice.colloquium at gmail*.

*client_secret.json* contains the Google Drive API credentials:

```json
{
  "web": {
    "client_id": "XXX.apps.googleusercontent.com",
    "client_secret": "YYY",
    "redirect_uris": ["https://www.example.com/oauth2callback"],
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://accounts.google.com/o/oauth2/token"
  }
}
```

## One-shot usage

```bash
$ python colloquium_reminder.py
```

## Cron jobs expected

* Once a day for checking new edits.
* Once a week for sending emails.
