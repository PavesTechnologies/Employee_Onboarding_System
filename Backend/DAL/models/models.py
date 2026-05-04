
from typing import Any, Optional
import datetime
import decimal

from sqlalchemy import BigInteger, CHAR, DECIMAL, Date, DateTime, Enum, ForeignKeyConstraint, Index, Integer, JSON, String, TIMESTAMP, Text, text, Boolean, ForeignKey
from sqlalchemy.dialects.mysql import ENUM, TINYINT, YEAR
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Column, Integer, String, DateTime
import uuid



class Base(DeclarativeBase):
    pass


class AuditTrail(Base):
    __tablename__ = 'audit_trail'

    audit_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    audit_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)
    entity_name: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(100), nullable=False)
    operation: Mapped[str] = mapped_column(Enum('CREATE', 'UPDATE', 'DELETE'), nullable=False)
    user_id: Mapped[Optional[str]] = mapped_column(String(100))
    old_data: Mapped[Optional[dict]] = mapped_column(JSON)
    new_data: Mapped[Optional[dict]] = mapped_column(JSON)
    ip_address: Mapped[Optional[str]] = mapped_column(String(50))
    host: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    endpoint: Mapped[Optional[str]] = mapped_column(String(100))


class Countries(Base):
    __tablename__ = 'countries'
    __table_args__ = (
        Index('country_uuid', 'country_uuid', unique=True),
        Index('idx_country_uuid', 'country_uuid')
    )

    country_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    country_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)
    country_name: Mapped[str] = mapped_column(String(100), nullable=False)
    calling_code: Mapped[Optional[str]] = mapped_column(String(5))
    is_active: Mapped[Optional[int]] = mapped_column(TINYINT(1), server_default=text("'1'"))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    addresses: Mapped[list['Addresses']] = relationship('Addresses', back_populates='countries')
    contacts: Mapped[list['Contacts']] = relationship('Contacts', back_populates='countries')
    country_education_document_mapping: Mapped[list['CountryEducationDocumentMapping']] = relationship('CountryEducationDocumentMapping', back_populates='countries')
    country_identity_mapping: Mapped[list['CountryIdentityMapping']] = relationship('CountryIdentityMapping', back_populates='countries')
    personal_details: Mapped[list['PersonalDetails']] = relationship('PersonalDetails', foreign_keys='[PersonalDetails.nationality_country_uuid]', back_populates='countries')
    personal_details_: Mapped[list['PersonalDetails']] = relationship('PersonalDetails', foreign_keys='[PersonalDetails.residence_country_uuid]', back_populates='countries_')


class DeliverableItems(Base):
    __tablename__ = 'deliverable_items'
    __table_args__ = (
        Index('deliverable_uuid', 'deliverable_uuid', unique=True),
    )

    deliverable_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    deliverable_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)
    item_name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    employee_deliverables: Mapped[list['EmployeeDeliverables']] = relationship('EmployeeDeliverables', back_populates='deliverable_items')


class Departments(Base):  
    __tablename__ = 'departments'  
    __table_args__ = (  
        Index('department_name', 'department_name', unique=True),  
        Index('department_name_2', 'department_name', unique=True),  
        Index('department_uuid', 'department_uuid', unique=True),  
        Index('unique_department_uuid', 'department_uuid', unique=True)  
    )  
  
    department_id: Mapped[int] = mapped_column(Integer, primary_key=True)  
    department_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)  
    department_name: Mapped[str] = mapped_column(String(100), nullable=False)  
    description: Mapped[Optional[str]] = mapped_column(String(255))  
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))  
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))  
  
    designations: Mapped[list['Designations']] = relationship('Designations', back_populates='departments')  
    employee_details: Mapped[list['EmployeeDetails']] = relationship('EmployeeDetails', back_populates='departments')  
    employee_exit: Mapped[list['EmployeeExit']] = relationship('EmployeeExit', back_populates='department')  
  
  

class Designations(Base):  
    __tablename__ = 'designations'  
    __table_args__ = (  
        ForeignKeyConstraint(['department_uuid'], ['departments.department_uuid'], ondelete='RESTRICT', onupdate='CASCADE', name='fk_designation_department'),  
        Index('designation_uuid', 'designation_uuid', unique=True),  
        Index('fk_designation_department', 'department_uuid')  
    )  
  
    designation_id: Mapped[int] = mapped_column(Integer, primary_key=True)  
    designation_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)  
    designation_name: Mapped[str] = mapped_column(String(100), nullable=False)  
    department_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)  
    description: Mapped[Optional[str]] = mapped_column(String(255))  
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))  
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))  
  
    departments: Mapped['Departments'] = relationship('Departments', back_populates='designations')  
    employee_details: Mapped[list['EmployeeDetails']] = relationship('EmployeeDetails', back_populates='designations')  
    employee_exit: Mapped[list['EmployeeExit']] = relationship('EmployeeExit', back_populates='designation')  
  
class EducationDocumentType(Base):
    __tablename__ = 'education_document_type'
    __table_args__ = (
        Index('education_document_uuid', 'education_document_uuid', unique=True),
    )

    education_document_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    education_document_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)
    document_name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(200))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    country_education_document_mapping: Mapped[list['CountryEducationDocumentMapping']] = relationship('CountryEducationDocumentMapping', back_populates='education_document_type')


class EducationLevel(Base):
    __tablename__ = 'education_level'
    __table_args__ = (
        Index('education_uuid', 'education_uuid', unique=True),
        Index('idx_edu_uuid_exact', 'education_uuid'),
        Index('idx_education_uuid', 'education_uuid')
    )

    education_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    education_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)
    education_name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(200))
    is_active: Mapped[Optional[int]] = mapped_column(TINYINT(1), server_default=text("'1'"))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    country_education_document_mapping: Mapped[list['CountryEducationDocumentMapping']] = relationship('CountryEducationDocumentMapping', back_populates='education_level')

    degree_master: Mapped[list["DegreeMaster"]] = relationship(
        "DegreeMaster",
        back_populates="education_level",
        lazy="selectin"
    )


class IdentityType(Base):
    __tablename__ = 'identity_type'
    __table_args__ = (
        Index('identity_type_uuid', 'identity_type_uuid', unique=True),
    )

    identity_type_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    identity_type_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)
    identity_type_name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255))
    is_active: Mapped[Optional[int]] = mapped_column(TINYINT(1), server_default=text("'1'"))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    country_identity_mapping: Mapped[list['CountryIdentityMapping']] = relationship('CountryIdentityMapping', back_populates='identity_type')


class OfferLetterDetails(Base):
    __tablename__ = 'offer_letter_details'
    __table_args__ = (
        Index('idx_offer_user_created', 'user_uuid', 'created_by'),
        Index('idx_offer_user_uuid', 'user_uuid'),
        Index('idx_user_uuid', 'user_uuid'),
        Index('mail', 'mail', unique=True),
        Index('user_uuid', 'user_uuid', unique=True)
    )

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)

   
    first_name: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    mail: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    country_code: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)
    contact_number: Mapped[Optional[str]] = mapped_column(String(15), nullable=True)
    designation: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    employee_type: Mapped[Optional[str]] = mapped_column(Enum('Full-Time', 'Part-Time', 'Intern', 'Contractor', 'Freelance'), nullable=True)
    package: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    currency: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    job_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    hire_type: Mapped[Optional[str]] = mapped_column(Enum('Direct', 'Offer'), nullable=True)
    middle_name: Mapped[Optional[str]] = mapped_column(String(100))
    package: Mapped[Optional[str]] = mapped_column(String(255))
    currency: Mapped[Optional[str]] = mapped_column(String(20))
    status: Mapped[Optional[str]] = mapped_column(ENUM('Created', 'Offered', 'Accepted', 'Rejected', 'Submitted', 'Verified', 'Joining','Completed','Joining Pending','Rescheduled'), server_default=text("'Created'"))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    file_path: Mapped[Optional[str]] = mapped_column(String(255))
    pandadoc_draft_id: Mapped[Optional[str]] = mapped_column(String(255))
    offer_response_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    joining_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    cc_emails: Mapped[Optional[str]] = mapped_column(String(256))
    total_ctc: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(12, 2))
    reporting_manager: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    joining_comments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    addresses: Mapped[list['Addresses']] = relationship('Addresses', back_populates='offer_letter_details')
    contacts: Mapped[list['Contacts']] = relationship('Contacts', back_populates='offer_letter_details')
    employee_deliverables: Mapped[list['EmployeeDeliverables']] = relationship('EmployeeDeliverables', back_populates='offer_letter_details')
    employee_details: Mapped[list['EmployeeDetails']] = relationship('EmployeeDetails', back_populates='offer_letter_details')
    employee_experience: Mapped[list['EmployeeExperience']] = relationship('EmployeeExperience', back_populates='offer_letter_details')
    employee_receivables: Mapped[list['EmployeeReceivables']] = relationship('EmployeeReceivables', back_populates='offer_letter_details')
    offer_approval_request: Mapped[list['OfferApprovalRequest']] = relationship('OfferApprovalRequest', back_populates='offer_letter_details')
    offer_compensation: Mapped[list['OfferCompensation']] = relationship('OfferCompensation', back_populates='offer_letter_details')
    onboarding_links: Mapped[list['OnboardingLinks']] = relationship('OnboardingLinks', back_populates='offer_letter_details')
    personal_details: Mapped[list['PersonalDetails']] = relationship('PersonalDetails', back_populates='offer_letter_details')
    employee_education_document: Mapped[list['EmployeeEducationDocument']] = relationship('EmployeeEducationDocument', back_populates='offer_letter_details')
    employee_identity_document: Mapped[list['EmployeeIdentityDocument']] = relationship('EmployeeIdentityDocument', back_populates='offer_letter_details')
    employee_social_links: Mapped[list['EmployeeSocialLink']] = relationship('EmployeeSocialLink', back_populates='offer_letter_details')
    employee_pay_slips: Mapped[list['EmployeePaySlips']] = relationship('EmployeePaySlips', back_populates='offer_letter_details')
    employee_relieving_letter: Mapped[list['EmployeeRelievingLetter']] = relationship('EmployeeRelievingLetter', back_populates='offer_letter_details')

    employee_bank_details: Mapped[list["EmployeeBankDetails"]] = relationship("EmployeeBankDetails",lazy="selectin")
    employee_pf_details: Mapped[list["EmployeePfDetails"]] = relationship("EmployeePfDetails",lazy="selectin")


class Otptable(Base):
    __tablename__ = 'otptable'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    otp: Mapped[str] = mapped_column(String(10), nullable=False)
    expirytime: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)


class ReceivableItems(Base):
    __tablename__ = 'receivable_items'
    __table_args__ = (
        Index('receivable_uuid', 'receivable_uuid', unique=True),
    )

    receivable_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    receivable_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)
    item_name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    employee_receivables: Mapped[list['EmployeeReceivables']] = relationship('EmployeeReceivables', back_populates='receivable_items')


# class Relation(Base):
#     __tablename__ = 'relation'
#     __table_args__ = (
#         Index('relation_uuid', 'relation_uuid', unique=True),
#     )

#     id: Mapped[int] = mapped_column(Integer, primary_key=True)
#     relation_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)
#     relation_name: Mapped[str] = mapped_column(String(50), nullable=False)
#     created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
#     updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))



class Addresses(Base):
    __tablename__ = 'addresses'
    __table_args__ = (
        ForeignKeyConstraint(['country_uuid'], ['countries.country_uuid'], name='addresses_ibfk_2'),
        ForeignKeyConstraint(['user_uuid'], ['offer_letter_details.user_uuid'], name='addresses_ibfk_1'),
        Index('address_uuid', 'address_uuid', unique=True),
        Index('country_uuid', 'country_uuid'),
        Index('idx_address_user', 'user_uuid'),
        Index('idx_addresses_user_type', 'user_uuid', 'address_type'),
        Index('user_uuid', 'user_uuid')
    )

    address_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    address_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)
    user_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)
    address_type: Mapped[str] = mapped_column(Enum('permanent', 'current'), nullable=False)
    address_line1: Mapped[str] = mapped_column(String(255), nullable=False)
    country_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)
    address_line2: Mapped[Optional[str]] = mapped_column(String(255))
    city: Mapped[Optional[str]] = mapped_column(String(150))
    district_or_ward: Mapped[Optional[str]] = mapped_column(String(150))
    state_or_region: Mapped[Optional[str]] = mapped_column(String(150))
    postal_code: Mapped[Optional[str]] = mapped_column(String(20))
    status: Mapped[Optional[str]] = mapped_column(Enum('uploaded', 'verified', 'rejected'), server_default=text("'uploaded'"))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    countries: Mapped['Countries'] = relationship('Countries', back_populates='addresses')
    offer_letter_details: Mapped['OfferLetterDetails'] = relationship('OfferLetterDetails', back_populates='addresses')


