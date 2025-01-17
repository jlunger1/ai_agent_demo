"use client";

import { useState } from "react";

export default function Home() {
  const [input, setInput] = useState("");
  const [response, setResponse] = useState("");
  const placeholderResponse =
    "Thank you for sharing! Let me gather some information and recommendations tailored to your travel plans. This might take a moment—stay tuned!";

  const handleSubmit = () => {
    if (!input.trim()) return;
    setResponse(""); // Clear previous response
    const responseArray = placeholderResponse.split(""); // Split response into characters

    // Simulate typing effect
    responseArray.forEach((char, index) => {
      setTimeout(() => {
        setResponse((prev) => prev + char); // Add characters one by one
      }, 30 * index); // Faster typing speed
    });

    setInput(""); // Clear input field
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      handleSubmit();
    }
  };

  return (
    <div className="min-h-screen bg-white text-gray-800 flex flex-col items-center justify-center p-6">
      {/* Title Section */}
      <header className="text-center mb-12">
        <h1 className="text-5xl font-light">Spotradius</h1>
        <p className="text-lg mt-2 text-gray-600">Your AI travel assistant</p>
      </header>

      {/* Input Box Section */}
      <div className="w-full max-w-lg">
        <div className="relative flex items-center bg-gray-200 rounded-lg p-4 shadow">
          {/* Input Field */}
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown} // Detect Enter key
            placeholder="Tell me about your trip..."
            className="flex-grow bg-transparent outline-none text-black placeholder-gray-500 text-sm"
          />
          {/* Submit Button */}
          <button
            onClick={handleSubmit}
            className="ml-3 w-10 h-10 bg-blue-500 text-white rounded-full flex items-center justify-center hover:bg-blue-600"
          >
            {/* Paper Airplane Icon */}
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth="2"
              stroke="currentColor"
              className="w-5 h-5"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M22 2L11 13"
              />
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M22 2L15 22L11 13L2 9L22 2Z"
              />
            </svg>
          </button>
        </div>

        {/* AI Response */}
        {response && (
          <div className="mt-6 text-gray-800 text-sm leading-relaxed">
            {response}
          </div>
        )}
      </div>
    </div>
  );
}
