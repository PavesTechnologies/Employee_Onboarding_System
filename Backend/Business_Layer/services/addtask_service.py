from fastapi import HTTPException
from requests import Session
from Backend.DAL.dao.addtask_dao import EmployeeTasksDAO
from Backend.API_Layer.interfaces.addtask_interfaces import (
    EmployeeTaskCreateResponse,
    EmployeeTaskUpdateResponse,
        EmployeeTaskListResponse,
        EmployeeTaskItemResponse
)
from Backend.DAL.models.models import EmployeeTasks


class EmployeeTasksService:

    @staticmethod
    async def create_employee_task(db, request):

        task = await EmployeeTasksDAO.create_employee_task(
            db,
            request
        )

        if not task:
            raise HTTPException(
                status_code=404,
                detail="User UUID not found in offer letter records"
            )

        return EmployeeTaskCreateResponse(
            message="Employee task created successfully",
            task_uuid=task.task_uuid,
            task_title=task.task_title,
            status=task.status
        )
    
    @staticmethod
    async def update_employee_task(db, task_uuid, request):
        task = await EmployeeTasksDAO.update_employee_task(
            db,
            task_uuid,
            request
        )

        if not task:
            raise HTTPException(
                status_code=404,
                detail="Task UUID not found"
            )

        return EmployeeTaskUpdateResponse(
            message="Employee task updated successfully",
            task_uuid=task.task_uuid,
            task_title=task.task_title,
            status=task.status
        )
    @staticmethod
    async def get_all_employee_tasks(db):
            tasks = await EmployeeTasksDAO.get_all_employee_tasks(db)

            return EmployeeTaskListResponse(
                message="Employee tasks fetched successfully",
                total_tasks=len(tasks),
                tasks=[
                    EmployeeTaskItemResponse.model_validate(task)
                    for task in tasks
                ]
            )

    # @staticmethod
    # def get_tasks_by_user(db: Session, user_uuid: str):
    #     tasks = db.query(EmployeeTasks).filter(
    #         EmployeeTasks.user_uuid == user_uuid
    #     ).all()

    #     return {
    #         "tasks": tasks
    #     }
    @staticmethod
    async def get_tasks_by_user(db, user_uuid: str):
        tasks = await EmployeeTasksDAO.get_tasks_by_user(db, user_uuid)

        return EmployeeTaskListResponse(
            message="Employee tasks fetched successfully",
            total_tasks=len(tasks),
            tasks=[
                EmployeeTaskItemResponse.model_validate(task)
                for task in tasks
            ]
        )  
    @staticmethod
    async def delete_employee_task(db, task_uuid: str):
        task = await EmployeeTasksDAO.delete_employee_task(db, task_uuid)

        if not task:
            raise HTTPException(
                status_code=404,
                detail="Task UUID not found"
            )

        return EmployeeTaskUpdateResponse(
            message="Employee task deleted successfully",
            task_uuid=task.task_uuid,
            task_title=task.task_title,
            status=task.status
        )