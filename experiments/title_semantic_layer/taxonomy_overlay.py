from __future__ import annotations


def get_semantic_taxonomy_overlay() -> dict[str, object]:
    # Experimental overlay used only by the semantic layer. It does not modify
    # the production taxonomy or classifier behavior.
    return {
        "existing_label_aliases": {
            "it_support_specialist": [
                "salesforce administrator",
                "senior salesforce administrator",
                "it administrator",
            ],
            "engineering_manager": [
                "software development manager",
            ],
            "manufacturing_engineer": [
                "production engineer",
            ],
            "electrical_engineer": [
                "fpga engineer",
            ],
            "solutions_architect": [
                "technical architect",
            ],
        },
        "proposed_new_labels": [
            {
                "normalized_title": "data_science_manager",
                "role_family": "data_science",
                "aliases": [
                    "data science manager",
                    "senior data science manager",
                    "manager data science",
                ],
                "status": "proposed_experimental",
                "rationale": "Managerial data science titles recur in residuals and have no clean internal target.",
            }
        ],
    }
