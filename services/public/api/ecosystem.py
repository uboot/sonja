from fastapi import APIRouter, Depends, HTTPException, status
from public.auth import get_read, get_write
from public.schemas.ecosystem import EcosystemReadItem, EcosystemReadList, EcosystemWriteItem
from public.crud.ecosystem import create_ecosystem, read_ecosystems, read_ecosystem, update_ecosystem,\
    delete_ecosystem
from sonja.database import get_session, Session, NotFound

router = APIRouter()


@router.get("/ecosystem", response_model=EcosystemReadList, response_model_by_alias=False)
def get_ecosystem_list(session: Session = Depends(get_session), authorized: bool = Depends(get_read)):
    ecosystems = read_ecosystems(session)
    return EcosystemReadList.from_db(ecosystems)


@router.get("/ecosystem/{ecosystem_id}", response_model=EcosystemReadItem, response_model_by_alias=False)
def get_ecosystem_item(ecosystem_id: str, session: Session = Depends(get_session),
                       authorized: bool = Depends(get_read)):
    ecosystem = read_ecosystem(session, ecosystem_id)
    if ecosystem is None:
        raise HTTPException(status_code=404, detail="Ecosystem not found")
    return EcosystemReadItem.from_db(ecosystem)


@router.post("/ecosystem", response_model=EcosystemReadItem, response_model_by_alias=False,
             status_code=status.HTTP_201_CREATED)
def post_ecosystem_item(ecosystem: EcosystemWriteItem, session: Session = Depends(get_session),
                   authorized: bool = Depends(get_write)):
    new_ecosystem = create_ecosystem(session, ecosystem)
    return EcosystemReadItem.from_db(new_ecosystem)


@router.delete("/ecosystem/{ecosystem_id}")
def delete_ecosystem_item(ecosystem_id: str, session: Session = Depends(get_session),
                          authorized: bool = Depends(get_write)):
    ecosystem = read_ecosystem(session, ecosystem_id)
    if not ecosystem:
        raise HTTPException(status_code=404, detail="Ecosystem not found")
    delete_ecosystem(session, ecosystem)


@router.patch("/ecosystem/{ecosystem_id}", response_model=EcosystemReadItem, response_model_by_alias=False)
def patch_ecosystem_item(ecosystem_id: str, ecosystem_item: EcosystemWriteItem, session: Session = Depends(get_session),
                  authorized: bool = Depends(get_write)):
    ecosystem = read_ecosystem(session, ecosystem_id)
    if ecosystem is None:
        raise HTTPException(status_code=404, detail="Ecosystem not found")
    patched_ecosystem = update_ecosystem(session, ecosystem, ecosystem_item)
    return EcosystemReadItem.from_db(patched_ecosystem)
