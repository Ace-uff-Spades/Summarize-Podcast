export async function uploadPodcastFile(file: File): Promise<string> {
    // Add file validation
    const MAX_SIZE = 10 * 1024 * 1024; // 10MB
    if (file.size > MAX_SIZE) {
        throw new Error("File too large. Maximum size is 10MB.");
    }
    
    // Validate file type
    if (file.type !== "application/pdf") {
        throw new Error("Only PDF files are allowed.");
    }
    
    const formData = new FormData();
    formData.append("file", file);
    
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 300000); // 5 min timeout
    
    try {
        // Make the API call to our FastAPI that we're running on the backend
        const res = await fetch("http://127.0.0.1:8000/summarize", {
            method: "POST",
            body: formData,
            signal: controller.signal,
        });
        
        clearTimeout(timeoutId);
        
        if (!res.ok) {
            const errorData = await res.json().catch(() => ({}));
            throw new Error(errorData.error || errorData.detail || `HTTP ${res.status}: ${res.statusText}`);
        }
        
        return await res.text();
    } catch (error) {
        clearTimeout(timeoutId);
        if (error.name === 'AbortError') {
            throw new Error("Request timed out. Please try again.");
        }
        throw error;
    }
}