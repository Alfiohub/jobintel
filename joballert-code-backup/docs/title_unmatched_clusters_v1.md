# Title Unmatched Clusters v1

Source run: `docs/title_eval_greenhouse_full_v4`
Other rows analyzed: `27546`

## Cluster Report

### other_long_tail
- total_frequency: 24815
- recommended_action: keep_other
- proposed_role_family: other
- proposed_normalized_title: other
- rationale: Lunga coda eterogenea: bassa frequenza o alta ambiguità; mantenere other in questa fase.
- sample_titles:
  - Producer
  - Senior Product Analyst
  - Senior QA Engineer
  - Per Diem Clinical Research Nurse - Home Visits
  - Story Desk Editor
  - Implementation Manager
  - Customer Support Representative
  - Sonder Responder
  - Medical Assistant
  - Hair Color Bar Assistant, Licensed Cosmetologist
  - Customer Support Specialist
  - Manager, Software Engineering

### operations_support_coordinator
- total_frequency: 582
- recommended_action: map_to_existing
- proposed_role_family: operations
- proposed_normalized_title: operations_specialist
- rationale: Pattern operativo/backoffice; copribile senza nuova family.
- sample_titles:
  - Rental Coordinator
  - Payroll Specialist
  - Project Coordinator
  - Office Coordinator
  - Logistics Coordinator
  - Production Coordinator
  - Workplace Experience Coordinator
  - Payroll Specialist Lead - Croatia - Serbia

### healthcare_nursing_physician
- total_frequency: 497
- recommended_action: add_new_normalized_title
- proposed_role_family: healthcare_clinical
- proposed_normalized_title: registered_nurse
- rationale: Volume alto; inferenza forte dal titolo. Conviene introdurre almeno il nodo nurse (ed eventualmente physician in step successivo).
- sample_titles:
  - Primary Care Physician
  - Registered Nurse (RN)
  - Licensed Practical Nurse (LPN)
  - Family Medicine Physician
  - Collaborating Physician (1099 Contract) - Virtual Women’s Health
  - Obesity Medicine Physician - Dedicated Collaborator W2 Telemedicine
  - Per Diem Family Medicine Physician (Casual Employee)
  - Registered Nurse (RN) Rehab Nurse Full-Time 12-Hour Day Shift

### mental_health_therapy
- total_frequency: 487
- recommended_action: add_new_normalized_title
- proposed_role_family: healthcare_clinical
- proposed_normalized_title: mental_health_specialist
- rationale: Cluster ricorrente e semanticamente coeso; oggi frammentato tra therapist/intervention/behavioral support.
- sample_titles:
  - Intervention Specialist
  - Direct Support Professional (DSP)
  - Behavioral Interventionist
  - Board Certified Behavior Analyst
  - Contracted In-Home Occupational Therapist
  - Occupational Therapist
  - Respiratory Therapist - Registered
  - Child and Adolescent Therapist - LCSW, LPC, LMFT - Contract - Hybrid

### retail_store
- total_frequency: 370
- recommended_action: add_new_normalized_title
- proposed_role_family: sales
- proposed_normalized_title: store_associate
- rationale: Cluster retail operativo frequente, poco coperto dalle label attuali enterprise/SaaS.
- sample_titles:
  - Entry-Level Automotive Detailer - Lot Attendant
  - Entry-Level Automotive Parts Associate
  - Entry-Level Automotive Detailer - Lot Attendant Post Production
  - Stylist (Retail) (Part-time)
  - Floor Lead (Retail) (Part-time)
  - Mid-Level Automotive Parts Associate
  - Retail Store Manager
  - Automotive Detailer - Lot Attendant

### manager_generic_business_manager
- total_frequency: 353
- recommended_action: map_to_existing
- proposed_role_family: mixed_policy
- proposed_normalized_title: mixed_policy
- rationale: Non trattare come un cluster unico: parte mappabile (business development/social media), parte da tenere other (general manager/safety manager ambiguo).
- sample_titles:
  - General Manager
  - Business Development Manager
  - Regional Safety Manager
  - Social Media Manager
  - Assistant General Manager
  - Restaurant General Manager
  - Senior Business Development Manager
  - General Manager, Licensed Cosmetologist

