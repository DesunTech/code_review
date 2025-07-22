#!/usr/bin/env python3
"""
Demo script to show the multi-provider AI code review system.
This demonstrates automatic provider detection and fallback functionality.
"""

import os
import asyncio
from ai_code_reviewer import AICodeReviewer

# Sample code diff to review
SAMPLE_DIFF = """
+def calculate_user_score(user_id):
+    user = db.query(f"SELECT * FROM users WHERE id = {user_id}")
+    score = 0
+    for i in range(len(user.purchases)):
+        for j in range(len(user.purchases)):
+            if user.purchases[i].amount > user.purchases[j].amount:
+                score = score + 1
+    return score
+
+def process_payment(card_number, password):
+    api_key = "sk-1234567890abcdef"
+    if card_number == "":
+        return None
+    # Process payment logic here
+    return True
"""

async def demo_provider_selection():
    """Demonstrate the provider selection and fallback system."""
    print("🚀 AI Code Review Multi-Provider Demo")
    print("=" * 50)

    # Demo 1: Auto-detection
    print("\n📍 Demo 1: Auto-detection of available providers")
    try:
        reviewer = AICodeReviewer()
        print(f"✅ Auto-selected provider setup successful!")

        # Show which providers were detected
        print(f"\n🔍 Available providers: {reviewer.available_providers}")
        print(f"🎯 Primary provider: {reviewer.primary_provider}")
        print(f"🔄 Fallback providers: {reviewer.fallback_providers}")

    except Exception as e:
        print(f"❌ No providers available: {e}")
        print("\n💡 To set up providers:")
        print("export ANTHROPIC_API_KEY='your-claude-key'")
        print("export OPENAI_API_KEY='your-openai-key'")
        print("export OPENROUTER_API_KEY='your-openrouter-key'")
        return

    # Demo 2: Manual provider selection
    print("\n📍 Demo 2: Manual provider selection")
    try:
        if 'claude' in reviewer.available_providers:
            claude_reviewer = AICodeReviewer(primary_provider='claude')
            print("✅ Claude selected as primary provider")
        elif 'openai' in reviewer.available_providers:
            openai_reviewer = AICodeReviewer(primary_provider='openai')
            print("✅ OpenAI selected as primary provider")
        else:
            print("⚠️ No major providers available for manual selection demo")
    except Exception as e:
        print(f"❌ Manual selection failed: {e}")

    # Demo 3: Code review with fallback
    print("\n📍 Demo 3: Code review with provider fallback")
    print("Reviewing sample code with potential issues...")

    try:
        context = {
            'language': 'python',
            'project_type': 'web-api'
        }

        reviews = await reviewer.review_diff(SAMPLE_DIFF, context)

        if reviews:
            print(f"\n✅ Review completed! Found {len(reviews)} issues:")
            for i, review in enumerate(reviews[:3], 1):  # Show first 3 issues
                print(f"\n{i}. {review.severity.upper()} - {review.category}")
                print(f"   📄 {review.file} (lines {review.line_start}-{review.line_end})")
                print(f"   💬 {review.message}")
                if review.suggestion:
                    print(f"   💡 Suggestion: {review.suggestion}")
        else:
            print("⚠️ No issues found or review failed")

    except Exception as e:
        print(f"❌ Review failed: {e}")

def demo_cli_usage():
    """Show CLI usage examples."""
    print("\n📍 CLI Usage Examples")
    print("=" * 30)

    print("\n🔍 List available providers:")
    print("python ai_code_reviewer.py --list-providers")

    print("\n🎯 Specify primary provider:")
    print("python ai_code_reviewer.py --provider claude --base main --head HEAD")
    print("python ai_code_reviewer.py --provider openai --base main --head HEAD")
    print("python ai_code_reviewer.py --provider openrouter --base main --head HEAD")

    print("\n🔄 Set fallback providers:")
    print("python ai_code_reviewer.py --provider claude --fallback-providers openai local")

    print("\n🤖 Auto-select best available:")
    print("python ai_code_reviewer.py --provider auto  # (default)")

    print("\n📊 Generate reports:")
    print("python ai_code_reviewer.py --output json --save-report review.json")
    print("python ai_code_reviewer.py --fail-on critical --language python")

if __name__ == "__main__":
    print("🎉 Multi-Provider AI Code Review System")
    print("This system automatically detects and uses available AI providers")
    print("with intelligent fallback support!\n")

    # Show CLI examples first
    demo_cli_usage()

    # Run async demo
    print("\n" + "=" * 60)
    asyncio.run(demo_provider_selection())

    print("\n" + "=" * 60)
    print("✨ Demo completed! The system is ready for production use.")
    print("\n💡 Pro tips:")
    print("- Set multiple API keys for best reliability")
    print("- Use --provider auto for intelligent selection")
    print("- Local models (Ollama) work great for private codebases")
    print("- OpenRouter provides access to many models with one API key")