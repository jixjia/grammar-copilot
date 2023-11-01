from flask import Flask, render_template, request, redirect, url_for, jsonify, session, Response
from flask_cors import CORS
from functools import wraps
import json
import time
import os
import logging
import requests
import openai
from datetime import datetime, timedelta
from utilities import config
from utilities import aoai_utils as au
from utilities import azuretable_utils as atu

# instantiate flask app
app = Flask(__name__)
app.secret_key = config.APP_SECRET
app.config['MAX_CONTENT_LENGTH'] = config.MAX_CONTENT_SIZE *1024*1024
CORS(app)


''' Authentication
'''
def register_session(email, first_name, last_name):
    session['username'] = email
    session['first_name'] = first_name.capitalize()
    session['last_name'] = last_name.capitalize()
    session.permanent = True
    app.permanent_session_lifetime = timedelta(days=config.SESSION_TIMEOUT)

def deregister_session():
    if 'username' in session.keys():
        session.pop('username', None)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/auth', methods=['POST'])
def auth():
    data = request.json
    username = data['email']
    password = data['password']

    print('[LOGIN]', username, password)
    # check if user exists in Azure Table
    results = atu.retrieve_entity(config.TABLE_NAME, f"RowKey eq '{username}'")

    if results and results[0]['data']['password']==password:       
        register_session(username, results[0]['data']['first_name'], results[0]['data']['last_name'])
        return jsonify({'status': 'ok'})
    else:
        return jsonify({'status': 'error', 'message': 'Invalid username or password'})

@app.route('/register', methods=['GET'])
def register():
    if 'username' in session.keys():
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/register_ajax', methods=['POST'])
def register_ajax():
    # get JSON post data
    data = request.json
    first_name = data['first_name']
    last_name = data['last_name']
    password = data['password']
    email = data['email']

    # save data to Azure Table
    status = atu.create_entity(email, json.dumps(data))
    
    if status:
        # auto login
        register_session(email, first_name, last_name)
        return jsonify({'status': 'ok'})
    else:
        return jsonify({'status': 'error', 'message': 'Unable to register user'})
    
@app.route('/login', methods=['GET'])
def login():
    if 'username' in session.keys():
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    deregister_session()
    return redirect(url_for('index'))


''' App Routes
'''
@app.route('/', methods=['GET'])
def index():
    if 'username' in session.keys():
        return render_template('index.html', templates=config.TEMPLATES, session=session)
    return redirect(url_for('login'))


@app.route('/run', methods=['POST'])
def run():
    try:
        data = request.form
        context = data['context'] if len(data['context'])>0 else None
        draft_writing = data['draft_writing']
        advanced_vocabulary = 'prefer' if 'advanced_vocabulary' in data and data['advanced_vocabulary']=='on' else 'prefer NOT'
        tone_style = data['tone_style']
        language = data['language'].capitalize()
        allow_feedback = True if 'allow_feedback' in data else False
        active_feedback = data['active_feedback']
        assistant_writing = data['assistant_writing']
        use_gpt4 = True if 'use_gpt4' in data and data['use_gpt4']=='on' else False

        # get Active Feedbacks for GenAI improvement
        feedbacks = [assistant_writing, active_feedback] if allow_feedback and len(active_feedback)>0 else None

        # instantiate AOAI client
        client = au.AOAIClient(use_gpt4)

        '''
        Streaming version
        '''
        return Response(client.generate_stream(
                                        context, 
                                        draft_writing, 
                                        tone_style, 
                                        advanced_vocabulary, 
                                        feedbacks, 
                                        language), 
                        mimetype='text/event-stream')
    
        '''
        Non streaming version
        '''
        success, output = client.generate(context, draft_writing, tone_style, advanced_vocabulary, feedbacks, language)
        
        if not success:
            return jsonify({'status': 'error', 'message': f'Process failed ({output}'})
        
        return jsonify({'status': 'ok', 'output': output})
        
    except Exception as e:
        if str(e.args[0]) == 'timeout':
            return jsonify({'status': 'error', 'message': 'Endpoint timed out. GPT model seems busy. Try again in a few minutes.'})
        
        return jsonify({'status': 'error', 'message': f'Exception occured {str(e.args)}'})


if __name__ == '__main__':
    app.run(port=5000, debug=True)
