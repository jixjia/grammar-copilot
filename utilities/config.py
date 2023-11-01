import os
from dotenv import load_dotenv

load_dotenv()
os.environ['AZURE_CLIENT_ID'] = os.getenv('AZURE_CLIENT_ID')
os.environ['AZURE_CLIENT_SECRET'] = os.getenv('AZURE_CLIENT_SECRET')
os.environ['AZURE_TENANT_ID'] = os.getenv('AZURE_TENANT_ID')


'''
APP Settings
'''
APP_SECRET = 'grammar-copilot-jixjia'
MAX_CONTENT_SIZE = 200 #MB only used for nginx.conf
TIMEOUT_SECONDS = 30 #sec
SESSION_TIMEOUT = 30 #days

'''
TEMPLATES Settings
'''
TEMPLATES = [
    {'name': 'Interview Assessment', 'context': "I am writing a summary about an interview with a candidate for {JOB NAME}. The job requires strong skills in {SKILLS}, put emphasis on candidates experience in {EXPERIENCES}."},
    {'name': 'Business Email', 'context': "I am writing a business email about {KEY TOPIC}. In this email I wish to highlight {KEY ITEMS}. This emails needs to be worded professionally."},
    {'name': 'Essay', 'context': "This is an essay about a {KEY TOPIC}. I need to present my perspective on both Pros and Cons of the issue being discussed."}
]

'''
Azure OAI Settings
'''
AOAI_API_KEY = os.getenv('AOAI_API_KEY')
AOAI_ENDPOINT = os.getenv('AOAI_ENDPOINT')
APPGW_ENDPOINT = os.getenv('APPGW_ENDPOINT')
AOAI_API_VERSION = '2023-08-01-preview'
GPT35_DEPLOYMENT = "gpt-35-turbo"
GPT4_DEPLOYMENT = 'gpt-4'

# Azure NoSQL storage (for user storage)
TABLE_NAME = 'grammarcopilot'
TABLE_STORAGE_CONNECTION_STRING = f"DefaultEndpointsProtocol=https;AccountName=vapistorage;AccountKey={os.getenv('AZURE_STORAGE_KEY')};EndpointSuffix=core.windows.net"