

import os
import streamlit as st
import requests
import json
import wget
import time
import pandas as pd
from deep_translator import GoogleTranslator

import vertexai

from vertexai.generative_models import (
    FunctionDeclaration,
    Content,
    GenerativeModel,
    Part,
    Tool,
)

# TODO(developer): Update & uncomment below line
PROJECT_ID = "mymlb-448914"

# Initialize Vertex AI
vertexai.init(project=PROJECT_ID, location="us-central1")

from config import model, video_summarization_system_instructions, video_homerun_analysis_system_instructions

from src.utils import extract_csv_content, save_uploaded_file

def video_analysis(url: str):
    model = GenerativeModel(model_name="models/gemini-1.5-flash-002", system_instruction=video_homerun_analysis_system_instructions)
    response = model.generate_content(
        [
            Part.from_uri(
                url, mime_type="video/mp4"
            ),
            "Summarise that video please.",
        ]
    )
    print(response.text)

    return response.text

def get_team_information(any: str):
    """
    Get Team Information.

    Args:
    
    Returns:
        the data about the MLB team

    """
    data=""
    try:
        url = "https://statsapi.mlb.com/api/v1/teams/119"
        print("function calling MLB Team Url:"+url)
        st.write("function callingMLB Team Url:"+url)

        response = requests.get(url)
        data = response.text
    except:
        data={"response": "empty due to error on request calling"}
    return data

def get_player_information(any: str):
    """
    Get Player Information.

    Args:
    
    Returns:
        the data about the MLB player

    """
    data=""
    try:
        url = "https://statsapi.mlb.com/api/v1/people/660271"
        print("function calling MLB Player Url:"+url)
        st.write("function callingMLB Player Url:"+url)

        response = requests.get(url)
        data = response.text
    except:
        data={"response": "empty due to error on request calling"}
    return data

def call_function(function_call, functions):
    function_name = function_call.name
    function_args = function_call.args
    #print(function_name)
    #print(function_args)
    return functions[function_name](**function_args)

functions = {
#        "set_light_values": set_light_values,
        "get_team_information": get_team_information,
        "get_player_information": get_player_information

    }

def internationalization(): 
    input_text='''
    Here is a summary of the provided video.

This video shows a Major League Baseball game between the Los Angeles Dodgers and the St. Louis Cardinals.  Freddie Freeman of the Dodgers hits a two-run homerun, increasing the Dodgers' lead to 3-0. The homerun had an exit velocity of 101.7 mph, a launch angle of 33°, and a projected distance of 409 feet.
    '''
    translated_text = deep_translate(input_text, "es".split("_")[0], "en")
    st.write(translated_text)


def load_bundle(locale):
    # Load in the text bundle and filter by language locale.
    df = pd.read_csv("text_bundle.csv")
    df = df.query(f"locale == '{locale}'")
    # Create and return a dictionary of key/values.
    lang_dict = {df.key.to_list()[i]:df.value.to_list()[i] for i in range(len(df.key.to_list()))}
    return lang_dict

def deep_translate(input_text: str, src_language: str, target_language: str):
    #print(language)
    try:
        output_text=GoogleTranslator(source=src_language, target=target_language).translate(input_text)
    except:
        output_text = input_text 
    return output_text

