import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [transcription, setTranscription] = useState('');
  const [result, setResult] = useState('');
  const [error, setError] = useState('');
  const [task, setTask] = useState('');
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);

  // summary try
  // const [summary, setSummary] = useState('');
  const [inputText, setInputText] = useState('');  // New state variable for user input text
  const [summary, setSummary] = useState(''); // New state for summary



  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleFileUpload = async () => {
    if (!file) {
      setError('Please select an audio file');
      return;
    }
    setLoading(true);
    const formData = new FormData();
    formData.append("file", file);
    try {
      const response = await axios.post("http://127.0.0.1:5000/upload", formData);
      setTranscription(response.data.result.toLowerCase());
      setResult('');
      setTask('');
      setError('');
    } catch (err) {
      setError('Failed to upload the file. Please try again.');
      console.error('There was an error!', err);
    }
    setLoading(false);
  };

  const handleTextProcess = async (endpoint) => {
    if (!transcription) {
      setError('No transcription available for processing');
      return;
    }
    setLoading(true);
    setTask(endpoint);
    try {
      const postData = {
        text: transcription,
        question: (endpoint === 'answer' ? question : undefined)
      };
      const response = await axios.post(`http://127.0.0.1:5000/${endpoint}`, postData);
      setResult(response.data.result.toLowerCase());
      setError('');
    } catch (err) {
      setError(`Failed to process the text for ${endpoint}. Please try again.`);
      console.error('There was an error!', err);
    }
    setLoading(false);
  };

  // summary try
  const handleInputTextSubmit = async () => {  // New function to handle text input submission
    if (!inputText) {
      setError('Please enter some text to summarize');
      return;
    }
    setLoading(true);
    setTask('summarize');
    try {
      const response = await axios.post("http://127.0.0.1:5000/summarize", { text: inputText });
      // setResult(response.data.result);
      // console.log(response.data); // Debug: log the response
      setSummary(response.data.result);

      setError('');

    } catch (err) {
      setError('Failed to summarize the text. Please try again.');
      console.error('There was an error!', err);
    }
    setLoading(false);
  };


  return (
    <div className="App">
      <header>
        <h1>Text Summarization of CNN News</h1>
        <h1>Summarization, Translation, QA </h1>
      </header>
      <main>
        {/*summary try*/}
        <section className="input-text-section">  {/* New section for user input text */}
          <input
              type="text"
              value={inputText}
              onChange={e => setInputText(e.target.value)}
              placeholder="Enter text to summarize"
          />
          <button className="btn" onClick={handleInputTextSubmit}>Summarize Text</button>
        </section>
        {summary && (
          <section className="summary output">
            <article className="summary">
              <h3>Summary:</h3>
              <p>{summary}</p>
            </article>
          </section>
        )}



        <section className="upload-section">
          <input type="file" onChange={handleFileChange} accept="audio/*"/>
          <button className="btn" onClick={handleFileUpload}>Process</button>
        </section>
        {loading && <div className="loading">Loading...</div>}
        {error && <div className="error">{error}</div>}
        {transcription && (
            <section className="output">
              <article className="transcription">
                <h3>Transcription:</h3>
                <p>{transcription}</p>
              </article>
              <div className="controls">
                <input type="text" value={question} onChange={e => setQuestion(e.target.value)}
                       placeholder="Enter your question"/>
                <div className="buttons">
                  <button className="btn" onClick={() => handleTextProcess('translate')}>Translate</button>
                  <button className="btn" onClick={() => handleTextProcess('summarize')}>Summarize</button>
                  <button className="btn" onClick={() => handleTextProcess('answer')}>Answer Question</button>
                </div>
              </div>
              {result && (
                  <article className="result">
                    <h3>{task.charAt(0).toUpperCase() + task.slice(1)} Result:</h3>
                    <p>{result}</p>
                  </article>
              )}
            </section>
        )}
      </main>
    </div>
  );
}

export default App;