class Contacts(Base):
    __tablename__ = 'contacts'
    __table_args__ = (
        ForeignKeyConstraint(['country_uuid'], ['countries.country_uuid'], name='contacts_ibfk_2'),
        ForeignKeyConstraint(['user_uuid'], ['offer_letter_details.user_uuid'], name='contacts_ibfk_1'),
        Index('contact_uuid', 'contact_uuid', unique=True),
        Index('country_uuid', 'country_uuid'),
        Index('user_uuid', 'user_uuid')
    )

    contact_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    contact_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)
    user_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)
    country_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)
    contact_number: Mapped[str] = mapped_column(String(15), nullable=False)
    emergency_contact: Mapped[str] = mapped_column(String(15), nullable=False)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    countries: Mapped['Countries'] = relationship('Countries', back_populates='contacts')
    offer_letter_details: Mapped['OfferLetterDetails'] = relationship('OfferLetterDetails', back_populates='contacts')


class CountryEducationDocumentMapping(Base):
    __tablename__ = 'country_education_document_mapping'
    __table_args__ = (
        ForeignKeyConstraint(['country_uuid'], ['countries.country_uuid'], name='country_education_document_mapping_ibfk_1'),
        ForeignKeyConstraint(['education_document_uuid'], ['education_document_type.education_document_uuid'], name='country_education_document_mapping_ibfk_3'),
        ForeignKeyConstraint(['education_uuid'], ['education_level.education_uuid'], name='country_education_document_mapping_ibfk_2'),
        Index('country_uuid', 'country_uuid'),
        Index('education_document_uuid', 'education_document_uuid'),
        Index('education_uuid', 'education_uuid'),
        Index('idx_edu_mapping', 'mapping_uuid'),
        Index('mapping_uuid', 'mapping_uuid', unique=True)
    )

    mapping_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    mapping_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)
    country_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)
    education_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)
    education_document_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)
    is_mandatory: Mapped[Optional[int]] = mapped_column(TINYINT(1), server_default=text("'1'"))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    countries: Mapped['Countries'] = relationship('Countries', back_populates='country_education_document_mapping')
    education_document_type: Mapped['EducationDocumentType'] = relationship('EducationDocumentType', back_populates='country_education_document_mapping')
    education_level: Mapped['EducationLevel'] = relationship('EducationLevel', back_populates='country_education_document_mapping')
    employee_education_document: Mapped[list['EmployeeEducationDocument']] = relationship('EmployeeEducationDocument', back_populates='country_education_document_mapping')


class CountryIdentityMapping(Base):
    __tablename__ = 'country_identity_mapping'
    __table_args__ = (
        ForeignKeyConstraint(['country_uuid'], ['countries.country_uuid'], name='country_identity_mapping_ibfk_1'),
        ForeignKeyConstraint(['identity_type_uuid'], ['identity_type.identity_type_uuid'], name='country_identity_mapping_ibfk_2'),
        Index('country_uuid', 'country_uuid'),
        Index('identity_type_uuid', 'identity_type_uuid'),
        Index('idx_identity_mapping', 'mapping_uuid'),
        Index('mapping_uuid', 'mapping_uuid', unique=True)
    )

    mapping_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    mapping_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)
    country_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)
    identity_type_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)
    is_mandatory: Mapped[Optional[int]] = mapped_column(TINYINT(1), server_default=text("'1'"))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    countries: Mapped['Countries'] = relationship('Countries', back_populates='country_identity_mapping')
    identity_type: Mapped['IdentityType'] = relationship('IdentityType', back_populates='country_identity_mapping')
    employee_identity_document: Mapped[list['EmployeeIdentityDocument']] = relationship('EmployeeIdentityDocument', back_populates='country_identity_mapping')


class EmployeeDeliverables(Base):
    __tablename__ = 'employee_deliverables'
    __table_args__ = (
        ForeignKeyConstraint(['deliverable_uuid'], ['deliverable_items.deliverable_uuid'], name='employee_deliverables_ibfk_2'),
        ForeignKeyConstraint(['user_uuid'], ['offer_letter_details.user_uuid'], name='employee_deliverables_ibfk_1'),
        Index('deliverable_uuid', 'deliverable_uuid'),
        Index('employee_deliverable_uuid', 'employee_deliverable_uuid', unique=True),
        Index('user_uuid', 'user_uuid')
    )

    employee_deliverable_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    employee_deliverable_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)
    user_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)
    deliverable_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)
    status: Mapped[Optional[str]] = mapped_column(Enum('Pending', 'Delivered', 'Returned'), server_default=text("'Pending'"))
    issued_by: Mapped[Optional[str]] = mapped_column(CHAR(36))
    issued_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    returned_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    remarks: Mapped[Optional[str]] = mapped_column(String(255))

    deliverable_items: Mapped['DeliverableItems'] = relationship('DeliverableItems', back_populates='employee_deliverables')
    offer_letter_details: Mapped['OfferLetterDetails'] = relationship('OfferLetterDetails', back_populates='employee_deliverables')


class EmployeeDetails(Base):  
    __tablename__ = 'employee_details'  
    __table_args__ = (  
        ForeignKeyConstraint(['department_uuid'], ['departments.department_uuid'], name='fk_employee_department'),  
        ForeignKeyConstraint(['designation_uuid'], ['designations.designation_uuid'], name='fk_employee_designation'),  
        ForeignKeyConstraint(['user_uuid'], ['offer_letter_details.user_uuid'], ondelete='CASCADE', name='fk_employee_offer'),  
        Index('employee_id', 'employee_id', unique=True),  
        Index('employee_uuid', 'employee_uuid', unique=True),  
        Index('fk_employee_department', 'department_uuid'),  
        Index('fk_employee_designation', 'designation_uuid'),  
        Index('fk_employee_offer', 'user_uuid'),  
        Index('work_email', 'work_email', unique=True)  
    )  
  
    id: Mapped[int] = mapped_column(Integer, primary_key=True)  
    employee_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)  
    user_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)  
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)  
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)  
    location: Mapped[str] = mapped_column(String(100), nullable=False)  
    work_mode: Mapped[str] = mapped_column(Enum('Office', 'Remote', 'Hybrid'), nullable=False)  
    employee_id: Mapped[Optional[str]] = mapped_column(String(20))  
    middle_name: Mapped[Optional[str]] = mapped_column(String(50))  
    date_of_birth: Mapped[Optional[datetime.date]] = mapped_column(Date)  
    work_email: Mapped[Optional[str]] = mapped_column(String(100))  
    contact_number: Mapped[Optional[str]] = mapped_column(String(15))  
    department_uuid: Mapped[Optional[str]] = mapped_column(CHAR(36))  
    designation_uuid: Mapped[Optional[str]] = mapped_column(CHAR(36))  
    reporting_manager_uuid: Mapped[Optional[str]] = mapped_column(CHAR(36))  
    employment_type: Mapped[Optional[str]] = mapped_column(Enum('Full-Time', 'Part-Time', 'Intern', 'Contractor', 'Freelance'))  
    joining_date: Mapped[Optional[datetime.date]] = mapped_column(Date)  
    employment_status: Mapped[Optional[str]] = mapped_column(Enum('Probation', 'Active', 'Resigned', 'Terminated', 'Absconded','Exited','On-Notice'), server_default=text("'Probation'"))  
    blood_group: Mapped[Optional[str]] = mapped_column(String(5))  
    gender: Mapped[Optional[str]] = mapped_column(Enum('Male', 'Female', 'Other'))  
    marital_status: Mapped[Optional[str]] = mapped_column(Enum('Single', 'Married', 'Divorced', 'Widowed'))  
    total_experience: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(4, 1))  
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))  
    created_by: Mapped[Optional[str]] = mapped_column(CHAR(36))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))  
    export_status: Mapped[Optional[str]] = mapped_column(
    Enum('NOT_EXPORTED', 'SUCCESS', 'FAILED', 'ALREADY_EXISTS'),server_default=text("'NOT_EXPORTED'"))
    export_error: Mapped[Optional[str]] = mapped_column(Text)
    exported_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP)
    departments: Mapped[Optional['Departments']] = relationship('Departments', back_populates='employee_details')  
    designations: Mapped[Optional['Designations']] = relationship('Designations', back_populates='employee_details')  
    offer_letter_details: Mapped['OfferLetterDetails'] = relationship('OfferLetterDetails', back_populates='employee_details')  
    employee_exit: Mapped[list['EmployeeExit']] = relationship('EmployeeExit', back_populates='employee_details')  
    exit_clearance: Mapped[list['ExitClearance']] = relationship('ExitClearance', back_populates='employee_details')  
    exit_documents: Mapped[list['ExitDocuments']] = relationship('ExitDocuments', back_populates='employee_details')  
    exit_final_settlement: Mapped[list['ExitFinalSettlement']] = relationship('ExitFinalSettlement', back_populates='employee_details')  
    exit_interview: Mapped[list['ExitInterview']] = relationship('ExitInterview', back_populates='employee_details')  
    employee_about: Mapped[Optional["EmployeeAbout"]] = relationship('EmployeeAbout', back_populates='employee_details', uselist=False)
  
class EmployeeExperience(Base):
    __tablename__ = 'employee_experience'
    __table_args__ = (
        ForeignKeyConstraint(['employee_uuid'], ['offer_letter_details.user_uuid'], name='employee_experience_ibfk_1'),
        Index('employee_uuid', 'employee_uuid'),
        Index('experience_uuid', 'experience_uuid', unique=True),
        Index('idx_experience_user', 'employee_uuid')
    )

    experience_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    experience_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)
    employee_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)
    company_name: Mapped[str] = mapped_column(String(150), nullable=False)
    start_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    role_title: Mapped[Optional[str]] = mapped_column(String(100))
    employment_type: Mapped[Optional[str]] = mapped_column(Enum('Full-Time', 'Part-Time', 'Intern', 'Contract', 'Freelance'))
    end_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    is_current: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text("'0'"))
    exp_certificate_path: Mapped[Optional[str]] = mapped_column(String(255))
    internship_certificate_path: Mapped[Optional[str]] = mapped_column(String(255))
    payslip_path: Mapped[Optional[str]] = mapped_column(String(255))
    contract_aggrement_path: Mapped[Optional[str]] = mapped_column(String(255))
    status: Mapped[Optional[str]] = mapped_column(Enum('uploaded', 'verified', 'rejected'),server_default=text("'uploaded'"))
    uploaded_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    verified_by: Mapped[Optional[str]] = mapped_column(CHAR(36))
    verified_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    notice_period_days: Mapped[Optional[int]] = mapped_column(Integer)
   # remarks: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    offer_letter_details: Mapped['OfferLetterDetails'] = relationship('OfferLetterDetails', back_populates='employee_experience')
    employee_pay_slips: Mapped[list['EmployeePaySlips']] = relationship('EmployeePaySlips', back_populates='employee_experience')
    employee_relieving_letter: Mapped[list['EmployeeRelievingLetter']] = relationship('EmployeeRelievingLetter', back_populates='employee_experience')

class EmployeeBankDetails(Base):
    __tablename__ = "employee_bank_details"
    bank_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    bank_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)
    user_uuid: Mapped[str] = mapped_column(
        CHAR(36),
        ForeignKey("offer_letter_details.user_uuid"),
        nullable=False
    )

    account_holder_name: Mapped[str] = mapped_column(String(150), nullable=False)
    bank_name: Mapped[str] = mapped_column(String(100), nullable=False)
    branch_name: Mapped[Optional[str]] = mapped_column(String(100))
    account_number: Mapped[str] = mapped_column(String(30), nullable=False)
    ifsc_code: Mapped[str] = mapped_column(String(15), nullable=False)
    account_type: Mapped[str] = mapped_column(Enum("Savings", "Current"))
    status: Mapped[Optional[str]] = mapped_column(Enum('uploaded', 'verified', 'rejected'), server_default=text("'uploaded'"))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

class EmployeePfDetails(Base):
    __tablename__ = "employee_pf_details"
    pf_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    pf_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)
    user_uuid: Mapped[str] = mapped_column(
        CHAR(36),
        ForeignKey("offer_letter_details.user_uuid"),
        nullable=False
    )

    pf_member: Mapped[bool] = mapped_column(Boolean, nullable=False)
    uan_number: Mapped[Optional[str]] = mapped_column(String(20))
    status: Mapped[Optional[str]] = mapped_column(Enum('uploaded', 'verified', 'rejected'), server_default=text("'uploaded'"))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