def main():
    lang_options = {
        "English (US)":"en_US",
        "日本語":"ja_JP",
        "español (SP)": "es_SP"
    }
    locale = st.radio(label='Language', options=list(lang_options.keys()),  horizontal=True)
    # Note we use the selected human-readable locale to get the relevant
    # ISO locale code from the lang_options dictionary.
    lang_dict = load_bundle(lang_options[locale])

    #()

    #st.image("img/logo-lomoai.png", width=64)
    model_function_call = None
    st.title(lang_dict['title']) #'MyMLB AI Bot on Google Gemini')
    init_prompt = st.selectbox(
    lang_dict['initPrompt'], #'You might want to try these prompts...',
    [
     lang_dict['placeHolderPrompt'], #'<Click Me to Expand>',
     lang_dict['optionOne'], #'Get Team Information about Los Angeles Dodgers',
     lang_dict['optionTwo'], #'Get Player Information about Shohei Ohtani',
     lang_dict['optionThree'], #'Summarize Homerun Video',
     #'Verify Location?',
     #'Remind maintenance for Electrical Vehicle Car?',
     #'Display Charging Stations map for Electrical Vehicle Car?',
     ]
    )

    #st.header('Current Prompt')
    #instr = 'Hi there! Enter what you want to let me know here.'
    #if prompt := st.text_input(
    #    instr,
    #    value=init_prompt,
    #    placeholder=instr,  # Instruct the user to enter sth
    #    label_visibility='collapsed'  # Hide the label
    #):
    if init_prompt.find("ideo") != -1:
        with st.expander(lang_dict['summarizeVideoInstructions']): #"view Video Summarization System Intructions"):
            st.write(video_summarization_system_instructions)
        
        #st.image("img/logo-lomoai.png", width=96)

        st.header(lang_dict['header']) #"Major League Baseball Homerun Data csv file")
        uploaded_file = st.file_uploader(
            lang_dict['placeHolderHeader'], #"upload your csv file",
             type="csv")
    
        save_directory = "data"  # You can change this to your desired directory

        if uploaded_file is not None:
            # Ensure the data directory exists
            # Create the directory if it doesn't exist, ignoring errors if it already exists
            os.makedirs(save_directory, exist_ok=True)
            saved_file_path = save_uploaded_file(uploaded_file, save_directory)
            #model._system_instruction=system_instructions
            #model._tools=None
            chat_session = model.start_chat(
                history=[
                    Content(
                        role= "user",
                        parts= extract_csv_content(saved_file_path)
                    )
                ]
            )
            user_question = st.text_input(lang_dict['yourQuestions']) #"Your questions:")
            if user_question:
                print(user_question)
                if lang_options[locale].split("_")[0] != 'en':
                    user_question = deep_translate(user_question, lang_options[locale].split("_")[0],'en')
                response = chat_session.send_message(user_question)
                #st.write(response.text)
                print(response.text)
                json_response = json.loads(response.text)
                st.json(json_response)
                print(json_response)
                li = [item.get('url') for item in json_response]
                print(li)
                #li.insert(0,'<Click Me to Expand>')
                if li is not None:
                    with st.expander(lang_dict['analyzeVideoInstructions']):
                        st.write(video_homerun_analysis_system_instructions)

                    video_url_input=st.selectbox(lang_dict['analyseVideo'], li, placeholder=lang_dict['placeHolderAnalyseVideo'])
                    if video_url_input.startswith("https://"):
                        st.video(video_url_input)
                        video_details=video_analysis(video_url_input)
                        if video_details is not None:
                            print(video_details)
                            translated_video_details = deep_translate(video_details, 'en', lang_options[locale].split("_")[0])
                            st.write(translated_video_details)
    else:
        result = ''
        #print("call gen ai")
        if (model_function_call == None):
            tool = Tool(
                function_declarations=[FunctionDeclaration.from_func(get_team_information), FunctionDeclaration.from_func(get_player_information)],
            )
            model_function_call = GenerativeModel(model_name='gemini-1.5-flash-002',
                            tools=[tool]) #set_light_values, verify_location, get_car_location])

        #model._system_instruction=None
        #model._tools=[get_car_location, get_geofencing_list, set_light_values] #set_light_values, verify_location, get_car_location])
        chat = model_function_call.start_chat()
        response = chat.send_message(init_prompt) 
        #'Get Geofencing List.' 'Get Car Location'
        #'Dim the lights so the room feels cozy and warm.')
        #print (response.candidates[0].content.parts)
        if response != '':
            #if response.candidates[0].content.parts:
            #    print(response.candidates[0].content.parts)

            part = response.candidates[0].content.parts[0]

            # Check if it's a function call; in real use you'd need to also handle text
            # responses as you won't know what the model will respond with.
            if part.function_call:
                result = call_function(part.function_call, functions)

            #response = generate_content(prompt)
            print(result)
            if result != '':
                json_response = json.loads(result)
                print(json_response)
                if json_response.get("teams") is not None:
                    st.json(json_response["teams"][0])
                if json_response.get("people") is not None:
                    st.json(json_response["people"][0])
        
if __name__ == "__main__":
    main()
