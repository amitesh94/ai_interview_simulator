import React, { useRef, useState } from "react";
import Webcam from "react-webcam";
import { authHeader } from "../utils/auth";

export default function Interview() {
  const webcamRef = useRef(null);

  // State
  const [recording, setRecording] = useState(false);
  const [mediaRecorder, setMediaRecorder] = useState(null);
  const [videoUrl, setVideoUrl] = useState(null);
  const [messages, setMessages] = useState([
    { from: "ai", text: "Welcome! Tell me about yourself." }
  ]);
  const [userInput, setUserInput] = useState("");

  // Start Recording
  const startRecording = () => {
    const stream = webcamRef.current.stream;
    const recorder = new MediaRecorder(stream);
    const chunks = [];

    recorder.ondataavailable = (e) => chunks.push(e.data);
    recorder.onstop = () => {
      const blob = new Blob(chunks, { type: "video/webm" });
      setVideoUrl(URL.createObjectURL(blob));
    };

    recorder.start();
    setMediaRecorder(recorder);
    setRecording(true);
  };

  // Stop Recording
  const stopRecording = () => {
    mediaRecorder.stop();
    setRecording(false);
  };

  const sendMessage = async () => {
  if (!userInput.trim()) return;

  // Add user message to UI
  setMessages((prev) => [...prev, { from: "user", text: userInput }]);

  try {
    const res = await fetch("http://127.0.0.1:8000/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...authHeader(),
      },
      body: JSON.stringify({ text: userInput }),
    });

    const data = await res.json();

    // Add AI reply to UI
    setMessages((prev) => [...prev, { from: "ai", text: data.reply }]);
  } catch (error) {
    setMessages((prev) => [
      ...prev,
      { from: "ai", text: "Error connecting to AI." }
    ]);
  }

  setUserInput(""); // Clear input
};

  return (
    <div className="min-h-screen bg-gray-100 p-6 flex flex-col items-center">

      {/* Page Title */}
      <h1 className="text-3xl font-bold mb-6">AI Interview Session</h1>

      {/* Webcam Section */}
      <div className="bg-white p-4 rounded-2xl shadow-lg mb-6">
        <Webcam
            ref={webcamRef}
            mirrored={true}
            forceScreenshotSourceSize={true}
            videoConstraints={{
                width: 640,
                height: 480,
                facingMode: "user",
  }}
        />
      </div>

      {/* Recording Buttons */}
      <div className="flex gap-4 mb-6">
        {!recording ? (
          <button
            onClick={startRecording}
            className="px-6 py-2 bg-green-600 text-white rounded-lg"
          >
            Start Recording
          </button>
        ) : (
          <button
            onClick={stopRecording}
            className="px-6 py-2 bg-red-600 text-white rounded-lg"
          >
            Stop Recording
          </button>
        )}
      </div>

      {/* Recorded Video Preview */}
      {videoUrl && (
        <video
          src={videoUrl}
          controls
          className="mb-8 rounded-xl shadow-lg"
          width="400"
        ></video>
      )}

      {/* Chat Section */}
      <div className="w-full max-w-2xl bg-white p-4 rounded-xl shadow">
        <div className="h-80 overflow-y-auto border-b mb-4 p-3 space-y-3">
          {messages.map((msg, index) => (
            <div
              key={index}
              className={`p-3 rounded-lg max-w-[75%] ${
                msg.from === "ai"
                  ? "bg-gray-200 self-start"
                  : "bg-blue-600 text-white self-end ml-auto"
              }`}
            >
              {msg.text}
            </div>
          ))}
        </div>

        {/* Input Box */}
        <div className="flex">
          <input
            type="text"
            placeholder="Type your answer..."
            className="flex-grow p-2 border rounded-l-lg"
            value={userInput}
            onChange={(e) => setUserInput(e.target.value)}
          />

          <button
            onClick={sendMessage}
            className="px-4 bg-blue-600 text-white rounded-r-lg"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
