import os
import streamlit as st
import requests
import json
import time
import pandas as pd
from deep_translator import GoogleTranslator
import traceback
import vertexai

from vertexai.generative_models import (
    FunctionDeclaration,
    Content,
    GenerativeModel,
    Part,
    Tool,
)

# TODO(developer): Update & uncomment below line
GEMINI_MODEL=os.environ.get("GEMINI_MODEL")
PROJECT_ID = os.environ.get("GCP_PROJECT")
LOCATION = os.environ.get("GCP_REGION")
HOMERUN_PATHNAME = os.environ.get("GCS_HOMERUN")
TEXT_BUNDLE_PATHNAME=os.environ.get("GCS_TEXT_BUNDLE")
TEAM_PLAYERS_ROASTER_PATHNAME=os.environ.get("GCS_TEAM_PLAYERS_ROASTER")
TEAM_PLAYER_ROASTER_RELATION=os.environ.get("TEAM_PLAYER_ROASTER_RELATION")

# Initialize Vertex AI
vertexai.init(project=PROJECT_ID, location=LOCATION)

from config import video_summarization_system_instructions, video_homerun_analysis_system_instructions, team_player_information_system_instructions, safety_settings, generation_config

def video_analysis(url: str):
    video_homerun_analysis_model = GenerativeModel(model_name="models/"+GEMINI_MODEL, system_instruction=video_homerun_analysis_system_instructions.format(TeamPlayerRoasterRelation=TEAM_PLAYER_ROASTER_RELATION))
    response = video_homerun_analysis_model.generate_content(
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
        url = "https://statsapi.mlb.com/api/v1/teams/"+any #119
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
        url = "https://statsapi.mlb.com/api/v1/people/"+any #660271
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
    return functions[function_name](function_args["id"])

functions = {
        "get_team_information": get_team_information,
        "get_player_information": get_player_information

    }

def load_bundle(locale):
    # Load in the text bundle and filter by language locale.
    df = pd.read_csv(TEXT_BUNDLE_PATHNAME)
    df = df.query(f"locale == '{locale}'")
    # Create and return a dictionary of key/values.
    lang_dict = {df.key.to_list()[i]:df.value.to_list()[i] for i in range(len(df.key.to_list()))}
    return lang_dict

def deep_translate(input_text: str, src_language: str, target_language: str):
    #print(language)
    try:
        output_text=GoogleTranslator(source=src_language, target=target_language).translate(input_text)
    except:
        traceback.print_exc()
        output_text = input_text 
    return output_text

def extract_homerun_csv_content(pathname: str) -> list[Part]:
    """
    Extracts the content of a CSV file and returns it as a list of strings.

    Args:
        pathname (str): The path to the CSV file.

    Returns:
        list[Part]: A list of Parts containing the content of the CSV file, with start and end indicators.
    """
    parts = [Part.from_text(f"--- START OF CSV {pathname} ---")]
    df = pd.read_csv(pathname, header=None)
    for index, row in df.iterrows():
        parts.append(Part.from_text(" ".join(row)))
    parts.append(Part.from_text(f"--- END OF CSV {pathname} ---"))
    return parts

def extract_team_player_csv_content(pathname: str) -> list[Part]:
    """
    Extracts the content of a CSV file and returns it as a list of Part.

    Args:
        pathname (str): The path to the CSV file.

    Returns:
        list[Part]: A list of Parts containing the content of the CSV file, with start and end indicators.
    """
    parts = [Part.from_text(f"--- START OF CSV {pathname} ---")]
    df = pd.read_csv(pathname, sep=';', header=None)
    for index, row in df.iterrows():
        parts.append(Part.from_text(" ".join(row)))
    parts.append(Part.from_text(f"--- END OF CSV {pathname} ---"))
    return parts

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
    model_team_player_information = None

    st.title(lang_dict['title']) #'MyMLB AI Bot on Google Gemini')
    init_prompt = st.selectbox(
    lang_dict['initPrompt'], #'You might want to try these prompts...',
    [
     lang_dict['placeHolderPrompt'], #'<Click Me to Expand>',
     lang_dict['optionOne'], #'Get Team Information about Los Angeles Dodgers',
     lang_dict['optionTwo'], #'Get Player Information about Shohei Ohtani',
     lang_dict['optionThree'], #'Summarize Homerun Video',
     ]
    )

    if init_prompt.find("ideo") != -1 or init_prompt.find("ビデオ") != -1:
        model_video_summarization = GenerativeModel(
            model_name=GEMINI_MODEL,
            safety_settings=safety_settings,
            generation_config=generation_config,
            system_instruction=video_summarization_system_instructions
        )

        with st.expander(lang_dict['summarizeVideoInstructions']): #"view Video Summarization System Intructions"):
            st.write(video_summarization_system_instructions)
        
        #st.image("img/logo-lomoai.png", width=96)

        st.header(lang_dict['header']) #"Major League Baseball Homerun Data csv file")

        chat_session = model_video_summarization.start_chat(
                history=[
                    Content(
                        role= "user",
                        parts= extract_homerun_csv_content(HOMERUN_PATHNAME)
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
                #li.insert(0,lang_dict['placeHolderPrompt'])
                if li is not None:
                    with st.expander(lang_dict['analyzeVideoInstructions']):
                        st.write(video_homerun_analysis_system_instructions.format(TeamPlayerRoasterRelation=TEAM_PLAYER_ROASTER_RELATION))

                    video_url_input=st.selectbox(lang_dict['analyseVideo'], li, placeholder=lang_dict['placeHolderAnalyseVideo'])
                    if video_url_input.startswith("https://"):
                        st.video(video_url_input)
                        video_details=video_analysis(video_url_input)
                        if video_details is not None:
                            print(video_details)
                            translated_video_details = deep_translate(video_details, 'en', lang_options[locale].split("_")[0])
                            st.write(translated_video_details)
    elif init_prompt.startswith("<") and init_prompt.endswith(">"):
        print("wait for user choice")
    else:
        if (model_team_player_information == None):
            model_team_player_information = GenerativeModel(
                model_name=GEMINI_MODEL,
                safety_settings=safety_settings,
                generation_config=generation_config,
                system_instruction=team_player_information_system_instructions.format(TeamPlayerRoasterRelation=TEAM_PLAYER_ROASTER_RELATION)
            )
            team_player_chat_session = model_team_player_information.start_chat()
            #    history=[
            #        Content(
            #            role= "user",
            #            parts= extract_team_player_csv_content(HOMERUN_PATHNAME)
            #        )
            #    ]
        #)
        response = team_player_chat_session.send_message(init_prompt)
        print(response.text)
        json_response = json.loads(response.text)
        print(json_response)
        li = [item.get('url') for item in json_response]
        print(li)
        response = ''

        if (model_function_call == None):
            get_team_information_func = FunctionDeclaration(
                name="get_team_information",
                description="Get team information in a given team id",
                # Function parameters are specified in JSON schema format
                parameters={
                    "type": "object",
                    "properties": {
                        "id": {"type": "string", "description": "The team information of some given id."}
                    },
                },
            )
            get_player_information_func = FunctionDeclaration(
                name="get_player_information",
                description="Get player information in a given team player id",
                # Function parameters are specified in JSON schema format
                parameters={
                    "type": "object",
                    "properties": {
                        "id": {"type": "string", "description": "The team player information of some given id."}
                    },
                },
            )
            tool = Tool(
            #     function_declarations=[FunctionDeclaration.from_func(get_team_information), FunctionDeclaration.from_func(get_player_information)],
                 function_declarations=[get_team_information_func, get_player_information_func],
            )
            model_function_call = GenerativeModel(model_name=GEMINI_MODEL, tools=[tool])

        chat = model_function_call.start_chat()
        response = chat.send_message(init_prompt + " with id "+li[0])

        if response != '':
            part = response.candidates[0].content.parts[0]

            # Check if it's a function call; in real use you'd need to also handle text
            # responses as you won't know what the model will respond with.
            if part.function_call:
                result = call_function(part.function_call, functions)

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
