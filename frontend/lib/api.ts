export async function uploadPodcastFile(file: File): Promise<string> {
    const formData = new FormData();
    formData.append("file", file);
  
    const res = await fetch("http://127.0.0.1:8000/summarize", {
      method: "POST",
      body: formData,
    });
  
    if (!res.ok) {
        console.log(`Error uploading file: ${res.status} ${res.statusText}`);   
        throw new Error("Failed to get summary");
    }
    
    const html = await res.text(); // API returns HTML string
    return html;
  }