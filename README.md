# ASF (Automation Service Framework) Implementation Documentation

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [User Personas](#user-personas)
4. [Implementation Workflows](#implementation-workflows)
5. [Core Components](#core-components)
6. [Data Normalization](#data-normalization)
7. [Technical Specifications](#technical-specifications)
8. [Testing Strategy](#testing-strategy)
9. [Deployment and Release](#deployment-and-release)

---

## Overview

The Automation Service Framework (ASF) is a comprehensive platform designed to streamline business process automation through a hierarchical user system. It enables organizations to create, customize, and deploy automated workflows with varying levels of complexity based on user expertise.

### Key Features
- Multi-tier user access (Super Admin, Complex Business User, Easy Business User)
- Object-oriented workflow design
- Dynamic action mapping
- Process blueprint templates
- Data source integration with normalization
- Ability-based context generation

---

## Architecture

### System Components
1. **Atlas** - Configuration and mapping interface
2. **Activepieces** - Workflow execution engine
3. **Process Blueprint Repository** - Template storage and management
4. **Data Normalization Layer** - Standardizes input data from various sources

### Data Flow
```
Source Data → Normalization Layer → Object Creation → Action Processing → Output
```

---

## User Personas

### 1. Super Admin
- Full system access
- Creates new objects and actions from scratch
- Defines process blueprints
- Manages tolerance rules and system configurations

### 2. Business User (Complex)
- Maps existing objects and actions
- Customizes stage abilities
- Modifies process blueprints
- Performs advanced testing

### 3. Business User (Easy) - 80% of users
- Selects pre-built process blueprints
- Basic object/action mapping
- Simplified testing and deployment

---

## Implementation Workflows

### Super Admin Workflow (From Scratch)

#### Step 1: Define Objects and Their JSON Structure

**Core Objects:**

1. **Invoice Object**
```json
{
  "invoice": {
    "id": "string",
    "invoice_number": "string",
    "vendor_id": "string",
    "po_reference": "string",
    "amount": "number",
    "currency": "string",
    "line_items": [
      {
        "item_id": "string",
        "description": "string",
        "quantity": "number",
        "unit_price": "number",
        "total": "number"
      }
    ],
    "status": "enum[pending, approved, rejected, paid]",
    "created_date": "datetime",
    "due_date": "datetime",
    "metadata": {
      "source_system": "string",
      "normalized_at": "datetime"
    }
  }
}
```

2. **Purchase Order (PO) Object**
```json
{
  "purchase_order": {
    "id": "string",
    "po_number": "string",
    "vendor_id": "string",
    "total_amount": "number",
    "currency": "string",
    "line_items": [
      {
        "item_id": "string",
        "description": "string",
        "quantity": "number",
        "unit_price": "number",
        "total": "number"
      }
    ],
    "status": "enum[draft, approved, sent, received, closed]",
    "created_date": "datetime",
    "approval_date": "datetime",
    "metadata": {
      "source_system": "string",
      "normalized_at": "datetime"
    }
  }
}
```

3. **Goods Receipt Note (GRN) Object**
```json
{
  "grn": {
    "id": "string",
    "grn_number": "string",
    "po_reference": "string",
    "vendor_id": "string",
    "received_items": [
      {
        "item_id": "string",
        "expected_quantity": "number",
        "received_quantity": "number",
        "status": "enum[accepted, rejected, partial]",
        "inspection_notes": "string"
      }
    ],
    "received_date": "datetime",
    "warehouse_location": "string",
    "status": "enum[pending, partial, complete]",
    "metadata": {
      "source_system": "string",
      "normalized_at": "datetime"
    }
  }
}
```

4. **Tolerance Rules Object**
```json
{
  "tolerance_rules": {
    "id": "string",
    "rule_name": "string",
    "rule_type": "enum[amount, percentage, quantity]",
    "threshold_value": "number",
    "applicable_to": "enum[invoice, po, grn]",
    "conditions": [
      {
        "field": "string",
        "operator": "enum[equals, greater_than, less_than, between]",
        "value": "any"
      }
    ],
    "actions": ["string"],
    "priority": "number",
    "active": "boolean",
    "metadata": {
      "created_by": "string",
      "created_date": "datetime",
      "last_modified": "datetime"
    }
  }
}
```

#### Step 2: Define Actions

**Core Actions:**

1. **human_review_invoice**
```json
{
  "action": "human_review_invoice",
  "parameters": {
    "invoice_id": "string",
    "review_reason": "string",
    "assigned_to": "string",
    "priority": "enum[low, medium, high, urgent]",
    "due_date": "datetime"
  },
  "output": {
    "review_id": "string",
    "status": "enum[assigned, in_progress, completed]"
  }
}
```

2. **update_invoice_status**
```json
{
  "action": "update_invoice_status",
  "parameters": {
    "invoice_id": "string",
    "new_status": "enum[pending, approved, rejected, paid]",
    "reason": "string",
    "updated_by": "string"
  },
  "output": {
    "success": "boolean",
    "previous_status": "string",
    "timestamp": "datetime"
  }
}
```

3. **notify_vendor**
```json
{
  "action": "notify_vendor",
  "parameters": {
    "vendor_id": "string",
    "notification_type": "enum[email, sms, api]",
    "template_id": "string",
    "context_data": "object"
  },
  "output": {
    "notification_id": "string",
    "sent_status": "boolean",
    "sent_at": "datetime"
  }
}
```

4. **archive_invoice_docs**
```json
{
  "action": "archive_invoice_docs",
  "parameters": {
    "invoice_id": "string",
    "document_ids": ["string"],
    "archive_location": "string",
    "retention_period": "number"
  },
  "output": {
    "archived_count": "number",
    "archive_reference": "string",
    "archive_date": "datetime"
  }
}
```

#### Step 3: Map Objects & Actions in Atlas

The mapping process involves:
1. Creating object definitions in Atlas UI
2. Defining relationships between objects
3. Associating actions with objects
4. Setting up trigger conditions

#### Step 4: Define Stage Abilities

**Ability Configuration:**
```json
{
  "stage": "invoice_processing",
  "abilities": [
    {
      "name": "validate_invoice",
      "description": "Validates invoice against PO and tolerance rules",
      "required_objects": ["invoice", "purchase_order", "tolerance_rules"],
      "actions": ["update_invoice_status", "human_review_invoice"]
    },
    {
      "name": "match_grn",
      "description": "Matches invoice items with GRN records",
      "required_objects": ["invoice", "grn"],
      "actions": ["update_invoice_status"]
    },
    {
      "name": "vendor_communication",
      "description": "Handles all vendor notifications",
      "required_objects": ["vendor"],
      "actions": ["notify_vendor"]
    }
  ]
}
```

#### Step 5: Generate Complex JSON Configuration

**Complete Workflow Configuration:**
```json
{
  "workflow_name": "invoice_processing_workflow",
  "version": "1.0",
  "abilities": [
    {
      "ability_id": "validate_invoice",
      "stage": "validation",
      "order": 1
    },
    {
      "ability_id": "match_grn",
      "stage": "matching",
      "order": 2
    },
    {
      "ability_id": "vendor_communication",
      "stage": "notification",
      "order": 3
    }
  ],
  "objects": {
    "invoice": {
      "source": "data_source_1",
      "normalization_rules": [
        {
          "field": "amount",
          "transform": "decimal_2_places"
        }
      ]
    },
    "purchase_order": {
      "source": "data_source_2",
      "normalization_rules": [
        {
          "field": "po_number",
          "transform": "uppercase"
        }
      ]
    }
  },
  "data_sources": [
    {
      "id": "data_source_1",
      "type": "api",
      "endpoint": "https://api.example.com/invoices",
      "authentication": "oauth2"
    },
    {
      "id": "data_source_2",
      "type": "database",
      "connection_string": "encrypted_connection_string"
    }
  ]
}
```

#### Step 6: Customize in Activepieces

In Activepieces:
1. Create tables for each object type
2. Implement data population logic
3. Configure action execution
4. Set up error handling and logging

#### Step 7: Test Process

Testing checklist:
- [ ] Object creation and population
- [ ] Data normalization accuracy
- [ ] Action execution flow
- [ ] Error handling scenarios
- [ ] Performance benchmarks
- [ ] Cross-customer compatibility

#### Step 8: Release as Process Blueprint

Blueprint metadata:
```json
{
  "blueprint_id": "invoice_processing_v1",
  "name": "Standard Invoice Processing",
  "description": "Automated invoice processing with 3-way matching",
  "category": "financial",
  "complexity": "medium",
  "estimated_setup_time": "2 hours",
  "supported_objects": ["invoice", "po", "grn"],
  "required_abilities": ["validate_invoice", "match_grn"],
  "version": "1.0",
  "release_date": "2024-01-01"
}
```

### Business User (Complex) Workflow

#### Step 1: Map Objects & Actions in Atlas
- Access Atlas interface
- Select existing objects from library
- Map to internal data structures
- Configure field mappings

#### Step 2: Select Process Blueprint
- Browse blueprint catalog
- Filter by category and complexity
- Review blueprint requirements
- Import selected blueprint

#### Step 3: Customize Stage Abilities
- Modify ability parameters
- Add custom validation rules
- Configure notification preferences
- Set approval thresholds

#### Step 4: Generate Complex JSON
- Review generated configuration
- Make manual adjustments if needed
- Validate JSON structure
- Save configuration version

#### Step 5: Test
- Run test scenarios
- Validate output accuracy
- Check performance metrics
- Document test results

#### Step 6: Start Running
- Deploy to production
- Monitor initial runs
- Configure alerts
- Schedule regular executions

### Business User (Easy) Workflow - 80% Use Case

#### Step 1: Select Process Blueprint and Map
- Choose from recommended blueprints
- Use guided mapping wizard
- Auto-detect compatible objects
- One-click field mapping

#### Step 2: Test
- Run pre-configured test suite
- Review automated test results
- Approve or request adjustments

#### Step 3: Start Running
- Single-click deployment
- Automated monitoring setup
- Default alert configuration

---

## Core Components

### Objects Management
- Centralized object repository
- Version control for object schemas
- Cross-reference validation
- Schema migration tools

### Actions Library
- Pre-built action templates
- Custom action builder
- Action chaining capabilities
- Rollback mechanisms

### Ability Framework
```
Ability → Context → Accurate JSON
```
Each ability encapsulates:
- Business logic
- Required objects
- Available actions
- Context generation rules

---

## Data Normalization

### Normalization Pipeline

1. **Data Ingestion**
   - Multiple source formats supported
   - Real-time and batch processing
   - Schema detection

2. **Transformation Rules**
   ```json
   {
     "normalization_rules": [
       {
         "source_field": "vendor_name",
         "target_field": "vendor.name",
         "transformations": [
           "trim",
           "uppercase",
           "remove_special_chars"
         ]
       },
       {
         "source_field": "invoice_amt",
         "target_field": "amount",
         "transformations": [
           "parse_currency",
           "convert_to_decimal",
           "round_2_places"
         ]
       }
     ]
   }
   ```

3. **Validation**
   - Data type checking
   - Required field validation
   - Business rule validation
   - Referential integrity

4. **Error Handling**
   - Invalid data quarantine
   - Transformation error logs
   - Manual review queue
   - Auto-retry mechanisms

### Normalization Strategies

**Field-Level Normalization:**
- Date formats → ISO 8601
- Currency → Standard decimal
- Text → UTF-8, trimmed
- Numbers → Consistent precision

**Object-Level Normalization:**
- Consistent ID formats
- Standardized status values
- Unified address formats
- Normalized relationships

---

## Technical Specifications

### System Requirements
- **Atlas Platform:** v2.0+
- **Activepieces:** v1.5+
- **Database:** PostgreSQL 12+
- **API Gateway:** REST/GraphQL support
- **Message Queue:** RabbitMQ/Kafka

### API Specifications

**Object API:**
```
POST /api/v1/objects
GET /api/v1/objects/{object_type}
PUT /api/v1/objects/{object_id}
DELETE /api/v1/objects/{object_id}
```

**Action API:**
```
POST /api/v1/actions/execute
GET /api/v1/actions/{action_id}/status
GET /api/v1/actions/available
```

**Workflow API:**
```
POST /api/v1/workflows/create
GET /api/v1/workflows/{workflow_id}
PUT /api/v1/workflows/{workflow_id}/deploy
GET /api/v1/workflows/{workflow_id}/metrics
```

### Security Considerations
- OAuth 2.0 authentication
- Role-based access control (RBAC)
- Data encryption at rest and in transit
- Audit logging for all operations
- PII data masking

### Performance Specifications
- Object creation: < 100ms
- Action execution: < 500ms
- Workflow processing: 1000 transactions/minute
- Data normalization: 10MB/second
- API response time: < 200ms (p95)

---

## Testing Strategy

### Unit Testing
- Individual action testing
- Object validation testing
- Normalization rule testing

### Integration Testing
- End-to-end workflow testing
- Cross-system data flow
- API integration validation

### Performance Testing
- Load testing scenarios
- Stress testing limits
- Scalability validation

### User Acceptance Testing
- Business scenario validation
- UI/UX testing
- Documentation review

---

## Deployment and Release

### Deployment Process
1. **Development Environment**
   - Feature development
   - Unit testing
   - Code review

2. **Staging Environment**
   - Integration testing
   - Performance testing
   - Security scanning

3. **Production Environment**
   - Blue-green deployment
   - Canary releases
   - Rollback procedures

### Release Management
- Semantic versioning (MAJOR.MINOR.PATCH)
- Release notes documentation
- Migration guides
- Backward compatibility matrix

### Monitoring and Maintenance
- Real-time dashboard
- Alert configuration
- Log aggregation
- Performance metrics
- Health checks

---

## Appendix

### Glossary
- **ASF**: Automation Service Framework
- **Atlas**: Configuration and mapping platform
- **Activepieces**: Workflow execution engine
- **Blueprint**: Pre-configured workflow template
- **Ability**: Encapsulated business logic unit
- **GRN**: Goods Receipt Note
- **PO**: Purchase Order

### References
- Atlas Documentation: [internal link]
- Activepieces Guide: [internal link]
- API Documentation: [internal link]
- Security Guidelines: [internal link]
