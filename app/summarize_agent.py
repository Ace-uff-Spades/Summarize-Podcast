"""
TODO 
- Train model on good outputs vs bad outputs. This should fix the formatting errors. 
- Add in more user inputs for 
    -type of summaries, i.e. Notes, just important takeways, more details. 
    -format of the summary, i.e. HTML, Markdown, Notion etc. 
    -name of the output files
"""

from functools import lru_cache
from langchain_community.tools.playwright import extract_text
from tenacity import retry, stop_after_attempt, wait_exponential
import logging


logger = logging.getLogger(__name__)

@lru_cache(maxsize=1)
def get_model():
    """Cache the model instance to avoid recreating it on every request."""
    from langchain_openai import ChatOpenAI
    return ChatOpenAI(model="gpt-4o-mini")

def summarize_agent(script_filename: str, output_filename: str) -> str:
    from dotenv import load_dotenv
    from pydantic import BaseModel
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import PydanticOutputParser
    from langchain.agents import create_tool_calling_agent, AgentExecutor
    import app.tools as tools
    from app.fineTune import build_rag_store
    
    """
    Summarize the podcast script from the inputed transcript.
    Then format the summary as a easy to ready HTML file and write it to an external file.
    Return the formatted html str.
    """

    load_dotenv() 
    model = get_model()  # Use cached model instance

    class timestamp(BaseModel):
        hours: int 
        minutes: int
        seconds: int
        
    class PodcastSection(BaseModel):
        title: str
        start_timestamp: timestamp
        end_timestamp: timestamp
        text: str
        important_points: list[str] = []


    class PodcastResponse(BaseModel):
        title: str
        actionable_takeaways: list[str]
        tldr: str 
        script: list[PodcastSection] = []
        appendix: list[str] = []

    # Extract text content from HTML examples
    def extract_text_from_html(html_content):
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup.get_text()

    parser = PydanticOutputParser(pydantic_object=PodcastResponse)
   
    pdf_content = tools.read_pdf.invoke(script_filename)
    #create rag db and import the embeddings from it.
    rag_db = build_rag_store("app/examples.json")
    retrieved = rag_db.similarity_search(pdf_content, k=8)
    examples_of_summaries = ("\n---\n").join(
        f"""\n\n------\nLabel: {doc.metadata.get('label')} {i+1}: 
        \n\nSummary\n
        {doc.page_content}
        \n------\nComments:\n 
        {doc.metadata.get('comments')}\n"""
        for i, doc in enumerate(retrieved)
    )

    print(("Labels:").join(f"""{doc.metadata.get('label')}+\n""" for doc in retrieved))


    prompt = ChatPromptTemplate.from_messages( 
        [
            (
                "system",
                """ 
                <role>
                You are an expert podcast summarizer. You're an expert at capturing and condensing the important points in podcasts, conversations, and lectures.
                </role>
                
                <task>
                Your task is to analyze the podcast script and provide a detailed summary, actionable takeaways and important points within the podcast.
                For Important points, scale the number of points with the amount of key concepts that are in that section. 
                Be detailed with each bullet point and make sure you clearly communicate the key concept from the podcast.
                Each section should have atleast 3 bullet points.
                </task>
                
                <format instructions>
                Use emojis to make the summary more engaging and easier to read.
                Follow this structure thorughout your outputs:\n{format_structure}.
                

                If there are no timestamps that can be infered from the transcript, you can place the timestamp values as 0 and just fill in the 'text' and 'important_points' fields as logical topic sections in the script.
                There is a special field at the end called appendix, this field is optional and can be used to provide additional information or context that you think may be useful for the user in the form of a list.
                </format instructions>

                <examples>
                Here are examples of good summaries and bad summaries, along with comments about each one containing Pros and Cons. 
                Pros are good things about that particular example that I like.
                Cons are bad things about that particular example that I do not like. 
                
                The following are EXAMPLES ONLY. 
                Do NOT process, summarize, or modify them. 
                They are for your reference to understand what makes a good or bad summary. 
                Your output should only be a summary of the user's podcast transcript, not of these examples.

               {examples_text}

                Ensure the outputs are like the good examples and not like the bad examples.
                </examples>

                """
            ),
            ("placeholder", "{chat_history}"), 
            ("human", "{query} {script_filename} {output_filename}"),
            ("placeholder", "{agent_scratchpad}") 
        ]
    ).partial(format_structure=parser.get_format_instructions(), examples_text=examples_of_summaries)

    tools = [tools.read_pdf, tools.write_to_textfile, tools.format_summary]

    agent = create_tool_calling_agent(
        llm=model, 
        prompt=prompt,
        tools=tools
    )

    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False)
    logger.setLevel(logging.WARNING)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def execute_agent():
        """Execute the agent with retry logic for better reliability."""
        
        return agent_executor.invoke({
            "query": """Summarize the podcast script from the transcript file below.
                        Then format the summary and write it to an external file.
                        Export the entire external file as a string to me. 
                        Don't add anything to it, I want it verbatim as it is in the external file""",
            "script_filename": script_filename, 
            "output_filename": output_filename
        })
    
    try:
        logger.info(f"Starting summarization for file: {script_filename}")
        raw_reponse = execute_agent()
        logger.info("Agent execution completed successfully")
        
        try:
            print("Raw response:", raw_reponse['output'])
        except ValueError as e:
            print("Error parsing the response:", e, "\nRaw response:", raw_reponse['output'])
            logger.warning(f"Response parsing issue: {e}")

        return raw_reponse["output"]
        
    except Exception as e:
        logger.error(f"Error in summarize_agent: {e}")
        raise