class EmployeeReceivables(Base):
    __tablename__ = 'employee_receivables'
    __table_args__ = (
        ForeignKeyConstraint(['receivable_uuid'], ['receivable_items.receivable_uuid'], name='employee_receivables_ibfk_2'),
        ForeignKeyConstraint(['user_uuid'], ['offer_letter_details.user_uuid'], name='employee_receivables_ibfk_1'),
        Index('employee_receivable_uuid', 'employee_receivable_uuid', unique=True),
        Index('receivable_uuid', 'receivable_uuid'),
        Index('user_uuid', 'user_uuid')
    )

    employee_receivable_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    employee_receivable_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)
    user_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)
    receivable_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)
    status: Mapped[Optional[str]] = mapped_column(Enum('Pending', 'Received', 'Not Received'), server_default=text("'Pending'"))
    collected_by: Mapped[Optional[str]] = mapped_column(CHAR(36))
    collected_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    remarks: Mapped[Optional[str]] = mapped_column(String(255))

    receivable_items: Mapped['ReceivableItems'] = relationship('ReceivableItems', back_populates='employee_receivables')
    offer_letter_details: Mapped['OfferLetterDetails'] = relationship('OfferLetterDetails', back_populates='employee_receivables')


class OfferApprovalRequest(Base):
    __tablename__ = 'offer_approval_request'
    __table_args__ = (
        ForeignKeyConstraint(['user_uuid'], ['offer_letter_details.user_uuid'], ondelete='CASCADE', name='fk_offer_req_user_uuid'),
        Index('idx_approval_user', 'user_uuid'),
        Index('idx_offer_request_user_uuid', 'user_uuid'),
        Index('idx_offer_request_uuid', 'user_uuid'),
        Index('idx_user_uuid', 'user_uuid')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)
    request_by: Mapped[int] = mapped_column(Integer, nullable=False)
    action_taker_id: Mapped[int] = mapped_column(Integer, nullable=False)
    request_time: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))

    offer_letter_details: Mapped['OfferLetterDetails'] = relationship('OfferLetterDetails', back_populates='offer_approval_request')
    offer_approval_action: Mapped[list['OfferApprovalAction']] = relationship('OfferApprovalAction', back_populates='request')


class OfferCompensation(Base):
    __tablename__ = 'offer_compensation'
    __table_args__ = (
        ForeignKeyConstraint(['offer_uuid'], ['offer_letter_details.user_uuid'], ondelete='CASCADE', name='fk_offer_compensation_offer'),
        Index('fk_offer_compensation_offer', 'offer_uuid')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    offer_uuid: Mapped[str] = mapped_column(String(36), nullable=False)
    name: Mapped[Optional[str]] = mapped_column(String(255))
    type: Mapped[Optional[str]] = mapped_column(String(50))
    frequency: Mapped[Optional[str]] = mapped_column(String(50))
    amount: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(12, 2))

    offer_letter_details: Mapped['OfferLetterDetails'] = relationship('OfferLetterDetails', back_populates='offer_compensation')


class OnboardingLinks(Base):
    __tablename__ = 'onboarding_links'
    __table_args__ = (
        ForeignKeyConstraint(['user_uuid'], ['offer_letter_details.user_uuid'], ondelete='CASCADE', name='fk_onboarding_user_uuid'),
        Index('uq_onboarding_token_hash', 'token_hash', unique=True),
        Index('uq_onboarding_user_uuid', 'user_uuid', unique=True)
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    token_hash: Mapped[str] = mapped_column(CHAR(64), nullable=False)
    expires_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)

    offer_letter_details: Mapped['OfferLetterDetails'] = relationship('OfferLetterDetails', back_populates='onboarding_links')


class PersonalDetails(Base):
    __tablename__ = 'personal_details'
    __table_args__ = (
        ForeignKeyConstraint(['nationality_country_uuid'], ['countries.country_uuid'], name='personal_details_ibfk_2'),
        ForeignKeyConstraint(['residence_country_uuid'], ['countries.country_uuid'], name='personal_details_ibfk_3'),
        ForeignKeyConstraint(['user_uuid'], ['offer_letter_details.user_uuid'], name='personal_details_ibfk_1'),
        ForeignKeyConstraint(['emergency_contact_relation_uuid'], ['relation_master.relation_uuid'], name='personal_details_ibfk_4'),

        Index('idx_personal_user', 'user_uuid'),
        Index('idx_personal_user_uuid', 'user_uuid'),
        Index('nationality_country_uuid', 'nationality_country_uuid'),
        Index('personal_uuid', 'personal_uuid', unique=True),
        Index('residence_country_uuid', 'residence_country_uuid'),
        Index('user_uuid', 'user_uuid')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    personal_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)
    user_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)
    date_of_birth: Mapped[Optional[datetime.date]] = mapped_column(Date)
    gender: Mapped[Optional[str]] = mapped_column(Enum('Male', 'Female', 'Other'))
    marital_status: Mapped[Optional[str]] = mapped_column(Enum('Single', 'Married', 'Divorced', 'Widowed'))
    blood_group: Mapped[Optional[str]] = mapped_column(String(5))
    nationality_country_uuid: Mapped[Optional[str]] = mapped_column(CHAR(36))
    residence_country_uuid: Mapped[Optional[str]] = mapped_column(CHAR(36))
    emergency_contact_name: Mapped[Optional[str]] = mapped_column(String(100))
    emergency_contact_phone: Mapped[Optional[str]] = mapped_column(String(20))
    emergency_contact_relation_uuid: Mapped[Optional[str]] = mapped_column(CHAR(36), ForeignKey("relation.relation_uuid"))
    status: Mapped[Optional[str]] = mapped_column(Enum('uploaded', 'verified', 'rejected'), server_default=text("'uploaded'"))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    countries: Mapped[Optional['Countries']] = relationship(
        'Countries',
        foreign_keys=[nationality_country_uuid],
        back_populates='personal_details',
        lazy="selectin"
    )

    countries_: Mapped[Optional['Countries']] = relationship(
        'Countries',
        foreign_keys=[residence_country_uuid],
        back_populates='personal_details_',
        lazy="selectin"
    )

    offer_letter_details: Mapped['OfferLetterDetails'] = relationship(
        'OfferLetterDetails',
        back_populates='personal_details',
        lazy="selectin"
    )

    # Relation Master Relationship
    relation: Mapped[Optional['RelationMaster']] = relationship(
        'RelationMaster',
        foreign_keys=[emergency_contact_relation_uuid],
        lazy="selectin"
    )

class RelationMaster(Base):
    __tablename__ = "relation_master"
    __table_args__ = (
        Index('relation_uuid', 'relation_uuid', unique=True),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    relation_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)
    relation_name: Mapped[str] = mapped_column(String(50), nullable=False)

    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime,
        server_default=text('CURRENT_TIMESTAMP')
    )

    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime,
        server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')
    )

class EmployeeEducationDocument(Base):
    __tablename__ = 'employee_education_document'
    __table_args__ = (
        ForeignKeyConstraint(['mapping_uuid'], ['country_education_document_mapping.mapping_uuid'], name='employee_education_document_ibfk_1'),
        ForeignKeyConstraint(['user_uuid'], ['offer_letter_details.user_uuid'], name='employee_education_document_ibfk_2'),
        ForeignKeyConstraint(['degree_uuid'], ['degree_master.degree_uuid'], name='employee_education_document_ibfk_3'),
        Index('document_uuid', 'document_uuid', unique=True),
        Index('idx_education_user', 'user_uuid'),
        Index('mapping_uuid', 'mapping_uuid'),
        Index('user_uuid', 'user_uuid')
    )

    employee_education_document_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    document_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)
    mapping_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)
    user_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)
    institution_name: Mapped[Optional[str]] = mapped_column(String(150))
    institute_location: Mapped[Optional[str]] = mapped_column(String(150))
    degree_uuid: Mapped[Optional[str]] = mapped_column(CHAR(36))
    specialization: Mapped[Optional[str]] = mapped_column(String(150))
    education_mode: Mapped[Optional[str]] = mapped_column(
        Enum('Regular', 'Distance', 'Part Time', 'Online')
    )
    start_year: Mapped[Optional[Any]] = mapped_column(YEAR)
    year_of_passing: Mapped[Optional[Any]] = mapped_column(YEAR)
    percentage_cgpa: Mapped[Optional[str]] = mapped_column(String(10))
    delay_reason: Mapped[Optional[str]] = mapped_column(String(255))
    file_path: Mapped[Optional[str]] = mapped_column(String(255))
    status: Mapped[Optional[str]] = mapped_column(Enum('uploaded', 'verified', 'rejected'), server_default=text("'uploaded'"))
    uploaded_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    verified_by: Mapped[Optional[str]] = mapped_column(CHAR(36))
    verified_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)


    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime,
        server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')
    )

    country_education_document_mapping: Mapped['CountryEducationDocumentMapping'] = relationship(
        'CountryEducationDocumentMapping',
        back_populates='employee_education_document',
        lazy="selectin"
    )

    offer_letter_details: Mapped['OfferLetterDetails'] = relationship(
        'OfferLetterDetails',
        back_populates='employee_education_document',
        lazy="selectin"
    )

    degree_master: Mapped['DegreeMaster'] = relationship(
        'DegreeMaster',
        lazy="selectin"
    )
class DegreeMaster(Base):
    __tablename__ = 'degree_master'
    __table_args__ = (
        ForeignKeyConstraint(
            ['education_uuid'],
            ['education_level.education_uuid'],
            name='degree_master_ibfk_1'
        ),
        Index('degree_uuid', 'degree_uuid', unique=True),
    )

    degree_id: Mapped[int] = mapped_column(Integer, primary_key=True)

    degree_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)

    degree_name: Mapped[str] = mapped_column(String(100), nullable=False)

    education_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)

    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime,
        server_default=text('CURRENT_TIMESTAMP')
    )

    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime,
        server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')
    )

    # relationships
    education_level: Mapped['EducationLevel'] = relationship(
        'EducationLevel',
        back_populates='degree_master',
        lazy="selectin"
    )

    employee_education_document: Mapped[list['EmployeeEducationDocument']] = relationship(
        'EmployeeEducationDocument',
        back_populates='degree_master',
        lazy="selectin"
    )
class EmployeeIdentityDocument(Base):
    __tablename__ = 'employee_identity_document'
    __table_args__ = (
        ForeignKeyConstraint(['mapping_uuid'], ['country_identity_mapping.mapping_uuid'], name='employee_identity_document_ibfk_1'),
        ForeignKeyConstraint(['user_uuid'], ['offer_letter_details.user_uuid'], name='employee_identity_document_ibfk_2'),
        Index('document_uuid', 'document_uuid', unique=True),
        Index('idx_identity_user', 'user_uuid'),
        Index('mapping_uuid', 'mapping_uuid'),
        Index('user_uuid', 'user_uuid')
    )

    employee_identity_document_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    document_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)
    mapping_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)
    user_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)
    identity_file_number: Mapped[Optional[str]] = mapped_column(String(255))
    file_path: Mapped[Optional[str]] = mapped_column(String(255))
    expiry_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    status: Mapped[Optional[str]] = mapped_column(Enum('uploaded', 'verified', 'rejected'), server_default=text("'uploaded'"))
    uploaded_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    verified_by: Mapped[Optional[str]] = mapped_column(CHAR(36))
    verified_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    remarks: Mapped[Optional[str]] = mapped_column(String(255))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    country_identity_mapping: Mapped['CountryIdentityMapping'] = relationship('CountryIdentityMapping', back_populates='employee_identity_document')
    offer_letter_details: Mapped['OfferLetterDetails'] = relationship('OfferLetterDetails', back_populates='employee_identity_document')

class EmployeeSocialLink(Base):
    __tablename__ = 'employee_social_links'
    __table_args__ = (
        ForeignKeyConstraint(
            ['user_uuid'],
            ['offer_letter_details.user_uuid'],
            name='employee_social_links_ibfk_1'
        ),
        Index('social_link_uuid', 'social_link_uuid', unique=True),
        Index('idx_social_link_user', 'user_uuid')
    )

    social_link_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    social_link_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)
    user_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)
    platform_name: Mapped[str] = mapped_column(String(100), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    offer_letter_details: Mapped['OfferLetterDetails'] = relationship('OfferLetterDetails', back_populates='employee_social_links')

class EmployeeAbout(Base):
    __tablename__ = "employee_about"
    __table_args__ = (
        ForeignKeyConstraint(
            ["employee_uuid"],
            ["employee_details.employee_uuid"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="fk_employee_about_employee"
        ),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    employee_about_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)
    employee_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)
    about_me: Mapped[Optional[str]] = mapped_column(Text)
    work_enjoyment: Mapped[Optional[str]] = mapped_column(Text)
    interests_hobbies: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
    employee_details: Mapped['EmployeeDetails'] = relationship('EmployeeDetails', back_populates='employee_about')
class EmployeePaySlips(Base):
    __tablename__ = 'employee_pay_slips'
    __table_args__ = (
        ForeignKeyConstraint(['employee_uuid'], ['offer_letter_details.user_uuid'], name='employee_pay_slips_ibfk_1'),
        ForeignKeyConstraint(['experience_uuid'], ['employee_experience.experience_uuid'], name='employee_pay_slips_ibfk_2'),
        Index('employee_uuid', 'employee_uuid'),
        Index('experience_uuid', 'experience_uuid'),
        Index('pay_slip_uuid', 'pay_slip_uuid', unique=True)
    )

    pay_slip_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    pay_slip_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)
    employee_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)
    experience_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)
    file_path: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[Optional[str]] = mapped_column(Enum('uploaded', 'pending', 'verified', 'rejected'), server_default=text("'pending'"))
    uploaded_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    verified_by: Mapped[Optional[str]] = mapped_column(CHAR(36))
    verified_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    offer_letter_details: Mapped['OfferLetterDetails'] = relationship('OfferLetterDetails', back_populates='employee_pay_slips')
    employee_experience: Mapped['EmployeeExperience'] = relationship('EmployeeExperience', back_populates='employee_pay_slips')


