"""
Recommendation Generator Module

This module takes category weights and gap summaries to generate a prioritized
list of recommendations across all categories in a single LLM call.
"""

import json
import os
from typing import Dict, List, Any
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

try:
    from openai import OpenAI
except ImportError:
    raise ImportError("OpenAI package not installed. Run: pip install openai")

# Load environment variables
load_dotenv()


class RecommendationGenerator:
    """
    Generate prioritized recommendations from category weights and gap summaries.
    Uses a single LLM call to analyze all categories holistically.
    """
    
    def __init__(self, api_key: str = None, model: str = "gpt-4-turbo-preview"):
        """
        Initialize the RecommendationGenerator.
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: LLM model to use (default: gpt-4-turbo-preview for 128k context)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key must be provided or set in OPENAI_API_KEY environment variable")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        
    def load_weights(self, weights_path: str = None) -> Dict[str, float]:
        """
        Load category weights from file or use defaults.
        
        Args:
            weights_path: Path to category weights JSON file
            
        Returns:
            Dictionary of category weights
        """
        # Try to load from scoring module
        try:
            from main_orchestrator.scoring import ScoringAgent
            agent = ScoringAgent()
            weights = agent._load_weights()
            if weights:
                print("✓ Loaded category weights from user inputs")
                return weights
        except Exception as e:
            print(f"Could not load weights from ScoringAgent: {e}")
        
        # Try from file path if provided
        if weights_path and Path(weights_path).exists():
            try:
                with open(weights_path, 'r') as f:
                    weights = json.load(f)
                print(f"✓ Loaded category weights from {weights_path}")
                return weights
            except Exception as e:
                print(f"Error loading weights from {weights_path}: {e}")
        
        # Fall back to defaults
        from main_orchestrator.scoring import CATEGORY_WEIGHTS
        print("⚠️  Using default category weights")
        return CATEGORY_WEIGHTS
    
    def load_gap_summaries(self, summaries_path: str = None) -> Dict[str, Any]:
        """
        Load gap summaries from file.
        
        Args:
            summaries_path: Path to gap_summaries.json (defaults to results/gap_summaries.json)
            
        Returns:
            Dictionary containing gap summaries for all categories
        """
        if summaries_path is None:
            # Default to workspace results directory
            workspace_root = Path(__file__).parent.parent
            summaries_path = workspace_root / "results" / "gap_summaries.json"
        
        with open(summaries_path, 'r') as f:
            data = json.load(f)
        
        print(f"✓ Loaded gap summaries from {summaries_path}")
        return data
    
    def generate_consolidated_prompt(self, weights: Dict[str, float], 
                                     summaries: Dict[str, Any]) -> str:
        """
        Generate a single prompt that includes all categories with their weights and summaries.
        
        Args:
            weights: Dictionary of category weights
            summaries: Dictionary of gap summaries
            
        Returns:
            Formatted prompt string for the LLM
        """
        # Normalize weights to percentages
        total_weight = sum(weights.values())
        normalized_weights = {k: (v / total_weight * 100) for k, v in weights.items()}
        
        # Build the category analysis section
        categories_text = []
        for category, weight_pct in sorted(normalized_weights.items(), key=lambda x: x[1], reverse=True):
            summary_data = summaries.get(category, {})
            score = summary_data.get("score", 0.0)
            recommendation = summary_data.get("recommendation", "No recommendations available.")
            
            categories_text.append(f"""
### {category}
- **Weight:** {weight_pct:.1f}%
- **Current Score:** {score}/5.0
- **Gap Summary:**
{recommendation}
""")
        
        categories_section = "\n".join(categories_text)
        
        prompt = f"""You are an expert AI maturity consultant tasked with generating prioritized recommendations for an organization based on their AI maturity assessment.

## Assessment Overview

You have been provided with 15 categories of AI maturity, each with:
1. A strategic weight (representing organizational priority)
2. A current maturity score (0-5 scale)
3. A detailed gap analysis and recommendations

## Category Details (Sorted by Weight)

{categories_section}

## Your Task

Analyze the above categories holistically and generate **exactly 10 prioritized recommendations** that will have the maximum impact on the organization's AI maturity score and strategic goals.

## Prioritization Criteria

1. **Weight Impact:** Prioritize categories with higher strategic weights
2. **Score Gap:** Prioritize categories with lower scores (more room for improvement)
3. **Quick Wins:** Include some achievable recommendations for momentum
4. **Dependencies:** Consider recommendations that benefit multiple categories
5. **Strategic Value:** Focus on actions that align with high-weight categories

## Output Format

Provide your response as a valid JSON array with exactly 10 recommendations:

```json
[
  {{
    "rank": 1,
    "title": "Brief, actionable title",
    "description": "Detailed description of the recommendation (2-3 sentences)",
    "impact": "High/Medium/Low",
    "affected_categories": ["01. Technical Infrastructure", "03. AI/ML Capabilities"]
  }},
  {{
    "rank": 2,
    "title": "Another recommendation",
    "description": "Description...",
    "impact": "High/Medium/Low",
    "affected_categories": ["02. Data Management & Quality"]
  }}
]
```

## Important Guidelines

