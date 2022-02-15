from fastapi import APIRouter, Depends, HTTPException, status
from public.auth import get_read, get_write
from public.schemas.ecosystem import EcosystemReadItem, EcosystemReadList, EcosystemWriteItem
from public.crud.ecosystem import create_ecosystem, read_ecosystems, read_ecosystem_by_id, update_ecosystem,\
    delete_ecosystem
from sonja.database import get_session, Session, NotFound

router = APIRouter()


@router.get("/ecosystem", response_model=EcosystemReadList)
def get_ecosystems(session: Session = Depends(get_session), authorized: bool = Depends(get_read)):
    ecosystems = read_ecosystems(session)
    return EcosystemReadList.from_db(ecosystems)


@router.get("/ecosystem/{ecosystem_id}", response_model=EcosystemReadItem)
def get_ecosystem_item(ecosystem_id: str, session: Session = Depends(get_session),
                       authorized: bool = Depends(get_read)):
    ecosystem = read_ecosystem_by_id(session, ecosystem_id)
    if ecosystem is None:
        raise HTTPException(status_code=404, detail="Ecosystem not found")
    return EcosystemReadItem.from_db(ecosystem)


@router.post("/ecosystem", response_model=EcosystemReadItem, status_code=status.HTTP_201_CREATED)
def post_user_item(ecosystem: EcosystemWriteItem, session: Session = Depends(get_session),
                   authorized: bool = Depends(get_write)):
    new_ecosystem = create_ecosystem(session, ecosystem)
    return EcosystemReadItem.from_db(new_ecosystem)


@router.delete("/ecosystem/{ecosystem_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ecosystem_item(ecosystem_id: str, session: Session = Depends(get_session),
                          authorized: bool = Depends(get_write)):
    try:
        delete_ecosystem(session, ecosystem_id)
    except NotFound:
        raise HTTPException(status_code=404, detail="User not found")


@router.patch("/ecosystem/{ecosystem_id}", response_model=EcosystemReadItem)
def get_user_item(ecosystem_id: str, ecosystem_item: EcosystemWriteItem, session: Session = Depends(get_session),
                  authorized: bool = Depends(get_write)):
    ecosystem = read_ecosystem_by_id(session, ecosystem_id)
    if ecosystem is None:
        raise HTTPException(status_code=404, detail="Ecosystem not found")
    patched_user = update_ecosystem(session, ecosystem, ecosystem_item)
    return EcosystemReadItem.from_db(patched_user)