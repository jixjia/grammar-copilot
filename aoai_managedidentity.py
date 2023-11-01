from azure.identity import DefaultAzureCredential, ChainedTokenCredential, ManagedIdentityCredential, EnvironmentCredential
import os, openai
from dotenv import load_dotenv

load_dotenv()
os.environ['AZURE_CLIENT_ID'] = os.getenv('AZURE_CLIENT_ID')
os.environ['AZURE_CLIENT_SECRET'] = os.getenv('AZURE_CLIENT_SECRET')
os.environ['AZURE_TENANT_ID'] = os.getenv('AZURE_TENANT_ID')

azure_credential = ChainedTokenCredential(EnvironmentCredential(), 
                                          ManagedIdentityCredential(), 
                                          DefaultAzureCredential())

ad_token = azure_credential.get_token("https://cognitiveservices.azure.com/.default")

openai.api_type = "azure_ad"
openai.api_key = ad_token.token
openai.api_base = 'http://cross-region-aoai.eastus.cloudapp.azure.com' # App GW
openai.api_version = '2023-08-01-preview'

messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Does Azure OpenAI support customer managed keys?"}
    ]

response = openai.ChatCompletion.create(
                engine='gpt-35-turbo', 
                messages=messages, 
                temperature=0,
                stop=None,
                frequency_penalty=0.3,
                presence_penalty=0.0
                )

output = response['choices'][0]['message']['content'].lstrip()
print(output)