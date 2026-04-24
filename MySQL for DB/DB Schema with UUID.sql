-- =========================================================
-- 1. Offer Letter Details
-- =========================================================
CREATE TABLE offer_letter_details (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    user_uuid CHAR(36) NOT NULL UNIQUE,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    mail VARCHAR(100) NOT NULL UNIQUE,
    country_code VARCHAR(5) NOT NULL, 
    contact_number VARCHAR(15) NOT NULL,
    designation VARCHAR(50) NOT NULL,
    package VARCHAR(20) NOT NULL,
    currency VARCHAR(10) NOT NULL,
    status ENUM('Created', 'Offered', 'Accepted', 'Rejected') DEFAULT 'Created',
    created_by INT NOT NULL, -- Refers to ums user table user id
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    file_path VARCHAR(255),
    pandadoc_draft_id VARCHAR(255),
    offer_response_at DATETIME
);

-- =========================================================
-- 2. Countries Master
-- =========================================================
CREATE TABLE countries (
    country_id INT PRIMARY KEY AUTO_INCREMENT,
    country_uuid CHAR(36) NOT NULL UNIQUE,
    country_name VARCHAR(100) NOT NULL,
    calling_code VARCHAR(5),
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- =========================================================
-- 3. Contact Details
-- =========================================================
CREATE TABLE contacts (
    contact_id INT PRIMARY KEY AUTO_INCREMENT,
    contact_uuid CHAR(36) NOT NULL UNIQUE,
    user_uuid CHAR(36) NOT NULL,
    country_uuid CHAR(36) NOT NULL,
    contact_number VARCHAR(15) NOT NULL,
    emergency_contact VARCHAR(15) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_uuid) REFERENCES offer_letter_details(user_uuid),
    FOREIGN KEY (country_uuid) REFERENCES countries(country_uuid)
);

-- =========================================================
-- 4. Personal Details
-- =========================================================
CREATE TABLE personal_details (
    id INT PRIMARY KEY AUTO_INCREMENT,
    personal_uuid CHAR(36) NOT NULL UNIQUE,
    user_uuid CHAR(36) NOT NULL,
    date_of_birth DATE,
    gender ENUM('Male', 'Female', 'Other'),
    marital_status ENUM('Single', 'Married', 'Divorced', 'Widowed'),
    blood_group VARCHAR(5),
    nationality_country_uuid CHAR(36),
    residence_country_uuid CHAR(36),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_uuid) REFERENCES offer_letter_details(user_uuid),
    FOREIGN KEY (nationality_country_uuid) REFERENCES countries(country_uuid),
    FOREIGN KEY (residence_country_uuid) REFERENCES countries(country_uuid)
);

-- =========================================================
-- 5. Employee Address Details
-- =========================================================
CREATE TABLE addresses (
    address_id INT PRIMARY KEY AUTO_INCREMENT,
    address_uuid CHAR(36) NOT NULL UNIQUE,
    user_uuid CHAR(36) NOT NULL,

    -- permanent / current / work / billing etc.
    address_type ENUM(
        'permanent',
        'current'
    ) NOT NULL,

    -- Core address fields
    address_line1 VARCHAR(255) NOT NULL,
    address_line2 VARCHAR(255),

    -- Internationally flexible fields
    city VARCHAR(150),
    district_or_ward VARCHAR(150),
    state_or_region VARCHAR(150),
    postal_code VARCHAR(20),

    country_uuid CHAR(36) NOT NULL,

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (user_uuid) REFERENCES offer_letter_details(user_uuid),
    FOREIGN KEY (country_uuid) REFERENCES countries(country_uuid)
);


