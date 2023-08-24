import React, { useState } from 'react';

function VideoUpload() {
  const [result, setResult] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [isLoading, setIsLoading] = useState(false); // New state for loading

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  const handleAnalyze = async () => {
    if (selectedFile === null) {
      window.alert("Select a file");
      return;
    }

    setIsLoading(true); // Start loading animation

    const formData = new FormData();
    formData.append('video', selectedFile);

    try {
      const response = await fetch('http://127.0.0.1:5000/analyze', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      console.log(data);
      setResult(data);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setIsLoading(false); // Stop loading animation
    }
  };

  return (
    <div className="App">
      <h1>Person Detection App</h1>
      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
        <input type="file" accept="video/*" onChange={handleFileChange} />
        <button onClick={handleAnalyze} disabled={isLoading}>
          {isLoading ? 'Analyzing...' : 'Analyze Video'}
        </button>
      </div>
      {isLoading ? (
        <p>Loading...</p>
      ) : (
        result && (
          <div>
            {result.length > 0 ? (
              <div>
                <p>Analysis Results:</p>
                <ul>
                  {result.map((frame, index) => (
                    <li key={index}>
                      Frame {index + 1}: {frame[0].class} found at timestamp {frame[0].timestamp}sec.
                    </li>
                  ))}
                </ul>
              </div>
            ) : (
              <p>No person detected.</p>
            )}
          </div>
        )
      )}
    </div>
  );
}

export default VideoUpload;