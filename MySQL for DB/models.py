# from typing import Any, Optional
# import datetime
# import uuid

# from sqlalchemy import BigInteger, CHAR, Column, Date, DateTime, Enum, ForeignKey, ForeignKeyConstraint, Index, Integer, JSON, String, TIMESTAMP, Text, text
# from sqlalchemy.dialects.mysql import ENUM, TINYINT, YEAR
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

#     addresses: Mapped[list['Addresses']] = relationship('Addresses', back_populates='countries', lazy="selectin")
#     contacts: Mapped[list['Contacts']] = relationship('Contacts', back_populates='countries', lazy="selectin")
#     country_education_document_mapping: Mapped[list['CountryEducationDocumentMapping']] = relationship('CountryEducationDocumentMapping', back_populates='countries', lazy="selectin")
#     country_identity_mapping: Mapped[list['CountryIdentityMapping']] = relationship('CountryIdentityMapping', back_populates='countries', lazy="selectin")
#     personal_details: Mapped[list['PersonalDetails']] = relationship('PersonalDetails', foreign_keys='[PersonalDetails.nationality_country_uuid]', back_populates='countries', lazy="selectin")
#     personal_details_: Mapped[list['PersonalDetails']] = relationship('PersonalDetails', foreign_keys='[PersonalDetails.residence_country_uuid]', back_populates='countries_', lazy="selectin")


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

#     employee_deliverables: Mapped[list['EmployeeDeliverables']] = relationship('EmployeeDeliverables', back_populates='deliverable_items', lazy="selectin")


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

#     country_education_document_mapping: Mapped[list['CountryEducationDocumentMapping']] = relationship('CountryEducationDocumentMapping', back_populates='education_document_type', lazy="selectin")


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

#     country_education_document_mapping: Mapped[list['CountryEducationDocumentMapping']] = relationship('CountryEducationDocumentMapping', back_populates='education_level', lazy="selectin")


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

#     country_identity_mapping: Mapped[list['CountryIdentityMapping']] = relationship('CountryIdentityMapping', back_populates='identity_type', lazy="selectin")


# class OfferLetterDetails(Base):
#     __tablename__ = 'offer_letter_details'
#     __table_args__ = (
#         Index('idx_offer_user_created', 'user_uuid', 'created_by'),
#         Index('idx_offer_user_uuid', 'user_uuid'),
#         Index('mail', 'mail', unique=True),
#         Index('user_uuid', 'user_uuid', unique=True)
#     )

#     user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
#     user_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)
#     first_name: Mapped[str] = mapped_column(String(50), nullable=False)
#     last_name: Mapped[str] = mapped_column(String(50), nullable=False)
#     mail: Mapped[str] = mapped_column(String(100), nullable=False)
#     country_code: Mapped[str] = mapped_column(String(5), nullable=False)
#     contact_number: Mapped[str] = mapped_column(String(15), nullable=False)
#     designation: Mapped[str] = mapped_column(String(50), nullable=False)
#     employee_type: Mapped[str] = mapped_column(Enum('Full-Time', 'Part-Time', 'Intern', 'Contractor', 'Freelance'), nullable=False)
#     package: Mapped[str] = mapped_column(String(20), nullable=False)
#     currency: Mapped[str] = mapped_column(String(10), nullable=False)
#     created_by: Mapped[int] = mapped_column(Integer, nullable=False)
#     status: Mapped[Optional[str]] = mapped_column(ENUM('Created', 'Offered', 'Accepted', 'Rejected', 'Submitted', 'Verified', 'Completed', 'InComplete'), server_default=text("'Created'"))
#     created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
#     updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
#     file_path: Mapped[Optional[str]] = mapped_column(String(255))
#     pandadoc_draft_id: Mapped[Optional[str]] = mapped_column(String(255))
#     offer_response_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
#     joining_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
#     cc_emails: Mapped[Optional[str]] = mapped_column(String(256))