class EmployeeRelievingLetter(Base):
    __tablename__ = 'employee_relieving_letter'
    __table_args__ = (
        ForeignKeyConstraint(['employee_uuid'], ['offer_letter_details.user_uuid'], name='employee_relieving_letter_ibfk_1'),
        ForeignKeyConstraint(['experience_uuid'], ['employee_experience.experience_uuid'], name='employee_relieving_letter_ibfk_2'),
        Index('employee_uuid', 'employee_uuid'),
        Index('experience_uuid', 'experience_uuid'),
        Index('relieving_uuid', 'relieving_uuid', unique=True)
    )

    relieving_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    relieving_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)
    employee_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)
    experience_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)
    file_path: Mapped[Optional[str]] = mapped_column(String(255))
    status: Mapped[Optional[str]] = mapped_column(Enum('uploaded', 'pending', 'verified', 'rejected'), server_default=text("'pending'"))
    uploaded_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    verified_by: Mapped[Optional[str]] = mapped_column(CHAR(36))
    verified_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    remarks: Mapped[Optional[str]] = mapped_column(String(255))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    offer_letter_details: Mapped['OfferLetterDetails'] = relationship('OfferLetterDetails', back_populates='employee_relieving_letter')
    employee_experience: Mapped['EmployeeExperience'] = relationship('EmployeeExperience', back_populates='employee_relieving_letter')


class OfferApprovalAction(Base):
    __tablename__ = 'offer_approval_action'
    __table_args__ = (
        ForeignKeyConstraint(['request_id'], ['offer_approval_request.id'], ondelete='CASCADE', name='fk_offer_action_request'),
        Index('idx_approval_action_request', 'request_id'),
        Index('idx_offer_action_request_id', 'request_id'),
        Index('idx_request_id', 'request_id')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    request_id: Mapped[int] = mapped_column(Integer, nullable=False)
    action: Mapped[str] = mapped_column(Enum('Pending', 'APPROVED', 'REJECTED', 'ON_HOLD'), nullable=False, server_default=text("'Pending'"))
    comment: Mapped[Optional[str]] = mapped_column(Text)
    action_time: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))

    request: Mapped['OfferApprovalRequest'] = relationship('OfferApprovalRequest', back_populates='offer_approval_action')


# from typing import Any, Optional  
# import datetime  
# import decimal  
  
# from sqlalchemy import BigInteger, CHAR, CheckConstraint, DECIMAL, Date, DateTime, Enum, ForeignKeyConstraint, Index, Integer, JSON, String, TIMESTAMP, Text, text  
# from sqlalchemy.dialects.mysql import TINYINT, YEAR  
# from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship  
  
# class Base(DeclarativeBase):  
#     pass  
  
  
# class AuditTrail(Base):  
#     __tablename__ = 'audit_trail'  
  
#     audit_id: Mapped[int] = mapped_column(Integer, primary_key=True)  
#     audit_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)  
#     entity_name: Mapped[str] = mapped_column(String(100), nullable=False)  
#     entity_id: Mapped[str] = mapped_column(String(100), nullable=False)  
#     operation: Mapped[str] = mapped_column(Enum('CREATE', 'UPDATE', 'DELETE'), nullable=False)  
#     user_id: Mapped[Optional[str]] = mapped_column(String(100))  
#     old_data: Mapped[Optional[dict]] = mapped_column(JSON)  
#     new_data: Mapped[Optional[dict]] = mapped_column(JSON)  
#     ip_address: Mapped[Optional[str]] = mapped_column(String(50))  
#     host: Mapped[Optional[str]] = mapped_column(String(255))  
#     created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))  
#     endpoint: Mapped[Optional[str]] = mapped_column(String(100))  
  
  
# class Countries(Base):  
#     __tablename__ = 'countries'  
#     __table_args__ = (  
#         Index('country_uuid', 'country_uuid', unique=True),  
#         Index('idx_country_uuid', 'country_uuid')  
#     )  
  
#     country_id: Mapped[int] = mapped_column(Integer, primary_key=True)  
#     country_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)  
#     country_name: Mapped[str] = mapped_column(String(100), nullable=False)  
#     calling_code: Mapped[Optional[str]] = mapped_column(String(5))  
#     is_active: Mapped[Optional[int]] = mapped_column(TINYINT(1), server_default=text("'1'"))  
#     created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))  
#     updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))  
  
#     addresses: Mapped[list['Addresses']] = relationship('Addresses', back_populates='countries')  
#     contacts: Mapped[list['Contacts']] = relationship('Contacts', back_populates='countries')  
#     country_education_document_mapping: Mapped[list['CountryEducationDocumentMapping']] = relationship('CountryEducationDocumentMapping', back_populates='countries')  
#     country_identity_mapping: Mapped[list['CountryIdentityMapping']] = relationship('CountryIdentityMapping', back_populates='countries')  
#     personal_details: Mapped[list['PersonalDetails']] = relationship('PersonalDetails', foreign_keys='[PersonalDetails.nationality_country_uuid]', back_populates='countries')  
#     personal_details_: Mapped[list['PersonalDetails']] = relationship('PersonalDetails', foreign_keys='[PersonalDetails.residence_country_uuid]', back_populates='countries_')  
  
  
# class DeliverableItems(Base):  
#     __tablename__ = 'deliverable_items'  
#     __table_args__ = (  
#         Index('deliverable_uuid', 'deliverable_uuid', unique=True),  
#     )  
  
#     deliverable_id: Mapped[int] = mapped_column(Integer, primary_key=True)  
#     deliverable_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)  
#     item_name: Mapped[str] = mapped_column(String(100), nullable=False)  
#     description: Mapped[Optional[str]] = mapped_column(String(255))  
#     created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))  
  
#     employee_deliverables: Mapped[list['EmployeeDeliverables']] = relationship('EmployeeDeliverables', back_populates='deliverable_items')  
  
  
# class Departments(Base):  
#     __tablename__ = 'departments'  
#     __table_args__ = (  
#         Index('department_name', 'department_name', unique=True),  
#         Index('department_name_2', 'department_name', unique=True),  
#         Index('department_uuid', 'department_uuid', unique=True),  
#         Index('unique_department_uuid', 'department_uuid', unique=True)  
#     )  
  
#     department_id: Mapped[int] = mapped_column(Integer, primary_key=True)  
#     department_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)  
#     department_name: Mapped[str] = mapped_column(String(100), nullable=False)  
#     description: Mapped[Optional[str]] = mapped_column(String(255))  
#     created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))  
#     updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))  
  
#     designations: Mapped[list['Designations']] = relationship('Designations', back_populates='departments')  
#     employee_details: Mapped[list['EmployeeDetails']] = relationship('EmployeeDetails', back_populates='departments')  
#     employee_exit: Mapped[list['EmployeeExit']] = relationship('EmployeeExit', back_populates='department')  
  
  
# class EducationDocumentType(Base):  
#     __tablename__ = 'education_document_type'  
#     __table_args__ = (  
#         Index('education_document_uuid', 'education_document_uuid', unique=True),  
#     )  
  
#     education_document_id: Mapped[int] = mapped_column(Integer, primary_key=True)  
#     education_document_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)  
#     document_name: Mapped[str] = mapped_column(String(100), nullable=False)  
#     description: Mapped[Optional[str]] = mapped_column(String(200))  
#     created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))  
  
#     country_education_document_mapping: Mapped[list['CountryEducationDocumentMapping']] = relationship('CountryEducationDocumentMapping', back_populates='education_document_type')  
  
  
# class EducationLevel(Base):  
#     __tablename__ = 'education_level'  
#     __table_args__ = (  
#         Index('education_uuid', 'education_uuid', unique=True),  
#         Index('idx_edu_uuid_exact', 'education_uuid'),  
#         Index('idx_education_uuid', 'education_uuid')  
#     )  
  
#     education_id: Mapped[int] = mapped_column(Integer, primary_key=True)  
#     education_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)  
#     education_name: Mapped[str] = mapped_column(String(100), nullable=False)  
#     description: Mapped[Optional[str]] = mapped_column(String(200))  
#     is_active: Mapped[Optional[int]] = mapped_column(TINYINT(1), server_default=text("'1'"))  
#     created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))  
#     updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))  
  
#     country_education_document_mapping: Mapped[list['CountryEducationDocumentMapping']] = relationship('CountryEducationDocumentMapping', back_populates='education_level')  
#     degree_master: Mapped[list['DegreeMaster']] = relationship('DegreeMaster', back_populates='education_level')  
  
  
# class IdentityType(Base):  
#     __tablename__ = 'identity_type'  
#     __table_args__ = (  
#         Index('identity_type_uuid', 'identity_type_uuid', unique=True),  
#     )  
  
#     identity_type_id: Mapped[int] = mapped_column(Integer, primary_key=True)  
#     identity_type_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)  
#     identity_type_name: Mapped[str] = mapped_column(String(100), nullable=False)  
#     description: Mapped[Optional[str]] = mapped_column(String(255))  
#     is_active: Mapped[Optional[int]] = mapped_column(TINYINT(1), server_default=text("'1'"))  
#     created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))  
#     updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))  
  
#     country_identity_mapping: Mapped[list['CountryIdentityMapping']] = relationship('CountryIdentityMapping', back_populates='identity_type')  
  
  
# # class OfferLetterDetails(Base):  
# #     __tablename__ = 'offer_letter_details'  
# #     __table_args__ = (  
# #         Index('idx_offer_user_created', 'user_uuid', 'created_by'),  
# #         Index('idx_offer_user_uuid', 'user_uuid'),  
# #         Index('idx_user_uuid', 'user_uuid'),  
# #         Index('mail', 'mail', unique=True),  
# #         Index('user_uuid', 'user_uuid', unique=True)  
# #     )  
  
# #     user_id: Mapped[int] = mapped_column(Integer, primary_key=True)  
# #     user_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)  
# #     first_name: Mapped[str] = mapped_column(String(50), nullable=False)  
# #     last_name: Mapped[str] = mapped_column(String(50), nullable=False)  
# #     mail: Mapped[str] = mapped_column(String(100), nullable=False)  
# #     country_code: Mapped[str] = mapped_column(String(5), nullable=False)  
# #     contact_number: Mapped[str] = mapped_column(String(15), nullable=False)  
# #     designation: Mapped[str] = mapped_column(String(50), nullable=False)  
# #     employee_type: Mapped[str] = mapped_column(Enum('Full-Time', 'Part-Time', 'Intern', 'Contractor', 'Freelance'), nullable=False)  
# #     created_by: Mapped[int] = mapped_column(Integer, nullable=False)  
# #     middle_name: Mapped[Optional[str]] = mapped_column(String(100))  
# #     package: Mapped[Optional[str]] = mapped_column(String(255))  
# #     currency: Mapped[Optional[str]] = mapped_column(String(20))  
# #     status: Mapped[Optional[str]] = mapped_column(Enum('Created', 'Offered', 'Accepted', 'Rejected', 'Submitted', 'Verified', 'Joining', 'Completed','Joining Pending'), server_default=text("'Created'"))  
# #     created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))  
# #     updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))  
# #     file_path: Mapped[Optional[str]] = mapped_column(String(255))  
# #     pandadoc_draft_id: Mapped[Optional[str]] = mapped_column(String(255))  
# #     offer_response_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)  
# #     joining_date: Mapped[Optional[datetime.date]] = mapped_column(Date)  
# #     cc_emails: Mapped[Optional[str]] = mapped_column(String(256))  
# #     total_ctc: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(12, 2))  
# #     job_id: Mapped[Optional[str]] = mapped_column(String(50))  
# #     hire_type: Mapped[Optional[str]] = mapped_column(Enum('Offer', 'Direct'), server_default=text("'Offer'"))  
# #     reporting_manager: Mapped[Optional[str]] = mapped_column(String(100))  
  
