import yaml
import streamlit_authenticator as stauth

# load the configuration file
with open('config.yaml') as file:
    config = yaml.safe_load(file)

# create the authenticator
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)
