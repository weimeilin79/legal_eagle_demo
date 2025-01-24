import os
import flask
import legal 
from flask import Flask, request, render_template


app = Flask(__name__, template_folder='templates', static_folder='static')

"""
PROMPT:
Create a Flask route that handles GET requests at the root URL ('/') and renders the 'index.html' template.
"""
@app.route('/',methods=['GET'])
def index():
    return render_template('index.html')


"""
PROMPT:
Create a Flask endpoint that accepts POST requests at the '/ask' route. 
The request should contain a JSON payload with a 'question' field. Extract the question from the JSON payload. 
Call a function named ask_llm (located in a file named legal.py) with the extracted question as an argument. 
Return the result of the ask_llm function as the response with a 200 status code. 
If any error occurs during the process, return a 500 status code with the error message.
"""
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


# Add this block to start the Flask app when running locally
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
    # app.run(debug=True)