# #     addresses: Mapped[list['Addresses']] = relationship('Addresses', back_populates='offer_letter_details')  
# #     contacts: Mapped[list['Contacts']] = relationship('Contacts', back_populates='offer_letter_details')  
# #     employee_bank_details: Mapped[list['EmployeeBankDetails']] = relationship('EmployeeBankDetails', back_populates='offer_letter_details')  
# #     employee_deliverables: Mapped[list['EmployeeDeliverables']] = relationship('EmployeeDeliverables', back_populates='offer_letter_details')  
# #     employee_experience: Mapped[list['EmployeeExperience']] = relationship('EmployeeExperience', back_populates='offer_letter_details')  
# #     employee_pf_details: Mapped[list['EmployeePfDetails']] = relationship('EmployeePfDetails', back_populates='offer_letter_details')  
# #     employee_receivables: Mapped[list['EmployeeReceivables']] = relationship('EmployeeReceivables', back_populates='offer_letter_details')  
# #     employee_social_links: Mapped[list['EmployeeSocialLinks']] = relationship('EmployeeSocialLinks', back_populates='offer_letter_details')  
# #     offer_approval_request: Mapped[list['OfferApprovalRequest']] = relationship('OfferApprovalRequest', back_populates='offer_letter_details')  
# #     offer_compensation: Mapped[list['OfferCompensation']] = relationship('OfferCompensation', back_populates='offer_letter_details')  
# #     onboarding_links: Mapped[list['OnboardingLinks']] = relationship('OnboardingLinks', back_populates='offer_letter_details')  
# #     personal_details: Mapped[list['PersonalDetails']] = relationship('PersonalDetails', back_populates='offer_letter_details')  
# #     employee_details: Mapped[list['EmployeeDetails']] = relationship('EmployeeDetails', back_populates='offer_letter_details')  
# #     employee_education_document: Mapped[list['EmployeeEducationDocument']] = relationship('EmployeeEducationDocument', back_populates='offer_letter_details')  
# #     employee_identity_document: Mapped[list['EmployeeIdentityDocument']] = relationship('EmployeeIdentityDocument', back_populates='offer_letter_details')  
# #     employee_pay_slips: Mapped[list['EmployeePaySlips']] = relationship('EmployeePaySlips', back_populates='offer_letter_details')  
# #     employee_relieving_letter: Mapped[list['EmployeeRelievingLetter']] = relationship('EmployeeRelievingLetter', back_populates='offer_letter_details')  
  
  
# class Otptable(Base):  
#     __tablename__ = 'otptable'  
  
#     id: Mapped[int] = mapped_column(Integer, primary_key=True)  
#     email: Mapped[str] = mapped_column(String(255), nullable=False)  
#     otp: Mapped[str] = mapped_column(String(10), nullable=False)  
#     expirytime: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)  
  
  
# class ReceivableItems(Base):  
#     __tablename__ = 'receivable_items'  
#     __table_args__ = (  
#         Index('receivable_uuid', 'receivable_uuid', unique=True),  
#     )  
  
#     receivable_id: Mapped[int] = mapped_column(Integer, primary_key=True)  
#     receivable_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)  
#     item_name: Mapped[str] = mapped_column(String(100), nullable=False)  
#     description: Mapped[Optional[str]] = mapped_column(String(255))  
#     created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))  
  
#     employee_receivables: Mapped[list['EmployeeReceivables']] = relationship('EmployeeReceivables', back_populates='receivable_items')  
  
  
# class RelationMaster(Base):  
#     __tablename__ = 'relation_master'  
#     __table_args__ = (  
#         Index('relation_uuid', 'relation_uuid', unique=True),  
#     )  
  
#     id: Mapped[int] = mapped_column(Integer, primary_key=True)  
#     relation_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)  
#     relation_name: Mapped[str] = mapped_column(String(50), nullable=False)  
#     created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))  
#     updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))  
  
  
# class Addresses(Base):  
#     __tablename__ = 'addresses'  
#     __table_args__ = (  
#         ForeignKeyConstraint(['country_uuid'], ['countries.country_uuid'], name='addresses_ibfk_2'),  
#         ForeignKeyConstraint(['user_uuid'], ['offer_letter_details.user_uuid'], name='addresses_ibfk_1'),  
#         Index('address_uuid', 'address_uuid', unique=True),  
#         Index('country_uuid', 'country_uuid'),  
#         Index('idx_address_user', 'user_uuid'),  
#         Index('idx_addresses_user_type', 'user_uuid', 'address_type'),  
#         Index('user_uuid', 'user_uuid')  
#     )  
  
#     address_id: Mapped[int] = mapped_column(Integer, primary_key=True)  
#     address_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)  
#     user_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)  
#     address_type: Mapped[str] = mapped_column(Enum('permanent', 'current'), nullable=False)  
#     address_line1: Mapped[str] = mapped_column(String(255), nullable=False)  
#     country_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)  
#     address_line2: Mapped[Optional[str]] = mapped_column(String(255))  
#     city: Mapped[Optional[str]] = mapped_column(String(150))  
#     district_or_ward: Mapped[Optional[str]] = mapped_column(String(150))  
#     state_or_region: Mapped[Optional[str]] = mapped_column(String(150))  
#     postal_code: Mapped[Optional[str]] = mapped_column(String(20))  
#     created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))  
#     updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))  
#     status: Mapped[Optional[str]] = mapped_column(Enum('uploaded', 'verified', 'rejected'), server_default=text("'uploaded'"))  
  
#     countries: Mapped['Countries'] = relationship('Countries', back_populates='addresses')  
#     offer_letter_details: Mapped['OfferLetterDetails'] = relationship('OfferLetterDetails', back_populates='addresses')  
  
  
# class Contacts(Base):  
#     __tablename__ = 'contacts'  
#     __table_args__ = (  
#         ForeignKeyConstraint(['country_uuid'], ['countries.country_uuid'], name='contacts_ibfk_2'),  
#         ForeignKeyConstraint(['user_uuid'], ['offer_letter_details.user_uuid'], name='contacts_ibfk_1'),  
#         Index('contact_uuid', 'contact_uuid', unique=True),  
#         Index('country_uuid', 'country_uuid'),  
#         Index('user_uuid', 'user_uuid')  
#     )  
  
#     contact_id: Mapped[int] = mapped_column(Integer, primary_key=True)  
#     contact_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)  
#     user_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)  
#     country_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)  
#     contact_number: Mapped[str] = mapped_column(String(15), nullable=False)  
#     emergency_contact: Mapped[str] = mapped_column(String(15), nullable=False)  
#     created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))  
#     updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))  
  
#     countries: Mapped['Countries'] = relationship('Countries', back_populates='contacts')  
#     offer_letter_details: Mapped['OfferLetterDetails'] = relationship('OfferLetterDetails', back_populates='contacts')  
  
  
# class CountryEducationDocumentMapping(Base):  
#     __tablename__ = 'country_education_document_mapping'  
#     __table_args__ = (  
#         ForeignKeyConstraint(['country_uuid'], ['countries.country_uuid'], name='country_education_document_mapping_ibfk_1'),  
#         ForeignKeyConstraint(['education_document_uuid'], ['education_document_type.education_document_uuid'], name='country_education_document_mapping_ibfk_3'),  
#         ForeignKeyConstraint(['education_uuid'], ['education_level.education_uuid'], name='country_education_document_mapping_ibfk_2'),  
#         Index('country_uuid', 'country_uuid'),  
#         Index('education_document_uuid', 'education_document_uuid'),  
#         Index('education_uuid', 'education_uuid'),  
#         Index('idx_edu_mapping', 'mapping_uuid'),  
#         Index('mapping_uuid', 'mapping_uuid', unique=True)  
#     )  
  
#     mapping_id: Mapped[int] = mapped_column(Integer, primary_key=True)  
#     mapping_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)  
#     country_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)  
#     education_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)  
#     education_document_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)  
#     is_mandatory: Mapped[Optional[int]] = mapped_column(TINYINT(1), server_default=text("'1'"))  
#     created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))  
#     updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))  
  
#     countries: Mapped['Countries'] = relationship('Countries', back_populates='country_education_document_mapping')  
#     education_document_type: Mapped['EducationDocumentType'] = relationship('EducationDocumentType', back_populates='country_education_document_mapping')  
#     education_level: Mapped['EducationLevel'] = relationship('EducationLevel', back_populates='country_education_document_mapping')  
#     employee_education_document: Mapped[list['EmployeeEducationDocument']] = relationship('EmployeeEducationDocument', back_populates='country_education_document_mapping')  
  
  
# class CountryIdentityMapping(Base):  
#     __tablename__ = 'country_identity_mapping'  
#     __table_args__ = (  
#         ForeignKeyConstraint(['country_uuid'], ['countries.country_uuid'], name='country_identity_mapping_ibfk_1'),  
#         ForeignKeyConstraint(['identity_type_uuid'], ['identity_type.identity_type_uuid'], name='country_identity_mapping_ibfk_2'),  
#         Index('country_uuid', 'country_uuid'),  
#         Index('identity_type_uuid', 'identity_type_uuid'),  
#         Index('idx_identity_mapping', 'mapping_uuid'),  
#         Index('mapping_uuid', 'mapping_uuid', unique=True)  
#     )  
  
#     mapping_id: Mapped[int] = mapped_column(Integer, primary_key=True)  
#     mapping_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)  
#     country_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)  
#     identity_type_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)  
#     is_mandatory: Mapped[Optional[int]] = mapped_column(TINYINT(1), server_default=text("'1'"))  
#     created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))  
#     updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))  
  
#     countries: Mapped['Countries'] = relationship('Countries', back_populates='country_identity_mapping')  
#     identity_type: Mapped['IdentityType'] = relationship('IdentityType', back_populates='country_identity_mapping')  
#     employee_identity_document: Mapped[list['EmployeeIdentityDocument']] = relationship('EmployeeIdentityDocument', back_populates='country_identity_mapping')  
  
  
# class DegreeMaster(Base):  
#     __tablename__ = 'degree_master'  
#     __table_args__ = (  
#         ForeignKeyConstraint(['education_uuid'], ['education_level.education_uuid'], name='degree_master_ibfk_1'),  
#         Index('degree_uuid', 'degree_uuid', unique=True),  
#         Index('education_uuid', 'education_uuid')  
#     )  
  
#     degree_id: Mapped[int] = mapped_column(Integer, primary_key=True)  
#     degree_name: Mapped[str] = mapped_column(String(100), nullable=False)  
#     education_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)  
#     degree_uuid: Mapped[Optional[str]] = mapped_column(CHAR(36))  
#     created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))  
#     updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))  
  
#     education_level: Mapped['EducationLevel'] = relationship('EducationLevel', back_populates='degree_master')  
#     employee_education_document: Mapped[list['EmployeeEducationDocument']] = relationship('EmployeeEducationDocument', back_populates='degree_master')  
  
  
# class Designations(Base):  
#     __tablename__ = 'designations'  
#     __table_args__ = (  
#         ForeignKeyConstraint(['department_uuid'], ['departments.department_uuid'], ondelete='RESTRICT', onupdate='CASCADE', name='fk_designation_department'),  
#         Index('designation_uuid', 'designation_uuid', unique=True),  
#         Index('fk_designation_department', 'department_uuid')  
#     )  
  
#     designation_id: Mapped[int] = mapped_column(Integer, primary_key=True)  
#     designation_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)  
#     designation_name: Mapped[str] = mapped_column(String(100), nullable=False)  
#     department_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)  
#     description: Mapped[Optional[str]] = mapped_column(String(255))  
#     created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))  
#     updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))  
  
#     departments: Mapped['Departments'] = relationship('Departments', back_populates='designations')  
#     employee_details: Mapped[list['EmployeeDetails']] = relationship('EmployeeDetails', back_populates='designations')  
#     employee_exit: Mapped[list['EmployeeExit']] = relationship('EmployeeExit', back_populates='designation')  
  
  
# class EmployeeBankDetails(Base):  
#     __tablename__ = 'employee_bank_details'  
#     __table_args__ = (  
#         ForeignKeyConstraint(['user_uuid'], ['offer_letter_details.user_uuid'], name='fk_bank_user'),  
#         Index('bank_uuid', 'bank_uuid', unique=True),  
#         Index('fk_bank_user', 'user_uuid')  
#     )  
  
#     bank_id: Mapped[int] = mapped_column(Integer, primary_key=True)  
#     bank_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)  
#     user_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)  
#     account_holder_name: Mapped[str] = mapped_column(String(150), nullable=False)  
#     bank_name: Mapped[str] = mapped_column(String(100), nullable=False)  
#     account_number: Mapped[str] = mapped_column(String(30), nullable=False)  
#     ifsc_code: Mapped[str] = mapped_column(String(15), nullable=False)  
#     account_type: Mapped[str] = mapped_column(Enum('Savings', 'Current'), nullable=False)  
#     branch_name: Mapped[Optional[str]] = mapped_column(String(100))  
#     created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))  
#     updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))  
#     status: Mapped[Optional[str]] = mapped_column(Enum('uploaded', 'verified', 'rejected'), server_default=text("'uploaded'"))  
  
