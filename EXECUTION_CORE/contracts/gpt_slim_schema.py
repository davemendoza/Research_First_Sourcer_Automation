"""
AI Talent Engine — GPT Slim Schema Contract
© 2026 L. David Mendoza

Purpose:
Minimal, determinative-only column set for GPT-based
evaluation, ranking, and hiring recommendation.

Derived strictly from:
AI_Talent_Engine_Canonical_People_Schema_LOCKED_82
"""

GPT_SLIM_COLUMNS = [
    # Identity
    "Person_ID",
    "Full_Name",
    "Current_Title",
    "Current_Company",

    # Role framing
    "Role_Type",
    "AI_Classification",

    # Core determinative skills
    "Primary_Model_Families",
    "Training_or_Alignment_Methods",
    "Systems_or_Retrieval_Architectures",
    "Inference_or_Deployment_Signals",

    # Evidence artifacts
    "GitHub_URL",
    "GitHub_IO_URL",
    "Resume_URL",
    "Google_Scholar_URL",
    "Personal_Website",

    # Research & impact
    "Determinative_Skill_Areas",
    "Benchmarks_Worked_On",
    "Publication_Count",
    "Citation_Count_Raw",
    "Citation_Velocity_3yr",
    "h_index",

    # Ownership & proof
    "GitHub_Repo_Evidence_Why",
    "Repo_Topics_Keywords",
    "Downstream_Adoption_Signal",

    # Narrative synthesis
    "Strengths",
    "Weaknesses",
    "Hiring_Manager_Summary"
]

GPT_SLIM_COLUMN_COUNT = len(GPT_SLIM_COLUMNS)