-- =========================================================
-- 6. Identity Type Master
-- =========================================================
CREATE TABLE identity_type (
    identity_type_id INT PRIMARY KEY AUTO_INCREMENT,
    identity_type_uuid CHAR(36) NOT NULL UNIQUE,
    identity_type_name VARCHAR(100) NOT NULL,
    description VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- =========================================================
-- 8. Country–Identity Mapping
-- =========================================================
CREATE TABLE country_identity_mapping (
    mapping_id INT PRIMARY KEY AUTO_INCREMENT,
    mapping_uuid CHAR(36) NOT NULL UNIQUE,
    country_uuid CHAR(36) NOT NULL,
    identity_type_uuid CHAR(36) NOT NULL,
    is_mandatory BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (country_uuid) REFERENCES countries(country_uuid),
    FOREIGN KEY (identity_type_uuid) REFERENCES identity_type(identity_type_uuid)
);

-- =========================================================
-- 9. Employee Identity Document Uploads
-- =========================================================
CREATE TABLE employee_identity_document (
    employee_identity_document_id INT PRIMARY KEY AUTO_INCREMENT,
    document_uuid CHAR(36) NOT NULL UNIQUE,
    mapping_uuid CHAR(36) NOT NULL,
    user_uuid CHAR(36) NOT NULL,
    file_path VARCHAR(255),
    expiry_date DATE,
    status ENUM('uploaded', 'pending', 'verified', 'rejected') DEFAULT 'pending',
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    verified_by CHAR(36) NULL,
    verified_at DATETIME NULL,
    remarks VARCHAR(255),
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (mapping_uuid) REFERENCES country_identity_mapping(mapping_uuid),
    FOREIGN KEY (user_uuid) REFERENCES offer_letter_details(user_uuid)
);

-- =========================================================
-- 10. Education Level Master
-- =========================================================
CREATE TABLE education_level (
    education_id INT PRIMARY KEY AUTO_INCREMENT,
    education_uuid CHAR(36) NOT NULL UNIQUE,
    education_name VARCHAR(100) NOT NULL,
    description VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- =========================================================
-- 11. Education Document Type Master
-- =========================================================
CREATE TABLE education_document_type (
    education_document_id INT PRIMARY KEY AUTO_INCREMENT,
    education_document_uuid CHAR(36) NOT NULL UNIQUE,
    document_name VARCHAR(100) NOT NULL,
    description VARCHAR(200),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- =========================================================
-- 12. Country–Education–Document Mapping
-- =========================================================
CREATE TABLE country_education_document_mapping (
    mapping_id INT PRIMARY KEY AUTO_INCREMENT,
    mapping_uuid CHAR(36) NOT NULL UNIQUE,
    country_uuid CHAR(36) NOT NULL,
    education_uuid CHAR(36) NOT NULL,
    education_document_uuid CHAR(36) NOT NULL,
    is_mandatory BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (country_uuid) REFERENCES countries(country_uuid),
    FOREIGN KEY (education_uuid) REFERENCES education_level(education_uuid),
    FOREIGN KEY (education_document_uuid) REFERENCES education_document_type(education_document_uuid)
);

-- =========================================================
-- 13. Employee Education Document Uploads
-- =========================================================
CREATE TABLE employee_education_document (
    employee_education_document_id INT PRIMARY KEY AUTO_INCREMENT,
    document_uuid CHAR(36) NOT NULL UNIQUE,
    mapping_uuid CHAR(36) NOT NULL,
    user_uuid CHAR(36) NOT NULL,
    institution_name VARCHAR(150),
    specialization VARCHAR(150),
    year_of_passing YEAR,
    file_path VARCHAR(255),
    status ENUM('uploaded', 'verified', 'rejected') DEFAULT 'uploaded',
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    verified_by CHAR(36) NULL,
    verified_at DATETIME NULL,
    remarks VARCHAR(255),
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (mapping_uuid) REFERENCES country_education_document_mapping(mapping_uuid),
    FOREIGN KEY (user_uuid) REFERENCES offer_letter_details(user_uuid)
);

-- =========================================================
-- 14. Employee Experience Details
-- =========================================================
CREATE TABLE employee_experience (
    experience_id INT PRIMARY KEY AUTO_INCREMENT,
    experience_uuid CHAR(36) NOT NULL UNIQUE,
    employee_uuid CHAR(36) NOT NULL,
    company_name VARCHAR(150) NOT NULL,
    role_title VARCHAR(100),
    employment_type ENUM('Full-Time', 'Part-Time', 'Intern', 'Contract', 'Freelance'),
    start_date DATE NOT NULL,
    end_date DATE NULL,
    is_current BOOLEAN DEFAULT FALSE,
    exp_certificate_path VARCHAR(255),
    certificate_status ENUM('uploaded', 'pending', 'verified', 'rejected') DEFAULT 'pending',
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    verified_by CHAR(36) NULL,
    verified_at DATETIME NULL,
    remarks VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_uuid) REFERENCES offer_letter_details(user_uuid)
);

-- =========================================================
-- 15. Employee Pay Slips (Only for Last Company)
-- =========================================================
CREATE TABLE employee_pay_slips (
    pay_slip_id INT PRIMARY KEY AUTO_INCREMENT,
    pay_slip_uuid CHAR(36) NOT NULL UNIQUE,
    employee_uuid CHAR(36) NOT NULL,
    experience_uuid CHAR(36) NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    status ENUM('uploaded', 'pending', 'verified', 'rejected') DEFAULT 'pending',
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    verified_by CHAR(36) NULL,
    verified_at DATETIME NULL,
    remarks VARCHAR(255),
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_uuid) REFERENCES offer_letter_details(user_uuid),
    FOREIGN KEY (experience_uuid) REFERENCES employee_experience(experience_uuid)
);

-- =========================================================
-- 16. Employee Relieving Letter (Submitted on Joining Day)
-- =========================================================
CREATE TABLE employee_relieving_letter (
    relieving_id INT PRIMARY KEY AUTO_INCREMENT,
    relieving_uuid CHAR(36) NOT NULL UNIQUE,
    employee_uuid CHAR(36) NOT NULL,
    experience_uuid CHAR(36) NOT NULL,
    file_path VARCHAR(255),
    status ENUM('uploaded', 'pending', 'verified', 'rejected') DEFAULT 'pending',
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    verified_by CHAR(36) NULL,
    verified_at DATETIME NULL,
    remarks VARCHAR(255),
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_uuid) REFERENCES offer_letter_details(user_uuid),
    FOREIGN KEY (experience_uuid) REFERENCES employee_experience(experience_uuid)
);

