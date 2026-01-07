# Add Groq API Key to Streamlit Cloud - Step by Step

## Follow these exact steps:

### Step 1: Go to Your App Dashboard
- Visit: https://share.streamlit.io
- Find your app: **smartbi**
- Click on it

### Step 2: Click App Menu
- Look for the **⋯ (three dots)** menu in the top right corner
- Click it
- Select **Settings**

### Step 3: Go to Secrets
- In the Settings panel, find **Secrets** section
- Click on it (it may say "Add secrets" if empty)

### Step 4: Add the Secret
In the text editor that appears, paste:

```
GROQ_API_KEY = "your_actual_groq_api_key_from_console.groq.com"
```

### Step 5: Save
- Click the **Save** button
- Your app will automatically redeploy (wait 1-2 minutes)

### Step 6: Verify
- Once deployed, go to your app
- Click **🤖 AI Assistant** tab
- You should see: ✅ **Groq API is Active**

## If you still don't see Secrets option:

Try this direct link (replace YOUR_USERNAME):
```
https://share.streamlit.io/yaserqaissi264-ship-it/smartbi/main/smartbi_bundle.py
```

Then:
1. Click ⋯ menu → **Edit secrets in the app settings**
2. Or go to: https://share.streamlit.io/user/settings/apps

---

**Need help?** Contact Streamlit support or let me know if stuck!
