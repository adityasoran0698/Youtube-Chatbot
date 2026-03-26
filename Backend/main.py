from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.output_parsers import StrOutputParser
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import (
    RunnableParallel,
    RunnablePassthrough,
    RunnableLambda,
)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from translate import Translator
from pydantic import BaseModel

load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
)


class user_entered_query(BaseModel):
    query: str


class uploaded_url(BaseModel):
    url: str


vector_store = None


@app.post("/url/upload")
def loading_transcripts(data: uploaded_url):
    global vector_store
    url = data.url
    # Loading transcripts
    if "youtu.be" in url:
        video_id = url.split("/")[-1].split("?")[0]
    else:
        video_id = url.split("v=")[-1].split("&")[0]

    api = YouTubeTranscriptApi()
    try:
        transcript_list = api.list(video_id=video_id)
        transcript = transcript_list.find_transcript(
            [t.language_code for t in transcript_list]
        )

        data = transcript.fetch()
        text = " ".join(chunk.text for chunk in data)
    except TranscriptsDisabled:
        print("No Transcript is available for this video")

    # Text Splitting

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=200)

    chunks = splitter.create_documents([text])

    # Vector Store

    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    vector_store = Chroma.from_documents(chunks, embedding=embeddings)
    return {"message": "Transcript processed successfully"}


@app.post("/api/chat")
def youtube_chatbot(data: user_entered_query):
    user_query = data.query
    global vector_store
    # Retriever
    retriever = vector_store.as_retriever(search_type="similarity", kwargs={"k": 5})
    prompt = PromptTemplate(
        template="""
You are a helpful assistant for answering questions about a YouTube video.

Follow these rules strictly:
1. If the question is a greeting or casual message (like "ok", "hi", "thanks", "cool", etc.), respond naturally and conversationally. Do NOT say you don't know.
2. If the question is about the video content AND the context is sufficient, answer in detail using ONLY the provided context.
3. If the question is about the video content BUT the context is insufficient, say you don't have enough information from the video to answer that.

The context can be in any language but always answer in English only.

Context:
{context}

Question:
{query}

Answer:
""",
        input_variables=["query", "context"],
    )

    def translate_to_english(chunks):
        translated_chunks = []
        translator = Translator(to_lang="en")
        for chunk in chunks:
            try:

                translated_text = translator.translate(chunk.page_content)

            except Exception:
                # Fallback: keep original text if translation fails
                translated_text = chunk.page_content

            translated_chunk = chunk.__class__(
                page_content=translated_text, metadata=chunk.metadata
            )
            translated_chunks.append(translated_chunk)

        return translated_chunks

    def format_docs(result):
        context_text = "\n\n".join(c.page_content for c in result)
        return context_text

    parallel_chain = RunnableParallel(
        {
            "context": retriever
            | RunnableLambda(translate_to_english)
            | RunnableLambda(format_docs),
            "query": RunnablePassthrough(),
        }
    )

    model = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
    parser = StrOutputParser()
    sequence_chain = prompt | model | parser

    final_chain = parallel_chain | sequence_chain

    result = final_chain.invoke(user_query)
    return result
