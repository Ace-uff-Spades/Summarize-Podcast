"""
TODO 
- Train model on good outputs vs bad outputs. This should fix the formatting errors. 
- Add in more user inputs for 
    -type of summaries, i.e. Notes, just important takeways, more details. 
    -format of the summary, i.e. HTML, Markdown, Notion etc. 
    -name of the output files
"""

def summarize_agent(script_filename: str, output_filename: str) -> str:
    from dotenv import load_dotenv
    from pydantic import BaseModel
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import PydanticOutputParser
    from langchain.agents import create_tool_calling_agent, AgentExecutor
    import app.tools as tools

    """
    Summarize the podcast script from the inputed transcript.
    Then format the summary as a easy to ready HTML file and write it to an external file.
    Return the formatted html str.
    """

    load_dotenv() 
    model = ChatOpenAI(model="gpt-4o-mini")

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

    parser = PydanticOutputParser(pydantic_object=PodcastResponse)

    prompt = ChatPromptTemplate.from_messages( 
        [
            (
                "system",
                "You are an expert podcast summarizer. You're amazing at capturing and condensing the important points in podcasts, conversations, and lectures." + 
                "Your task is to analyze the podcast script and provide a detailed summary, actionable takeaways and important points within the podcast." + 
                "For Important points, scale the number of points with the amount of key concepts that are in that section." +
                "Use emojis to make the summary more engaging and easier to read." +
                "Your output must be structured with the following structure:\n{format_structure}." +  
                "If there are no timestamps that can be infered from the transcript, you can place the timestamp values as 0 and just fill in the 'text' and 'important_points' fields as logical topic sections in the script." +
                "There is a special field at the end called appendix, this field is optional and can be used to provide additional information or context that you think may be useful for the user in the form of a list." 
            ),
            ("placeholder", "{chat_history}"), 
            ("human", "{query} {script_filename} {output_filename}"),
            ("placeholder", "{agent_scratchpad}") 
        ]
    ).partial(format_structure=parser.get_format_instructions())

    tools = [tools.read_pdf, tools.write_to_textfile, tools.format_summary]

    agent = create_tool_calling_agent(
        llm=model, 
        prompt=prompt,
        tools=tools
    )

    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    raw_reponse = agent_executor.invoke({"query": "Summarize the podcast script from the transcript file below." + 
                                        "Then format the summary as a easy to ready HTML file and write it to an external file." + 
                                        "Return to me everything written in the external file as a string",
                                        "script_filename": script_filename, 
                                        "output_filename": output_filename})
    try:
        print("Raw response:", raw_reponse['output'])
    except ValueError as e:
        print("Error parsing the response:", e, "\nRaw response:", raw_reponse['output'])

    return raw_reponse["output"]



