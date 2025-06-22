from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.tools import Tool, tool
from datetime import datetime

@tool
def read_pdf(filename:str) -> str:
    """
    Extract text from a PDF file. Provide the filename as input.
    """
    from pypdf import PdfReader

    reader = PdfReader(filename)
    extracted_text = []
    for page in reader.pages:
        extracted_text.append(page.extract_text())
    return "\n".join(extracted_text)

@tool
def write_to_textfile(podcast_summary_html:str, filename:str = "Notes_formatted_summary.html") -> str:
    """
    Write the HTML formatted podcast summary to an external text file. The arguments for the function are filename and a html formatted podcast summary.

    Podcast_summary_html is the summary of the podcast script in html format. The filename is the name of the html file to write to.
    
    Return is the html formatted podcast summary that was written to the external file.
    """
    print(filename)
    # See if the file exists
    try: 
        f = open(filename, "r")
        # Read the existing content of the file
        with open(filename, "r") as f:
            content = f.read()
        # Check if the file contains any text
        if content.strip():
            # Erase the text by rewriting an empty string
            with open(filename, "w") as f:
                f.write("")
        # Write the HTML formatted summary to the file        
        with open(filename, "w") as f:
            f.write(podcast_summary_html)
    # If the file does not exist, create it and write the HTML formatted summary to it
    except FileNotFoundError as e:
        with open(filename, "x") as f:
            f.write(podcast_summary_html)

    return podcast_summary_html
    
@tool
def format_summary(raw_summary: str, design: str = "Notes") -> dict:
    """
    Format a raw podcast summary into a structured HTML format. 
    We take two inputs in. One for the raw summary and one for the design that the user wants the summary to be in.

    Returning the formatted HTML summary as a string. 
    """

    model = ChatOpenAI(model="gpt-4o-mini")

    system = ("You are an expert notes formatter. Your task is to format the podcast summary into a readable HTML file while keeping the same format as the inputed raw summary. " +
              "Use emojis, podcast sections, and timestamps to make the summary more engaging and easier to read." + 
              "Copy all facts as verbatim, do not change or condense any information." + 
              "Design it in the way the user wants to" + 
              "Return the formatted HTML file as a string\n\n")
    inputs = f"Podcast Raw Summary: {raw_summary}\n\nDesign for Formating: {design}"

    format_prompt = f"{system}\n\n{inputs}"

    formatted_summary = model.invoke(format_prompt)
    
    # use if returning a dictionary with the following values: original raw summary, the HTML formatted string, the name of the file to write the html to.   
    return_dict = {"Raw_summary": raw_summary,
        "formatted_summary": formatted_summary.content, 
        "filename": f"{design}_formatted_summary.html"}
        
    return formatted_summary.content

