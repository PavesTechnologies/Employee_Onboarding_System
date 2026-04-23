from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.DAL.utils.dependencies import get_db
from Backend.Business_Layer.services.exit_approval_service import ExitApprovalService
from Backend.API_Layer.interfaces.exit_approval_interface import ExitApprovalCreate, ManagerApprovalRequest, ExitApprovalResponse, HRApprovalRequest
from fastapi import Request
from Backend.API_Layer.utils.role_based import require_roles


router = APIRouter(
    prefix="/exit-approvals",
    tags=["Exit Approvals"]
)

@router.post("/create")
async def create_exit_approval(
    data: ExitApprovalCreate,
    db: AsyncSession = Depends(get_db)
):
    try:
        service = ExitApprovalService()
        result = await service.create_exit_approval(db, data)
        return result

    except HTTPException as he:
        raise he

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.put(
    "/manager-approve",
    response_model=ExitApprovalResponse,
    dependencies=[Depends(require_roles("MANAGER"))]
)
async def manager_approve(
    payload: ManagerApprovalRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    try:
        user = request.state.user

        user_id = int(user.get("user_id"))
        user_name = user.get("name")

        service = ExitApprovalService()

        result = await service.manager_approve(
            db,
            payload.approval_uuid,
            user_id,
            payload.status,
            payload.remarks
        )

        result.approved_by_name = user_name

        return result

    except HTTPException as he:
        raise he

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
@router.put(
    "/hr-approve",
    response_model=ExitApprovalResponse,
    dependencies=[Depends(require_roles("HR"))]
)
async def hr_approve(
    payload: HRApprovalRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    try:
        user = request.state.user

        user_id = int(user.get("user_id"))
        user_name = user.get("name")

        service = ExitApprovalService()

        result = await service.hr_approve(
            db,
            payload.approval_uuid,
            user_id,
            payload.status,
            payload.remarks
        )

        result.approved_by_name = user_name

        return result

    except HTTPException as he:
        raise he

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
# get all approvals
@router.get(
    "/",
    response_model=list[ExitApprovalResponse],
    dependencies=[Depends(require_roles("MANAGER", "HR"))]
)
async def get_all_approvals(
    db: AsyncSession = Depends(get_db)
):
    try:
        service = ExitApprovalService()
        result = await service.get_all_approvals(db)
        return result

    except HTTPException as he:
        raise he

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

# get /exit-approvals/my-pending
@router.get("/pending/my-pending", response_model=list[ExitApprovalResponse])
async def get_my_pending_approvals(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    try:
        user = request.state.user
        roles = [role.upper() for role in user.get("roles", [])]

        service = ExitApprovalService()

        if "HR" in roles:
            role = "HR"
        elif "MANAGER" in roles:
            role = "Manager"
        else:
            return []

        result = await service.get_my_pending_approvals(
            db,
            role
        )
        print("User Roles::", roles)
        print("Selected Role:", role)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# get approvals by exit_uuid
@router.get(
    "/{exit_uuid}",
    response_model=list[ExitApprovalResponse],
    dependencies=[Depends(require_roles("MANAGER", "HR"))]
)
async def get_approvals_by_exit_uuid(
    exit_uuid: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        service = ExitApprovalService()
        result = await service.get_approvals_by_exit_uuid(db, exit_uuid)
        return result

    except HTTPException as he:
        raise he

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
# get approvals by employee_uuid
@router.get(
    "/employee/{employee_uuid}",
    response_model=list[ExitApprovalResponse],
    dependencies=[Depends(require_roles("MANAGER", "HR"))]
)
async def get_approvals_by_employee_uuid(
    employee_uuid: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        service = ExitApprovalService()
        result = await service.get_approvals_by_employee_uuid(db, employee_uuid)
        return result

    except HTTPException as he:
        raise he

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
# get /exit-approvals/history/{exit_uuid}
@router.get(
    "/history/{exit_uuid}",
    response_model=list[ExitApprovalResponse],
    dependencies=[Depends(require_roles("MANAGER", "HR"))]
)
async def get_approvals_history(
    exit_uuid: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        service = ExitApprovalService()
        result = await service.get_approvals_history(db, exit_uuid)
        return result

    except HTTPException as he:
        raise he

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
