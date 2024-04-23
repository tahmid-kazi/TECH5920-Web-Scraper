# python3 -m pip install langchain==0.0.351
# python3 -m pip install -U openai             #(1.14.3)
# export OPENAI_API_KEY="..."

import os
import datetime
import langchain
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain.chains import TransformChain, ConversationalRetrievalChain
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langchain import globals
from langchain_core.runnables import chain
from typing import TypedDict
from langchain_core.output_parsers import JsonOutputParser
# Embeddings Related
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS # by facebook
from langchain.vectorstores import Chroma # another vector store
from langchain.text_splitter import CharacterTextSplitter
# retriever
from langchain.retrievers.multi_query import MultiQueryRetriever
# CSV
from langchain_community.document_loaders.csv_loader import CSVLoader
import json


class InsightGenerator:
    def __init__(self):
        self.teamProfilePath = "../TeamBigData_test"
        self.projectPath = "../testProject"
        
        self.model = ChatOpenAI(temperature=0.5, model="gpt-4-turbo")
        self.embeddings_model = OpenAIEmbeddings()
        
        # define dictinary Structure
    
    def loadData(self):
        dataPath = f"{self.projectPath}/databases"
        filenames = [os.path.join(dataPath, filename) for filename in os.listdir(dataPath)]
        
        loaders = [CSVLoader(file_path=filename) for filename in filenames]
        data = []
        for loader in loaders:
            data.extend(loader.load())
        
        # split them into smaller chunks
        text_splitter = CharacterTextSplitter(separator = "\n", chunk_size=1000, chunk_overlap=0, length_function=len)
        texts = text_splitter.split_documents(data)
        
        # Vectorize dataset using chroma
        docsearch = Chroma.from_documents(texts, self.embeddings_model)
        
        # Test Query with the vectorstore
        # query = "Chronic Lymphocytic Leukemia/Small Lymphocytic Lymphoma"
        # results = docsearch.similarity_search(query)
        # for result in results:
        #     print(result)
        
        multiqueryRetriever = MultiQueryRetriever.from_llm(
            # use Maximum marginal relevance retrieval (default = similarity)
            retriever=docsearch.as_retriever(search_type="mmr", 
                                            search_kwargs={'k': 10, # the amount of documents returned
                                                           'fetch_k': 100, # amount of documents to pass to MMR algorithm (Default: 20)
                                                           'lambda_mult': 0.2 # Diversity of results returned by MMR; 1 for minimum diversity and 0 for maximum. (Default: 0.5)
                                                           }
                                            ), 
            llm=self.model
        )
        return multiqueryRetriever
    
    def getProfiles(self):
        # get team profile, project context, project objective, and project query
        filenames = [
            os.path.join(self.teamProfilePath, "teamprofile.txt"), # team profile
            os.path.join(self.projectPath, "projectprofile/projectContext.txt"), # project context
            os.path.join(self.projectPath, "projectprofile/projectObjective.txt"), # project objective
            os.path.join(self.projectPath, "projectprofile/queryPrompt.txt"), # project query
        ]
        
        profiles = []
        
        for filename in filenames:
            print("Loading: ", filename)
            with open(filename, 'r') as file:
                # Read the entire file content as a string
                content = file.read()
                profiles.append(content)
        
        return profiles[0], profiles[1], profiles[2], profiles[3]
        
    
    def getReport(self):
        # Set verbose
        globals.set_debug(True)
        # define output Strcture
        class Source(TypedDict):
            title: str
            url: str
            # description: str
        
        class Insight(BaseModel):
            summary: str = Field(description="A comprehensive report of the insights gained from the data that conforms to user's requests")
            sources: list[Source] = Field(description="List of sources that you have mentioned in your insight report. Or those that you think with greater importance")
        
        # Output Parser
        parser = JsonOutputParser(pydantic_object=Insight)
        print(type(parser.get_format_instructions()))
        
        teamprofile, context, objective, query = self.getProfiles()
        doc_retriever = self.loadData()
        
        system_prompt = f"""
        You are a expert researcher in the industry, You will be working on a project with a team that has a specific focus and objectives
        You will be provided with informations gathered from multiple sources online and your task is to generate insights based on user's query. 
        You will consider every aspect of the project (background, query, objectives) carefully and generate a comprehensive report
        You will also carefully cite the sources
        
        Here is a briefing on the team:
        {teamprofile}
        
        Here is what' already known to the team:
        {context}
        
        Here is the team's objective for this project:
        {objective}
        
        And lastly, here is the team's query:
        {query}
        
        Use as many sources as you can.
        
        STICK STRICTLY WITH THE FOLLOWING FORMAT INSTRUCTIONS, REPLY ONLY IN JSON FORMAT AND NOTHING ELSE!!!
        
        {parser.get_format_instructions()}
        """

        chain = ConversationalRetrievalChain.from_llm(
            llm=self.model,
            retriever=doc_retriever,
            return_source_documents=False,
        )
        
        response = chain.invoke({"question": system_prompt, "chat_history": []})
        # print("ANSWER ---------------------------")
        # print(response['answer'])
        # return response
        output = parser.parse(response['answer'])
        
        self.saveReport(output)  
        
        return output
    
    def saveReport(self, content):
        now = datetime.datetime.now()
        formatted_date = now.strftime("Report_%d_%B_%Y_%H-%M")
        # Append the file extension
        filename = f"{formatted_date}.json"
        
        savePath = os.path.join(self.projectPath, "reports/", filename)
        indexPath = os.path.join(self.projectPath, "reports/reports_index.json")
        # Write the dictionary to a JSON file
        with open(savePath, 'w') as f:
            json.dump(content, f, indent=4, sort_keys=True)
        
        print(f"Report saved to: {savePath}")
        
        # update reports index
        with open(indexPath, 'r') as file:
            reportsIndex = json.load(file)
        new_report = {
            "name": formatted_date,
            "filename": filename,
            "date": now.strftime("%d_%B_%Y_%H-%M")
        }
        reportsIndex['reports'].append(new_report)
        
        with open(indexPath, 'w') as file:
            json.dump(reportsIndex, file, indent=4)
    
    def setTeamProfile(self, path):
        self.teamProfilePath = path
        
    def setProject(self, path):
        self.projectPath = path


insight = InsightGenerator()
# insight.setProject("../testProject")
response = insight.getReport()

print("Summary -----------------------------")
print(response['summary'])
print("Sources -----------------------------")
for source in response['sources']:
    print(source)
    print("-----------------------------")