#     offer_letter_details: Mapped['OfferLetterDetails'] = relationship('OfferLetterDetails', back_populates='employee_bank_details')  
  
  
# class EmployeeDeliverables(Base):  
#     __tablename__ = 'employee_deliverables'  
#     __table_args__ = (  
#         ForeignKeyConstraint(['deliverable_uuid'], ['deliverable_items.deliverable_uuid'], name='employee_deliverables_ibfk_2'),  
#         ForeignKeyConstraint(['user_uuid'], ['offer_letter_details.user_uuid'], name='employee_deliverables_ibfk_1'),  
#         Index('deliverable_uuid', 'deliverable_uuid'),  
#         Index('employee_deliverable_uuid', 'employee_deliverable_uuid', unique=True),  
#         Index('user_uuid', 'user_uuid')  
#     )  
  
#     employee_deliverable_id: Mapped[int] = mapped_column(Integer, primary_key=True)  
#     employee_deliverable_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)  
#     user_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)  
#     deliverable_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)  
#     status: Mapped[Optional[str]] = mapped_column(Enum('Pending', 'Delivered', 'Returned'), server_default=text("'Pending'"))  
#     issued_by: Mapped[Optional[str]] = mapped_column(CHAR(36))  
#     issued_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)  
#     returned_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)  
#     remarks: Mapped[Optional[str]] = mapped_column(String(255))  
  
#     deliverable_items: Mapped['DeliverableItems'] = relationship('DeliverableItems', back_populates='employee_deliverables')  
#     offer_letter_details: Mapped['OfferLetterDetails'] = relationship('OfferLetterDetails', back_populates='employee_deliverables')  
  
  
# class EmployeeExperience(Base):  
#     __tablename__ = 'employee_experience'  
#     __table_args__ = (  
#         CheckConstraint('((`notice_period_days` >= 0) and (`notice_period_days` <= 120))', name='check_notice_period'),  
#         ForeignKeyConstraint(['employee_uuid'], ['offer_letter_details.user_uuid'], name='employee_experience_ibfk_1'),  
#         Index('employee_uuid', 'employee_uuid'),  
#         Index('experience_uuid', 'experience_uuid', unique=True),  
#         Index('idx_experience_user', 'employee_uuid')  
#     )  
  
#     experience_id: Mapped[int] = mapped_column(Integer, primary_key=True)  
#     experience_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)  
#     employee_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)  
#     company_name: Mapped[str] = mapped_column(String(150), nullable=False)  
#     start_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)  
#     role_title: Mapped[Optional[str]] = mapped_column(String(100))  
#     employment_type: Mapped[Optional[str]] = mapped_column(Enum('Full-Time', 'Part-Time', 'Intern', 'Contract', 'Freelance'))  
#     end_date: Mapped[Optional[datetime.date]] = mapped_column(Date)  
#     is_current: Mapped[Optional[int]] = mapped_column(TINYINT(1), server_default=text("'0'"))  
#     exp_certificate_path: Mapped[Optional[str]] = mapped_column(String(255))  
#     internship_certificate_path: Mapped[Optional[str]] = mapped_column(String(255))  
#     payslip_path: Mapped[Optional[str]] = mapped_column(String(255))  
#     contract_aggrement_path: Mapped[Optional[str]] = mapped_column(String(255))  
#     status: Mapped[Optional[str]] = mapped_column(Enum('uploaded', 'verified', 'rejected'), server_default=text("'uploaded'"))  
#     uploaded_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))  
#     verified_by: Mapped[Optional[str]] = mapped_column(CHAR(36))  
#     verified_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)  
#     created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))  
#     updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))  
#     notice_period_days: Mapped[Optional[int]] = mapped_column(Integer)  
  
#     offer_letter_details: Mapped['OfferLetterDetails'] = relationship('OfferLetterDetails', back_populates='employee_experience')  
#     employee_pay_slips: Mapped[list['EmployeePaySlips']] = relationship('EmployeePaySlips', back_populates='employee_experience')  
#     employee_relieving_letter: Mapped[list['EmployeeRelievingLetter']] = relationship('EmployeeRelievingLetter', back_populates='employee_experience')  
  
  
# class EmployeePfDetails(Base):  
#     __tablename__ = 'employee_pf_details'  
#     __table_args__ = (  
#         ForeignKeyConstraint(['user_uuid'], ['offer_letter_details.user_uuid'], name='fk_pf_user'),  
#         Index('fk_pf_user', 'user_uuid'),  
#         Index('pf_uuid', 'pf_uuid', unique=True)  
#     )  
  
#     pf_id: Mapped[int] = mapped_column(Integer, primary_key=True)  
#     pf_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)  
#     user_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)  
#     pf_member: Mapped[int] = mapped_column(TINYINT(1), nullable=False)  
#     uan_number: Mapped[Optional[str]] = mapped_column(String(20))  
#     created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))  
#     updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))  
#     status: Mapped[Optional[str]] = mapped_column(Enum('uploaded', 'verified', 'rejected'), server_default=text("'uploaded'"))  
  
#     offer_letter_details: Mapped['OfferLetterDetails'] = relationship('OfferLetterDetails', back_populates='employee_pf_details')  
  
  
# class EmployeeReceivables(Base):  
#     __tablename__ = 'employee_receivables'  
#     __table_args__ = (  
#         ForeignKeyConstraint(['receivable_uuid'], ['receivable_items.receivable_uuid'], name='employee_receivables_ibfk_2'),  
#         ForeignKeyConstraint(['user_uuid'], ['offer_letter_details.user_uuid'], name='employee_receivables_ibfk_1'),  
#         Index('employee_receivable_uuid', 'employee_receivable_uuid', unique=True),  
#         Index('receivable_uuid', 'receivable_uuid'),  
#         Index('user_uuid', 'user_uuid')  
#     )  
  
#     employee_receivable_id: Mapped[int] = mapped_column(Integer, primary_key=True)  
#     employee_receivable_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)  
#     user_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)  
#     receivable_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)  
#     status: Mapped[Optional[str]] = mapped_column(Enum('Pending', 'Received', 'Not Received'), server_default=text("'Pending'"))  
#     collected_by: Mapped[Optional[str]] = mapped_column(CHAR(36))  
#     collected_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)  
#     remarks: Mapped[Optional[str]] = mapped_column(String(255))  
  
#     receivable_items: Mapped['ReceivableItems'] = relationship('ReceivableItems', back_populates='employee_receivables')  
#     offer_letter_details: Mapped['OfferLetterDetails'] = relationship('OfferLetterDetails', back_populates='employee_receivables')  
  
  
# class EmployeeSocialLinks(Base):  
#     __tablename__ = 'employee_social_links'  
#     __table_args__ = (  
#         ForeignKeyConstraint(['user_uuid'], ['offer_letter_details.user_uuid'], name='employee_social_links_ibfk_1'),  
#         Index('employee_social_links_ibfk_1', 'user_uuid')  
#     )  
  
#     social_link_id: Mapped[int] = mapped_column(Integer, primary_key=True)  
#     social_link_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)  
#     user_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)  
#     platform_name: Mapped[str] = mapped_column(String(100), nullable=False)  
#     url: Mapped[str] = mapped_column(String(500), nullable=False)  
#     created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))  
#     updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))  
  
#     offer_letter_details: Mapped['OfferLetterDetails'] = relationship('OfferLetterDetails', back_populates='employee_social_links')  
  
  
# class OfferApprovalRequest(Base):  
#     __tablename__ = 'offer_approval_request'  
#     __table_args__ = (  
#         ForeignKeyConstraint(['user_uuid'], ['offer_letter_details.user_uuid'], ondelete='CASCADE', name='fk_offer_req_user_uuid'),  
#         Index('idx_approval_user', 'user_uuid'),  
#         Index('idx_offer_request_user_uuid', 'user_uuid'),  
#         Index('idx_offer_request_uuid', 'user_uuid'),  
#         Index('idx_user_uuid', 'user_uuid')  
#     )  
  
#     id: Mapped[int] = mapped_column(Integer, primary_key=True)  
#     user_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)  
#     request_by: Mapped[int] = mapped_column(Integer, nullable=False)  
#     action_taker_id: Mapped[int] = mapped_column(Integer, nullable=False)  
#     request_time: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))  
  
#     offer_letter_details: Mapped['OfferLetterDetails'] = relationship('OfferLetterDetails', back_populates='offer_approval_request')  
#     offer_approval_action: Mapped[list['OfferApprovalAction']] = relationship('OfferApprovalAction', back_populates='request')  
  
  
# class OfferCompensation(Base):  
#     __tablename__ = 'offer_compensation'  
#     __table_args__ = (  
#         ForeignKeyConstraint(['offer_uuid'], ['offer_letter_details.user_uuid'], ondelete='CASCADE', name='fk_offer_compensation_offer'),  
#         Index('fk_offer_compensation_offer', 'offer_uuid')  
#     )  
  
#     id: Mapped[int] = mapped_column(Integer, primary_key=True)  
#     offer_uuid: Mapped[str] = mapped_column(String(36), nullable=False)  
#     name: Mapped[Optional[str]] = mapped_column(String(255))  
#     type: Mapped[Optional[str]] = mapped_column(String(50))  
#     frequency: Mapped[Optional[str]] = mapped_column(String(50))  
#     amount: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(12, 2))  
  
#     offer_letter_details: Mapped['OfferLetterDetails'] = relationship('OfferLetterDetails', back_populates='offer_compensation')  
  
  
# class OnboardingLinks(Base):  
#     __tablename__ = 'onboarding_links'  
#     __table_args__ = (  
#         ForeignKeyConstraint(['user_uuid'], ['offer_letter_details.user_uuid'], ondelete='CASCADE', name='fk_onboarding_user_uuid'),  
#         Index('uq_onboarding_token_hash', 'token_hash', unique=True),  
#         Index('uq_onboarding_user_uuid', 'user_uuid', unique=True)  
#     )  
  
#     id: Mapped[int] = mapped_column(BigInteger, primary_key=True)  
#     user_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)  
#     email: Mapped[str] = mapped_column(String(100), nullable=False)  
#     token_hash: Mapped[str] = mapped_column(CHAR(64), nullable=False)  
#     expires_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)  
  
#     offer_letter_details: Mapped['OfferLetterDetails'] = relationship('OfferLetterDetails', back_populates='onboarding_links')  
  
  
# class PersonalDetails(Base):  
#     __tablename__ = 'personal_details'  
#     __table_args__ = (  
#         ForeignKeyConstraint(['nationality_country_uuid'], ['countries.country_uuid'], name='personal_details_ibfk_2'),  
#         ForeignKeyConstraint(['residence_country_uuid'], ['countries.country_uuid'], name='personal_details_ibfk_3'),  
#         ForeignKeyConstraint(['user_uuid'], ['offer_letter_details.user_uuid'], name='personal_details_ibfk_1'),  
#         Index('idx_personal_user', 'user_uuid'),  
#         Index('idx_personal_user_uuid', 'user_uuid'),  
#         Index('idx_personal_uuid', 'personal_uuid'),  
#         Index('nationality_country_uuid', 'nationality_country_uuid'),  
#         Index('personal_uuid', 'personal_uuid', unique=True),  
#         Index('residence_country_uuid', 'residence_country_uuid'),  
#         Index('user_uuid', 'user_uuid')  
#     )  
  
#     id: Mapped[int] = mapped_column(Integer, primary_key=True)  
#     personal_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)  
#     user_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)  
#     date_of_birth: Mapped[Optional[datetime.date]] = mapped_column(Date)  
#     gender: Mapped[Optional[str]] = mapped_column(Enum('Male', 'Female', 'Other'))  
#     marital_status: Mapped[Optional[str]] = mapped_column(Enum('Single', 'Married', 'Divorced', 'Widowed'))  
#     blood_group: Mapped[Optional[str]] = mapped_column(String(5))  
#     nationality_country_uuid: Mapped[Optional[str]] = mapped_column(CHAR(36))  
#     residence_country_uuid: Mapped[Optional[str]] = mapped_column(CHAR(36))  
#     created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))  
#     updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))  
#     emergency_contact_name: Mapped[Optional[str]] = mapped_column(String(100))  
#     emergency_contact_phone: Mapped[Optional[str]] = mapped_column(String(20))  
#     emergency_contact_relation_uuid: Mapped[Optional[str]] = mapped_column(CHAR(36))  
#     status: Mapped[Optional[str]] = mapped_column(Enum('uploaded', 'verified', 'rejected'), server_default=text("'uploaded'"))  
  
