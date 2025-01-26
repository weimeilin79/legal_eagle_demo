# Legal Eagles in the Cloud: Hacking the Court System (Legally) with Google

The best part of *Breaking Bad* is the lawyer—and yes, I did binge-watch all seven seasons of *Better Call Saul*. Since then, I've imagined deftly navigating the complexities of the courtroom and delivering dramatic closing arguments. While my legal career may have taken a different turn, I'm excited to say that, with the help of AI, we might all be closer to that courtroom dream.

Today, we’re diving into how to use Google’s powerful AI tools—like Vertex AI, Firestore, and Cloud Run functions—to process and understand legal data, perform lightning-fast searches, and maybe, just maybe, help your imaginary client (or yourself) out of a sticky situation.

You might not be cross-examining a witness, but with our system, you’ll be able to sift through mountains of information, generate clear summaries, and present the most relevant data in seconds.

### Create a project

1.  In the Google Cloud Console, on the project selector page, select or create a Google Cloud project.
2.  Make sure that billing is enabled for your Cloud project. [Learn how to check if billing is enabled on a project](https://cloud.google.com/billing/docs/how-to/verify-billing-enabled).
3.  You'll use Cloud Shell, a command-line environment running in Google Cloud. Click **Activate Cloud Shell** at the top of the Google Cloud console.
4.  Once connected to Cloud Shell, verify that you're already authenticated and that the project is set to your project ID using the following command:
    ```bash
    gcloud auth list
    ```
5.  Use the following command to set your project:
    ```bash
    gcloud config set project <YOUR_PROJECT_ID>
    ```

### Enable the required APIs

Run the following command to enable the necessary Google Cloud APIs:

```bash
gcloud services enable storage.googleapis.com  \
                        run.googleapis.com  \
                        artifactregistry.googleapis.com  \
                        aiplatform.googleapis.com  \
                        eventarc.googleapis.com
```
### Generate code with help from Google Cloud Assist

**Google Cloud Shell** provides a browser-based IDE that is very convenient for developing and managing your cloud resources.

1. In the Google Cloud Console, look for the "Activate Cloud Shell" button in the top right toolbar (it looks like a terminal prompt icon: >_). Click on it.
Cloud Shell will open in a pane at the bottom of your browser window. It might take a moment to provision the environment.

2.In the Cloud Shell toolbar (t the top of the Cloud Shell pane), click on the "Open Editor" button (it looks like an open folder with a pencil).
This will open the Cloud Shell Code Editor in a new browser tab or window. You'll see a file explorer on the left side. 

3. Enable Gemini Code Assist in Cloud Shell IDE
    - Click on the **Cloud Code Sign-in** button in the bottom status bar as shown. Authorize the plugin as instructed. If you see **Cloud Code - no project** in the status bar, select that and then select the specific Google Cloud Project from the list of projects that you plan to work with.
    - Click on the **Code Assist** button in the bottom right corner as shown and select one last time the correct Google Cloud project. If you are asked to enable the Cloud AI Companion API, please do so and move forward. Once you've selected your Google Cloud project, ensure that you are able to see that in the Cloud Code status message in the status bar and that you also have Code Assist enabled on the right, in the status bar as shown below:

4. Download the Bootstrap Skeleton Project 
```
git clone <YOUR_GIT_REPOSITORY_URL_HERE>
```
After running this command in the Cloud Shell terminal, a new folder with the repository name will be created in your Cloud Shell environment.

5. In the Cloud Code Editor's Explorer pane (usually on the left side), you should now see the folder that was created when you cloned the Git repository `legal-eagle`, Open the root folder of your project in the Explorer. If the instructions mention navigating to a legal-eagle folder and then expecting a webapp subfolder within it, you should find and open the legal-eagle folder .


6. Create legal.py, 
    - In the Explorer pane within your opened **webapp** folder, right-click in the file explorer area.
    - Select "New File" from the context menu.
    - Enter the filename `legal.py` and press Enter. This will create an empty `legal.py` file and open it in the editor.

7. In the empty legal.py file in the Cloud Code Editor, you can use different methods to prompt Gemini Code Assist. Type a Comment Prompt: Start by typing a comment in legal.py that clearly describes what you want Gemini Code Assist to generate:

```
"""
Write a Python function called `ask_llm` that takes a user `query` as input. This function should use the `langchain` library to interact with a Vertex AI Gemini Large Language Model.  Specifically, it should:

1.  Create a `HumanMessage` object from the user's `query`.
2.  Create a `ChatPromptTemplate` that includes a `SystemMessage` and the `HumanMessage`. The system message should instruct the LLM to act as a helpful assistant in a courtroom setting, aiding an attorney by providing necessary information. It should also specify that the LLM should respond in a high-energy tone, using no more than 100 words, and offer a humorous apology if it doesn't know the answer.  
3.  Format the `ChatPromptTemplate` with the provided messages.
4.  Invoke the Vertex AI LLM with the formatted prompt using the `VertexAI` class (assuming it's already initialized elsewhere as `llm`).
5.  Print the LLM's `response`.
6.  Return the `response`.
7.  Include error handling that prints an error message to the console and returns a user-friendly error message if any issues occur during the process.  The Vertex AI model should be "gemini-1.5-flash-002".
"""
```

8. Right-click in the `legal.py` editor window after the comment block. Look for options in the context menu. Select **code generation** (the exact menu item might vary slightly depending on the Cloud Code version).

9. Carefully review the generated code
    - Does it roughly follow the steps you outlined in the comment?
    - Does it import necessary libraries (`langchain`, `vertexai`)?
    - Does it create a `ChatPromptTemplate` with `SystemMessage` and `HumanMessage`?
    - Does it invoke a Vertex AI LLM (assuming `llm` is initialized)?
    - Does it include basic error handling (`try...except`)?
    - Is the model name `"gemini-1.5-flash-002"` used?

If the generated code is good and mostly correct, you can accept it (often by pressing Tab or Enter for inline suggestions, or by clicking "Accept" for larger code blocks). If the generated code isn’t exactly what you want, or has errors, don't worry! Gemini Code Assist is a tool to assist you, not to write perfect code on the first try. Edit and modify the generated code to refine it, correct errors, and better match your requirements. You can further prompt Gemini Code Assist by adding more comments or asking specific questions in the Code Assist chat panel.

11. If you are still new to the SDK, here is a working example. Feel free to copy and paste this code into your legal.py:
```
import os
import signal
import sys
import vertexai
import random
from langchain_google_vertexai import VertexAI, VertexAIEmbeddings,VectorSearchVectorStore
from langchain.chains import RetrievalQA
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage


# Connect to resourse needed from Google Cloud
llm = VertexAI(model_name="gemini-1.5-flash-002")

def ask_llm(query):
    try:
        query_message = {
            "type": "text",
            "text": query,
        }
       
        input_msg = HumanMessage(content=[query_message])
        prompt_template = ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content=(
                        "You are a helpful assistant, and you are with the attorney in a courtroom, you are helping him to win the case by providing the information he needs "
                        "Don't answer if you don't know the answer, just say sorry in a funny way possible"
                        "Use high engergy tone, don't use more than 100 words to answer"
                       # f"Here are some past conversation history between you and the user {relevant_history}"
                       # f"Here are some contenxt that is relavant to the question {relevant_resource} that you might use"
                    )
                ),
                input_msg,
            ]
        )

        prompt = prompt_template.format()
        
        response = llm.invoke(prompt)
        print(f"response: {response}")

        return response
    except Exception as e:
        print(f"Error sending message to chatbot: {e}") # Log this error too!
        return f"Unable to process your request at this time. Due to the following reason: {str(e)}"

```

12. Create a function to handle a route that will respond to user's questions. Open main.py in the Cloud Shell Editor. Similar to how you generated ask_llm in `legal.py`, use Gemini Code Assist to Generate Flask Route and ask_question Function. Type in the following PROMPT as a comment in `main.py`:
```
"""
PROMPT:
Create a Flask endpoint that accepts POST requests at the '/ask' route. 
The request should contain a JSON payload with a 'question' field. Extract the question from the JSON payload. 
Call a function named ask_llm (located in a file named legal.py) with the extracted question as an argument. 
Return the result of the ask_llm function as the response with a 200 status code. 
If any error occurs during the process, return a 500 status code with the error message.
"""
```
If the generated code is good and mostly correct, you can accept it (often by pressing Tab or Enter for inline suggestions, or by clicking "Accept" for larger code blocks). If the generated code isn’t exactly what you want, or has errors, don't worry! Gemini Code Assist is there to assist you, not to write perfect code on the first attempt. Edit and modify the generated code to refine it, correct errors, and better match your requirements. You can further prompt Gemini Code Assist by adding more comments or by asking specific questions in the Code Assist chat panel.

13. By following these refined steps, you should be able to successfully enable Gemini Code Assist, set up your project, and leverage Gemini Code Assist to generate the `ask` function in your `main.py` file. If you are not fimiliar with Python, here is a working example, feel free to copy and paste this into your `main.py`

```
@app.route('/ask', methods=['POST'])
def ask_question():
    data = request.get_json()
    question = data.get('question')
    try:
        # call the ask_llm in legal.py
        answer_markdown = legal.ask_llm(question)

        
        print(f"answer_markdown: {answer_markdown}")

        # Return the Markdown as the response
        return answer_markdown, 200

    except Exception as e:
        return f"Error: {str(e)}", 500  # Handle errors appropriately
```

### Run the Application Locally in Cloud Shell

1. Open Cloud Shell Terminal: If you closed the Cloud Shell terminal pane, re-open it from the Cloud Shell toolbar ("Open Terminal" button) and run: 
```
cd ~/legal-eagle/webapp
python3 main.py
```
Observe Startup Messages: Look for startup messages in the Cloud Shell terminal output. Flask usually prints messages indicating that it's running and on what port. 
 * Running on http://127.0.0.1:8080
Keep the Terminal Running: Do not close the Cloud Shell terminal or stop the running python3 main.py process while you want to access the web preview. 
The  application needs to keep running to serve requests.

2. From the "Web preview" menu,choose **Preview on port 8080**. Cloud Shell will open a new browser tab or window with the web preview of your application.
3. In the application interface, type in a couple of questions and see how the LLM responds. If you look closely at the answers, you’ll likely notice it can hallucinate, be vague or generic, and sometimes misinterpret your questions.
