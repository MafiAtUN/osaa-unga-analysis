# Deployment Guide

## Local Development

1. Clone the repository
2. Create virtual environment: `python -m venv venv`
3. Activate virtual environment: `source venv/bin/activate`
4. Install dependencies: `pip install -e .`
5. Set up environment variables (copy `src/unga_analysis/config/env.template` to `.env`)
6. Run the application: `streamlit run app.py`

## Azure Deployment

### Prerequisites
- Azure account with App Service access
- Azure CLI installed
- Environment variables configured

### Deployment Steps

1. **Prepare Environment**
   ```bash
   cp src/unga_analysis/config/env.template .env
   # Edit .env with your Azure OpenAI credentials
   ```

2. **Deploy to Azure**
   ```bash
   chmod +x scripts/azure-deploy.sh
   ./scripts/azure-deploy.sh
   ```

3. **Configure App Service**
   - Set environment variables in Azure Portal
   - Configure startup command: `streamlit run app.py --server.port 8000`
   - Set Python version to 3.9+

### Environment Variables

Required environment variables for Azure deployment:

```bash
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_ENDPOINT=your_endpoint
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
```

## Production Considerations

- Use Azure Key Vault for sensitive configuration
- Configure proper logging and monitoring
- Set up CI/CD pipeline for automated deployments
- Implement proper error handling and recovery
- Configure backup strategies for the database
