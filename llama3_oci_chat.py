#######################################################################
## The following code is free to use for the general public.
## The author makes no promises and provides no warranty.
## This code is meant to be a starting point for others to use.
## Initial code patterns developed with the assistance of 
##   Oracle Cloud Infrastructure's Generative AI Playground:
##   https://cloud.oracle.com/ai-service/generative-ai/playground/chat
#######################################################################
import oci


#################################################################
## UNIQUE CONFIG
##   Setup your unique config, like config file location, region
##   endpoint, and model for use
#################################################################
## get your configuration
config = oci.config.from_file(file_location='~/.oci/config', profile_name="DEFAULT")

## set the region in correspondence with the endpoint
config['region']='us-chicago-1'

## set the compartment ID where this will be run
compartment_id = config['tenancy']

## Service endpoint
endpoint = "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com"

## OCID of the model to use for interaction
## model below represents meta.llama-3.1-405b-instruct
# model_id="ocid1.generativeaimodel.oc1.us-chicago-1.amaaaaaask7dceyarleil5jr7k2rykljkhapnvhrqvzx4cwuvtfedlfxet4q"
## model below represents meta.llama-3.1-70b-instruct
model_id="ocid1.generativeaimodel.oc1.us-chicago-1.amaaaaaask7dceyaiir6nnhmlgwvh37dr2mvragxzszqmz3hok52pcgmpqta"

## set the timeouts for the interaction with the chat client
connection_timeout_seconds=10 # default is 10
read_timeout_seconds=240 # default is 60

## set the parameters for the chat interaction
## https://docs.oracle.com/en-us/iaas/Content/generative-ai/chat-models.htm#parameters-chat
max_tokens = 600
temperature = 1
frequency_penalty = 0
presence_penalty = 0
top_p = 0.75
top_k = -1


#################################################################
## CONSTANT SETUP
##   In this first block before the while statement:
##   we setup the client, initialize the models, 
##   and set the attributes that need to persist
#################################################################

## if using Instance Principals, be sure to setup your signer and then use it for authentication in the client creation below
## signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()

##  define the client
generative_ai_inference_client = oci.generative_ai_inference.GenerativeAiInferenceClient(config=config, service_endpoint=endpoint, retry_strategy=oci.retry.NoneRetryStrategy(), timeout=(connection_timeout_seconds,read_timeout_seconds))

## Initialize the Chat Details model
chat_details = oci.generative_ai_inference.models.ChatDetails()
chat_details.serving_mode = oci.generative_ai_inference.models.OnDemandServingMode(model_id=model_id)
chat_details.compartment_id = compartment_id

## Initialize the GenericChatRequest model
chat_request = oci.generative_ai_inference.models.GenericChatRequest()
chat_request.api_format = oci.generative_ai_inference.models.BaseChatRequest.API_FORMAT_GENERIC
chat_request.max_tokens = max_tokens
chat_request.temperature = temperature
chat_request.frequency_penalty = frequency_penalty
chat_request.presence_penalty = presence_penalty
chat_request.top_p = top_p
chat_request.top_k = top_k

#################################################################
## start the endless loop of asking questions 
##   (ctrl+c to end chat session)
#################################################################
while True:

    ## get the user prompt
    print("="*72)
    user_input=input("You: ")

    ## here is where you could insert some prompt engineering,
    ## such as asking it to cite its sources or giving direction
    ## on how to respond (voice)
    # if user_input[-1] not in [".","?","!"]:
    #     user_input+="."
    # user_input+=" Please be sure to cite your sources."

    ## create the content model for this question
    content = oci.generative_ai_inference.models.TextContent()
    content.text = user_input

    ## create a message model from that content
    message = oci.generative_ai_inference.models.Message()
    message.role = "USER"
    message.content = [content]

    ## If there has been any interaction so far, we need to append the message to the chat request
    if chat_request.messages:
        chat_request.messages.append(message)
    ## If this is the first run through, we need to initialize the messages attribute of the chat request
    else:
        chat_request.messages = [message]
    

    ## add the updated chat request to the chat
    chat_details.chat_request = chat_request
    ## send the chat detail to the chat method
    result = generative_ai_inference_client.chat(chat_details)

    ## print the results
    print("-"*72)
    print(result.data.chat_response.choices[0].message.content[0].text)
    ## append the chatbot's response to the chat_request messages list attribute
    ##   in order to maintain a conversation
    chat_request.messages.append(result.data.chat_response.choices[0].message)

    ## Detailed outputs if you'd like to see more info about the response
    # print("**************************Detail Chat Result**************************")
    # print(vars(result))
    # print("------------------------------------------------------------------------")
    # print(chat_request.messages)
