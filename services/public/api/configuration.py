from fastapi import APIRouter, Depends, status, HTTPException
from public.auth import get_admin
from public.schemas.configuration import ConfigurationItem
from public.crud.configuration import read_configuration, update_configuration
from sonja.database import get_session, Session

router = APIRouter()


@router.get("/configuration/current", response_model=ConfigurationItem, response_model_by_alias=False,
            dependencies=[Depends(get_admin)])
def get_current_configuration_item(session: Session = Depends(get_session)):
    return ConfigurationItem.from_db(read_configuration(session))


@router.patch("/configuration/{configuration_id}", response_model=ConfigurationItem, response_model_by_alias=False,
              dependencies=[Depends(get_admin)])
def patch_configuration_item(configuration_id: str, configuration_item: ConfigurationItem,
                            session: Session = Depends(get_session)):
    configuration = read_configuration(session)
    if configuration is None:
        raise HTTPException(status_code=404, detail="Configuration not found")
    patched_configuration = update_configuration(session, configuration, configuration_item)
    return ConfigurationItem.from_db(patched_configuration)