#     addresses: Mapped[list['Addresses']] = relationship('Addresses', back_populates='offer_letter_details', lazy="selectin")
#     contacts: Mapped[list['Contacts']] = relationship('Contacts', back_populates='offer_letter_details', lazy="selectin")
#     employee_deliverables: Mapped[list['EmployeeDeliverables']] = relationship('EmployeeDeliverables', back_populates='offer_letter_details', lazy="selectin")
#     employee_experience: Mapped[list['EmployeeExperience']] = relationship('EmployeeExperience', back_populates='offer_letter_details', lazy="selectin")
#     employee_receivables: Mapped[list['EmployeeReceivables']] = relationship('EmployeeReceivables', back_populates='offer_letter_details', lazy="selectin")
#     offer_approval_request: Mapped[list['OfferApprovalRequest']] = relationship('OfferApprovalRequest', back_populates='offer_letter_details', lazy="selectin")
#     onboarding_links: Mapped[list['OnboardingLinks']] = relationship('OnboardingLinks', back_populates='offer_letter_details', lazy="selectin")
#     personal_details: Mapped[list['PersonalDetails']] = relationship('PersonalDetails', back_populates='offer_letter_details', lazy="selectin")
#     employee_education_document: Mapped[list['EmployeeEducationDocument']] = relationship('EmployeeEducationDocument', back_populates='offer_letter_details', lazy="selectin")
#     employee_identity_document: Mapped[list['EmployeeIdentityDocument']] = relationship('EmployeeIdentityDocument', back_populates='offer_letter_details', lazy="selectin")
#     employee_pay_slips: Mapped[list['EmployeePaySlips']] = relationship('EmployeePaySlips', back_populates='offer_letter_details', lazy="selectin")
#     employee_relieving_letter: Mapped[list['EmployeeRelievingLetter']] = relationship('EmployeeRelievingLetter', back_populates='offer_letter_details', lazy="selectin")


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

#     employee_receivables: Mapped[list['EmployeeReceivables']] = relationship('EmployeeReceivables', back_populates='receivable_items', lazy="selectin")


# class Addresses(Base):
#     __tablename__ = 'addresses'
#     __table_args__ = (
#         ForeignKeyConstraint(['country_uuid'], ['countries.country_uuid'], name='addresses_ibfk_2'),
#         ForeignKeyConstraint(['user_uuid'], ['offer_letter_details.user_uuid'], name='addresses_ibfk_1'),
#         Index('address_uuid', 'address_uuid', unique=True),
#         Index('country_uuid', 'country_uuid'),
#         Index('idx_address_user', 'user_uuid'),
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
#     verification_status: Mapped[Optional[str]] = mapped_column(Enum('Pending', 'Verified', 'Rejected'),default='Pending')
#     created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
#     updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

#     countries: Mapped['Countries'] = relationship('Countries', back_populates='addresses', lazy="selectin")
#     offer_letter_details: Mapped['OfferLetterDetails'] = relationship('OfferLetterDetails', back_populates='addresses', lazy="selectin")


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

#     countries: Mapped['Countries'] = relationship('Countries', back_populates='contacts', lazy="selectin")
#     offer_letter_details: Mapped['OfferLetterDetails'] = relationship('OfferLetterDetails', back_populates='contacts', lazy="selectin")


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

#     countries: Mapped['Countries'] = relationship('Countries', back_populates='country_education_document_mapping', lazy="selectin")
#     education_document_type: Mapped['EducationDocumentType'] = relationship('EducationDocumentType', back_populates='country_education_document_mapping', lazy="selectin")
#     education_level: Mapped['EducationLevel'] = relationship('EducationLevel', back_populates='country_education_document_mapping', lazy="selectin")
#     employee_education_document: Mapped[list['EmployeeEducationDocument']] = relationship('EmployeeEducationDocument', back_populates='country_education_document_mapping', lazy="selectin")


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

#     countries: Mapped['Countries'] = relationship('Countries', back_populates='country_identity_mapping', lazy="selectin")
#     identity_type: Mapped['IdentityType'] = relationship('IdentityType', back_populates='country_identity_mapping', lazy="selectin")
#     employee_identity_document: Mapped[list['EmployeeIdentityDocument']] = relationship('EmployeeIdentityDocument', back_populates='country_identity_mapping', lazy="selectin")


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

