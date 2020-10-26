import json
import ibm_watson
import os
from dotenv import load_dotenv
load_dotenv()
import pandas as panda
from ibm_watson import ApiException
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

wa_version = os.getenv("WA_VERSION")
wa_apikey = os.getenv("WA_APIKEY")
wa_url = os.getenv("WA_URL")
wa_skill = os.getenv("WA_SKILL")

if(wa_version == '' or wa_apikey == '' or wa_url == ''):
    print("No or invalid Watson Assistant credentials detected. Check your credentials and try again.")
else:
    print("Starting Watson Assistant dialog export...")

    authenticator = IAMAuthenticator(wa_apikey)

    assistant_service=ibm_watson.AssistantV1(
        version = wa_version,
        authenticator = authenticator
    )

    assistant_service.set_service_url(wa_url)

    # move back to one try/except statement

    try:
        print("Downloading dialog...")
        workspace_response = assistant_service.get_workspace(
            workspace_id = wa_skill,
            export=True
        ).get_result()
    except (ApiException, Exception) as ex:
        print(" download failed: " + str(ex))

    try:
        formattedOutputDict = []

        for node in workspace_response['dialog_nodes']:
            outputText = ""
            if 'output' in node:
                if 'generic' in node['output']:
                    print()
                    print(json.dumps(node['output']))
                    print()
                    for item in node['output']['generic']:
                        if item['response_type'] == "text":
                            for response in item['values']:
                                outputText += "\n" + response['text'] + "\n"
                        # if item['response_type'] == "image":
                        #     outputText += str(item)
                        if item['response_type'] == "option":
                            outputText += str(item)
                        if item['response_type'] == "connect_to_agent":
                            outputText += "\nCONNECT TO AGENT\n"
                        if item['response_type'] == "search_skill":
                            outputText += "\nSEARCH SKILL\n"

                        if 'title' in node:
                            title = node['title']
                        else:
                            title = 'NONE'

            thisNode = {'title': title, 'conditions': node['conditions'], 'dialog_node': node['dialog_node'], 'outputText': outputText}
            formattedOutputDict.append(thisNode)

        df = panda.DataFrame(formattedOutputDict)
        print(df)

        df.to_csv("./dialog-export.csv", index=False)

        print("Dialog downloaded ✅")
        print()
    except (Exception) as ex:
        print(" conversion failed: " + str(ex))
