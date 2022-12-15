from fastapi import APIRouter, Depends, HTTPException
from public.auth import get_read
from public.schemas.package import PackageReadItem
from public.crud.package import read_package
from sonja.database import get_session, Session

router = APIRouter()


@router.get("/package/{package_id}", response_model=PackageReadItem, response_model_by_alias=False,
            dependencies=[Depends(get_read)])
def get_package_item(package_id: str, session: Session = Depends(get_session)):
    package = read_package(session, package_id)
    if package is None:
        raise HTTPException(status_code=404, detail="Package not found")
    return PackageReadItem.from_db(package)
