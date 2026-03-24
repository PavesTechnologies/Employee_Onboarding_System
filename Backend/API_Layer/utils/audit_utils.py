# Backend/API_Layer/utils/audit_utils.py
from typing import Optional
class AuditUtils:
    def __init__(self):

        # Endpoints that should not be audited
        self.open_endpoints = [
            "/docs", "/openapi.json",
            "/redoc", "/login", "/health", "/employee-details", "/employee-upload"
        ]
        
        # Entity mapping for common patterns
        self.entity_mappings = {
            "offerletters": {
                "table": "offer_letter_details",
                "id_field": "user_uuid",
                "alternate_id_fields": ["offer_uuid", "pandadoc_draft_id"]   # optional alternate key
            },
            "offerresponse": {
                "table": "offer_letter_details",
                "id_field": "user_uuid",
                "alternate_id_fields": ["offer_uuid", "pandadoc_draft_id"]   # optional alternate key
            },
            "masters/country": {
                "table": "countries",
                "id_field": "country_uuid"
            },
            "masters/education-level": {
                "table": "education_level",
                "id_field": "education_uuid"
            },
            "masters/": {
                "table": "country_education_document_mapping",
                "id_field": "mapping_uuid"
            },
            "masters-contacts": {
                "table": "contacts",
                "id_field": "contact_uuid"
            },
            "education/employee-education-document": {
                "table": "employee_education_document",
                "id_field": "document_uuid"
            },
            "education/education-document": {
                "table": "education_document_type", 
                "id_field": "education_document_uuid"
            },
            "employee-upload": {
                "table": "personal_details",
                "id_field": "personal_uuid"
            },
            
            "employee-upload/address": {
                "table": "addresses",
                "id_field": "address_uuid"
            },
            "employee-upload/identity-documents": {
                "table": "employee_identity_document",
                "id_field": "document_uuid"
            },
            "addresses": {
                "table": "addresses",
                "id_field": "address_uuid"
            },
            "identity/country-mapping": {
                "table": "country_identity_mapping",
                "id_field": "mapping_uuid"
            },
            "identity": {
                "table": "identity_type",
                "id_field": "identity_type_uuid"
            },
            "employee-details/identity": {
                "table": "employee_identity_document",
                "id_field": "document_uuid"
            },
            "experience": {
                "table": "employee_experience",
                "id_field": "experience_uuid"
            },
                "employee-upload/relations": {
                "table": "relation",
                "id_field": "relation_uuid"
            },
            "education/degree-master": {
                "table": "degree_master",
                "id_field": "degree_uuid"
            }
        }


    def extract_entity_info(self, path: str, req_body: dict, method: str):
        print("path", path, req_body)

        cleaned_path = path.strip("/")
        path_parts = cleaned_path.split("/")
        print("cleaned path", cleaned_path)

        #  Step 1: find the longest matching entity key
        matched_entity = None
        for key in sorted(self.entity_mappings.keys(), key=len, reverse=True):
            if cleaned_path.startswith(key):
                matched_entity = key
                break

        if not matched_entity:
            return "unknown", None

        # Step 2: Extract entity_id only for PUT/DELETE
        if method in ("PUT", "DELETE"):
            entity_id = path_parts[-1] if len(path_parts) > 1 else None
        else:
            entity_id = None

        return matched_entity, entity_id


    def get_operation_type(self, method: str) -> str:
        """Map HTTP method to operation type"""
        return {
            "POST": "CREATE",
            "PUT": "UPDATE",
            "PATCH": "UPDATE",
            "DELETE": "DELETE"
        }.get(method, "UNKNOWN")

    async def get_data(self, db, entity_name: str, entity_id: str) -> Optional[dict]:
        """Fetch old data before update/delete"""
        if not entity_id or entity_name not in self.entity_mappings:
            return None
        
        try:
            table_name = self.entity_mappings[entity_name]["table"]
            id_field = self.entity_mappings[entity_name]["id_field"]
            
            # Use parameterized query to prevent SQL injection
            from sqlalchemy import text
            query = text(f"SELECT * FROM {table_name} WHERE {id_field} = :id")
            result = await db.execute(query, {"id": entity_id})
            row = result.mappings().first()
            
            if row:
                # Convert to dict and handle non-serializable types
                return {k: str(v) if not isinstance(v, (str, int, float, bool, type(None))) else v 
                        for k, v in dict(row).items()}
        except Exception as e:
            print(f"Error fetching old data: {e}")
        
        return None
    def _get_ip_address(*args, **kwargs) -> Optional[str]:
        request = kwargs.get("request")
        if request and hasattr(request, 'client') and request.client:
            return request.client.host
        return None