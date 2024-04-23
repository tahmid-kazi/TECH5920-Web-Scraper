import os
API_KEY = ''
#os.environ['OPENAI_API_KEY'] = API_KEY

from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI

# Import chain

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.docstore.document import Document
from langchain.prompts import PromptTemplate
from langchain.indexes.vectorstore import VectorstoreIndexCreator
from langchain.chains.question_answering import load_qa_chain



llm = ChatOpenAI(temperature=0.9, model_name='gpt-3.5-turbo-1106')

# print(llm.predict("Give me a dad joke"))


with open("interview.txt") as f:
    article = f.read()
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
texts = text_splitter.split_text(article)

embeddings = OpenAIEmbeddings(openai_api_key=API_KEY)

# vectorize dataset using chroma.
docsearch = Chroma.from_texts(texts, embeddings, metadatas=[{"source": str(i)} for i in range(len(texts))]).as_retriever()

query = "what makes a successful interview?"

# query the data using the QA Chain
docs = docsearch.get_relevant_documents(query)
chain = load_qa_chain(llm, chain_type="stuff")
result = chain({"input_documents": docs, "question": query}, return_only_outputs=True)

print(result)

# before: 0.00062
