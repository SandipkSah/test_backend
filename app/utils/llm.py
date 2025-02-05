import os
from typing import List, Dict
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

openai_key = os.getenv("OPENAI_KEY")
llm_model = ChatOpenAI(model="gpt-4o-mini-2024-07-18", temperature=0.7, openai_api_key=openai_key)

# Template for the LLM prompt
prompt_template = PromptTemplate(
    input_variables=["context", "question"],
    template="""Du bist ein Assistent, der Personen dabei hilft ihre Fragen zu beantworten. Du bist Teil einer RAG-Pipeline. Gebe eine Antwort basierend auf der
    Liste die du bekommst zurück. 
    Du bekommst eine durchnummerierte Liste an ausgewählten Links, die bereits gut zur Frage passen. In dieser Liste sind einzelne Links, eine Kurzbeschreibung der Webseite und 
    der spezifische Text (Chunk) der passenden Stelle im Webseitentext.
    In deiner Antwort gebe zuerst eine direkte Antwort auf die Frage basierend auf den Kurzbeschreibungen und Chunks. 
    Liste dann jeden erhaltenen Link und beschreibe in einem Satz warum dieser Link passend für die Frage ist. Füge danach den Link an. 
    Nutze für die Antwort nur die Links, die dir aus der Datenbank zur Verfügung gestellt wurden. Diese erkennst du daran, dass sie nach "[Quelle]:" stehen. 
    
    Kontext:
    {context}
    
    Frage: {question}"""
)


async def generate_response_from_retrieved_documents(
    query: str,
    retrieved_docs: List[Dict],
) -> str:
    """
    Generate a response based on the retrieved documents and query.
    
    Args:
        query (str): The query text.
        retrieved_docs (List[Dict]): A list of documents retrieved from the database.
        
    Returns:
        str: The generated response.
    """
    # Initialize the OpenAI model

    # Create the context from retrieved documents
    context = "\n".join(
        [f"{i+1}. [Quelle]: {doc['metadata'].get('url', 'No URL available')}\n [Summary]: {doc['metadata'].get('summary', 'No text available')}\n [Relevant chunk]: {doc['chunk']}\n\n" 
         for i, doc in enumerate(retrieved_docs)]
    )

    # Create the chain using the pipe operator
    chain = prompt_template | llm_model | StrOutputParser() 
    
    # Generate the response
    response = chain.invoke({"context": context, "question": query})

    return response
