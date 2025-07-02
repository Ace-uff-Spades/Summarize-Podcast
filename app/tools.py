from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.tools import Tool, tool
from datetime import datetime
from pathlib import Path
import logging
from app.fineTune import build_rag_store

logger = logging.getLogger(__name__)

@tool
def read_pdf(filename:str) -> str:
    """
    Extract text from a PDF file. Provide the filename as input.
    """
    try:
        from pypdf import PdfReader
        reader = PdfReader(filename)
        extracted_text = []
        for page in reader.pages:
            extracted_text.append(page.extract_text())
        return "\n".join(extracted_text)
    except Exception as e:
        logger.error(f"Failed to read PDF {filename}: {e}")
        raise ValueError(f"Failed to read PDF: {e}")

@tool
def write_to_textfile(podcast_summary_html:str, filename:str = "Notes_formatted_summary.html") -> str:
    """
    Write the HTML formatted podcast summary to an external text file. The arguments for the function are filename and a html formatted podcast summary.

    Podcast_summary_html is the summary of the podcast script in html format. The filename is the name of the html file to write to.
    
    Return is the html formatted podcast summary that was written to the external file.
    """
    try:
        print(filename)
        file_path = Path(filename)
        
        # Ensure output directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write the HTML formatted summary to the file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(podcast_summary_html)
            
        logger.info(f"Successfully wrote summary to {filename}")
        return podcast_summary_html
        
    except Exception as e:
        logger.error(f"Failed to write file {filename}: {e}")
        raise ValueError(f"Failed to write file: {e}")
    
@tool
def format_summary(raw_summary: str, design: str = "Fun Notes") -> str:
    """
    Format a raw podcast summary into a structured HTML format. 
    We take two inputs in. One for the raw summary and one for the design that the user wants the summary to be in.

    Returning the formatted HTML summary as a string. 
    """
    try:
        model = ChatOpenAI(model="gpt-4o-mini")
    
        #create rag db and import the embeddings from it.
        rag_db = build_rag_store("app/examples.json")
        retrieved = rag_db.similarity_search(raw_summary, k=8)
        examples_text = ("\n---\n").join(
            f"""\n\n------\nLabel: {doc.metadata.get('label')} {i+1}: 
            \n\nSummary\n
            {doc.page_content}
            \n------\nComments:\n 
            {doc.metadata.get('comments')}\n"""
            for i, doc in enumerate(retrieved)
            )
        
        #base system prompt for formatting
        system = f""" You are an expert notes formatter. Your task is to format the podcast summary into a readable HTML file while keeping the same format as the inputed raw summary. 
                  Use emojis, podcast sections, and timestamps to make the summary more engaging and easier to read.
                  Copy all facts as verbatim, do not change or condense any information.
                  Design it in the way the user wants to 
                  Return the formatted HTML file as a string\n\n

                  Here are examples of good formatted summaries and bad formatted summaries, along with comments about each one. Pros are good things about that particular example that I like.
                  Cons are bad things about that particular example that I do not like. 
                  
                  {examples_text}

                  Now, format the following Podcast raw summary keeping in mind pros and cons from the examples. I do not want any cons in the result.
                """

        inputs = f"Podcast Raw Summary: {raw_summary}\n\nDesign for Formating: {design}"

        format_prompt = f"{system}\n\n{inputs}"

        # Use direct LLM call instead of LLMChain to avoid nested agent execution
        formatted_summary = model.invoke(format_prompt)
        
        # use if returning a dictionary with the following values: original raw summary, the HTML formatted string, the name of the file to write the html to.   
        # return_dict = {"Raw_summary": raw_summary,
         #   "formatted_summary": formatted_summary.content, 
         #   "filename": f"{design}_formatted_summary.html"}
        logger.info(f"Successfully formatted summary with design: {design}")
        return str(formatted_summary.content)
        
    except Exception as e:
        logger.error(f"Failed to format summary: {e}")
        raise ValueError(f"Failed to format summary: {e}")

