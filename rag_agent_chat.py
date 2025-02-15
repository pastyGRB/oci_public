#########################################################################
## The following code is free to use for the general public.
## The author makes no promises and provides no warranty.
## This code is meant to be a starting point for others to use.
## CREDITS:
##   Thank you to the following contributors that helped with this code:
##     Vasu Rangarajan, Oracle Cloud Infrastructure
##     Aditya Banerjee, Oracle Cloud Infrastructure
##     Amir Rezaeian, Oracle Cloud Infrastructure
#########################################################################


'''
This script interacts with a generative AI agent using Oracle Cloud Infrastructure (OCI) services. It includes functions to create a session for the AI agent and to chat with the AI agent using user input.
Functions:
    get_session(agent_endpoint_id, generative_ai_agent_runtime_client, generative_ai_agent_client, display_name=None, description=None):
    chat_with_ai(user_input, agent_endpoint_id, generative_ai_agent_runtime_client, session_id=None):
            generative_ai_agent_runtime_client (oci.generative_ai_agent_runtime.GenerativeAiAgentRuntimeClient): The client instance used to communicate with the generative AI agent.
            session_id (str, optional): An optional session ID to maintain context across multiple interactions. Defaults to None.
            str: The AI agent's response message content.
Usage:
    The script is executed as a standalone program. It authenticates using OCI configuration, sets up the necessary clients, and enters a loop to interact with the AI agent based on user input.
'''

import oci
import datetime


def get_session(agent_endpoint_id, generative_ai_agent_runtime_client, generative_ai_agent_client, display_name=None, description=None):
    """
    Creates a session for a generative AI agent if the agent endpoint requires a session.

    Args:
        agent_endpoint_id (str): The OCID of the agent endpoint.
        generative_ai_agent_runtime_client (oci.generative_ai_agent_runtime.GenerativeAiAgentRuntimeClient): The client to interact with the generative AI agent runtime.
        generative_ai_agent_client (oci.generative_ai_agent.GenerativeAiAgentClient): The client to interact with the generative AI agent.
        display_name (str, optional): The display name for the session. Defaults to None.
        description (str, optional): The description for the session. Defaults to None.

    Returns:
        str: The session ID if a session is created, otherwise None.
    """

    # Get the current date and time in UTC
    current_utc_time = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d_%H:%M:%S')

    # define the display_name and description if not set
    if not display_name:
        display_name = "chat_session_" + current_utc_time
    if not description:
        description = "Chat session started at " + current_utc_time

    # Set agent OCID and endpoint
    session_id = None

    # Get the agent endpoint information
    agent_endpoint_info: oci.generative_ai_agent.models.AgentEndpoint = generative_ai_agent_client.get_agent_endpoint(agent_endpoint_id).data

    # if this agent expects to use a session, then create one
    if agent_endpoint_info.should_enable_session:
        # Create a session
        create_session_response = generative_ai_agent_runtime_client.create_session(
            oci.generative_ai_agent_runtime.models.CreateSessionDetails(
                display_name =display_name,
                description = description
            ),
            agent_endpoint_id,
        )

        # Get the data from response
        session_id = create_session_response.data.id

    return session_id


def chat_with_ai(user_input, agent_endpoint_id, generative_ai_agent_runtime_client, session_id=None):
    """
    Interacts with a generative AI agent using the provided user input and returns the agent's response.

    Args:
        user_input (str): The message or query from the user to be sent to the AI agent.
        agent_endpoint_id (str): The endpoint ID of the AI agent to interact with.
        generative_ai_agent_runtime_client (oci.generative_ai_agent_runtime.GenerativeAiAgentRuntimeClient): 
            The client instance used to communicate with the generative AI agent.
        session_id (str, optional): An optional session ID to maintain context across multiple interactions. 
            Defaults to None.

    Returns:
        str: The AI agent's response message content.
    """

    # Chat with the AI
    chat_response = generative_ai_agent_runtime_client.chat(
                                agent_endpoint_id=agent_endpoint_id,
                                chat_details=oci.generative_ai_agent_runtime.models.ChatDetails(
                                                                        user_message=user_input,
                                                                        should_stream=False,
                                                                        session_id=session_id
                                                                        ),
                                allow_control_chars=True
                                ).data
    return chat_response.message.content.text



    

if __name__ == "__main__":

    # get the configuration details for authentication
    config = oci.config.from_file(file_location='~/.oci/config', profile_name="DEFAULT")

    # Set the agent endpoints - Chicago is used for example below - be sure to change them to the correct region
    agent_runtime_endpoint = "https://agent-runtime.generativeai.us-chicago-1.oci.oraclecloud.com"
    agent_endpoint = "https://agent.generativeai.us-chicago-1.oci.oraclecloud.com"

    # Set agent OCID and endpoint
    agent_endpoint_id = "ocid1.genaiagentendpoint.oc1........"

    # get the clients used for asking questions
    generative_ai_agent_runtime_client = oci.generative_ai_agent_runtime.GenerativeAiAgentRuntimeClient(
        config,
        service_endpoint=agent_runtime_endpoint
    )

    generative_ai_agent_client = oci.generative_ai_agent.GenerativeAiAgentClient(
        config,
        service_endpoint=agent_endpoint
    )

    # get the session id
    session_id=get_session(agent_endpoint_id, generative_ai_agent_runtime_client, generative_ai_agent_client)

    while True:
        ## get the user prompt
        print("="*72)
        user_input=input("You: ")
        print("-"*72)

        # return the response
        print(chat_with_ai(user_input, agent_endpoint_id, generative_ai_agent_runtime_client, session_id))
        print()