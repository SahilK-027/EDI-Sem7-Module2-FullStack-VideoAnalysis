import React, { useState, useEffect } from 'react';
import io from 'socket.io-client';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import './VideoUpload.scss'
import { useDropzone } from 'react-dropzone';

function ProgressBar({ progress, estimatedRemainingTime }) {
  const progressBarWidth = `${progress}%`;
  const estimatedTimeText = `Estimated remaining time: ${estimatedRemainingTime}`;

  return (
    <div className="progress-container">
      <div style={{ display: 'flex', alignItems: 'center' }}>
        <div className="progress-out">
          <div className="progress-bar" style={{ width: progressBarWidth }}></div>
        </div>
        <p style={{ display: 'flex', alignItems: 'center', width: '20%', justifyContent: 'center' }}>{progress.toFixed(2)}%</p>
      </div>

      <div className="estimated-time">
        {estimatedTimeText}
      </div>
    </div>
  );
}
function VideoUpload() {
  const [result, setResult] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [isLoading, setIsLoading] = useState(false); // New state for loading
  const [progressData, setProgressData] = useState({
    progress: 0,
    estimated_remaining_time: ''
  });

  const handleRefresh = () => {
    handleStop();
  };

  useEffect(() => {
    const socket = io('http://127.0.0.1:5000');

    socket.on('progress_update', (data) => {
      setProgressData(data);
    });

    window.addEventListener('beforeunload', handleRefresh);

    return () => {
      socket.disconnect();
      window.removeEventListener('beforeunload', handleRefresh);
    };
  }, []);  // Empty dependency array ensures the effect runs only once

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  const handleAnalyze = async () => {
    if (selectedFile === null) {
      toast.error('Please Select a file', {
        position: "top-center",
        autoClose: 4000,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: false,
        draggable: false,
        progress: undefined,
        theme: "dark",
      });
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
      setResult(data);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setIsLoading(false); // Stop loading animation
    }
  };

  const handleStop = async () => {
    toast.warning('Process has been Interrupted', {
      position: "top-center",
      autoClose: 4000,
      hideProgressBar: false,
      closeOnClick: true,
      pauseOnHover: false,
      draggable: false,
      progress: undefined,
      theme: "dark",
    });
    try {
      const response = await fetch('http://127.0.0.1:5000/stop');
      const data = await response.json();
      console.log(data);
    } catch (error) {
      console.error('Error:', error);
    }
  };
  const onDrop = (acceptedFiles) => {  
    if (!acceptedFiles[0].type.startsWith("video/")) {
      toast.error('Please Upload Video File', {
        position: "top-center",
        autoClose: 4000,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: false,
        draggable: false,
        progress: undefined,
        theme: "dark",
      });
      return;
    }
    setSelectedFile(acceptedFiles[0]);
  };
  const { getRootProps, getInputProps } = useDropzone({
    onDrop,
    accept: 'mp4',
    multiple: false,
  });

  return (
    <div className="App">
      <h1 style={{ textAlign: 'center', color: '#fff' }}>Video Analyzer</h1>
      <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
        <div {...getRootProps()} className="drop-zone">
          <input accept="mp4" {...getInputProps()} />
          {selectedFile ? (
            <p>Selected File: {selectedFile.name}</p>
          ) : (
            <>
              <p><i className="fa-solid fa-cloud-arrow-up"></i></p>
              <p>Drag and drop a video file here, or click to select a file.</p>
            </>
          )}
        </div>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '30px' }}>
          <button onClick={handleAnalyze} disabled={isLoading}>
            {isLoading ? 'Analyzing...' : 'Analyze Video'}
          </button>
          {

            isLoading ?
              (
                <button className='stop' onClick={handleStop} disabled={!isLoading}>
                  Stop
                </button>
              )
              :
              (
                null
              )
          }
        </div>
      </div>
      {isLoading ? (
        <>
          <div class="panel">
            <div class="scanner"></div>
            <ul class="something">
              <li></li>
              <li></li>
              <li></li>
              <li></li>
              <li></li>
              <li></li>
            </ul>
          </div>

          <ProgressBar progress={progressData.progress} estimatedRemainingTime={progressData.estimated_remaining_time} />
        </>
      ) : (
        result && (
          <div>
            {result.length > 0 ? (
              <div>
                <p>Analysis Results:</p>
                <ul>
                  {result.map((frame, index) => (
                    <li key={index}>
                      Frame {index + 1}: {frame[0].class} detected at timestamp {frame[0].timestamp.toFixed(2)} sec.
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

      <ToastContainer
        position="top-center"
        autoClose={4000}
        hideProgressBar={false}
        newestOnTop={false}
        closeOnClick
        rtl={false}
        pauseOnFocusLoss={false}
        draggable={false}
        pauseOnHover={false}
        theme="dark"
      />
    </div>
  );
}

export default VideoUpload;