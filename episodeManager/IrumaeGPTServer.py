import chromadb
from torch import cuda
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel
import embedding_model.modelUpload as modelUpload
import numpy as np
from typing import List
import ast
from model.User import User
from model.User import Item
from api.user_memory_controller import userRouter
from api.episodeManager import episodeRouter

#uvicorn IrumaeGPTServer:app --reload --host=0.0.0.0 --port=8800
#python -m uvicorn FastApi:app --reload

app=FastAPI()

app.include_router(userRouter)
app.include_router(episodeRouter)

client=chromadb.PersistentClient()

embed_model=modelUpload.model_upload()