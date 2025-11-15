# Deploy to Streamlit Community Cloud (100% Free)

## Why Streamlit Cloud?
- ✅ Completely free
- ✅ No credit card required
- ✅ Perfect for Python/Streamlit apps
- ✅ Auto-deployment from GitHub
- ✅ Built-in secrets management

## Step 1: Push to GitHub

```bash
cd "/home/kuldeep/Code/Capstone Project"

# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Add personalized learning path generator"

# Create a new repository on GitHub at https://github.com/new
# Then connect and push:
git remote add origin https://github.com/YOUR_USERNAME/learning-path-generator.git
git branch -M main
git push -u origin main
```

## Step 2: Deploy on Streamlit Cloud

1. Go to https://share.streamlit.io/
2. Click "Sign in with GitHub"
3. Click "New app" button
4. Configure:
   - **Repository:** `YOUR_USERNAME/learning-path-generator`
   - **Branch:** `main`
   - **Main file path:** `app.py`

5. **Add your API key** (Click "Advanced settings" before deploying):
   - In the "Secrets" section, add:
   ```toml
   GOOGLE_API_KEY = "your_actual_google_ai_api_key_here"
   ```

6. Click "Deploy!"

## Step 3: Get Your URL

After 2-3 minutes, you'll get a public URL like:
```
https://YOUR_USERNAME-learning-path-generator-app-XXXXX.streamlit.app
```

Share this URL for your capstone project demo! 🎉

## Updating Your App

Just push to GitHub and it auto-deploys:
```bash
git add .
git commit -m "Update feature"
git push
```

## Troubleshooting

**Problem:** "GOOGLE_API_KEY not found"
**Solution:** Make sure you added the secret in Advanced Settings, not as a regular environment variable

**Problem:** App crashes or timeout
**Solution:** Streamlit Cloud has resource limits. Your app should work fine, but if you hit limits, use caching:
```python
@st.cache_data
def cached_function():
    ...
```

**Problem:** Can't access GitHub
**Solution:** Make sure your repository is public (or give Streamlit access to private repos)