1. Return **exactly 10 recommendations** ranked by priority (1-10)
2. Each recommendation must list all affected categories
3. Ensure recommendations span multiple categories based on their weights
4. Balance quick wins with strategic long-term improvements
5. Provide specific, actionable recommendations (not generic advice)
6. Return ONLY valid JSON array (no markdown code blocks, no extra text, no wrapper objects)
7. Use the category weights provided to determine priority - higher weight categories should have more focus
8. Impact should be "High", "Medium", or "Low"

Generate the recommendations now:"""
        
        return prompt
    
    def call_llm(self, prompt: str) -> str:
        """
        Call the LLM API to generate recommendations.
        
        Args:
            prompt: The consolidated prompt
            
        Returns:
            Generated recommendations as JSON string
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert AI maturity consultant. You provide strategic, prioritized recommendations based on holistic analysis. Always respond with valid JSON array format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=3000
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error calling LLM API: {e}")
            raise
    
    def generate_recommendations(self, weights_path: str = None, 
                                summaries_path: str = None,
                                save_output: bool = True,
                                output_path: str = None) -> Dict[str, Any]:
        """
        Generate prioritized recommendations across all categories.
        
        Args:
            weights_path: Path to category weights file (optional)
            summaries_path: Path to gap summaries file (optional)
            save_output: Whether to save results to file (default: True)
            output_path: Custom output path (defaults to results/prioritized_recommendations.json)
            
        Returns:
            Dictionary containing prioritized recommendations in gap_summaries format
        """
        print("\n" + "=" * 80)
        print("RECOMMENDATION GENERATOR - Holistic Priority Analysis")
        print("=" * 80 + "\n")
        
        # Load inputs
        print("Loading category weights...")
        weights = self.load_weights(weights_path)
        
        print("Loading gap summaries...")
        summaries_path_resolved = summaries_path or (Path(__file__).parent.parent / "results" / "gap_summaries.json")
        summaries = self.load_gap_summaries(summaries_path)
        
        # Display weight distribution
        print("\n📊 Category Weight Distribution:")
        total_weight = sum(weights.values())
        for cat, weight in sorted(weights.items(), key=lambda x: x[1], reverse=True)[:5]:
            pct = (weight / total_weight * 100)
            print(f"  • {cat}: {pct:.1f}%")
        print("  ...")
        
        # Generate prompt
        print("\n🤖 Generating consolidated prompt...")
        prompt = self.generate_consolidated_prompt(weights, summaries)
        
        # Call LLM
        print(f"📡 Calling LLM ({self.model})...")
        response_text = self.call_llm(prompt)
        
        # Parse JSON response
        try:
            recommendations_array = json.loads(response_text)
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing LLM response as JSON: {e}")
            print(f"Response text: {response_text[:500]}...")
            raise
        
        result = {
            "Overall Prioritized Recommendations": {
                "recommendation": f"Generated {len(recommendations_array)} prioritized recommendations based on category weights and gap analysis.",
                "prioritized_actions": recommendations_array
            }
        }
        
        # Save output
        if save_output:
            if output_path is None:
                workspace_root = Path(__file__).parent.parent
                output_path = workspace_root / "results" / "prioritized_recommendations.json"
            
            with open(output_path, 'w') as f:
                json.dump(result, f, indent=2)
            
            print(f"\n✅ Recommendations saved to: {output_path}")
        
        # Print summary
        self._print_summary(result)
        
        return result
    
    def _print_summary(self, result: Dict[str, Any]):
        """Print a formatted summary of the recommendations."""
        print("\n" + "=" * 80)
        print("📋 RECOMMENDATION SUMMARY")
        print("=" * 80)
        
        overall_data = result.get("Overall Prioritized Recommendations", {})
        prioritized_actions = overall_data.get("prioritized_actions", [])
        
        print(f"\nTotal Recommendations: {len(prioritized_actions)}")
        
        # Count high impact recommendations
        high_impact_count = sum(1 for rec in prioritized_actions if rec.get("impact", "").lower() == "high")
        print(f"High Impact Recommendations: {high_impact_count}")
        
        # Count unique categories
        all_categories = set()
        for rec in prioritized_actions:
            all_categories.update(rec.get("affected_categories", []))
        print(f"Categories Addressed: {len(all_categories)}")
        
        if prioritized_actions:
            print(f"\n🎯 Top 3 Recommendations:")
            for rec in prioritized_actions[:3]:
                print(f"\n  {rec['rank']}. {rec['title']}")
                print(f"     Impact: {rec['impact']}")
                affected = rec.get('affected_categories', [])
                print(f"     Affects: {', '.join(affected[:2])}{'...' if len(affected) > 2 else ''}")
        
        print("\n" + "=" * 80)


def main():
    """
    Main execution function.
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate prioritized recommendations from category weights and gap summaries"
    )
    parser.add_argument("--api-key", help="OpenAI API key (or set OPENAI_API_KEY env var)")
    parser.add_argument("--model", default="gpt-4-turbo-preview", 
                       help="LLM model to use (default: gpt-4-turbo-preview)")
    parser.add_argument("--weights", help="Path to category weights JSON file")
    parser.add_argument("--summaries", help="Path to gap summaries JSON file")
    parser.add_argument("--no-save", action="store_true", help="Don't save output to file")
    
    args = parser.parse_args()
    
    try:
        generator = RecommendationGenerator(api_key=args.api_key, model=args.model)
        
        results = generator.generate_recommendations(
            weights_path=args.weights,
            summaries_path=args.summaries,
            save_output=not args.no_save
        )
        
        print("\n✅ Recommendation generation complete!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

