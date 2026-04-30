from sqlalchemy import select
from Backend.DAL.models.models import ExitDocuments, EmployeeExit
from Backend.Business_Layer.utils.uuid_generator import generate_uuid7

class ExitDocumentsDAO:
    async def get_exit(self, db, exit_uuid):

        query = select(EmployeeExit).where(
            EmployeeExit.exit_uuid == exit_uuid
        )
        result = await db.execute(query)

        return result.scalars().first()

    async def create_document(
        self,
        db,
        exit_uuid,
        employee_uuid,
        document_type,
        file_name,
        file_path,
        user_id
    ):

        document = ExitDocuments(

            document_uuid=str(generate_uuid7()),
            exit_uuid=exit_uuid,
            employee_uuid=employee_uuid,
            document_type=document_type,
            file_name=file_name,
            file_path=file_path,
            uploaded_by=user_id
        )

        db.add(document)
        await db.commit()
        await db.refresh(document)

        return document


    async def get_documents(self, db, exit_uuid):

        query = select(ExitDocuments).where(
            ExitDocuments.exit_uuid == exit_uuid
        )

        result = await db.execute(query)

        return result.scalars().all()


    async def get_document(self, db, document_uuid):

        query = select(ExitDocuments).where(
            ExitDocuments.document_uuid == document_uuid
        )

        result = await db.execute(query)

        return result.scalars().first()