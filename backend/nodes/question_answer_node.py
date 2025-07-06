import os
import configparser
import numpy as np
import yaml
from pydantic import BaseModel, ValidationError
from sentence_transformers import SentenceTransformer
from huggingface_hub import InferenceClient

import sqlalchemy
from utils.db_connections import get_session
from models.table_structure import PDFData
from models.chat_history_table import store_chat_log


class QuestionAnswer(BaseModel):
    answer: str

# --- Load configuration ---
config = configparser.ConfigParser()
config.read("config/env-files.properties")
print("Config file loaded successfully.", config.sections(), "config_path:", os.path.abspath("env-files.properties"))

if "ENVIRONMENT" in config:
    env_config = config["ENVIRONMENT"]
elif "Default" in config:
    env_config = config["Default"]
else:
    raise KeyError("Config file missing both [ENVIRONMENT] and [Default] sections.")

os.environ["ai_key"] = env_config.get("ai_key", "")
os.environ["HUGGINGFACEHUB_API_TOKEN"] = env_config.get("ai_key", "")
os.environ["api_model"] = env_config.get("api_model", "")
os.environ["api_url"] = env_config.get("api_url", "")
os.environ["prompt_template"] = config.get("question_answer_prompt", "prompt_template", fallback="prompt_templates/default_prompt.txt")

api_key = os.environ.get("ai_key")
hf_token = os.environ.get("HUGGINGFACEHUB_API_TOKEN")
prompt_path = os.environ.get("prompt_template")

# --- Load sentence transformer model for embeddings ---
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


def load_prompt_template_from_env() -> str:
    with open(prompt_path, "r", encoding="utf-8") as file:
        return file.read()

def create_question_embeddings(question: str) -> list:
    embeddings = model.encode(question, convert_to_tensor=True)
    return embeddings.tolist()

def cosine_similarity(vec1, vec2):
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def parse_yaml_to_question_answer(yaml_text: str):
    try:
        # Clean up wrapping quotes
        if isinstance(yaml_text, str) and yaml_text.strip().startswith(("'", '"')) and yaml_text.strip().endswith(("'", '"')):
            yaml_text = yaml_text.strip()[1:-1]

        data = yaml.safe_load(yaml_text)

        if isinstance(data, str):  # fallback if it's just a string
            data = {"answer": data}

        if not isinstance(data, dict):
            raise TypeError("Parsed YAML is not a dictionary.")

        return QuestionAnswer(**data)

    except (yaml.YAMLError, ValidationError, TypeError) as e:
        print("Failed to parse YAML or validate QuestionAnswer:", e)
        return None

# --- Core functions ---

def get_similar_chunks_for_the_question(question: str) -> str:
    session = get_session()
    question_embedding = create_question_embeddings(question)
    pdf_chunks = session.query(PDFData).all()
    similar_chunks = []

    for pdf_chunk in pdf_chunks:
        stored_embedding = np.frombuffer(pdf_chunk.embeddings, dtype=np.float32)
        similarity = cosine_similarity(question_embedding, stored_embedding)
        similar_chunks.append((similarity, pdf_chunk.chunk))

    similar_chunks.sort(key=lambda x: x[0], reverse=True)
    context = "\n\n".join([chunk for _, chunk in similar_chunks[:15]])
    answer = get_answer_from_context(question, context)
    store_chat_log(question, answer)
    return answer

def get_answer_from_context(text: str, context: str) -> str:
    prompt_template = load_prompt_template_from_env()

    # Manually define the format instructions based on your QuestionAnswer model
    format_instructions = """
    You must respond with valid YAML in exactly this format:

    {answer: <your answer here>}
    """

    prompt_text = prompt_template.format(
        context=context,
        text=text,
        format_instructions=format_instructions
    )
    # print("Prompt text sent to LLM:\n", prompt_text)

    client = InferenceClient(
        provider="fireworks-ai",
        api_key=hf_token,
    )

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt_text},
    ]

    completion = client.chat.completions.create(
        model="meta-llama/Llama-3.1-8B-Instruct",
        messages=messages,
    )

    response_content = completion.choices[0].message["content"]
    # print("Raw LLM Response:\n", response_content)
    # print("Raw response from LLM (before YAML parse):")
    print(repr(response_content))
    qa_obj = parse_yaml_to_question_answer(response_content)
    if qa_obj and qa_obj.answer:
        return qa_obj.answer
    else:
        return "I don't know."

# Example usage
if __name__ == "__main__":
    question = "What is the capital of France?"
    answer = get_similar_chunks_for_the_question(question)
    print("Answer:", answer)