#     countries: Mapped[Optional['Countries']] = relationship('Countries', foreign_keys=[nationality_country_uuid], back_populates='personal_details')  
#     countries_: Mapped[Optional['Countries']] = relationship('Countries', foreign_keys=[residence_country_uuid], back_populates='personal_details_')  
#     offer_letter_details: Mapped['OfferLetterDetails'] = relationship('OfferLetterDetails', back_populates='personal_details')  
  
  
# class EmployeeDetails(Base):  
#     __tablename__ = 'employee_details'  
#     __table_args__ = (  
#         ForeignKeyConstraint(['department_uuid'], ['departments.department_uuid'], name='fk_employee_department'),  
#         ForeignKeyConstraint(['designation_uuid'], ['designations.designation_uuid'], name='fk_employee_designation'),  
#         ForeignKeyConstraint(['user_uuid'], ['offer_letter_details.user_uuid'], ondelete='CASCADE', name='fk_employee_offer'),  
#         Index('employee_id', 'employee_id', unique=True),  
#         Index('employee_uuid', 'employee_uuid', unique=True),  
#         Index('fk_employee_department', 'department_uuid'),  
#         Index('fk_employee_designation', 'designation_uuid'),  
#         Index('fk_employee_offer', 'user_uuid'),  
#         Index('work_email', 'work_email', unique=True)  
#     )  
  
#     id: Mapped[int] = mapped_column(Integer, primary_key=True)  
#     employee_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)  
#     user_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)  
#     first_name: Mapped[str] = mapped_column(String(50), nullable=False)  
#     last_name: Mapped[str] = mapped_column(String(50), nullable=False)  
#     location: Mapped[str] = mapped_column(String(100), nullable=False)  
#     work_mode: Mapped[str] = mapped_column(Enum('Office', 'Remote', 'Hybrid'), nullable=False)  
#     employee_id: Mapped[Optional[str]] = mapped_column(String(20))  
#     middle_name: Mapped[Optional[str]] = mapped_column(String(50))  
#     date_of_birth: Mapped[Optional[datetime.date]] = mapped_column(Date)  
#     work_email: Mapped[Optional[str]] = mapped_column(String(100))  
#     contact_number: Mapped[Optional[str]] = mapped_column(String(15))  
#     department_uuid: Mapped[Optional[str]] = mapped_column(CHAR(36))  
#     designation_uuid: Mapped[Optional[str]] = mapped_column(CHAR(36))  
#     reporting_manager_uuid: Mapped[Optional[str]] = mapped_column(CHAR(36))  
#     employment_type: Mapped[Optional[str]] = mapped_column(Enum('Full-Time', 'Part-Time', 'Intern', 'Contractor', 'Freelance'))  
#     joining_date: Mapped[Optional[datetime.date]] = mapped_column(Date)  
#     employment_status: Mapped[Optional[str]] = mapped_column(Enum('Probation', 'Active', 'Resigned', 'Terminated', 'Absconded'), server_default=text("'Probation'"))  
#     blood_group: Mapped[Optional[str]] = mapped_column(String(5))  
#     gender: Mapped[Optional[str]] = mapped_column(Enum('Male', 'Female', 'Other'))  
#     marital_status: Mapped[Optional[str]] = mapped_column(Enum('Single', 'Married', 'Divorced', 'Widowed'))  
#     total_experience: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(4, 1))  
#     created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))  
#     updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))  
  
#     departments: Mapped[Optional['Departments']] = relationship('Departments', back_populates='employee_details')  
#     designations: Mapped[Optional['Designations']] = relationship('Designations', back_populates='employee_details')  
#     offer_letter_details: Mapped['OfferLetterDetails'] = relationship('OfferLetterDetails', back_populates='employee_details')  
#     employee_exit: Mapped[list['EmployeeExit']] = relationship('EmployeeExit', back_populates='employee_details')  
#     exit_clearance: Mapped[list['ExitClearance']] = relationship('ExitClearance', back_populates='employee_details')  
#     exit_documents: Mapped[list['ExitDocuments']] = relationship('ExitDocuments', back_populates='employee_details')  
#     exit_final_settlement: Mapped[list['ExitFinalSettlement']] = relationship('ExitFinalSettlement', back_populates='employee_details')  
#     exit_interview: Mapped[list['ExitInterview']] = relationship('ExitInterview', back_populates='employee_details')  
  
  
# class EmployeeEducationDocument(Base):  
#     __tablename__ = 'employee_education_document'  
#     __table_args__ = (  
#         ForeignKeyConstraint(['degree_uuid'], ['degree_master.degree_uuid'], name='fk_degree_uuid'),  
#         ForeignKeyConstraint(['mapping_uuid'], ['country_education_document_mapping.mapping_uuid'], name='employee_education_document_ibfk_1'),  
#         ForeignKeyConstraint(['user_uuid'], ['offer_letter_details.user_uuid'], name='employee_education_document_ibfk_2'),  
#         Index('document_uuid', 'document_uuid', unique=True),  
#         Index('fk_degree_uuid', 'degree_uuid'),  
#         Index('idx_education_user', 'user_uuid'),  
#         Index('mapping_uuid', 'mapping_uuid'),  
#         Index('user_uuid', 'user_uuid')  
#     )  
  
#     employee_education_document_id: Mapped[int] = mapped_column(Integer, primary_key=True)  
#     document_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)  
#     mapping_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)  
#     user_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)  
#     institution_name: Mapped[Optional[str]] = mapped_column(String(150))  
#     institute_location: Mapped[Optional[str]] = mapped_column(String(150))  
#     degree_uuid: Mapped[Optional[str]] = mapped_column(CHAR(36))  
#     specialization: Mapped[Optional[str]] = mapped_column(String(150))  
#     education_mode: Mapped[Optional[str]] = mapped_column(Enum('Regular', 'Distance', 'Part Time', 'Online'))  
#     start_year: Mapped[Optional[Any]] = mapped_column(YEAR)  
#     year_of_passing: Mapped[Optional[Any]] = mapped_column(YEAR)  
#     delay_reason: Mapped[Optional[str]] = mapped_column(String(255))  
#     percentage_cgpa: Mapped[Optional[str]] = mapped_column(String(10))  
#     file_path: Mapped[Optional[str]] = mapped_column(String(255))  
#     status: Mapped[Optional[str]] = mapped_column(Enum('uploaded', 'verified', 'rejected'), server_default=text("'uploaded'"))  
#     uploaded_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))  
#     verified_by: Mapped[Optional[str]] = mapped_column(CHAR(36))  
#     verified_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)  
#     remarks: Mapped[Optional[str]] = mapped_column(String(255))  
#     updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))  
#     education_document_uuid: Mapped[Optional[str]] = mapped_column(CHAR(36))  
  
#     degree_master: Mapped[Optional['DegreeMaster']] = relationship('DegreeMaster', back_populates='employee_education_document')  
#     country_education_document_mapping: Mapped['CountryEducationDocumentMapping'] = relationship('CountryEducationDocumentMapping', back_populates='employee_education_document')  
#     offer_letter_details: Mapped['OfferLetterDetails'] = relationship('OfferLetterDetails', back_populates='employee_education_document')  
  
  
# class EmployeeIdentityDocument(Base):  
#     __tablename__ = 'employee_identity_document'  
#     __table_args__ = (  
#         ForeignKeyConstraint(['mapping_uuid'], ['country_identity_mapping.mapping_uuid'], name='employee_identity_document_ibfk_1'),  
#         ForeignKeyConstraint(['user_uuid'], ['offer_letter_details.user_uuid'], name='employee_identity_document_ibfk_2'),  
#         Index('document_uuid', 'document_uuid', unique=True),  
#         Index('idx_identity_user', 'user_uuid'),  
#         Index('mapping_uuid', 'mapping_uuid'),  
#         Index('user_uuid', 'user_uuid')  
#     )  
  
#     employee_identity_document_id: Mapped[int] = mapped_column(Integer, primary_key=True)  
#     document_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)  
#     mapping_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)  
#     user_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)  
#     identity_file_number: Mapped[Optional[str]] = mapped_column(String(255))  
#     file_path: Mapped[Optional[str]] = mapped_column(String(255))  
#     expiry_date: Mapped[Optional[datetime.date]] = mapped_column(Date)  
#     status: Mapped[Optional[str]] = mapped_column(Enum('uploaded', 'pending', 'verified', 'rejected'), server_default=text("'pending'"))  
#     uploaded_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))  
#     verified_by: Mapped[Optional[str]] = mapped_column(CHAR(36))  
#     verified_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)  
#     remarks: Mapped[Optional[str]] = mapped_column(String(255))  
#     updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))  
  
#     country_identity_mapping: Mapped['CountryIdentityMapping'] = relationship('CountryIdentityMapping', back_populates='employee_identity_document')  
#     offer_letter_details: Mapped['OfferLetterDetails'] = relationship('OfferLetterDetails', back_populates='employee_identity_document')  
  
  
# class EmployeePaySlips(Base):  
#     __tablename__ = 'employee_pay_slips'  
#     __table_args__ = (  
#         ForeignKeyConstraint(['employee_uuid'], ['offer_letter_details.user_uuid'], name='employee_pay_slips_ibfk_1'),  
#         ForeignKeyConstraint(['experience_uuid'], ['employee_experience.experience_uuid'], name='employee_pay_slips_ibfk_2'),  
#         Index('employee_uuid', 'employee_uuid'),  
#         Index('experience_uuid', 'experience_uuid'),  
#         Index('pay_slip_uuid', 'pay_slip_uuid', unique=True)  
#     )  
  
#     pay_slip_id: Mapped[int] = mapped_column(Integer, primary_key=True)  
#     pay_slip_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)  
#     employee_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)  
#     experience_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)  
#     file_path: Mapped[str] = mapped_column(String(255), nullable=False)  
#     status: Mapped[Optional[str]] = mapped_column(Enum('uploaded', 'pending', 'verified', 'rejected'), server_default=text("'pending'"))  
#     uploaded_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))  
#     verified_by: Mapped[Optional[str]] = mapped_column(CHAR(36))  
#     verified_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)  
#     remarks: Mapped[Optional[str]] = mapped_column(String(255))  
#     updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))  
  
#     offer_letter_details: Mapped['OfferLetterDetails'] = relationship('OfferLetterDetails', back_populates='employee_pay_slips')  
#     employee_experience: Mapped['EmployeeExperience'] = relationship('EmployeeExperience', back_populates='employee_pay_slips')  
  
  
# class EmployeeRelievingLetter(Base):  
#     __tablename__ = 'employee_relieving_letter'  
#     __table_args__ = (  
#         ForeignKeyConstraint(['employee_uuid'], ['offer_letter_details.user_uuid'], name='employee_relieving_letter_ibfk_1'),  
#         ForeignKeyConstraint(['experience_uuid'], ['employee_experience.experience_uuid'], name='employee_relieving_letter_ibfk_2'),  
#         Index('employee_uuid', 'employee_uuid'),  
#         Index('experience_uuid', 'experience_uuid'),  
#         Index('relieving_uuid', 'relieving_uuid', unique=True)  
#     )  
  
#     relieving_id: Mapped[int] = mapped_column(Integer, primary_key=True)  
#     relieving_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)  
#     employee_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)  
#     experience_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)  
#     file_path: Mapped[Optional[str]] = mapped_column(String(255))  
#     status: Mapped[Optional[str]] = mapped_column(Enum('uploaded', 'pending', 'verified', 'rejected'), server_default=text("'pending'"))  
#     uploaded_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))  
#     verified_by: Mapped[Optional[str]] = mapped_column(CHAR(36))  
#     verified_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)  
#     remarks: Mapped[Optional[str]] = mapped_column(String(255))  
#     updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))  
  
#     offer_letter_details: Mapped['OfferLetterDetails'] = relationship('OfferLetterDetails', back_populates='employee_relieving_letter')  
#     employee_experience: Mapped['EmployeeExperience'] = relationship('EmployeeExperience', back_populates='employee_relieving_letter')  
  
  
# class OfferApprovalAction(Base):  
#     __tablename__ = 'offer_approval_action'  
#     __table_args__ = (  
#         ForeignKeyConstraint(['request_id'], ['offer_approval_request.id'], ondelete='CASCADE', name='fk_offer_action_request'),  
#         Index('idx_approval_action_request', 'request_id'),  
#         Index('idx_offer_action_request_id', 'request_id'),  
#         Index('idx_request_id', 'request_id')  
#     )  
  
#     id: Mapped[int] = mapped_column(Integer, primary_key=True)  
#     request_id: Mapped[int] = mapped_column(Integer, nullable=False)  
#     action: Mapped[str] = mapped_column(Enum('Pending', 'APPROVED', 'REJECTED', 'ON_HOLD'), nullable=False, server_default=text("'Pending'"))  
#     comment: Mapped[Optional[str]] = mapped_column(Text)  
#     action_time: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))  
  
