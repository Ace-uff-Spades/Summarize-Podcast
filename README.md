# Podcast Summarizer 🎙️

An AI-powered application that takes podcast transcripts (PDF format) and generates comprehensive, well-formatted summaries with actionable takeaways, timestamps, and key insights.

## ✨ Features

- **AI-Powered Summarization**: Uses GPT-4o-mini to analyze and condense podcast content
- **Structured Output**: Generates summaries with:
  - Title and TL;DR
  - Section-by-section breakdown with timestamps
  - Important points for each section
  - Actionable takeaways
  - Appendix with additional context
- **Beautiful Formatting**: Outputs professionally styled HTML files with emojis and clean design
- **Web Interface**: Simple, intuitive frontend for easy file upload and processing
- **PDF Support**: Extracts text from PDF transcripts automatically

## 🏗️ Architecture

- **Backend**: FastAPI server with LangChain AI agent
- **Frontend**: Next.js React application
- **AI**: OpenAI GPT-4o-mini via LangChain
- **File Processing**: PDF text extraction and HTML formatting

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Node.js 18 or higher
- OpenAI API key

### Installation

1. **Clone the repository**

2. **Set up the Python backend**
   ```bash
   # Create and activate virtual environment (recommended)
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install Python dependencies
   pip install -r modules.txt
   ```

3. **Set up the Next.js frontend**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

4. **Configure environment variables**
   ```bash
   # Create a .env file in the root directory
   echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
   ```

### Running the Application

1. **Start the FastAPI backend**
   ```bash
   # From the root directory
   uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```

2. **Start the Next.js frontend**
   ```bash
   # In a new terminal, from the frontend directory
   cd frontend
   npm run dev
   ```

3. **Access the application**
   - Frontend: http://127.0.0.1:8000
   - Backend API: http://localhost:8000

## 📖 Usage

1. **Upload a PDF transcript** of any podcast episode
2. **Click "Generate Summary"** to process the transcript
3. **View the formatted summary** with timestamps, key points, and actionable takeaways
4. **Download or copy** the HTML output four notes

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory with:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

### Testing

- Backend: The FastAPI server includes automatic API documentation at http://127.0.0.1:8000/docs
- Frontend: Use `npm run dev` for development with hot reloading

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues

1. **"Module not found" errors**: Ensure you're in the correct virtual environment and all dependencies are installed
2. **API key errors**: Verify your OpenAI API key is correctly set in the `.env` file
3. **CORS errors**: The backend is configured to allow all origins in development mode
4. **File upload issues**: Ensure the `uploads/` directory exists and has write permissions
5. **Backend API is not found**: Make sure the FastAPI server is running. By default, it should be at http://127.0.0.1:8000/.
If you run the server with just uvicorn app.main:app --reload, check the terminal for the actual URL (it may be http://127.0.0.1:8000 or another address).
If the server is running on a different URL or port, update the API URL in frontend/lib/api.ts to match.

### Getting Help

If you encounter any issues, please:
1. Check the console logs for error messages
2. Verify all dependencies are installed correctly
3. Ensure your OpenAI API key is valid and has sufficient credits

---

**Happy podcast summarizing! 🎧✨**