#     deliverable_items: Mapped['DeliverableItems'] = relationship('DeliverableItems', back_populates='employee_deliverables', lazy="selectin")
#     offer_letter_details: Mapped['OfferLetterDetails'] = relationship('OfferLetterDetails', back_populates='employee_deliverables', lazy="selectin")


# class EmployeeExperience(Base):
#     __tablename__ = 'employee_experience'
#     __table_args__ = (
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
#     certificate_status: Mapped[Optional[str]] = mapped_column(Enum('uploaded', 'pending', 'verified', 'rejected'), server_default=text("'pending'"))
#     uploaded_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
#     verified_by: Mapped[Optional[str]] = mapped_column(CHAR(36))
#     verified_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
#     remarks: Mapped[Optional[str]] = mapped_column(String(255))
#     created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
#     updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

#     offer_letter_details: Mapped['OfferLetterDetails'] = relationship('OfferLetterDetails', back_populates='employee_experience', lazy="selectin")
#     employee_pay_slips: Mapped[list['EmployeePaySlips']] = relationship('EmployeePaySlips', back_populates='employee_experience', lazy="selectin")
#     employee_relieving_letter: Mapped[list['EmployeeRelievingLetter']] = relationship('EmployeeRelievingLetter', back_populates='employee_experience', lazy="selectin")


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

#     receivable_items: Mapped['ReceivableItems'] = relationship('ReceivableItems', back_populates='employee_receivables', lazy="selectin")
#     offer_letter_details: Mapped['OfferLetterDetails'] = relationship('OfferLetterDetails', back_populates='employee_receivables', lazy="selectin")


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

#     offer_letter_details: Mapped['OfferLetterDetails'] = relationship('OfferLetterDetails', back_populates='offer_approval_request', lazy="selectin")
#     offer_approval_action: Mapped[list['OfferApprovalAction']] = relationship('OfferApprovalAction', back_populates='request', lazy="selectin")


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

#     offer_letter_details: Mapped['OfferLetterDetails'] = relationship('OfferLetterDetails', back_populates='onboarding_links', lazy="selectin")


# class PersonalDetails(Base):
#     __tablename__ = 'personal_details'
#     __table_args__ = (
#         ForeignKeyConstraint(['nationality_country_uuid'], ['countries.country_uuid'], name='personal_details_ibfk_2'),
#         ForeignKeyConstraint(['residence_country_uuid'], ['countries.country_uuid'], name='personal_details_ibfk_3'),
#         ForeignKeyConstraint(['user_uuid'], ['offer_letter_details.user_uuid'], name='personal_details_ibfk_1'),
#         ForeignKeyConstraint(['emergency_contact_relation_uuid'], ['relation_master.relation_uuid'], name='personal_details_ibfk_4'),

#         Index('idx_personal_user', 'user_uuid'),
#         Index('idx_personal_user_uuid', 'user_uuid'),
#         Index('nationality_country_uuid', 'nationality_country_uuid'),
#         Index('personal_uuid', 'personal_uuid', unique=True),
#         Index('residence_country_uuid', 'residence_country_uuid'),
#         Index('user_uuid', 'user_uuid'),
#     )

#     id: Mapped[int] = mapped_column(Integer, primary_key=True)
#     personal_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)
#     user_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)

#     date_of_birth: Mapped[Optional[datetime.date]] = mapped_column(Date)
#     gender: Mapped[Optional[str]] = mapped_column(Enum('Male', 'Female', 'Other'))
#     marital_status: Mapped[Optional[str]] = mapped_column(Enum('Single', 'Married', 'Divorced', 'Widowed'))
#     blood_group: Mapped[Optional[str]] = mapped_column(String(5))
#     verification_status: Mapped[Optional[str]] = mapped_column(Enum('Pending', 'Verified', 'Rejected'),default='Pending')
#     nationality_country_uuid: Mapped[Optional[str]] = mapped_column(CHAR(36))
#     residence_country_uuid: Mapped[Optional[str]] = mapped_column(CHAR(36))

#     # NEW FIELDS
#     emergency_contact_name: Mapped[Optional[str]] = mapped_column(String(100))
#     emergency_contact_phone: Mapped[Optional[str]] = mapped_column(String(20))
#     emergency_contact_relation_uuid: Mapped[Optional[str]] = mapped_column(CHAR(36))
#     status: Mapped[Optional[str]] = mapped_column(
#         Enum('uploaded', 'verified', 'rejected'),
#         server_default=text("'uploaded'")
#     )

