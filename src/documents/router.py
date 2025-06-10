from fastapi import APIRouter, Depends
from typing import Annotated

from documents.models import DocumentModel, DocTypeModel
from documents.service import get_list_docs, create_doc, update_doc, delete_doc, get_list_doctypes, create_doctype

document_router = APIRouter(
    tags=["Document"]
)

@document_router.get("/get", response_model=list[DocumentModel])
async def get_doc(docs: Annotated[list[DocumentModel], Depends(get_list_docs)],):
    return docs

@document_router.post("/add", response_model=DocumentModel)
async def add_doc(doc: Annotated[DocumentModel, Depends(create_doc)],):
    return doc

@document_router.put("/update/{id}", response_model=DocumentModel)
async def edit_doc(doc: Annotated[None, Depends(update_doc)],):
    return doc

@document_router.delete("/delete/{id}")
async def remove_doc(response: Annotated[None, Depends(delete_doc)],):
    return response

@document_router.get("/doctype/get", response_model=list[DocTypeModel])
async def get_doctype(doctypes: Annotated[list[DocTypeModel], Depends(get_list_doctypes)],):
    return doctypes

@document_router.post("/doctype/add", response_model=DocTypeModel)
async def add_doc(doctype: Annotated[DocTypeModel, Depends(create_doctype)],):
    return doctype