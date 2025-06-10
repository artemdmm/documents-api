from fastapi import Depends, HTTPException, status, UploadFile, File, Form
from sqlmodel import Session, select
from typing import Annotated
from datetime import datetime
import aiofiles
import os
from pathlib import Path as Path_pathlib
from loguru import logger

from database import get_session
from documents.schemas import DocumentBase
from documents.models import DocumentModel, DocTypeModel
from documents.utils import unique_slug
from auth.models import UserModel
from auth.service import get_current_user

async def get_list_docs(current_user: Annotated[UserModel, Depends(get_current_user)],
                        session: Session = Depends(get_session)):
    result = session.exec(select(DocumentModel))
    documents = result.all()
    return [doc for doc in documents]

async def create_doc(current_user: Annotated[UserModel, Depends(get_current_user)],
                   title: str = Form(...),
                   descript: str = Form(...),
                   type: int = Form(...),
                   file_upload: UploadFile = File(...),
                   session: Session = Depends(get_session)):
    if current_user.permissions > 0:
        result = DocumentModel(doc_name=title, doc_type=type, description=descript)
        result = unique_slug(result, session)
        result.creation_date = datetime.today()
        result.owner_id = current_user.id

        if file_upload is not None:
            file_extension = Path_pathlib(file_upload.filename).suffix
            if file_upload.content_type not in ["application/pdf", "text/plain", "application/msword"] or file_extension not in [".pdf", ".txt", ".doc"]:
                raise HTTPException(400, detail="Invalid document type")
            upload_path = Path_pathlib("docs/" + str(result.owner_id) + "/" + str(result.slug) + file_extension)
            upload_path.parent.mkdir(exist_ok=True, parents=True)
            async with aiofiles.open(upload_path, 'wb') as out_file:
                while content := await file_upload.read(1024):
                    await out_file.write(content)
            result.path = "docs/" + str(result.owner_id) + "/" + str(result.slug) + file_extension
            logger.info(f"File {result.doc_name} was uploaded by user {current_user.email} to {result.path}")

        session.add(result)
        session.commit()
        session.refresh(result)
        return result
    else:
        raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="No permissions"
    )

async def update_doc(current_user: Annotated[UserModel, Depends(get_current_user)],
                     id: int,
                     doc: DocumentBase,
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

async def delete_doc(current_user: Annotated[UserModel, Depends(get_current_user)],
                     id: int,
                     session: Session = Depends(get_session)):
    document = session.get(DocumentModel, id)
    if document:
        if current_user.permissions > 1 or document.owner_id == current_user.id:
            if document.path:
                if os.path.isfile(document.path):
                    os.remove(document.path)
            session.delete(document)
            session.commit()
            logger.info(f"File {document.doc_name} was deleted by user {current_user.email}")
            return {"status": "Success"}
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not allowed"
            )
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="N/A"
    )

async def get_list_doctypes(current_user: Annotated[UserModel, Depends(get_current_user)],
                            session: Session = Depends(get_session)):
    result = session.exec(select(DocTypeModel))
    doctypes = result.all()
    return [doc for doc in doctypes]

async def create_doctype(current_user: Annotated[UserModel, Depends(get_current_user)],
                       type_title: str = Form(...),
                       session: Session = Depends(get_session)) -> dict:
    if current_user.permissions >= 2:
        result = DocTypeModel(title=type_title)
        session.add(result)
        session.commit()
        session.refresh(result)
        logger.info(f"Document type {result.title} was added by user {current_user.email}")
        return result
    else:
        raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="No permissions"
    )