#     created_at: Mapped[Optional[datetime.datetime]] = mapped_column(
#         DateTime, server_default=text('CURRENT_TIMESTAMP')
#     )
#     updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(
#         DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')
#     )

#     countries: Mapped[Optional['Countries']] = relationship(
#         'Countries',
#         foreign_keys=[nationality_country_uuid],
#         back_populates='personal_details',
#         lazy="selectin"
#     )

#     countries_: Mapped[Optional['Countries']] = relationship(
#         'Countries',
#         foreign_keys=[residence_country_uuid],
#         back_populates='personal_details_',
#         lazy="selectin"
#     )

#     offer_letter_details: Mapped['OfferLetterDetails'] = relationship(
#         'OfferLetterDetails',
#         back_populates='personal_details',
#         lazy="selectin"
#     )

#     # NEW RELATIONSHIP
#     relation: Mapped[Optional['RelationMaster']] = relationship(
#         'RelationMaster',
#         foreign_keys=[emergency_contact_relation_uuid],
#         lazy="selectin"
#     )

# class RelationMaster(Base):
#     __tablename__ = "relation"

#     id: Mapped[int] = mapped_column(Integer, primary_key=True)
#     relation_uuid: Mapped[str] = mapped_column(CHAR(36), unique=True)
#     relation_name: Mapped[str] = mapped_column(String(50))

#     created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
#     updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

# class EmployeeEducationDocument(Base):
#     __tablename__ = 'employee_education_document'
#     __table_args__ = (
#         ForeignKeyConstraint(['mapping_uuid'], ['country_education_document_mapping.mapping_uuid'], name='employee_education_document_ibfk_1'),
#         ForeignKeyConstraint(['user_uuid'], ['offer_letter_details.user_uuid'], name='employee_education_document_ibfk_2'),
#         Index('document_uuid', 'document_uuid', unique=True),
#         Index('idx_education_user', 'user_uuid'),
#         Index('mapping_uuid', 'mapping_uuid'),
#         Index('user_uuid', 'user_uuid')
#     )

#     employee_education_document_id: Mapped[int] = mapped_column(Integer, primary_key=True)
#     document_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)
#     mapping_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)
#     user_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)
#     institution_name: Mapped[Optional[str]] = mapped_column(String(150))
#     specialization: Mapped[Optional[str]] = mapped_column(String(150))
#     year_of_passing: Mapped[Optional[Any]] = mapped_column(YEAR)
#     percentage_cgpa: Mapped[Optional[str]] = mapped_column(String(10))
#     file_path: Mapped[Optional[str]] = mapped_column(String(255))
#     status: Mapped[Optional[str]] = mapped_column(Enum('uploaded', 'verified', 'rejected'), server_default=text("'uploaded'"))
#     uploaded_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
#     verified_by: Mapped[Optional[str]] = mapped_column(CHAR(36))
#     verified_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
#     remarks: Mapped[Optional[str]] = mapped_column(String(255))
#     updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

#     country_education_document_mapping: Mapped['CountryEducationDocumentMapping'] = relationship('CountryEducationDocumentMapping', back_populates='employee_education_document', lazy="selectin")
#     offer_letter_details: Mapped['OfferLetterDetails'] = relationship('OfferLetterDetails', back_populates='employee_education_document', lazy="selectin")


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
#     verification_status: Mapped[Optional[str]] = mapped_column(Enum('Pending', 'Verified', 'Rejected'),default='Pending')
#     status: Mapped[Optional[str]] = mapped_column(Enum('uploaded', 'pending', 'verified', 'rejected'), server_default=text("'pending'"))
#     uploaded_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
#     verified_by: Mapped[Optional[str]] = mapped_column(CHAR(36))
#     verified_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
#     remarks: Mapped[Optional[str]] = mapped_column(String(255))
#     updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

