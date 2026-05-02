"""
Carbon scoring logic and CO2 estimation.
Converts AI analysis into sustainability scores and environmental impact metrics.
"""

from typing import Dict, List, Any
import json


class CarbonScorer:
    """Calculate sustainability scores and CO2 savings from code analysis."""
    
    # Penalty weights for different issue categories
    CATEGORY_WEIGHTS = {
        "loops": 0.40,      # 40% - Loop efficiency
        "memory": 0.30,     # 30% - Memory usage
        "network": 0.20,    # 20% - API/Network calls
        "complexity": 0.10  # 10% - Code complexity
    }
    
    # Severity multipliers
    SEVERITY_MULTIPLIERS = {
        "Critical": 1.0,
        "High": 0.7,
        "Medium": 0.4,
        "Low": 0.2
    }
    
    # CO2 estimation constants
    # Based on average cloud infrastructure energy consumption
    CPU_CYCLE_REDUCTION_FACTOR = 0.5    # kg CO2 per year per optimization
    MEMORY_REDUCTION_FACTOR = 0.3       # kg CO2 per year per MB saved
    NETWORK_REDUCTION_FACTOR = 0.2      # kg CO2 per year per API call eliminated
    CLOUD_CARBON_INTENSITY = 0.000379   # kg CO2 per kWh (AWS average)
    USAGE_FACTOR = 1000                 # Estimated executions per year
    
    def __init__(self):
        """Initialize the carbon scorer."""
        pass
    
    def calculate_score(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate sustainability score from AI analysis.
        
        Args:
            analysis: Parsed analysis from watsonx.ai containing issues list
            
        Returns:
            Dictionary with score, breakdown, and CO2 estimates
        """
        issues = analysis.get("issues", [])
        
        if not issues:
            # Perfect score if no issues found
            return {
                "score": 100,
                "grade": "A+",
                "category_scores": {
                    "loops": 100,
                    "memory": 100,
                    "network": 100,
                    "complexity": 100
                },
                "total_issues": 0,
                "co2_savings_kg_year": 0.0,
                "summary": analysis.get("summary", "No issues detected. Code is optimized!")
            }
        
        # Calculate penalties by category
        category_penalties = self._calculate_category_penalties(issues)
        
        # Calculate weighted total penalty
        total_penalty = sum(
            category_penalties[cat] * self.CATEGORY_WEIGHTS[cat]
            for cat in self.CATEGORY_WEIGHTS
        )
        
        # Calculate final score (0-100)
        score = max(0, min(100, 100 - total_penalty))
        
        # Calculate category scores
        category_scores = {
            cat: max(0, min(100, 100 - category_penalties[cat]))
            for cat in self.CATEGORY_WEIGHTS
        }
        
        # Estimate CO2 savings
        co2_savings = self._estimate_co2_savings(issues)
        
        # Determine grade
        grade = self._calculate_grade(score)
        
        return {
            "score": round(score, 1),
            "grade": grade,
            "category_scores": {k: round(v, 1) for k, v in category_scores.items()},
            "total_issues": len(issues),
            "critical_issues": sum(1 for i in issues if i.get("severity") == "Critical"),
            "high_issues": sum(1 for i in issues if i.get("severity") == "High"),
            "medium_issues": sum(1 for i in issues if i.get("severity") == "Medium"),
            "low_issues": sum(1 for i in issues if i.get("severity") == "Low"),
            "co2_savings_kg_year": round(co2_savings, 2),
            "co2_savings_tons_year": round(co2_savings / 1000, 4),
            "summary": analysis.get("summary", "Analysis complete")
        }
    
    def _calculate_category_penalties(self, issues: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Calculate penalty points for each category.
        
        Args:
            issues: List of issues from analysis
            
        Returns:
            Dictionary mapping category to penalty points
        """
        penalties = {cat: 0.0 for cat in self.CATEGORY_WEIGHTS}
        
        for issue in issues:
            category = issue.get("category", "complexity").lower()
            severity = issue.get("severity", "Medium")
            
            # Map category to standard categories
            if category not in penalties:
                # Try to infer category from description
                description = issue.get("description", "").lower()
                if "loop" in description or "iteration" in description:
                    category = "loops"
                elif "memory" in description or "allocation" in description:
                    category = "memory"
                elif "api" in description or "network" in description or "call" in description:
                    category = "network"
                else:
                    category = "complexity"
            
            # Calculate penalty for this issue
            base_penalty = 15  # Base penalty per issue
            severity_multiplier = self.SEVERITY_MULTIPLIERS.get(severity, 0.4)
            issue_penalty = base_penalty * severity_multiplier
            
            penalties[category] += issue_penalty
        
        return penalties
    
    def _estimate_co2_savings(self, issues: List[Dict[str, Any]]) -> float:
        """
        Estimate CO2 savings if all issues are fixed.
        
        Args:
            issues: List of issues from analysis
            
        Returns:
            Estimated CO2 savings in kg per year
        """
        total_savings = 0.0
        
        for issue in issues:
            category = issue.get("category", "complexity").lower()
            severity = issue.get("severity", "Medium")
            severity_multiplier = self.SEVERITY_MULTIPLIERS.get(severity, 0.4)
            
            # Estimate savings based on category
            if "loop" in category:
                # CPU cycle reduction
                savings = self.CPU_CYCLE_REDUCTION_FACTOR * severity_multiplier * self.USAGE_FACTOR
            elif "memory" in category:
                # Memory reduction (assume 10MB average per issue)
                savings = self.MEMORY_REDUCTION_FACTOR * 10 * severity_multiplier * self.USAGE_FACTOR
            elif "network" in category:
                # Network call reduction
                savings = self.NETWORK_REDUCTION_FACTOR * severity_multiplier * self.USAGE_FACTOR
            else:
                # Complexity reduction (general CPU savings)
                savings = self.CPU_CYCLE_REDUCTION_FACTOR * 0.5 * severity_multiplier * self.USAGE_FACTOR
            
            total_savings += savings
        
        return total_savings
    
    def _calculate_grade(self, score: float) -> str:
        """
        Convert numerical score to letter grade.
        
        Args:
            score: Sustainability score (0-100)
            
        Returns:
            Letter grade (A+ to F)
        """
        if score >= 95:
            return "A+"
        elif score >= 90:
            return "A"
        elif score >= 85:
            return "A-"
        elif score >= 80:
            return "B+"
        elif score >= 75:
            return "B"
        elif score >= 70:
            return "B-"
        elif score >= 65:
            return "C+"
        elif score >= 60:
            return "C"
        elif score >= 55:
            return "C-"
        elif score >= 50:
            return "D"
        else:
            return "F"
    
    def format_results(self, results: Dict[str, Any]) -> str:
        """
        Format scoring results as human-readable text.
        
        Args:
            results: Results from calculate_score()
            
        Returns:
            Formatted string
        """
        output = []
        output.append("=" * 60)
        output.append("GREENCODE SENTINEL - SUSTAINABILITY REPORT")
        output.append("=" * 60)
        output.append(f"\nOverall Score: {results['score']}/100 (Grade: {results['grade']})")
        output.append(f"\nTotal Issues Found: {results['total_issues']}")
        
        if results['total_issues'] > 0:
            output.append(f"  - Critical: {results['critical_issues']}")
            output.append(f"  - High: {results['high_issues']}")
            output.append(f"  - Medium: {results['medium_issues']}")
            output.append(f"  - Low: {results['low_issues']}")
        
        output.append("\nCategory Breakdown:")
        for category, score in results['category_scores'].items():
            output.append(f"  - {category.capitalize()}: {score}/100")
        
        output.append(f"\nEstimated CO₂ Savings (if optimized):")
        output.append(f"  - {results['co2_savings_kg_year']} kg/year")
        output.append(f"  - {results['co2_savings_tons_year']} tons/year")
        
        output.append(f"\nSummary: {results['summary']}")
        output.append("=" * 60)
        
        return "\n".join(output)

# Made with Bob
