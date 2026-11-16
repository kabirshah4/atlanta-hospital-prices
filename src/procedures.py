"""The procedures we compare: common, shoppable services people can plan ahead for.

Outpatient services are identified by CPT/HCPCS code. Inpatient stays (childbirth,
joint replacement) are billed as a whole case under an MS-DRG code.
"""

PROCEDURES = [
    # code, code_system, plain-English name, category, search keywords
    ("70553", "CPT", "Brain MRI (with and without contrast)", "Imaging", "mri brain head scan"),
    ("70551", "CPT", "Brain MRI (no contrast)", "Imaging", "mri brain head scan"),
    ("73721", "CPT", "Knee/leg joint MRI (no contrast)", "Imaging", "mri knee joint leg ankle hip"),
    ("72148", "CPT", "Lower back MRI (no contrast)", "Imaging", "mri back spine lumbar"),
    ("74177", "CPT", "CT scan of abdomen and pelvis (with contrast)", "Imaging", "ct cat scan belly stomach abdomen pelvis"),
    ("70450", "CPT", "CT scan of head (no contrast)", "Imaging", "ct cat scan head brain"),
    ("71250", "CPT", "CT scan of chest (no contrast)", "Imaging", "ct cat scan chest lungs"),
    ("77067", "CPT", "Screening mammogram", "Imaging", "mammogram breast screening"),
    ("76700", "CPT", "Abdominal ultrasound", "Imaging", "ultrasound sonogram belly abdomen"),
    ("76805", "CPT", "Pregnancy ultrasound", "Imaging", "ultrasound sonogram pregnancy prenatal ob"),
    ("71046", "CPT", "Chest X-ray (2 views)", "Imaging", "xray x-ray chest lungs"),
    ("93306", "CPT", "Echocardiogram (heart ultrasound)", "Imaging", "echo heart ultrasound echocardiogram"),
    ("93000", "CPT", "Electrocardiogram (ECG/EKG)", "Tests", "ekg ecg heart rhythm"),
    ("80053", "CPT", "Comprehensive metabolic panel (blood test)", "Lab", "blood test cmp metabolic"),
    ("85025", "CPT", "Complete blood count (CBC)", "Lab", "blood test cbc count"),
    ("80061", "CPT", "Cholesterol (lipid) panel", "Lab", "blood test cholesterol lipid"),
    ("84443", "CPT", "Thyroid test (TSH)", "Lab", "blood test thyroid tsh"),
    ("45378", "CPT", "Colonoscopy (diagnostic)", "Procedures", "colonoscopy colon scope"),
    ("45380", "CPT", "Colonoscopy with biopsy", "Procedures", "colonoscopy colon scope biopsy"),
    ("43239", "CPT", "Upper endoscopy with biopsy", "Procedures", "endoscopy egd stomach scope"),
    ("66984", "CPT", "Cataract surgery", "Surgery", "cataract eye lens surgery"),
    ("29881", "CPT", "Knee arthroscopy (meniscus repair)", "Surgery", "knee arthroscopy meniscus scope surgery"),
    ("47562", "CPT", "Gallbladder removal (laparoscopic)", "Surgery", "gallbladder cholecystectomy surgery"),
    ("49505", "CPT", "Inguinal hernia repair", "Surgery", "hernia repair surgery groin"),
    ("99283", "CPT", "ER visit (moderate)", "Emergency", "er emergency room visit"),
    ("99284", "CPT", "ER visit (serious)", "Emergency", "er emergency room visit"),
    ("99285", "CPT", "ER visit (severe)", "Emergency", "er emergency room visit"),
    ("97110", "CPT", "Physical therapy (therapeutic exercise, 15 min)", "Therapy", "physical therapy pt rehab"),
    ("807", "MS-DRG", "Vaginal childbirth (no complications)", "Inpatient", "birth baby delivery childbirth labor pregnancy"),
    ("788", "MS-DRG", "C-section birth (no complications)", "Inpatient", "c-section cesarean birth baby delivery"),
    ("470", "MS-DRG", "Hip or knee replacement", "Inpatient", "knee hip replacement joint surgery"),
]

CODES = {p[0] for p in PROCEDURES}
