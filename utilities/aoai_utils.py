import datetime
import uuid
import openai
import logging
import json
from . import config
from . import timeout_utils as tu
import os
from azure.identity import DefaultAzureCredential, ChainedTokenCredential, ManagedIdentityCredential, EnvironmentCredential

# Logging
logging.basicConfig(level=logging.WARNING)

class AOAIClient:
    def __init__(self, use_gpt4=False, use_appgw=False):
        if use_appgw:
            azure_credential = ChainedTokenCredential(EnvironmentCredential(), 
                                                    ManagedIdentityCredential(), 
                                                    DefaultAzureCredential())

            ad_token = azure_credential.get_token("https://cognitiveservices.azure.com/.default")
            openai.api_type = "azure_ad"
            openai.api_key = ad_token.token
            openai.api_base =  config.APPGW_ENDPOINT

        else:
            openai.api_type = 'azure'
            openai.api_key = config.AOAI_API_KEY
            openai.api_base =  config.AOAI_ENDPOINT
        
        openai.api_version = config.AOAI_API_VERSION
            
        if use_gpt4:
            self.model_name = config.GPT4_DEPLOYMENT
        else:
            self.model_name = config.GPT35_DEPLOYMENT


    def get_aoai_response(response, debug=False):
        output = response['choices'][0]['message']['content'].lstrip()
        
        if debug:
            print('Finish: ', response['choices'][0]['finish_reason'])
            print('Model: ', response['model'])
            print('Type: ', response['object'])
            print('Prompt Tokens: ', response['usage']['prompt_tokens'])
            print('Completion Tokens: ', response['usage']['completion_tokens'])
            print('Output:\n', output)
        return output


    def generate_prompts(context, draft_writing, tone_style, advanced_vocabulary, feedbacks, language):
        
        # Preprocess user inputs
        advanced_vocabulary = 'more' if advanced_vocabulary=='on' else 'less'
        
        chatHistory = []
        if feedbacks:
            # Fetch chat histroy in the order of assistant, user, assistant, user, ... 
            for idx, content in enumerate(feedbacks): 
                chatHistory.append({
                    'role': 'assistant' if idx%2==0 else 'user',
                    'content': content
                }) 

        use_context = f'\nBelow is additional information to help explain the context of writing:\n{context}.' if context else ''
        
        # Generate prompts
        systemInsructions = [{
            'role':'system', 
            'content': '''You are an excellent {language} teacher. 
                          Help review user's draft writing and rewrite it in {language} so that it is more concise, less verbose with improved readability. 
                          Tips: 
                          1. Use {advanced_vocabulary} advanced vocabularies
                          2. Write in {tone_style} tone. 
                          3. Only include your improved writing and DO NOT adde additional comments or double quotes.
                        '''.format(advanced_vocabulary=advanced_vocabulary, tone_style=tone_style, language=language)
        }]

        messages = [{
            'role':'user', 'content': '''hi, here is my draft writing. Please help improve its readability and make it less verbose. Thank you.
             draft writing:\n"{draft_writing}".\n{use_context}'''.format(draft_writing=draft_writing, use_context=use_context)
        }]


        return systemInsructions+messages+chatHistory


    @tu.with_timeout(config.TIMEOUT_SECONDS)
    def generate(self, context, draft_writing, tone_style, advanced_vocabulary, feedbacks, language, temperature=0.3):
        '''
        Input
            -- context: string
            -- draft_writing: string
            -- tone_style: string
            -- advanced_vocabulary: string
            -- active_feedback: list of string containing past user-agent interaction
        
        Output
            -- status: boolean
            -- response: string
        '''
        
        try:
            response = openai.ChatCompletion.create(
                engine=self.model_name, 
                messages=AOAIClient.generate_prompts(context,draft_writing,tone_style,advanced_vocabulary,feedbacks,language), 
                temperature=temperature,
                stop=None,
                frequency_penalty=0.3
                )
            
            return True, AOAIClient.get_aoai_response(response)
        
        except Exception as e:
            return False, str(e)


    @tu.with_timeout(config.TIMEOUT_SECONDS)
    def generate_stream(self, context, draft_writing, tone_style, advanced_vocabulary, feedbacks, language, temperature=0.3):
        '''
        Input
            -- context: string
            -- draft_writing: string
            -- tone_style: string
            -- advanced_vocabulary: string
            -- active_feedback: list of string containing past user-agent interaction
        
        Output
            -- response: generator object
        '''
                
        try:
            response = openai.ChatCompletion.create(
                engine=self.model_name, 
                messages=AOAIClient.generate_prompts(context,draft_writing,tone_style,advanced_vocabulary,feedbacks,language), 
                temperature=temperature,
                stop=None,
                frequency_penalty=0.3,
                stream=True
                )
            
            for line in response:
                if line['choices'] and line['choices'][0]['delta'].get('content') is not None:
                    yield line['choices'][0]['delta']['content']
        
        except Exception as e:
            yield f'Error occured. ({str(e)})'