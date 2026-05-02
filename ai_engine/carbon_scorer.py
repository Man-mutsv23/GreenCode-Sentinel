"""
Carbon scoring logic and CO2 estimation.
"""
from typing import Dict, List, Any

class CarbonScorer:
    """Carbon scoring and CO2 estimation for code analysis."""

    # This matrix MUST be inside the class and defined before methods
    CO2_SAVINGS_MATRIX = {
        "loops": {"critical": 500, "high": 200, "medium": 80, "low": 30},
        "memory": {"critical": 300, "high": 120, "medium": 50, "low": 20},
        "network": {"critical": 250, "high": 100, "medium": 40, "low": 15},
        "complexity": {"critical": 180, "high": 90, "medium": 40, "low": 12},
        "other": {"critical": 200, "high": 80, "medium": 30, "low": 10}
    }

    def calculate_score(self, analysis: dict) -> dict:
        issues = analysis.get("issues", [])
        
        # Reduced penalties so 12 issues doesn't automatically mean 0.0
        score = 100.0
        severity_weights = {"critical": 8.0, "high": 5.0, "medium": 3.0, "low": 1.0}
        
        counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        category_hits = {"loops": 0, "memory": 0, "network": 0, "complexity": 0}
        
        for issue in issues:
            sev = issue.get("severity", "medium").lower()
            # Normalize category name to match our UI badges
            cat = issue.get("type", issue.get("category", "complexity")).lower()
            if cat not in category_hits: cat = "complexity"
            
            counts[sev] = counts.get(sev, 0) + 1
            category_hits[cat] = category_hits.get(cat, 0) + 1
            score -= severity_weights.get(sev, 2.0)
            
        score = max(5.0, min(100.0, score)) # Cap floor at 5.0 for better UX

        # Determine Grade
        if score >= 90: grade = "A+"
        elif score >= 80: grade = "B"
        elif score >= 70: grade = "C"
        elif score >= 60: grade = "D"
        else: grade = "F"

        # Calculate CO2 savings using the Matrix
        co2_savings_g_day = self._calculate_co2_savings(issues)
        kg_year = (co2_savings_g_day * 365) / 1000

        return {
            "score": round(score, 1),
            "grade": grade,
            "category_scores": {k: max(10, 100 - (v * 15)) for k, v in category_hits.items()},
            "total_issues": len(issues),
            "critical_issues": counts["critical"],
            "high_issues": counts["high"],
            "medium_issues": counts["medium"],
            "low_issues": counts["low"],
            "co2_savings_kg_year": round(kg_year, 2),
            "co2_savings_tons_year": round(kg_year / 1000, 4),
            "summary": f"Detected {len(issues)} sustainability leaks."
        }

    def _calculate_co2_savings(self, issues: List[Dict[str, Any]]) -> float:
        total_savings = 0.0
        for issue in issues:
            # Check for 'type' or 'category' to be robust
            issue_type = issue.get("type", issue.get("category", "other")).lower()
            severity = issue.get("severity", "medium").lower()
            
            # Accessing via Class Name fixes the BasedPyright linter error
            matrix = CarbonScorer.CO2_SAVINGS_MATRIX
            
            if issue_type in matrix:
                savings = matrix[issue_type].get(severity, 0)
            else:
                savings = matrix["other"].get(severity, 0)
            
            total_savings += savings
        return total_savings