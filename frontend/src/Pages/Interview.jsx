import React, { useRef, useState, useEffect } from "react";
import Webcam from "react-webcam";
import { authHeader } from "../utils/auth";

export default function Interview() {
  const webcamRef = useRef(null);

  const [recording, setRecording] = useState(false);
  const [mediaRecorder, setMediaRecorder] = useState(null);
  const [videoUrl, setVideoUrl] = useState(null);

  const [messages, setMessages] = useState([
    { from: "ai", text: "Welcome! The interview will now begin." },
  ]);

  const [userInput, setUserInput] = useState("");

  // =======================================================
  // 🔊 AUTO PLAY FIRST QUESTION AT PAGE LOAD
  // =======================================================
  useEffect(() => {
    playAudioQuestion();
  }, []);

  // =======================================================
  // 🔊 FETCH & PLAY AI QUESTION AUDIO
  // =======================================================
  const playAudioQuestion = async () => {
    const token = localStorage.getItem("token");

    const res = await fetch("http://127.0.0.1:8000/ask", {
      headers: { Authorization: `Bearer ${token}` },
    });

    const data = await res.json();

    // Play AI question audio
    const audio = new Audio(`http://127.0.0.1:8000/uploads/${data.audio}`);
    audio.play();

    // Show question text
    setMessages((prev) => [...prev, { from: "ai", text: data.question }]);
  };

  // =======================================================
  // 🔥 UPLOAD + TRANSCRIBE + EVALUATE
  // =======================================================
  const uploadVideo = async (blob) => {
    const formData = new FormData();
    formData.append("file", blob, "interview.webm");

    const token = localStorage.getItem("token");

    // ⬆ Upload
    const uploadRes = await fetch("http://127.0.0.1:8000/upload_video", {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
      body: formData,
    });

    const uploadData = await uploadRes.json();
    if (!uploadData.filename) {
      setMessages((prev) => [
        ...prev,
        { from: "ai", text: "❌ Error uploading file." },
      ]);
      return;
    }

    const filename = uploadData.filename;

    // ✍ TRANSCRIBE
    const transRes = await fetch(
      `http://127.0.0.1:8000/transcribe?filename=${filename}`,
      {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      }
    );

    const transData = await transRes.json();
    const transText = transData.text || "⚠️ Unable to transcribe.";

    setMessages((prev) => [
      ...prev,
      { from: "user", text: `(Transcription) ${transText}` },
    ]);

    // 📊 EVALUATE ANSWER
    const evalRes = await fetch("http://127.0.0.1:8000/evaluate", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ text: transText }),
    });

    const evalData = await evalRes.json();

    setMessages((prev) => [
      ...prev,
      { from: "ai", text: `📊 Evaluation:\n${evalData.evaluation}` },
    ]);

    // 🎤 ASK NEXT QUESTION
    await playAudioQuestion();
  };

  // =======================================================
  // 🎥 START RECORDING
  // =======================================================
  const startRecording = async () => {
    const audioStream = await navigator.mediaDevices.getUserMedia({
      audio: true,
    });

    const videoStream = webcamRef.current.stream;

    const combinedStream = new MediaStream([
      ...videoStream.getVideoTracks(),
      ...audioStream.getAudioTracks(),
    ]);

    const recorder = new MediaRecorder(combinedStream);
    const chunks = [];

    recorder.ondataavailable = (e) => chunks.push(e.data);

    recorder.onstop = async () => {
      const blob = new Blob(chunks, { type: "video/webm" });
      setVideoUrl(URL.createObjectURL(blob));
      await uploadVideo(blob);
    };

    recorder.start();
    setMediaRecorder(recorder);
    setRecording(true);
  };

  // =======================================================
  // ⏹ STOP RECORDING
  // =======================================================
  const stopRecording = () => {
    mediaRecorder.stop();
    setRecording(false);
  };

  // =======================================================
  // 💬 SEND TEXT MESSAGE (OPTIONAL)
  // =======================================================
  const sendMessage = async () => {
    if (!userInput.trim()) return;

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

      setMessages((prev) => [...prev, { from: "ai", text: data.reply }]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        { from: "ai", text: "❌ Error connecting to AI." },
      ]);
    }

    setUserInput("");
  };

  return (
    <div className="min-h-screen bg-gray-100 p-6 flex flex-col items-center">
      <h1 className="text-3xl font-bold mb-6 text-gray-800">
        🎤 AI Interview Session
      </h1>

      {/* Top Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full max-w-5xl">
        {/* AI Avatar */}
        <div className="bg-white p-4 rounded-2xl shadow-lg">
          <h3 className="text-xl font-semibold mb-2 text-center">AI Interviewer</h3>
          <video
            autoPlay
            muted
            loop
            className="rounded-xl w-full shadow"
            src="https://cdn.pixabay.com/video/2023/03/15/153833-809022617_large.mp4"
          />
        </div>

        {/* User Webcam */}
        <div className="bg-white p-4 rounded-2xl shadow-lg">
          <h3 className="text-xl font-semibold mb-2 text-center">Your Camera</h3>
          <Webcam
            ref={webcamRef}
            audio={true}
            muted={true}
            mirrored={true}
            className="rounded-xl shadow"
            videoConstraints={{
              width: 640,
              height: 480,
              facingMode: "user",
            }}
          />
        </div>
      </div>

      {/* Recording Buttons */}
      <div className="flex gap-4 mt-6">
        {!recording ? (
          <button
            onClick={startRecording}
            className="px-6 py-3 bg-green-600 text-white rounded-lg shadow hover:bg-green-700 transition"
          >
            ▶️ Answer Question
          </button>
        ) : (
          <button
            onClick={stopRecording}
            className="px-6 py-3 bg-red-600 text-white rounded-lg shadow hover:bg-red-700 transition"
          >
            ⏹ Stop Recording
          </button>
        )}
      </div>

      {/* Video Preview */}
      {videoUrl && (
        <div className="mt-6">
          <h3 className="text-lg font-semibold mb-2 text-center">
            Recorded Answer Preview
          </h3>
          <video
            src={videoUrl}
            controls
            className="rounded-xl shadow-lg w-96"
          />
        </div>
      )}

      {/* Chat UI */}
      <div className="w-full max-w-3xl bg-white mt-10 p-5 rounded-xl shadow-xl">
        <h2 className="text-xl font-semibold mb-4">💬 Interview Chat</h2>

        <div className="h-80 overflow-y-auto border rounded-xl p-4 mb-4 bg-gray-50 space-y-3">
          {messages.map((msg, index) => (
            <div
              key={index}
              className={`p-3 rounded-lg max-w-[75%] ${
                msg.from === "ai"
                  ? "bg-gray-200 text-gray-800 self-start"
                  : "bg-blue-600 text-white self-end ml-auto"
              }`}
            >
              {msg.text}
            </div>
          ))}
        </div>

        {/* Text Input */}
        <div className="flex">
          <input
            type="text"
            placeholder="Type your answer"
            className="flex-grow p-3 border rounded-l-lg"
            value={userInput}
            onChange={(e) => setUserInput(e.target.value)}
          />

          <button
            onClick={sendMessage}
            className="px-6 bg-blue-600 text-white rounded-r-lg hover:bg-blue-700 transition"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
