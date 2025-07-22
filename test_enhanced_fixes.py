#!/usr/bin/env python3
"""
Test script to demonstrate enhanced AI code review with detailed fixes.
"""

import asyncio
import os
from ai_code_reviewer.ai_code_reviewer import AICodeReviewer

# Sample code with multiple issues for testing
SAMPLE_DIFF_WITH_ISSUES = """diff --git a/security-test.js b/security-test.js
new file mode 100644
index 0000000..1234567
--- /dev/null
+++ b/security-test.js
@@ -0,0 +1,25 @@
+// Test file with intentional security and performance issues
+const express = require('express');
+const app = express();
+
+// Hardcoded credentials (CRITICAL security issue)
+const API_KEY = "sk-1234567890abcdef";
+const DB_PASSWORD = "admin123";
+
+app.get('/user/:id', (req, res) => {
+    const userId = req.params.id;
+
+    // SQL injection vulnerability (CRITICAL)
+    const query = `SELECT * FROM users WHERE id = ${userId}`;
+
+    // Poor error handling (MAJOR)
+    try {
+        const result = db.query(query);
+        res.json(result);
+    } catch (err) {
+        // Empty catch block
+    }
+});
+
+// Inefficient algorithm (MINOR performance issue)
+function findDuplicates(arr) {
+    const duplicates = [];
+    for (let i = 0; i < arr.length; i++) {
+        for (let j = i + 1; j < arr.length; j++) {
+            if (arr[i] === arr[j] && !duplicates.includes(arr[i])) {
+                duplicates.push(arr[i]);
+            }
+        }
+    }
+    return duplicates;
+}
+
+// Missing input validation (MAJOR)
+app.post('/data', (req, res) => {
+    const data = req.body;
+    processData(data); // No validation!
+    res.send('OK');
+});"""

async def test_enhanced_ai_review():
    """Test the enhanced AI review with fix suggestions."""
    print("🧪 Testing Enhanced AI Code Review with Fixes")
    print("=" * 50)

    # Check if we have an API key
    if not (os.getenv('OPENROUTER_API_KEY') or os.getenv('ANTHROPIC_API_KEY') or os.getenv('OPENAI_API_KEY')):
        print("❌ No AI provider API key found!")
        print("Set one of: OPENROUTER_API_KEY, ANTHROPIC_API_KEY, or OPENAI_API_KEY")
        return

    try:
        # Initialize reviewer
        print("🔧 Initializing AI reviewer...")
        reviewer = AICodeReviewer()

        # Set context for better analysis
        context = {
            'language': 'javascript',
            'project_type': 'nodejs'
        }

        print(f"🎯 Using provider: {reviewer.primary_provider}")
        print("🔍 Analyzing code with intentional issues...")

        # Perform review
        reviews = await reviewer.review_diff(SAMPLE_DIFF_WITH_ISSUES, context)

        # Display results
        if reviews:
            print(f"\n✅ AI Review Complete! Found {len(reviews)} issues:")
            print("=" * 60)

            for i, review in enumerate(reviews, 1):
                emoji = {'critical': '🔴', 'major': '🟠', 'minor': '🟡', 'info': 'ℹ️'}[review.severity]
                confidence_emoji = {'high': '🎯', 'medium': '🤔', 'low': '❓'}.get(review.confidence, '🤔')

                print(f"\n{i}. {emoji} **{review.severity.upper()}** - {review.category} {confidence_emoji}")
                print(f"📄 File: {review.file} (Lines {review.line_start}-{review.line_end})")
                print(f"💬 Issue: {review.message}")

                if review.impact:
                    print(f"⚠️ Impact: {review.impact}")

                if review.suggestion:
                    print(f"💡 Suggestion: {review.suggestion}")

                if review.fixed_code:
                    print(f"\n✅ Fixed Code:")
                    print("```")
                    print(review.fixed_code)
                    print("```")

                if review.confidence:
                    print(f"🎯 Confidence: {review.confidence}")

                print("-" * 60)

            # Test report generation
            from ai_code_reviewer.ai_code_reviewer import CodeQualityEnforcer
            enforcer = CodeQualityEnforcer()

            print("\n📄 Generating Enhanced Markdown Report...")
            report = enforcer.generate_report(reviews, "markdown")

            # Save report to file
            with open("enhanced-review-results.md", "w") as f:
                f.write(report)

            print("✅ Enhanced report saved to: enhanced-review-results.md")

            # Show summary
            severity_counts = {'critical': 0, 'major': 0, 'minor': 0, 'info': 0}
            for review in reviews:
                severity_counts[review.severity] = severity_counts.get(review.severity, 0) + 1

            print(f"\n📊 Summary:")
            print(f"- 🔴 Critical: {severity_counts['critical']}")
            print(f"- 🟠 Major: {severity_counts['major']}")
            print(f"- 🟡 Minor: {severity_counts['minor']}")
            print(f"- ℹ️ Info: {severity_counts['info']}")

        else:
            print("❌ No issues found or review failed")

    except Exception as e:
        print(f"❌ Test failed: {e}")

def main():
    """Run the enhanced AI review test."""
    print("🤖 Enhanced AI Code Review Test")
    print("This test demonstrates the new features:")
    print("- Detailed fix suggestions")
    print("- Actual corrected code snippets")
    print("- Impact assessment")
    print("- Confidence levels")
    print("- Enhanced markdown reports")
    print()

    asyncio.run(test_enhanced_ai_review())

if __name__ == "__main__":
    main()