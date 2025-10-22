# Security Notice

**Developed by:** Mafizul Islam  
**Copyright:** © 2025 Mafizul Islam. All rights reserved.

## 🔒 API Key Protection

Your Azure OpenAI API key is stored in the `.env` file and is **automatically excluded** from Git commits.

### What's Protected:
- ✅ `.env` file is in `.gitignore`
- ✅ API keys won't be uploaded to GitHub
- ✅ Database files are excluded
- ✅ Virtual environment is excluded

### Quick Security Check:
```bash
git status  # Should NOT show .env file
```

### Production Deployment:
- Use Azure App Service environment variables
- Never commit API keys to version control
- Use Azure Key Vault for production secrets

## 🚨 Security Reminders

1. **Never share your .env file**
2. **Don't commit API keys to Git**
3. **Use environment variables in production**
4. **Rotate API keys regularly**
