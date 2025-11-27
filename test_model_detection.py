#!/usr/bin/env python3
"""
Test Model-Specific AI Detection Patterns

This script demonstrates the new v8.1 model-specific detection capabilities
by testing various AI-generated text samples against the detection engine.

Author: SPOT v8.1
Date: November 23, 2025
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from ai_detection_engine import AIDetectionEngine


# Sample texts representing different AI models
SAMPLE_TEXTS = {
    "ollama_llama": """
## Overview of Climate Change Mitigation Strategies

Climate change mitigation requires comprehensive action across multiple sectors. It's important to note that while individual actions matter, systemic changes are most effective.

### Key Strategies

1. **Renewable Energy Transition**: Moving from fossil fuels to clean energy sources
2. **Energy Efficiency**: Reducing consumption through better technology
3. **Carbon Capture**: Removing CO2 from the atmosphere
4. **Sustainable Transportation**: Shifting to electric and public transit

It's worth noting that implementation timelines vary by region. Additionally, funding mechanisms must be carefully considered to ensure equitable distribution of resources.

### Implementation Challenges

While progress has been made, several obstacles remain:

- Political resistance to policy changes
- Economic costs of transition
- Technological limitations
- Public awareness gaps

That being said, international cooperation is essential for success. On one hand, developed nations have greater resources; on the other hand, developing nations face unique challenges.
""",
    
    "google_gemini": """
🌍 Climate Change Solutions - Here's What You Need to Know! 

Great question! Let me help you understand the key ways we can tackle climate change. ✨

**Step 1: Understand the Problem**
Climate change is like turning up the heat on Earth's thermostat. Think of it like leaving your car in the sun - it gets hotter inside!

**Step 2: Take Action**
Here are the main solutions:

1️⃣ Switch to clean energy 💡
2️⃣ Drive electric vehicles 🚗
3️⃣ Plant more trees 🌳
4️⃣ Reduce waste ♻️

**Quick Summary - Key Takeaways:**
| Solution | Impact | Timeline |
|----------|--------|----------|
| Solar power | High | 5-10 years |
| Wind energy | High | 3-7 years |
| EVs | Medium | 10-15 years |

Here's what I found: Studies show renewable energy can reduce emissions by 70% by 2050! 🎯

Absolutely! With the right steps, we can make a real difference. Let me know if you'd like more details! 😊
""",

    "claude_anthropic": """
I should note that climate change mitigation is a complex topic that requires careful consideration of multiple factors. Let me think through this systematically.

When considering climate policy [particularly in the context of international cooperation], it's worth noting several important nuances:

First, there's significant complexity around implementation timelines. It depends on various factors including technological readiness, economic constraints, and political will. To be more precise, we need to consider both immediate actions and long-term strategies.

I aim to be helpful here by outlining the main approaches:

1. Renewable energy transition - This involves substantial infrastructure changes
2. Carbon pricing mechanisms - Though it's important to consider equity implications
3. Nature-based solutions - Including reforestation and ecosystem restoration

It's important to consider the ethical dimensions of climate action. We should note that the impacts fall disproportionately on vulnerable populations [both within and across nations]. This creates moral obligations that extend beyond simple cost-benefit analysis.

Upon reflection, I should mention that there are nuances to each approach. While renewable energy is crucial, it's more nuanced than simply replacing fossil fuels - we must consider grid stability, storage solutions, and just transition for workers.

After consideration, I'd emphasize that responsible climate action requires balancing effectiveness with care for affected communities.
""",

    "mistral_ai": """
# Climate Mitigation: Technical Analysis

## Core Strategies

Optimisation of energy systems requires:

```python
def calculate_emissions(energy_source, efficiency):
    base_emissions = EMISSION_FACTORS[energy_source]
    return base_emissions * (1 - efficiency)
```

### Mathematical Framework

The carbon budget equation: ∑(emissions_t) ≤ C_max

where C_max represents maximum cumulative emissions.

## Implementation

Key parameters:
- `renewable_fraction`: 0.7 target by 2030
- `efficiency_gain`: 2.5% annually
- `cost_per_tonne`: €50-100

Algorithm performance metrics show 40% reduction achievable through optimised grid architecture.

### Technical Solutions

1. Grid modernisation
2. Battery storage (lithium-ion optimisation)
3. Smart metre deployment
4. Algorithm-driven demand response

Code implementation available in repository. Performance benchmarks indicate scalability to 100GW capacity.

Function definitions and parameter tuning documented separately.
""",

    "cohere_business": """
# Climate Change: Key Business Insights

## Executive Summary

According to recent analysis, enterprise climate strategies show strong ROI potential. Based on market research, companies investing in sustainability see 15% efficiency gains.

### Key Findings

1. **Financial Impact**: Organizations adopting green practices reduce operational costs by 20-30%
2. **Market Opportunity**: Clean energy market projected at $2.15T by 2030
3. **Risk Mitigation**: Climate-resilient infrastructure protects stakeholder value

Data suggests early movers gain competitive advantage. Evidence indicates 67% of enterprises now prioritize ESG metrics.

### Strategic Recommendations

As reported by industry leaders, three priorities emerge:

1. Carbon accounting integration across workflows
2. Renewable energy procurement (PPA strategies)
3. Supply chain sustainability KPIs

Research shows successful implementation requires cross-functional stakeholder alignment. Analysis indicates productivity improvements correlate with environmental performance.

### Investment Framework

Portfolio allocation should consider:
- Clean tech scalability factors
- Regulatory compliance timelines  
- ESG reporting standards

Business case analysis demonstrates positive NPV across most scenarios. Main findings support accelerated transition planning.
"""
}


def run_detection_tests():
    """Run detection tests on sample texts."""
    
    print("=" * 80)
    print("AI MODEL-SPECIFIC DETECTION TEST")
    print("Sparrow SPOT Scale™ v8.1")
    print("=" * 80)
    print()
    
    engine = AIDetectionEngine()
    
    for model_name, sample_text in SAMPLE_TEXTS.items():
        print(f"\n{'─' * 80}")
        print(f"Testing: {model_name.upper().replace('_', ' ')}")
        print(f"{'─' * 80}")
        
        result = engine.analyze_document(sample_text)
        
        print(f"\n📊 Detection Results:")
        print(f"   Overall AI Score: {result['ai_detection_score']:.3f}")
        print(f"   Confidence: {result['confidence']:.3f}")
        print(f"   AI Detected: {'✓ YES' if result['detected'] else '✗ NO'}")
        
        print(f"\n🤖 Model Identification:")
        likely_model = result['likely_ai_model']
        print(f"   Identified Model: {likely_model['model'] or 'None'}")
        print(f"   Model Confidence: {likely_model['confidence']:.3f}")
        print(f"   Analysis: {likely_model['analysis']}")
        
        print(f"\n📈 Individual Model Scores:")
        for model, score in sorted(likely_model['model_scores'].items(), 
                                   key=lambda x: x[1], reverse=True):
            bar = '█' * int(score * 40)
            print(f"   {model:20s}: {score:.3f} {bar}")
        
        print(f"\n💡 Interpretation:")
        print(f"   {result['interpretation']}")
        
        print(f"\n⚠️  Recommendation:")
        print(f"   {result['recommendation']}")
    
    print(f"\n{'=' * 80}")
    print("Test Complete!")
    print("=" * 80)


def main():
    """Main entry point."""
    try:
        run_detection_tests()
        return 0
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
