from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from Backend.DAL.utils.dependencies import get_db
from Backend.API_Layer.interfaces.addtask_interfaces import (
    EmployeeTaskCreateRequest,
    EmployeeTaskCreateResponse,
    EmployeeTaskListResponse,
    EmployeeTaskListResponse,
    EmployeeTaskUpdateRequest,
    EmployeeTaskUpdateResponse
)
from Backend.Business_Layer.services.addtask_service import EmployeeTasksService

router = APIRouter(
    prefix="/tasks",
    tags=["Employee Tasks"]
)


@router.post(
    "/create",
    response_model=EmployeeTaskCreateResponse
)
async def create_employee_task(
    request: EmployeeTaskCreateRequest,
    db: Session = Depends(get_db)
):
    return await EmployeeTasksService.create_employee_task(
        db,
        request
    )

@router.put(
    "/update/{task_uuid}",
    response_model=EmployeeTaskUpdateResponse
)
async def update_employee_task(
    task_uuid: str,
    request: EmployeeTaskUpdateRequest,
    db=Depends(get_db)
):
    return await EmployeeTasksService.update_employee_task(
        db,
        task_uuid,
        request
    )
@router.get(
    "/all",
    response_model=EmployeeTaskListResponse
)
async def get_all_employee_tasks(
    db=Depends(get_db)
):
    return await EmployeeTasksService.get_all_employee_tasks(db)

@router.get(
    "/by-user/{user_uuid}",
    response_model=EmployeeTaskListResponse
)
async def get_tasks_by_user(
    user_uuid: str,
    db: Session = Depends(get_db)
):
    return await EmployeeTasksService.get_tasks_by_user(db, user_uuid)
@router.delete(
    "/delete/{task_uuid}",
    response_model=EmployeeTaskUpdateResponse
)
async def delete_employee_task(
    task_uuid: str,
    db: Session = Depends(get_db)
):
    return await EmployeeTasksService.delete_employee_task(db, task_uuid)