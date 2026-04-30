from fastapi import HTTPException
from datetime import datetime

from Backend.DAL.dao.exit_documents_dao import ExitDocumentsDAO
from Backend.Business_Layer.utils.document_generator import generate_pdf
from Backend.DAL.utils.storage_utils import get_storage_service


class ExitDocumentsService:

    def __init__(self):

        self.dao = ExitDocumentsDAO()
        self.storage = get_storage_service()


    async def generate_single_document(
        self,
        db,
        exit_uuid,
        user_id,
        doc_type,
        template
    ):

        exit_data = await self.dao.get_exit(
            db,
            exit_uuid
        )

        if not exit_data:
            raise HTTPException(
                status_code=404,
                detail="Exit record not found"
            )

        context = {

            "first_name": exit_data.first_name,
            "last_name": exit_data.last_name,
            "employee_id": exit_data.employee_id,
            "designation": "Software Engineer",
            "joining_date": "",
            "last_working_day": exit_data.last_working_day,
            "date": datetime.today().date(),
            "net_payable": ""
        }

        file_name = f"{doc_type}_{exit_data.employee_id}.pdf"

        pdf_bytes = generate_pdf(
            template,
            context
        )

        s3_path = await self.storage.upload_file(
            pdf_bytes,
            folder="exit_documents",
            employee_uuid=exit_data.employee_uuid,
            custom_filename=file_name
        )

        record = await self.dao.create_document(
            db,
            exit_uuid,
            exit_data.employee_uuid,
            doc_type,
            file_name,
            s3_path,
            user_id
        )

        return record


    async def get_documents(self, db, exit_uuid):

        return await self.dao.get_documents(
            db,
            exit_uuid
        )


    async def get_document(self, db, document_uuid):

        return await self.dao.get_document(
            db,
            document_uuid
        )


    async def download_document(self, db, document_uuid):

        document = await self.dao.get_document(
            db,
            document_uuid
        )

        url = await self.storage.get_presigned_url(
            document.file_path,
            download=True
        )

        return {"download_url": url}


    async def view_document(self, db, document_uuid):

        document = await self.dao.get_document(
            db,
            document_uuid
        )

        url = await self.storage.get_presigned_url(
            document.file_path,
            download=False
        )

        return {"view_url": url}