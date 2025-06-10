from fastapi import APIRouter, Depends, Request, Form, UploadFile, File
from typing import Annotated

from documents.models import DocumentModel, DocTypeModel
from documents.service import DocumentService
from documents.schemas import DocumentBase

from auth.models import UserModel
from auth.utils import get_current_user

document_router = APIRouter(
    tags=["Document"]
)

@document_router.get("/get", response_model=list[DocumentModel])
async def get_doc(response: Annotated[DocumentService, Depends(DocumentService)],
                  current_user: Annotated[UserModel, Depends(get_current_user)]):
    return await response.get_list_docs()

@document_router.post("/add", response_model=DocumentModel)
async def add_doc(response: Annotated[DocumentService, Depends(DocumentService)],
                  current_user: Annotated[UserModel, Depends(get_current_user)],
                  title: str = Form(...),
                  descript: str = Form(...),
                  type: int = Form(...),
                  file_upload: UploadFile = File(...)):
    return await response.create_doc(current_user, title, descript, type, file_upload)

@document_router.put("/update/{id}", response_model=DocumentModel)
async def edit_doc(response: Annotated[DocumentService, Depends(DocumentService)],
                   current_user: Annotated[UserModel, Depends(get_current_user)],
                   id: int,
                   docbase: DocumentBase):
    return await response.update_doc(current_user, id, docbase)

@document_router.delete("/delete/{id}")
async def remove_doc(response: Annotated[DocumentService, Depends(DocumentService)],
                     current_user: Annotated[UserModel, Depends(get_current_user)],
                     id: int):
    return await response.delete_doc(current_user, id)

@document_router.get("/doctype/get", response_model=list[DocTypeModel])
async def get_doctype(response: Annotated[DocumentService, Depends(DocumentService)],
                      current_user: Annotated[UserModel, Depends(get_current_user)]):
    return await response.get_list_doctypes()

@document_router.post("/doctype/add", response_model=DocTypeModel)
async def add_doc(response: Annotated[DocumentService, Depends(DocumentService)],
                  current_user: Annotated[UserModel, Depends(get_current_user)],
                  type_title: str = Form(...)):
    return await response.create_doctype(current_user, type_title)