"""
Gap Summarizer Module

This module reads the clubbed_result.json file and uses an LLM to generate
actionable recommendation summaries for each of the 15 categories based on their gaps.
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


class GapSummarizer:
    """
    Generate LLM-based recommendation summaries from category gaps.
    """
    
    def __init__(self, api_key: str = None, model: str = "gpt-4-turbo-preview"):
        """
        Initialize the GapSummarizer.
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: LLM model to use (default: gpt-4-turbo-preview for 128k context)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key must be provided or set in OPENAI_API_KEY environment variable")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        
    def load_clubbed_results(self, file_path: str = None) -> Dict[str, Any]:
        """
        Load the clubbed_result.json file.
        
        Args:
            file_path: Path to clubbed_result.json (defaults to results/clubbed_result.json)
            
        Returns:
            Dictionary containing category data
        """
        if file_path is None:
            # Default to workspace results directory
            workspace_root = Path(__file__).parent.parent
            file_path = workspace_root / "results" / "clubbed_result.json"
        
        with open(file_path, 'r') as f:
            return json.load(f)
    
    def generate_summary_prompt(self, category_name: str, score: float, 
                               gaps: List[str], subsections: List[str]) -> str:
        """
        Generate the prompt for the LLM to create a recommendation summary.
        
        Args:
            category_name: Name of the category
            score: Current category score
            gaps: List of gaps/recommendations
            subsections: List of subsections in the category
            
        Returns:
            Formatted prompt string
        """
        gaps_text = "\n".join([f"{i+1}. {gap}" for i, gap in enumerate(gaps)])
        subsections_text = "\n".join(subsections)
        
        prompt = f"""You are an AI maturity assessment expert. Analyze the following category and provide a concise, actionable recommendation summary.

**Category:** {category_name}
**Current Score:** {score}/5.0
**Subsections:**
{subsections_text}

**Identified Gaps & Recommendations:**
{gaps_text if gaps else "No specific gaps identified."}

**Task:**
Generate a concise executive summary (150-250 words) that:
1. Summarizes the key themes across the gaps
2. Prioritizes the top 3-5 most impactful actions
3. Provides specific, actionable recommendations
4. Highlights potential score improvements if implemented
5. Groups similar recommendations together
6. Uses clear, business-oriented language

**Output Format:**
Provide a well-structured summary with:
- A brief overview paragraph
- Priority recommendations (numbered list)
- Expected impact on score improvement

Keep the tone professional and actionable."""
        
        return prompt
    
    def call_llm(self, prompt: str) -> str:
        """
        Call the LLM API to generate a summary.
        
        Args:
            prompt: The prompt to send to the LLM
            
        Returns:
            Generated summary text
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an AI maturity assessment expert specializing in generating actionable recommendations from gap analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error calling LLM API: {e}")
            return f"Error generating summary: {str(e)}"
    
    def summarize_category(self, category_name: str, category_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a summary for a single category.
        
        Args:
            category_name: Name of the category
            category_data: Dictionary containing score, gaps, and subsections
            
        Returns:
            Dictionary with category summary information (matching clubbed_result format)
        """
        score = category_data.get("score", 0.0)
        gaps = category_data.get("gaps", [])
        subsections = category_data.get("subsections", [])
        
        # Limit gaps to avoid token limit issues with gpt-4 (16k context)
        # Process Maturity has 685 gaps which exceeds token limit
        # max_gaps = 50
        # if len(gaps) > max_gaps:
        #     print(f"⚠️  {category_name} has {len(gaps)} gaps, truncating to {max_gaps}")
        #     gaps = gaps[:max_gaps]
        
        print(f"Generating summary for: {category_name} (Score: {score}, Gaps: {len(gaps)})")
        
        if not gaps:
            recommendation = f"No specific gaps identified for {category_name}. The category currently has no actionable recommendations."
        else:
            prompt = self.generate_summary_prompt(category_name, score, gaps, subsections)
            recommendation = self.call_llm(prompt)
            print(recommendation)
        
        return {
            "score": score,
            "recommendation": recommendation,
            "subsections": subsections
        }
    
    def summarize_all_categories(self, save_output: bool = True, 
                                 output_path: str = None) -> Dict[str, Any]:
        """
        Generate summaries for all 15 categories.
        
        Args:
            save_output: Whether to save results to file (default: True)
            output_path: Custom output path (defaults to results/gap_summaries.json)
            
        Returns:
            Dictionary containing all category summaries (matching clubbed_result format)
        """
        print("Loading clubbed results...")
        clubbed_data = self.load_clubbed_results()
        
        summaries = {}
        total_categories = len(clubbed_data)
        
        print(f"Processing {total_categories} categories...\n")
        
        for idx, (category_name, category_data) in enumerate(clubbed_data.items(), 1):
            print(f"[{idx}/{total_categories}] Processing: {category_name}")
            summary = self.summarize_category(category_name, category_data)
            summaries[category_name] = summary
            print(f"✓ Completed {category_name}\n")
        
        if save_output:
            if output_path is None:
                workspace_root = Path(__file__).parent.parent
                output_path = workspace_root / "results" / "gap_summaries.json"
            
            with open(output_path, 'w') as f:
                json.dump(summaries, f, indent=2)
            
            print(f"\n✅ Summaries saved to: {output_path}")
        
        return summaries


def main():
    """
    Main execution function.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate LLM-based gap summaries from clubbed results")
    parser.add_argument("--api-key", help="OpenAI API key (or set OPENAI_API_KEY env var)")
    parser.add_argument("--model", default="gpt-4", help="LLM model to use (default: gpt-4)")
    parser.add_argument("--no-save", action="store_true", help="Don't save output to file")
    parser.add_argument("--markdown", action="store_true", help="Also generate markdown report")
    
    args = parser.parse_args()
    
    try:
        summarizer = GapSummarizer(api_key=args.api_key, model=args.model)
        
        print("=" * 80)
        print("GAP SUMMARIZER - LLM-Based Recommendation Generator")
        print("=" * 80)
        print()
        
        results = summarizer.summarize_all_categories(save_output=not args.no_save)
        
        print("\n" + "=" * 80)
        print("✅ Gap summarization complete!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

