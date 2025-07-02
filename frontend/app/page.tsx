"use client";

import React, { useState, useEffect } from "react";
import { uploadPodcastFile } from "../lib/api";
import "../styles/globals.css";

export default function HomePage() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [htmlContent, setHtmlContent] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.length) {
      const selectedFile = e.target.files[0];
      
      // Validate file type
      if (selectedFile.type !== "application/pdf") {
        setError("Please select a PDF file.");
        return;
      }
      
      // Validate file size (10MB)
      if (selectedFile.size > 10 * 1024 * 1024) {
        setError("File size must be less than 10MB.");
        return;
      }
      
      setFile(selectedFile);
      setHtmlContent(null);
      setError(null);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault(); 
    if (!file) return;

    try {
      setLoading(true);
      setError(null);
      const html = await uploadPodcastFile(file);
      setHtmlContent(html);
    } catch (err: any) {
      console.error("Upload error:", err);
      setError(err.message || "Something went wrong while summarizing the podcast.");
    } finally {
      setLoading(false);
    }
  };

  // Create a Blob URL for downloading the HTML content
  useEffect(() => {
    if (htmlContent) {
      const blob = new Blob([htmlContent], { type: "text/html" });
      const url = URL.createObjectURL(blob);
      setDownloadUrl(url);
      return () => URL.revokeObjectURL(url);
    } else {
      setDownloadUrl(null);
    }
  }, [htmlContent]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50 flex items-center justify-center">
      <div className="w-full max-w-6xl h-[80vh] bg-white/80 rounded-3xl shadow-2xl flex flex-col md:flex-row overflow-hidden border border-gray-200">
        {/* Left: Controls */}
        <div className="w-full md:w-1/2 p-10 flex flex-col justify-center gap-8 bg-white/90">
          <div>
            <h1 className="text-3xl font-extrabold text-gray-900 mb-2 tracking-tight">Podcast Summarizer <span className="text-blue-600">🎙️</span></h1>
            <p className="text-gray-500 mb-6">Upload a podcast transcript (PDF) and get a beautiful, actionable summary in seconds.</p>
          </div>
          <form onSubmit={handleSubmit} className="flex flex-col gap-6">
            <label className="block">
              <span className="text-gray-700 font-medium mb-2 block">Select Podcast Transcript (PDF)</span>
              <input
                type="file"
                accept="application/pdf"
                onChange={handleFileChange}
                className="block w-full text-sm text-gray-700 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 transition-all duration-150"
                disabled={loading}
              />
            </label>
            <div className="flex gap-4 items-center">
              <button
                type="submit"
                disabled={!file || loading}
                className="bg-blue-600 hover:bg-blue-700 transition-colors text-white font-semibold px-6 py-2 rounded-lg shadow disabled:opacity-50 flex items-center gap-2"
              >
                {loading ? (
                  <>
                    <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Summarizing...
                  </>
                ) : (
                  <>
                    <span>Generate Summary</span>
                  </>
                )}
              </button>
              {downloadUrl && (
                <a
                  href={downloadUrl}
                  download="podcast_summary.html"
                  className="bg-green-600 hover:bg-green-700 transition-colors text-white font-semibold px-6 py-2 rounded-lg shadow"
                >
                  Download HTML
                </a>
              )}
            </div>
            <p className="text-xs text-gray-400 mt-2">Maximum file size: 10MB. Only PDF files are supported.</p>
            {error && (
              <div className="mt-2 p-3 bg-red-50 border border-red-200 rounded-md">
                <p className="text-red-600 text-sm">{error}</p>
              </div>
            )}
          </form>
        </div>
        {/* Right: Output */}
        <div className="w-full md:w-1/2 h-full bg-gradient-to-br from-blue-50 to-white p-0 md:p-10 flex flex-col overflow-auto">
          <div className="flex-1 flex flex-col justify-center items-center h-full">
            {htmlContent ? (
              <section className="w-full h-full border-none rounded-xl bg-white/80 shadow-inner p-6 overflow-auto">
                <h2 className="text-lg font-semibold mb-4 text-blue-700">📝 Summary</h2>
                <div
                  dangerouslySetInnerHTML={{ __html: htmlContent }}
                  className="prose max-w-none"
                />
              </section>
            ) : (
              <div className="flex flex-col items-center justify-center h-full text-gray-400">
                <svg className="w-24 h-24 mb-4" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
                </svg>
                <span className="text-xl font-medium">Your summary will appear here</span>
                <span className="text-sm mt-2">Upload a PDF transcript and click Generate Summary</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}