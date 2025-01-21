"use client";

import { useEffect, useRef, useState } from "react";
import { useSearchParams } from "next/navigation";

export default function ChatPage() {
  const searchParams = useSearchParams();
  const firstMessage = searchParams.get("firstMessage") || ""; // Get the first message
  const [input, setInput] = useState("");
  const [conversationHistory, setConversationHistory] = useState<
    { role: string; content: string }[]
  >([]);
  const [isTyping, setIsTyping] = useState(false);
  const [typingDots, setTypingDots] = useState(".");
  const firstMessageHandled = useRef(false); // Ref to ensure the first message is only handled once

  // Handle the first message from the landing page
  useEffect(() => {
    if (firstMessage && !firstMessageHandled.current) {
      console.log("Processing firstMessage:", firstMessage); // Debugging log
      firstMessageHandled.current = true; // Mark as handled
      addMessage({ role: "user", content: firstMessage });
      fetchResponse(firstMessage);
    }
  }, [firstMessage]); // Dependency on firstMessage

  // Typing animation effect
  useEffect(() => {
    if (isTyping) {
      const interval = setInterval(() => {
        setTypingDots((prev) => (prev.length < 3 ? prev + "." : "."));
      }, 500);
      return () => clearInterval(interval);
    }
  }, [isTyping]);

  const addMessage = (message: { role: string; content: string }) => {
    setConversationHistory((prev) => [...prev, message]);
  };

  const fetchResponse = async (message: string) => {
    setIsTyping(true);
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/ask/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: message }),
      });
      const data = await res.json();
      addMessage({ role: "assistant", content: data.message || "No response." });
    } catch (error) {
      addMessage({ role: "assistant", content: "Error connecting to the server." });
    } finally {
      setIsTyping(false);
    }
  };

  const handleSubmit = async () => {
    if (!input.trim()) return;

    const userMessage = { role: "user", content: input };
    addMessage(userMessage);
    const currentInput = input; // Capture the input before clearing
    setInput(""); // Clear the input box
    await fetchResponse(currentInput);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") handleSubmit();
  };

  return (
    <div className="min-h-screen bg-white text-gray-800 flex flex-col p-6">
      <header className="mb-4 flex justify-between items-center">
        <h1 className="text-2xl font-light">Spotradius</h1>
      </header>
      <div className="flex-grow overflow-y-auto mb-4">
        {conversationHistory.map((message, index) => (
          <div key={index} className={`mb-4 ${message.role === "user" ? "text-right" : "text-left"}`}>
            <div
              className={`inline-block px-4 py-2 rounded-lg ${
                message.role === "user" ? "bg-blue-500 text-white" : "bg-gray-200 text-gray-800"
              }`}
            >
              {message.content}
            </div>
          </div>
        ))}
        {isTyping && (
          <div className="text-gray-500 text-sm">
            Spotradius is typing{typingDots}
          </div>
        )}
      </div>
      <div className="w-full max-w-lg">
        <div className="relative flex items-center bg-gray-200 rounded-lg p-4 shadow">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your message..."
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
