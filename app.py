import streamlit as st

st.set_page_config(
    page_title="UNGA Analysis - Azure",
    page_icon="🇺🇳",
    layout="wide"
)

st.title("🇺🇳 UNGA Analysis App")
st.markdown("**Successfully deployed to Azure App Service!**")

st.success("✅ Azure deployment working!")
st.info("The app is running on Azure App Service with P1V2 SKU.")

st.markdown("### 🚀 Deployment Details")
st.markdown("- **Resource Group:** unga-analysis-prod")
st.markdown("- **App Service Plan:** P1V2 (Premium V2)")
st.markdown("- **Location:** East US 2")
st.markdown("- **Runtime:** Python 3.11")

st.markdown("### 🌐 App URLs")
st.markdown("- **Main App:** https://unga-analysis-prod.azurewebsites.net")
st.markdown("- **Test App:** https://unga-analysis-simple.azurewebsites.net")

st.markdown("---")
st.markdown("**Ready for full application deployment!** 🚀")