### research_quant
- total_frequency: 268
- recommended_action: add_new_normalized_title
- proposed_role_family: data_science
- proposed_normalized_title: research_scientist
- rationale: Ruolo distinto e frequente in dataset tech/quant; valutare label dedicata se confermato su più run.
- sample_titles:
  - Quantitative Researcher
  - Machine Learning Researcher
  - UX Researcher
  - Cubist Quantitative Researcher
  - Senior UX Researcher
  - Market Microstructure Researcher
  - Security Researcher
  - Senior Researcher

### customer_service
- total_frequency: 113
- recommended_action: map_to_existing
- proposed_role_family: operations
- proposed_normalized_title: customer_service_specialist
- rationale: Cluster operativo service già introdotto; estendere varianti testuali.
- sample_titles:
  - Customer Service Representative
  - Bilingual Customer Service Representative
  - Senior Agent, Customer Service (Russian Speaker) - Willing to relocate to Kuala Lumpur, Malaysia
  - Full-Time Customer Service Representative
  - Customer Service Coordinator - Vehicle Delivery
  - Team Lead, Vendor Customer Service
  - Customer Service Supervisor
  - Customer Service Advisor

### technicians_skilled_trades
- total_frequency: 52
- recommended_action: map_to_existing
- proposed_role_family: skilled_trades
- proposed_normalized_title: technician
- rationale: Molti titoli possono essere assorbiti da technician/car_detailer/mechanic già in taxonomy.
- sample_titles:
  - Telematics Installer
  - HVAC Lead Installer (Relocation Offered!!!)
  - Quality Assurance Technician
  - Onsite POS Installer, Sr Associate
  - ADESA - Detailer
  - Auto Detailer - ADESA Lansing
  - Auto Detailer - ADESA Lexington
  - Auto Detailer - ADESA Orlando

### logistics_drivers
- total_frequency: 7
- recommended_action: map_to_existing
- proposed_role_family: logistics
- proposed_normalized_title: driver
- rationale: Driver/CDL cluster già standardizzabile con label esistenti.
- sample_titles:
  - Autonomous Vehicle Test Operator - CDL
  - Customer Support (Driver) Representative
  - Autonomous Vehicle Operator (Driver)
  - Autonomous Vehicle Test Operator - CDL & IT Specialist
  - CDL or Non CDL (Delivery Driver)

### project_program
- total_frequency: 2
- recommended_action: map_to_existing
- proposed_role_family: program_management
- proposed_normalized_title: project_manager
- rationale: Cluster già indirizzato dal pass precedente; mantenere come policy stabile.
- sample_titles:
  - Specialist Education Professional, Actimize(Content Developer, Project Manager)
  - Contractor Staffing Lead (Operations Program Manager)

## Implementation Pass v1 (Recommended)

1. Nursing/physician healthcare pack (`add_new_normalized_title`): Aggiungere registered_nurse (+ opzionale physician) in healthcare_clinical e relative regole RN/LPN/Primary Care Physician.
2. Mental health pack (`add_new_normalized_title`): Aggiungere mental_health_specialist in healthcare_clinical e regole therapist/intervention/behavioral/DSP.
3. Retail/store associate pack (`add_new_normalized_title`): Aggiungere store_associate in sales e mappare lead store associate / parts associate / stylist retail / lot attendant.
4. Manager policy hardening (`map_to_existing`): Business Development Manager -> account_manager; Social Media Manager -> marketing_specialist; General Manager resta other con reason esplicita.
5. Operations support pack (`map_to_existing`): Rental Coordinator e Case Manager -> operations_specialist; Payroll Specialist -> financial_analyst (finance).
6. Skilled trades variants pack (`map_to_existing`): Telematics Installer/Installer -> technician; Automotive Detailer/Lot Attendant -> car_detailer.
7. Project/program normalization closure (`map_to_existing`): Confermare Program Manager -> project_manager in modo stabile in tutte le varianti.
8. Research/quant decision gate (`add_new_normalized_title`): Valutare research_scientist in data_science solo se volume persistente su 2-3 run consecutivi.