#     country_identity_mapping: Mapped['CountryIdentityMapping'] = relationship('CountryIdentityMapping', back_populates='employee_identity_document', lazy="selectin")
#     offer_letter_details: Mapped['OfferLetterDetails'] = relationship('OfferLetterDetails', back_populates='employee_identity_document', lazy="selectin")


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

#     offer_letter_details: Mapped['OfferLetterDetails'] = relationship('OfferLetterDetails', back_populates='employee_pay_slips', lazy="selectin")
#     employee_experience: Mapped['EmployeeExperience'] = relationship('EmployeeExperience', back_populates='employee_pay_slips', lazy="selectin")


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

#     offer_letter_details: Mapped['OfferLetterDetails'] = relationship('OfferLetterDetails', back_populates='employee_relieving_letter', lazy="selectin")
#     employee_experience: Mapped['EmployeeExperience'] = relationship('EmployeeExperience', back_populates='employee_relieving_letter', lazy="selectin")


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

#     request: Mapped['OfferApprovalRequest'] = relationship('OfferApprovalRequest', back_populates='offer_approval_action', lazy="selectin")


# class EmployeeDetails(Base):
#     __tablename__ = "employee_details"

#     __table_args__ = (

#         ForeignKeyConstraint(["department_uuid"],["departments.department_uuid"],name="fk_employee_department"
#         ),

#         ForeignKeyConstraint( ["designation_uuid"], ["designations.designation_uuid"], name="fk_employee_designation"
#         ),

#         ForeignKeyConstraint(
#             ["reporting_manager_uuid"],
#             ["employee_details.employee_uuid"],
#             name="fk_employee_manager"
#         ),

#         Index("idx_employee_uuid", "employee_uuid", unique=True),
#         Index("idx_employee_id", "employee_id", unique=True),
#         Index("idx_employee_department", "department_uuid"),
#         Index("idx_employee_designation", "designation_uuid"),
#         Index("idx_employee_manager", "reporting_manager_uuid"),
#         Index("idx_employee_email", "work_email", unique=True),
#     )

#     id: Mapped[int] = mapped_column(Integer, primary_key=True)
#     employee_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)
#     user_uuid: Mapped[Optional[str]] = mapped_column(CHAR(36))
#     employee_id: Mapped[Optional[str]] = mapped_column(String(20))
#     first_name: Mapped[str] = mapped_column(String(50), nullable=False)
#     middle_name: Mapped[Optional[str]] = mapped_column(String(50))
#     last_name: Mapped[str] = mapped_column(String(50), nullable=False)
#     date_of_birth: Mapped[datetime.date] = mapped_column(Date)
#     work_email: Mapped[Optional[str]] = mapped_column(String(100))
#     contact_number: Mapped[Optional[str]] = mapped_column(String(15))
#     department_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)
#     designation_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)
#     reporting_manager_uuid: Mapped[Optional[str]] = mapped_column(CHAR(36))
#     employment_type: Mapped[str] = mapped_column(
#         Enum('Full-Time','Part-Time','Intern','Contractor','Freelance'),
#         nullable=False
#     )
#     joining_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
#     location: Mapped[str] = mapped_column(String(100), nullable=False)
#     work_mode: Mapped[str] = mapped_column(
#         Enum('Office','Remote','Hybrid'),
#         nullable=False
#     )
#     employment_status: Mapped[str] = mapped_column(
#         Enum('Probation','Active','Resigned','Terminated','Absconded'),
#         nullable=False
#     )
#     blood_group: Mapped[Optional[str]] = mapped_column(String(5))
#     gender: Mapped[Optional[str]] = mapped_column(
#         Enum('Male','Female','Other')
#     )
#     marital_status: Mapped[Optional[str]] = mapped_column(
#         Enum('Single','Married','Divorced','Widowed')
#     )
#     total_experience: Mapped[Optional[float]]
#     created_at: Mapped[Optional[datetime.datetime]] = mapped_column(
#         DateTime,
#         server_default=text("CURRENT_TIMESTAMP")
#     )
#     updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(
#         DateTime,
#         server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")
#     )
# class Departments(Base):
#     __tablename__ = "departments"

#     __table_args__ = (
#         Index("idx_department_uuid", "department_uuid", unique=True),
#     )

