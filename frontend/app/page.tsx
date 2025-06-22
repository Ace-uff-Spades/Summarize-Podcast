"use client";

import React from "react";
import { useState } from "react";
import { uploadPodcastFile } from "../lib/api";

export default function HomePage() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [htmlContent, setHtmlContent] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.length) {
      setFile(e.target.files[0]);
      setHtmlContent(null);
      setError(null);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault(); 
    if (!file) return;

    try {
      setLoading(true);
      const html = await uploadPodcastFile(file);
      setHtmlContent(html);
    } catch (err) {
      console.log(err.message);
      setError("Something went wrong while summarizing the podcast.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="p-8 max-w-xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Podcast Summarizer 🎙️</h1>

      <form onSubmit={handleSubmit} className="space-y-4">
        <input
          type="file"
          accept="application/pdf"
          onChange={handleFileChange}
          className="block"
        />
        <button
          type="submit"
          disabled={!file || loading}
          className="bg-blue-600 text-white px-4 py-2 rounded disabled:opacity-50"
        >
          {loading ? "Summarizing..." : "Generate Summary"}
        </button>
      </form>

      {error && <p className="text-red-500 mt-4">{error}</p>}

      {htmlContent && (
        <section className="mt-8 border p-4 rounded bg-gray-50">
          <h2 className="text-lg font-semibold mb-2">📝 Summary</h2>
          <div
            dangerouslySetInnerHTML={{ __html: htmlContent }}
            className="prose max-w-none"
          />
        </section>
      )}
    </main>
  );
}