#     request: Mapped['OfferApprovalRequest'] = relationship('OfferApprovalRequest', back_populates='offer_approval_action')  
  
  

  

  


  
  

class EmployeeExit(Base):
    __tablename__ = 'employee_exit'
    __table_args__ = (

        ForeignKeyConstraint(
            ['employee_uuid'],
            ['employee_details.employee_uuid'],
            name='employee_exit_ibfk_1'
        ),

        ForeignKeyConstraint(
            ['department_uuid'],
            ['departments.department_uuid'],
            name='employee_exit_ibfk_2'
        ),

        ForeignKeyConstraint(
            ['designation_uuid'],
            ['designations.designation_uuid'],
            name='employee_exit_ibfk_3'
        ),

        Index('exit_uuid', 'exit_uuid', unique=True),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    exit_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)

    employee_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)

    employee_id: Mapped[Optional[str]] = mapped_column(String(20))
    first_name: Mapped[Optional[str]] = mapped_column(String(50))
    last_name: Mapped[Optional[str]] = mapped_column(String(50))

    department_uuid: Mapped[Optional[str]] = mapped_column(CHAR(36))
    designation_uuid: Mapped[Optional[str]] = mapped_column(CHAR(36))

    exit_type: Mapped[str] = mapped_column(
        Enum(
            'Resignation',
            'Termination',
            'Contract End',
            'Absconded',
            'Retirement'
        )
    )

    resignation_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    last_working_day: Mapped[Optional[datetime.date]] = mapped_column(Date)
    notice_period: Mapped[Optional[int]] = mapped_column(Integer)
    notice_start_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    notice_end_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    reason: Mapped[Optional[str]] = mapped_column(Text)
    remarks: Mapped[Optional[str]] = mapped_column(Text)

    status: Mapped[str] = mapped_column(
        Enum(
            'Initiated',
            'Manager Approved',
            'HR Approved',
            'Clearance Pending',
            'FnF Pending',
            'Settlement Approved',
            'Paid',
            'Documents Generated',
            'Completed',
            'Rejected'
        ),
        server_default=text("'Initiated'")
    )

    created_by: Mapped[Optional[int]] = mapped_column(Integer)

    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime,
        server_default=text('CURRENT_TIMESTAMP')
    )

    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime,
        server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')
    )

    # relationships
    department: Mapped['Departments'] = relationship(
        "Departments",
        back_populates="employee_exit",
        lazy="selectin"
    )

    designation: Mapped['Designations'] = relationship(
        "Designations",
        back_populates="employee_exit",
        lazy="selectin")

    employee_details: Mapped['EmployeeDetails'] = relationship(
        "EmployeeDetails",
        back_populates="employee_exit",
        lazy="selectin")

    approvals: Mapped[list['ExitApprovals']] = relationship(
        "ExitApprovals",
        back_populates="employee_exit",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    clearances: Mapped[list['ExitClearance']] = relationship(
        "ExitClearance",
        back_populates="employee_exit",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    interview: Mapped[list['ExitInterview']] = relationship(
        "ExitInterview",
        back_populates="employee_exit",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    documents: Mapped[list['ExitDocuments']] = relationship(
        "ExitDocuments",
        back_populates="employee_exit",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    settlement: Mapped[list['ExitFinalSettlement']] = relationship(
        "ExitFinalSettlement",
        back_populates="employee_exit",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    employee_details: Mapped[Optional["EmployeeDetails"]] = relationship(
        "EmployeeDetails",
        back_populates="employee_exit",
    )
    department: Mapped[Optional["Departments"]] = relationship(
        "Departments",
        back_populates="employee_exit",
    )
    designation: Mapped[Optional["Designations"]] = relationship(
        "Designations",
        back_populates="employee_exit",
    )
# ==========================================
# Exit Approvals
# ==========================================

class ExitApprovals(Base):
    __tablename__ = 'exit_approvals'

    __table_args__ = (
        ForeignKeyConstraint(
            ['exit_uuid'],
            ['employee_exit.exit_uuid'],
            name='exit_approvals_ibfk_1'
        ),
        Index('approval_uuid', 'approval_uuid', unique=True),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    approval_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)

    exit_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)

    approval_type: Mapped[str] = mapped_column(
        Enum('Manager', 'HR')
    )

    status: Mapped[str] = mapped_column(
        Enum('Pending', 'Approved', 'Rejected'),
        server_default=text("'Pending'")
    )

    remarks: Mapped[Optional[str]] = mapped_column(Text)

    approved_by: Mapped[Optional[int]] = mapped_column(Integer)

    approved_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime,
        server_default=text('CURRENT_TIMESTAMP')
    )

    employee_exit: Mapped["EmployeeExit"] = relationship(
        "EmployeeExit",
        back_populates="approvals",
        lazy="selectin"
    )
    

# ==========================================


class ExitClearance(Base):
    __tablename__ = 'exit_clearance'

    __table_args__ = (
        ForeignKeyConstraint(['exit_uuid'], ['employee_exit.exit_uuid']),
        ForeignKeyConstraint(['employee_uuid'], ['employee_details.employee_uuid']),
        Index('clearance_uuid', 'clearance_uuid', unique=True),
    )
      

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    clearance_uuid: Mapped[str] = mapped_column(CHAR(36))
    exit_uuid: Mapped[str] = mapped_column(CHAR(36))
    employee_uuid: Mapped[str] = mapped_column(CHAR(36))

    department: Mapped[str] = mapped_column(
        Enum('Manager','IT','HR','Finance','Admin')
    )

    status: Mapped[str] = mapped_column(
        Enum('Pending','Approved','Rejected'),
        server_default=text("'Pending'")
    )

    remarks: Mapped[Optional[str]] = mapped_column(Text)

    approved_by: Mapped[Optional[int]] = mapped_column(Integer)
    approved_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime, server_default=text('CURRENT_TIMESTAMP')
    )

    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime,
        server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')
    )

    employee_exit = relationship("EmployeeExit", back_populates="clearances")

    items: Mapped[list['ExitClearanceItems']] = relationship(
        "ExitClearanceItems",
        back_populates="exit_clearance",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    employee_details = relationship("EmployeeDetails", back_populates="exit_clearance")

# ==========================================


class ExitInterview(Base):
    __tablename__ = 'exit_interview'

    __table_args__ = (
        ForeignKeyConstraint(['exit_uuid'], ['employee_exit.exit_uuid']),
        ForeignKeyConstraint(['employee_uuid'], ['employee_details.employee_uuid']),
        Index('interview_uuid', 'interview_uuid', unique=True),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    interview_uuid: Mapped[str] = mapped_column(CHAR(36))
    exit_uuid: Mapped[str] = mapped_column(CHAR(36))
    employee_uuid: Mapped[str] = mapped_column(CHAR(36))

    reason_for_leaving: Mapped[Optional[str]] = mapped_column(Text)
    company_feedback: Mapped[Optional[str]] = mapped_column(Text)
    manager_feedback: Mapped[Optional[str]] = mapped_column(Text)

    rating: Mapped[Optional[int]] = mapped_column(Integer)

    submitted_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime, server_default=text('CURRENT_TIMESTAMP')
    )

    employee_exit = relationship("EmployeeExit", back_populates="interview")
    employee_details = relationship("EmployeeDetails", back_populates="exit_interview")

# ==========================================

class ExitDocuments(Base):
    __tablename__ = 'exit_documents'

    __table_args__ = (
        ForeignKeyConstraint(['exit_uuid'], ['employee_exit.exit_uuid']),
        ForeignKeyConstraint(['employee_uuid'], ['employee_details.employee_uuid']),
        Index('document_uuid', 'document_uuid', unique=True),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    document_uuid: Mapped[str] = mapped_column(CHAR(36))
    exit_uuid: Mapped[str] = mapped_column(CHAR(36))
    employee_uuid: Mapped[str] = mapped_column(CHAR(36))

    document_type: Mapped[str] = mapped_column(
        Enum(
            'Relieving Letter',
            'Experience Letter',
            'Full & Final',
            'NOC',
            'Resignation Letter',
            'Termination Letter'
        )
    )

    file_name: Mapped[Optional[str]] = mapped_column(String(255))
    file_path: Mapped[Optional[str]] = mapped_column(String(255))

    uploaded_by: Mapped[Optional[int]] = mapped_column(Integer)

    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime, server_default=text('CURRENT_TIMESTAMP')
    )

    employee_exit = relationship("EmployeeExit", back_populates="documents")
    employee_details = relationship("EmployeeDetails", back_populates="exit_documents")

# ==========================================


class ExitFinalSettlement(Base):
    __tablename__ = 'exit_final_settlement'

    __table_args__ = (
        ForeignKeyConstraint(['exit_uuid'], ['employee_exit.exit_uuid']),
        ForeignKeyConstraint(['employee_uuid'], ['employee_details.employee_uuid']),
        Index('settlement_uuid', 'settlement_uuid', unique=True),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    settlement_uuid: Mapped[str] = mapped_column(CHAR(36))
    exit_uuid: Mapped[str] = mapped_column(CHAR(36))
    employee_uuid: Mapped[str] = mapped_column(CHAR(36))

    last_salary: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(10,2))
    leave_encashment: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(10,2))
    bonus: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(10,2))
    deductions: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(10,2))
    net_payable: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(10,2))

    status: Mapped[str] = mapped_column(
        Enum('Pending','Approved','Paid'),
        server_default=text("'Pending'")
    )

    approved_by: Mapped[Optional[int]] = mapped_column(Integer)
    approved_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime, server_default=text('CURRENT_TIMESTAMP')
    )

    employee_exit = relationship("EmployeeExit", back_populates="settlement")
    employee_details = relationship("EmployeeDetails", back_populates="exit_final_settlement")

class EmployeeTasks(Base):
    __tablename__ = "employee_tasks"

    # Primary Key
    task_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    # Unique UUID for task
    task_uuid: Mapped[str] = mapped_column(
        CHAR(36),
        unique=True,
        nullable=False
    )

    # Link to Offer Letter Table
    user_uuid: Mapped[str] = mapped_column(
        CHAR(36),
        ForeignKey("offer_letter_details.user_uuid"),
        nullable=False
    )

    # Task Details
    task_title: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    task_type: Mapped[str] = mapped_column(
        Enum(
            "Onboarding",
            "Exit",
            "IT Provisioning",
            "Finance Clearance",
            "Admin",
            name="task_type_enum"
        ),
        nullable=False
    )

    description: Mapped[Optional[str]] = mapped_column(Text)

    # Assignment Info
    assigned_to: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    assigned_team: Mapped[Optional[str]] = mapped_column(
        String(100)
    )

    # Priority
    priority: Mapped[str] = mapped_column(
        Enum(
            "High",
            "Medium",
            "Low",
            name="task_priority_enum"
        ),
        default="Medium",
        nullable=False
    )

    # Status
    status: Mapped[str] = mapped_column(
        Enum(
            "To Do",
            "In Progress",
            "Completed",
            "Cancelled",
            name="task_status_enum"
        ),
        default="To Do",
        nullable=False
    )

    # Progress %
    progress: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    # Dates
    due_date: Mapped[Optional[datetime.date]] = mapped_column(Date)

    reminder_date: Mapped[Optional[datetime.date]] = mapped_column(Date)

    # Notification
    send_notification: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )

    # Escalation
    escalation_owner: Mapped[Optional[str]] = mapped_column(
        String(150)
    )

    # Notes
    internal_notes: Mapped[Optional[str]] = mapped_column(Text)

    comments: Mapped[Optional[str]] = mapped_column(Text)

    # Audit Fields
    created_by: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP")
    )

    updated_by: Mapped[Optional[str]] = mapped_column(
        String(150)
    )

    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=datetime.datetime.utcnow
    )

    completed_by: Mapped[Optional[str]] = mapped_column(
        String(150)
    )

    completed_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime
    )

    # Relationship with Offer Letter Details
    offer_letter = relationship(
        "OfferLetterDetails",
        backref="employee_tasks"
    )
class ExitClearanceItems(Base):
    __tablename__ = 'exit_clearance_items'

    __table_args__ = (
        ForeignKeyConstraint(
            ['clearance_uuid'],
            ['exit_clearance.clearance_uuid']
        ),
        Index('clearance_item_uuid', 'clearance_item_uuid', unique=True),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    clearance_item_uuid: Mapped[str] = mapped_column(CHAR(36))

    clearance_uuid: Mapped[str] = mapped_column(CHAR(36))

    item_name: Mapped[str] = mapped_column(String(255))

    status: Mapped[str] = mapped_column(
        Enum('Pending','Completed'),
        server_default=text("'Pending'")
    )

    remarks: Mapped[Optional[str]] = mapped_column(Text)

    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime,
        server_default=text('CURRENT_TIMESTAMP')
    )

    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime,
        server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')
    )

    exit_clearance = relationship(
        "ExitClearance",
        back_populates="items"
    )
