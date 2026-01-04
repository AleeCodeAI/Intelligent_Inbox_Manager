# ====================================== IMPORTING LIBRARIES =========================================
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from chromadb import PersistentClient
import os
import re
import logging
from langchain_huggingface import HuggingFaceEmbeddings
from sentence_transformers import SentenceTransformer
from tenacity import retry, wait_exponential
from litellm import completion, query
from Backend.color import Agent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)

# ==================================== CREDENTIALS =========================================
load_dotenv(override=True)

openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
openrouter_url = os.getenv("OPENROUTER_URL")

openrouter = OpenAI(api_key=openrouter_api_key, base_url=openrouter_url)

DB_NAME = r"D:\Projects\inbox-manager\databases\vector_db"
KNOWLEDGE_BASE_PATH = Path("knowledge_base")

collection_name = "docs"
embedding_model = "all-MiniLM-L6-v2"

chroma = PersistentClient(path=DB_NAME)
collection = chroma.get_or_create_collection(collection_name)
RETRIEVAL_K = 20
FINAL_K = 10

embeddings = SentenceTransformer(embedding_model)

# this is a way that makes our code be retried after failing!
wait = wait_exponential(multiplier=1, min=10, max=240)

class Result(BaseModel):
    page_content: str
    metadata: dict
# ========================================================================================

# DEFINING DATA TEMPLATE FOR RANKING OF CHUNKS:
class RankOrder(BaseModel):
    order: list[int] = Field(
        description="The order of relevance of chunks, from most relevant to least relevant, by chunk id number"
    )

# DEFINING SYSTEM PROMPT FOR THE ANSWER_QUESTION FUNCTION:
SYSTEM_PROMPT = """
You are a knowledgeable, friendly virtual assistant representing an Applied AI Engineer.

CRITICAL INSTRUCTIONS:
- You MUST use ONLY the information provided in the knowledge base extracts below.
- DO NOT use your general knowledge or training data to answer questions.
- DO NOT make up, invent, or fabricate any information, statistics, numbers, achievements, or details.
- If the knowledge base does not contain the answer, explicitly state: "I don't have that information in my knowledge base."
- Never mention specific tools, frameworks, companies, or achievements unless they appear in the extracts below.

Here are relevant extracts from the knowledge base:
{context}

Answer the question using ONLY the information above. Be accurate, professional, and concise.
Don't use tables only reply with text.
"""


