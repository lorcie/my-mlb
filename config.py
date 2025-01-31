import vertexai
from vertexai.generative_models import (
    Content,
    FunctionDeclaration,
    GenerationConfig,
    GenerativeModel,
    SafetySetting,
    HarmCategory,
    HarmBlockThreshold,
    Part,
    Tool,
)

response_schema = {
    "type": "ARRAY",
    "items": {
        "type": "OBJECT",
        "properties": {
            "title": {"type": "STRING"},
            "url": {"type": "STRING"},
        },
        "required": ["title", "url"],
    },
}

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
   # "response_mime_type": "text/plain",
    "response_mime_type": "application/json", 
    "response_schema": response_schema
}
safety_settings = [
    SafetySetting(
        category=HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    ),
    SafetySetting(
        category=HarmCategory.HARM_CATEGORY_HARASSMENT,
        threshold=HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    ),
    SafetySetting(
        category=HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        threshold=HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    ),
    SafetySetting(
        category=HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        threshold=HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    ),
]

video_summarization_system_instructions = '''
You are an expert of Major League Baseball Data (team, player, homerun,...) Analysis.

You will be given Major League Baseball CSV File with following headers :
- play_id : alphanumeric video play id
- title : video title
- ExitVelocity : exit velocity of homerun
- HitDistance : hit distance of homerun
- LaunchAngle : launch angle of homerun
- video : video clip identification

The user may request to query about player information, and also for some homerun parameters (exitVelocity, HitDistance, LaunchAngle, score).
 
You will apply following Major League Baseball video homerun analysis rules :
- match the user request with the video title field and if needed with homerun parameters fields
- return only up to 3 rows unless the user precises more rows in his query

- You will return the following video details : title field and video identification url

'''

video_homerun_analysis_system_instructions= '''
Your task is to answer the user's question using the Major League Baseball Team Players Roaster declared in the <DATA> section below.
    - You can consider that the Player (name or jerseyId) extracted automatically from the video should belong to the Team Roaster declared in the <TEAM_PLAYERS> subsection of the <DATA> section
    - All players associated to some team id in TEAM_PLAYERS section belong to the same team declared in TEAMS section identified by unique TeamId
    
    <DATA>
    <TEAMS>
    {TeamId|TeamName
    108|Los Angeles Angels
    119|Los Angleles Dodges
    }
    </TEAMS>
    <TEAM_PLAYERS>
    {TeamId|PlayerName|PlayerJerseyId
    119|Shohei Ohtani|17
    }
    <TEAM_PLAYER>
    </DATA>

    <INSTRUCTION>
    You should provide a quick 2 or 3 sentence summary of what is happening in the major League Baseball Homerun video, and give information about the teams, the players and score extracted from the video, also the exit velocity, launch angle, projected distance normally available at end of the video.
    <INSTRUCTION>

    QUESTION:

'''

team_player_information_system_instructions= '''
Your task is to answer the user's question using the Major League Baseball Team Players Roaster declared in the <DATA> section below.
    - You can consider that the Team name extracted automatically from the user query should match a row n the <TEAMS> subsection of the <DATA> section.
    - You can consider that the Player (name or jerseyId) extracted automatically from the user query should belong to the Team Roaster declared in the <TEAM_PLAYERS> subsection of the <DATA> section. You can just return the Player Id value if the user query is about the Player Information
    - All players associated to some team id in TEAM_PLAYERS section belong to the same team declared in TEAMS section identified by unique TeamId
    
    <DATA>
    <TEAMS>
    {TeamId|TeamName
    108|Los Angeles Angels
    109|Arizona Diamondbacks
    110|Baltimore Orioles
    111|Boston Red Sox
    112|Chicago Cubs
    113|Cincinnati Reds
    114|Cleveland Guardians
    115|Colorado Rockies
    116|Detroit Tigers
    117|Houston Astros
    118|Kansas City Royals
    119|Los Angleles Dodges
    120|Washington Nationals
    121|New York Mets
    133|Athletics
    134|Pittsburgh Pirates
    135|San Diego Padres
    136|Seattle Mariners
    137|San Francisco Giants
    138|St. Louis Cardinals
    139|Tampa Bay Rays
    140|Texas Rangers
    141|Toronto Blue Jays
    142|Minnesota Twins
    143|Philadelphia Phillies
    144|Atlanta Braves
    145|Chicago White Sox
    146|Miami Marlins
    147|New York Yankees
    158|Milwaukee Brewers
    }
    </TEAMS>
    <TEAM_PLAYERS>
    {TeamId|PlayerName|PlayerJerseyId|PlayerId
    119|Shohei Ohtani|17|660271
    }
    <TEAM_PLAYER>
    </DATA>

    <INSTRUCTION>
    Just return only the Team Id if the user query is about the Team Information, and return only the PLayer Id if the user query is about Player Information
    <INSTRUCTION>

    QUESTION:

'''
