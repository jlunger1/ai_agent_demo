"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function Home() {
  const [input, setInput] = useState("");
  const router = useRouter();

  const startSession = async () => {
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/start_session/`, {
        method: "POST",
      });
      const data = await res.json();
      if (res.ok && data.session_id) {
        return data.session_id; // Return the session ID
      } else {
        throw new Error("Failed to start session.");
      }
    } catch (error) {
      console.error("Error starting session:", error);
      return null;
    }
  };

  const handleSubmit = async () => {
    if (!input.trim()) return;

    const sessionId = await startSession();
    if (!sessionId) {
      alert("Could not start a new session. Please try again.");
      return;
    }

    // Redirect to the chat page with the session ID and first message as query parameters
    router.push(`/chat?session_id=${sessionId}&firstMessage=${encodeURIComponent(input)}`);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      handleSubmit();
    }
  };

  return (
    <div className="min-h-screen bg-white text-gray-800 flex flex-col items-center justify-center p-6">
      <header className="text-center mb-12">
        <h1 className="text-5xl font-light">Spotradius</h1>
        <p className="text-lg mt-2 text-gray-600">Your AI travel assistant</p>
      </header>
      <div className="w-full max-w-lg">
        <div className="relative flex items-center bg-gray-200 rounded-lg p-4 shadow">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Tell me about your trip..."
            className="flex-grow bg-transparent outline-none text-black placeholder-gray-500 text-sm"
          />
          <button
            onClick={handleSubmit}
            className="ml-3 w-10 h-10 bg-blue-500 text-white rounded-full flex items-center justify-center hover:bg-blue-600"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth="2"
              stroke="currentColor"
              className="w-5 h-5"
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="M22 2L11 13" />
              <path strokeLinecap="round" strokeLinejoin="round" d="M22 2L15 22L11 13L2 9L22 2Z" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}
