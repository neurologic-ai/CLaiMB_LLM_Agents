# """
# Simple runner script for the Recommendation Generator.

# Usage:
#     python run_recommendations.py
#     python run_recommendations.py --model gpt-4o
# """

# from main_orchestrator.recommendation_generator import RecommendationGenerator


# def main():
#     """Run the recommendation generator with default settings."""
#     import argparse
    
#     parser = argparse.ArgumentParser(
#         description="Generate prioritized recommendations from category weights and gap summaries"
#     )
#     parser.add_argument(
#         "--model", 
#         default="gpt-4-turbo-preview",
#         help="LLM model to use (default: gpt-4-turbo-preview)"
#     )
#     parser.add_argument(
#         "--weights",
#         help="Path to custom category weights JSON file"
#     )
#     parser.add_argument(
#         "--summaries",
#         help="Path to custom gap summaries JSON file"
#     )
    
#     args = parser.parse_args()
    
#     try:
#         # Initialize generator
#         print("Initializing Recommendation Generator...")
#         generator = RecommendationGenerator(model=args.model)
        
#         # Generate recommendations
#         results = generator.generate_recommendations(
#             weights_path=args.weights,
#             summaries_path=args.summaries,
#             save_output=True
#         )
        
#         print("\n" + "=" * 80)
#         print("🎉 SUCCESS! Check results/prioritized_recommendations.json for output")
#         print("=" * 80)
        
#     except FileNotFoundError as e:
#         print(f"\n❌ File not found: {e}")
#         print("\nMake sure you have:")
#         print("  1. results/gap_summaries.json (run gap summarizer first)")
#         print("  2. Category weights configured or using defaults")
        
#     except Exception as e:
#         print(f"\n❌ Error: {e}")
#         import traceback
#         traceback.print_exc()


# if __name__ == "__main__":
#     main()