-- =========================================================
-- 17. Deliverable Master
-- =========================================================
CREATE TABLE deliverable_items (
    deliverable_id INT PRIMARY KEY AUTO_INCREMENT,
    deliverable_uuid CHAR(36) NOT NULL UNIQUE,
    item_name VARCHAR(100) NOT NULL,
    description VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- =========================================================
-- 18. Employee Deliverables
-- =========================================================
CREATE TABLE employee_deliverables (
    employee_deliverable_id INT PRIMARY KEY AUTO_INCREMENT,
    employee_deliverable_uuid CHAR(36) NOT NULL UNIQUE,
    user_uuid CHAR(36) NOT NULL,
    deliverable_uuid CHAR(36) NOT NULL,
    status ENUM('Pending', 'Delivered', 'Returned') DEFAULT 'Pending',
    issued_by CHAR(36) NULL,
    issued_at DATETIME NULL,
    returned_at DATETIME NULL,
    remarks VARCHAR(255),
    FOREIGN KEY (user_uuid) REFERENCES offer_letter_details(user_uuid),
    FOREIGN KEY (deliverable_uuid) REFERENCES deliverable_items(deliverable_uuid)
);

-- =========================================================
-- 19. Receivable Master
-- =========================================================
CREATE TABLE receivable_items (
    receivable_id INT PRIMARY KEY AUTO_INCREMENT,
    receivable_uuid CHAR(36) NOT NULL UNIQUE,
    item_name VARCHAR(100) NOT NULL,
    description VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- =========================================================
-- 20. Employee Receivables
-- =========================================================
CREATE TABLE employee_receivables (
    employee_receivable_id INT PRIMARY KEY AUTO_INCREMENT,
    employee_receivable_uuid CHAR(36) NOT NULL UNIQUE,
    user_uuid CHAR(36) NOT NULL,
    receivable_uuid CHAR(36) NOT NULL,
    status ENUM('Pending', 'Received', 'Not Received') DEFAULT 'Pending',
    collected_by CHAR(36) NULL,
    collected_at DATETIME NULL,
    remarks VARCHAR(255),
    FOREIGN KEY (user_uuid) REFERENCES offer_letter_details(user_uuid),
    FOREIGN KEY (receivable_uuid) REFERENCES receivable_items(receivable_uuid)
);

-- 21 Audit Logs Table 
CREATE TABLE audit_trail (
    audit_id INT AUTO_INCREMENT PRIMARY KEY,
    audit_uuid CHAR(36) NOT NULL,
    entity_name VARCHAR(100) NOT NULL,         -- table name
    entity_id VARCHAR(100) NOT NULL,           -- row id from that table
    operation ENUM('CREATE', 'UPDATE', 'DELETE') NOT NULL,
    user_id VARCHAR(100) DEFAULT NULL,         -- who performed the action
    old_data JSON DEFAULT NULL,                -- before update
    new_data JSON DEFAULT NULL,                -- after update
    ip_address VARCHAR(50) DEFAULT NULL,
    host VARCHAR(255) DEFAULT NULL,            -- localhost:8000 or EC2 DNS
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE otptable (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    otp VARCHAR(10) NOT NULL,
    expirytime DATETIME NOT NULL
);

CREATE TABLE employee_tasks (
    task_id INT AUTO_INCREMENT PRIMARY KEY,
    task_uuid CHAR(36) UNIQUE NOT NULL,

    user_uuid CHAR(36) NOT NULL,

    task_title VARCHAR(255) NOT NULL,

    task_type ENUM(
        'Onboarding',
        'Exit',
        'IT Provisioning',
        'Finance Clearance',
        'Admin'
    ) NOT NULL,

    description TEXT,

    assigned_to VARCHAR(150) NOT NULL,
    assigned_team VARCHAR(100),

    priority ENUM('High','Medium','Low') DEFAULT 'Medium',

    status ENUM(
        'To Do',
        'In Progress',
        'Completed',
        'Cancelled'
    ) DEFAULT 'To Do',

    progress INT DEFAULT 0,

    due_date DATE,
    reminder_date DATE,

    send_notification BOOLEAN DEFAULT TRUE,

    escalation_owner VARCHAR(150),

    internal_notes TEXT,
    comments TEXT,

    created_by VARCHAR(150) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    updated_by VARCHAR(150),
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    completed_by VARCHAR(150),
    completed_at DATETIME NULL
);