from fastapi import APIRouter, Path, Depends, HTTPException, status, UploadFile, File, Form
from sqlmodel import Session, select, exists, text
from slugify import slugify
from typing import Annotated
from datetime import datetime
import aiofiles
import os
from pathlib import Path as Path_pathlib

from database.connection import get_session
from models.documents import DocumentModel, DocumentCreate
from models.users import UserModel
from models.document_type import DocTypeModel
from utils.auth import get_current_user

document_router = APIRouter(
    tags=["Document"]
)

@document_router.get("/get", response_model=list[DocumentModel])
async def get_doc(current_user: Annotated[UserModel, Depends(get_current_user)],
                    session: Session = Depends(get_session)) -> dict:
    result = session.exec(select(DocumentModel))
    documents = result.all()
    return [doc for doc in documents]

@document_router.post("/add", response_model=DocumentModel)
async def post_doc(current_user: Annotated[UserModel, Depends(get_current_user)],
                   title: str = Form(...),
                   descript: str = Form(...),
                   type: int = Form(...),
                   file_upload: UploadFile = File(...),
                   session: Session = Depends(get_session)) -> dict:
    if current_user.permissions > 0:
        result = DocumentModel(doc_name=title,
                            doc_type=type,
                            description=descript)
        doc_slug = slugify(title).lower()
        statement = text("SELECT COALESCE(NULLIF(regexp_replace(slug, '\D','','g'), '')::numeric, 0) AS num_only \
                    FROM documents \
                    WHERE (slug ~ '^{0}-[0-9]') or (slug = '{0}')\
                    ORDER BY num_only desc\
                    LIMIT 1;".format(doc_slug))
        min_slug = session.exec(statement).all()
        if not min_slug:
            result.slug = doc_slug
        else:
            result.slug = doc_slug + '-' + str(min_slug[0].num_only + 1)
        
        result.creation_date = datetime.today()
        result.owner_id = current_user.id

        if file_upload is not None:
            file_extension = Path_pathlib(file_upload.filename).suffix
            if file_upload.content_type not in ["application/pdf", "text/plain", "application/msword"] or file_extension not in [".pdf", ".txt", ".doc"]:
                raise HTTPException(400, detail="Invalid document type")
            upload_path = Path_pathlib("documents/" + str(result.owner_id) + "/" + str(result.slug) + file_extension)
            upload_path.parent.mkdir(exist_ok=True, parents=True)
            async with aiofiles.open(upload_path, 'wb') as out_file:
                while content := await file_upload.read(1024):
                    await out_file.write(content)
        result.path = "documents/" + str(result.owner_id) + "/" + str(result.slug) + file_extension

        session.add(result)
        session.commit()
        session.refresh(result)
        return result
    else:
        raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="No permissions"
    )

@document_router.put("/update/{id}")
async def update_doc(current_user: Annotated[UserModel, Depends(get_current_user)], id: int,
                 doc: DocumentCreate,
                 session: Session = Depends(get_session)):
    document = session.get(DocumentModel, id)
    if document:
        if current_user.permissions > 1 or document.owner_id == current_user.id:
            newdoc_data = doc.model_dump(exclude_unset=True)
            for key, value in newdoc_data.items(): 
                setattr(document, key, value)
            session.add(document)
            session.commit()
            session.refresh(document)
            return document
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not allowed"
            )
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="N/A"
    )

@document_router.delete("/delete/{id}")
async def delete_doc(current_user: Annotated[UserModel, Depends(get_current_user)], id: int,
                 session: Session = Depends(get_session)):
    document = session.get(DocumentModel, id)
    if document:
        if current_user.permissions > 1 or document.owner_id == current_user.id:
            if os.path.isfile(document.path):
                os.remove(document.path)
            session.delete(document)
            session.commit()
            return {"message": "Success"}
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not allowed"
            )
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="N/A"
    )

@document_router.get("/doctype/get", response_model=list[DocTypeModel])
async def get_doctype(current_user: Annotated[UserModel, Depends(get_current_user)],
                   session: Session = Depends(get_session)) -> dict:
    result = session.exec(select(DocTypeModel))
    doctypes = result.all()
    return [doc for doc in doctypes]

@document_router.post("/doctype/add", response_model=DocTypeModel)
async def post_doctype(current_user: Annotated[UserModel, Depends(get_current_user)],
                   type_title: str = Form(...),
                   session: Session = Depends(get_session)) -> dict:
    if current_user.permissions >= 2:
        result = DocTypeModel(title=type_title)
        session.add(result)
        session.commit()
        session.refresh(result)
        return result
    else:
        raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="No permissions"
    )