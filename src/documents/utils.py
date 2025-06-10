from fastapi import Depends
from sqlmodel import Session, text
from slugify import slugify

from documents.models import DocumentModel
from database import get_session

def unique_slug(document: DocumentModel,
                session: Session = Depends(get_session)):
    doc_slug = slugify(document.doc_name).lower()
    statement = text("SELECT COALESCE(NULLIF(regexp_replace(slug, '\D','','g'), '')::numeric, 0) AS num_only \
                FROM documents \
                WHERE (slug ~ '^{0}-[0-9]') or (slug = '{0}')\
                ORDER BY num_only desc\
                LIMIT 1;".format(doc_slug))
    min_slug = session.exec(statement).all()
    if not min_slug:
        document.slug = doc_slug
    else:
        document.slug = doc_slug + '-' + str(min_slug[0].num_only + 1)
    return document