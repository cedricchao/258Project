from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
from DeepDataMiningLearning.hfaudio.inference import MyAudioInference
import torch
from transformers import pipeline
from transformers import AutoTokenizer
from transformers import pipeline
from transformers import AutoModelForSeq2SeqLM

# Load models


# Initialize translation pipeline (English to Chinese)
translation_pipeline = pipeline("translation_en_to_zh", model="Helsinki-NLP/opus-mt-en-zh")


# Initialize summarization pipeline with a different model
summarization_pipeline = pipeline("summarization", model="t5-base")

# Initialize question-answering pipeline with a different model
qa_pipeline = pipeline('question-answering', model='distilbert-base-uncased-distilled-squad')
# def perform_translation(text, target_language="de"):
#     return translation_pipeline(text, tgt_lang=target_language)[0]['translation_text']

def perform_summarization(text):
    tokenizer = AutoTokenizer.from_pretrained("./models/t5")
    model = AutoModelForSeq2SeqLM.from_pretrained("./models/t5")

    # Load the trained model
    summarizer = pipeline("summarization", model=model, tokenizer=tokenizer, framework="pt")
    summary = summarizer(text, max_length=150, min_length=50, do_sample=False)
    return summary[0]['summary_text']
    # return summarization_pipeline(text)[0]['summary_text']


# def perform_question_answering(question, context):
#     return qa_pipeline(question=question, context=context)['answer']


app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes and methods

# Configurations
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'wav'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Perform model inference
        model_name = "facebook/wav2vec2-large-robust-ft-libri-960h"
        task = "audio-asr"
        device = "cuda:0" if torch.cuda.is_available() else "cpu"
        mycache_dir = "./output"

        audio_inference = MyAudioInference(model_name, task=task, target_language='eng', cache_dir=mycache_dir)
        result = audio_inference(file_path)

        os.remove(file_path)  # Clean up after processing
        return jsonify({'result': result})

    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/translate', methods=['POST'])
def translate_text():
    data = request.get_json()
    text = data.get('text')
    # Assuming the Helsinki-NLP model is loaded as `translation_pipeline`
    result = translation_pipeline(text)
    return jsonify({'result': result[0]['translation_text']})

@app.route('/answer', methods=['POST'])
def answer_question():
    data = request.get_json()
    context = data.get('text')
    question = data.get('question')
    if not question:
        return jsonify({'error': 'No question provided'}), 400
    if not context:
        return jsonify({'error': 'No context provided'}), 400
    answer = qa_pipeline(question=question, context=context)
    return jsonify({'result': answer['answer']})

# @app.route('/summarize', methods=['POST'])
# def summarize_text():
#     data = request.get_json()
#     text = data.get('text')
#     summary = perform_summarization(text)
#     return jsonify({'result': summary})


# @app.route('/summarize', methods=['POST'])
# def summarize():
#     data = request.get_json()
#     text = data.get('text', '')
#     if not text:
#         return jsonify({'error': 'No text provided'}), 400
#     summary = summarization_pipeline(text, max_length=150, min_length=30, do_sample=False)
#     #
#     # tokenizer = AutoTokenizer.from_pretrained("./models/t5")
#     # model = AutoModelForSeq2SeqLM.from_pretrained("./models/t5")
#     #
#     # # Load the trained model
#     # summarizer = pipeline("summarization", model=model, tokenizer=tokenizer, framework="pt")
#     # summary = summarizer(text, max_length=150, min_length=50, do_sample=False)

    # return jsonify({'summary': summary[0]['summary_text']})

# Function to perform summarization
def perform_summarization_text(text):
    #  Load the tokenizer and model
    tokenizer = AutoTokenizer.from_pretrained("./models/t5")
    model = AutoModelForSeq2SeqLM.from_pretrained("./models/t5")

    # Load the trained model
    summarizer = pipeline("summarization", model=model, tokenizer=tokenizer, framework="pt")
    summary = summarizer(text, max_length=150, min_length=50, do_sample=False)

    return summary
    # summary = summarization_pipeline(text, max_length=48, min_length=30, do_sample=False)
    # return summary[0]['summary_text']



# @app.route('/summarize', methods=['POST'])
# def summarize_text():
#     data = request.get_json()
#     text = data.get('text')
#     if not text:
#         return jsonify({'error': 'No text provided'}), 400
#
#     summary = perform_summarization_text(text)
#
#     return jsonify({'result': summary})
@app.route('/summarize', methods=['POST'])
def summarize_text():
    data = request.get_json()
    text = data['text']
    summary = perform_summarization(text)
    return jsonify({"result": summary})


if __name__ == '__main__':
    app.run(debug=True)