class AnswerQuestion(Agent):
    name = "RAG"
    color = Agent.CYAN
    
    def __init__(self):
        self.openrouter = openrouter
        self.collection = collection
        self.embeddings = embeddings
        self.RETRIEVAL_K = RETRIEVAL_K
        self.FINAL_K = FINAL_K
        self.SYSTEM_PROMPT = SYSTEM_PROMPT
        self.log("Initialized AnswerQuestion RAG system")
    
    # DEFINING FUNCTION TO RANK THE CHUNKS:
    #@retry(wait=wait)
    def rerank(self, question, chunks):
        self.log(f"Reranking {len(chunks)} chunks")
        system_prompt = """
You are a document re-ranker.
You are provided with a question and a list of relevant chunks of text from a query of a knowledge
base.
The chunks are provided in the order they were retrieved; this should be approximately ordered by 
relevance, but you may be able to improve on that.
You must rank order the provided chunks by relevance to the question, with the most relevant chunk
first.
Reply only with the list of ranked chunk ids, nothing else. Include all the chunk ids you are 
provided with, reranked.
IMPORTANT: don't use commas between the numbers, just spaces 
Good Example: "1 3 2 4 5"
Bad Example: "1, 3, 2, 4, 5"
"""

        user_prompt = f"The user has asked the following question:\n\n{question}\n\nOrder all the chunks of text by relevance to the question, from most relevant to least relevant. Include all the chunk ids you are provided with, reranked.\n\n"
        user_prompt += "Here are the chunks:\n\n"
        for index, chunk in enumerate(chunks):
            user_prompt += f"# CHUNK ID: {index + 1}:\n\n{chunk.page_content}\n\n"
        user_prompt += "Reply only with the list of ranked chunk ids, nothing else."

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        response = self.openrouter.chat.completions.create(
            model="gpt-oss-120b",
            messages=messages,
            temperature=0,
            max_tokens=500
        )

        content = response.choices[0].message.content.strip()

        # Remove any non-digit/space characters (in case the model adds extra text)
        clean_content = re.findall(r'\d+', content)
        order_list = [int(x) for x in clean_content]

        # Fallback: if model fails, keep original order
        if not order_list:
            order_list = list(range(1, len(chunks)+1))

        # Validate using RankOrder
        order = RankOrder(order=order_list).order

        return [chunks[i - 1] for i in order]

    def merge_chunks(self, chunks, reranked):
        merged = chunks[:]
        existing = [chunk.page_content for chunk in chunks]
        for chunk in reranked:
            if chunk.page_content not in existing:
                merged.append(chunk)
        return merged

    # DEFINING FUNCTION THAT FETCH UNRANKED CHUNKS:
    def fetch_context_unranked(self, question):
        query_embedding = self.embeddings.encode(question)
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=self.RETRIEVAL_K,
            include=["documents", "metadatas", "distances"]
        )
        
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        
        chunks = [Result(page_content=d, metadata=m) for d, m in zip(docs, metas)]
        
        if not chunks:
            self.log("No chunks retrieved from vector DB")
        else:
            self.log(f"Retrieved {len(chunks)} chunks from vector DB")

        return chunks

    # MAKING FUNCTION THAT FETCHES CONTEXT AND RERANKS IT WITH FALLBACK
    def fetch_context(self, original_question):
        """
        Fetch context with fallback mechanism:
        1. Try with rewritten query
        2. If no results, fallback to original query only
        """
        rewritten_question = self.rewrite_query(original_question)
        
        # First attempt: use both original and rewritten queries
        chunks1 = self.fetch_context_unranked(original_question)
        chunks2 = self.fetch_context_unranked(rewritten_question)
        chunks = self.merge_chunks(chunks1, chunks2)
        
        # Fallback: if no chunks were retrieved, try with just original query
        if not chunks:
            self.log("No chunks found, trying fallback with original query only")
            chunks = self.fetch_context_unranked(original_question)
        
        # If still no chunks, return empty list
        if not chunks:
            self.log("No chunks retrieved after fallback")
            return []
        
        # Rerank and return top K chunks
        reranked = self.rerank(original_question, chunks)
        final_chunks = reranked[:self.FINAL_K]
        self.log(f"Returning top {len(final_chunks)} reranked chunks")
        return final_chunks

    # MAKE RAG MESSAGES:
    def make_rag_messages(self, question, history, chunks):
        context = "\n\n".join(f"Extract from {chunk.metadata['source']}:\n{chunk.page_content}" for chunk in chunks)
        system_prompt = self.SYSTEM_PROMPT.format(context=context)
        return [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": question}]

    # MAKING FUNCTION TO REWRITE QUERY:
    #@retry(wait=wait)
    def rewrite_query(self, question, history=[]):
        """Rewrite the user's question to be a concise, retrieval-optimized query for the Knowledge Base."""
        self.log("Rewriting query for better retrieval")
        message = f"""
You are assisting an Applied AI Engineer by generating a refined search query 
that will be used to retrieve relevant content from their Knowledge Base.

Rules:
- Always write the query **from the perspective of the user** (i.e., 'your' refers to the user's expertise, offerings, and experience). 
- The output must be **a short, specific, keyword-rich question** designed to retrieve relevant chunks from the Knowledge Base.
- Do NOT summarize, explain, or answer the question—only generate the refined query.
- Avoid generic terms like "summary", "bio", or "story" unless they are explicitly relevant to the question.
- Do not mention the company name unless necessary.
- Respond **ONLY with the refined query**, nothing else.

Conversation history:
{history}

User's current question:
{question}
"""
        response = self.openrouter.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "system", "content": message}],
            temperature=0,
            max_tokens=150
        )
        rewritten = response.choices[0].message.content.strip()
        return rewritten

    # @retry(wait=wait)
    def answer_question(self, question: str, history: list[dict] = []) -> tuple[str, list]:
        """
        Answer a question using RAG and return the answer and the retrieved context
        """
        self.log(f"Answering question: {question[:50]}...")
        query = self.rewrite_query(question, history)
        chunks = self.fetch_context(query)
        
        # Handle case where no chunks were retrieved even after fallback
        if not chunks:
            self.log("No relevant context found in knowledge base")
            return "I don't have that information in my knowledge base.", []
        
        messages = self.make_rag_messages(question, history, chunks)
        response = self.openrouter.chat.completions.create(
            model="gpt-oss-120b",
            messages=messages,
            temperature=0,
            max_tokens=1000  
        )
        answer = response.choices[0].message.content.strip()
        self.log("Successfully generated answer from RAG")
        return answer, chunks