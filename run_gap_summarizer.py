# #!/usr/bin/env python3
# """
# Simple CLI script to run the Gap Summarizer.

# Usage:
#     python run_gap_summarizer.py
    
# Make sure to set OPENAI_API_KEY environment variable before running.
# """

# import sys
# import os
# from pathlib import Path

# # Add the project root to the Python path
# project_root = Path(__file__).parent
# sys.path.insert(0, str(project_root))

# from main_orchestrator.gap_summarizer import GapSummarizer


# def main():
#     """
#     Run the gap summarizer with default settings.
#     """
#     print("=" * 80)
#     print("AI Maturity Gap Summarizer")
#     print("=" * 80)
#     print()
    
#     # Check for API key
#     api_key = os.getenv("OPENAI_API_KEY")
#     if not api_key:
#         print("❌ Error: OPENAI_API_KEY environment variable not set!")
#         print()
#         print("Please set your OpenAI API key:")
#         print("  export OPENAI_API_KEY='your-api-key-here'")
#         print()
#         sys.exit(1)
    
#     try:
#         # Initialize summarizer
#         print("Initializing Gap Summarizer...")
#         summarizer = GapSummarizer(model="gpt-4-turbo-preview")  # 128k context for large gap lists
        
#         # Generate summaries
#         print("\nGenerating recommendation summaries for all categories...")
#         print("This may take a few minutes...\n")
        
#         results = summarizer.summarize_all_categories(save_output=True)
        
#         # Generate markdown report
#         print("\nGenerating markdown report...")
#         summarizer.generate_markdown_report(results)
        
#         print("\n" + "=" * 80)
#         print("✅ SUCCESS!")
#         print("=" * 80)
#         print("\nGenerated files:")
#         print(f"  - JSON: {project_root}/results/gap_summaries.json")
#         print(f"  - Markdown: {project_root}/results/gap_summaries.md")
#         print()
        
#     except Exception as e:
#         print(f"\n❌ Error occurred: {e}")
#         import traceback
#         traceback.print_exc()
#         sys.exit(1)


# if __name__ == "__main__":
#     main()