#     department_id: Mapped[int] = mapped_column(Integer, primary_key=True)
#     department_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)
#     department_name: Mapped[str] = mapped_column(String(100), nullable=False)
#     description: Mapped[Optional[str]] = mapped_column(String(255))

#     created_at: Mapped[Optional[datetime.datetime]] = mapped_column(
#         DateTime,
#         server_default=text("CURRENT_TIMESTAMP")
#     )

#     updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(
#         DateTime,
#         server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")
#     )

class Designations(Base):
    __tablename__ = "designations"

    __table_args__ = (
        Index("idx_designation_uuid", "designation_uuid", unique=True),
    )

    designation_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    designation_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)
    designation_name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255))

    department_uuid: Mapped[str] = mapped_column(
        CHAR(36),
        ForeignKey("departments.department_uuid"),
        nullable=False
    )

    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP")
    )

    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")
    )

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
        Index('department_uuid', 'department_uuid', unique=True),
    )

    department_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    department_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)
    department_name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    employee_details: Mapped[list['EmployeeDetails']] = relationship('EmployeeDetails', back_populates='departments')


# class Designations(Base):
#     __tablename__ = 'designations'
#     __table_args__ = (
#         Index('designation_uuid', 'designation_uuid', unique=True),
#     )

#     designation_id: Mapped[int] = mapped_column(Integer, primary_key=True)
#     designation_uuid: Mapped[str] = mapped_column(CHAR(36), nullable=False)
#     designation_name: Mapped[str] = mapped_column(String(100), nullable=False)
#     description: Mapped[Optional[str]] = mapped_column(String(255))
#     created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
#     updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

#     employee_details: Mapped[list['EmployeeDetails']] = relationship('EmployeeDetails', back_populates='designations')


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
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    mail: Mapped[str] = mapped_column(String(100), nullable=False)
    country_code: Mapped[str] = mapped_column(String(5), nullable=False)
    contact_number: Mapped[str] = mapped_column(String(15), nullable=False)
    designation: Mapped[str] = mapped_column(String(50), nullable=False)
    employee_type: Mapped[str] = mapped_column(Enum('Full-Time', 'Part-Time', 'Intern', 'Contractor', 'Freelance'), nullable=False)
    package: Mapped[str] = mapped_column(String(20), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), nullable=False)
    job_id: Mapped[str] = mapped_column(String(255), nullable=False)
    created_by: Mapped[int] = mapped_column(Integer, nullable=False)
    middle_name: Mapped[Optional[str]] = mapped_column(String(100))
    package: Mapped[Optional[str]] = mapped_column(String(255))
    currency: Mapped[Optional[str]] = mapped_column(String(20))
    status: Mapped[Optional[str]] = mapped_column(ENUM('Created', 'Offered', 'Accepted', 'Rejected', 'Submitted', 'Verified', 'Completed'), server_default=text("'Created'"))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    file_path: Mapped[Optional[str]] = mapped_column(String(255))
    pandadoc_draft_id: Mapped[Optional[str]] = mapped_column(String(255))
    offer_response_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    joining_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    cc_emails: Mapped[Optional[str]] = mapped_column(String(256))
    total_ctc: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(12, 2))

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
    employment_status: Mapped[Optional[str]] = mapped_column(Enum('Probation', 'Active', 'Resigned', 'Terminated', 'Absconded'), server_default=text("'Probation'"))
    blood_group: Mapped[Optional[str]] = mapped_column(String(5))
    gender: Mapped[Optional[str]] = mapped_column(Enum('Male', 'Female', 'Other'))
    marital_status: Mapped[Optional[str]] = mapped_column(Enum('Single', 'Married', 'Divorced', 'Widowed'))
    total_experience: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(4, 1))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    departments: Mapped[Optional['Departments']] = relationship('Departments', back_populates='employee_details')
    designations: Mapped[Optional['Designations']] = relationship('Designations', back_populates='employee_details')
    offer_letter_details: Mapped['OfferLetterDetails'] = relationship('OfferLetterDetails', back_populates='employee_details')


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
        ForeignKeyConstraint(['emergency_contact_relation_uuid'], ['relation.relation_uuid'], name='personal_details_ibfk_4'),

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
    __tablename__ = "relation"
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



