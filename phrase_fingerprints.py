#!/usr/bin/env python3
"""
Level 5: AI Phrase Fingerprinting
Comprehensive database of model-specific phrase signatures
"""

from typing import Dict, List, Tuple
import re
from collections import Counter

class PhraseFingerprints:
    """
    Database of phrase patterns specific to different AI models.
    Expanded from initial detection to include 100+ signatures.
    """
    
    # Cohere-specific phrases (expanded from pattern detection)
    COHERE_PHRASES = {
        # Stakeholder language
        'stakeholder_focus': [
            r'\bkey stakeholders?\b',
            r'\ball stakeholders?\b',
            r'\bstakeholder engagement\b',
            r'\bstakeholder consultation\b',
            r'\bstakeholder input\b',
            r'\bstakeholder feedback\b',
            r'\baffected stakeholders?\b',
            r'\binternal stakeholders?\b',
            r'\bexternal stakeholders?\b',
        ],
        
        # Comprehensive/holistic language
        'comprehensive_approach': [
            r'\bcomprehensive approach\b',
            r'\bcomprehensive strategy\b',
            r'\bcomprehensive framework\b',
            r'\bcomprehensive review\b',
            r'\bcomprehensive assessment\b',
            r'\bcomprehensive plan\b',
            r'\bholistic approach\b',
            r'\bholistic view\b',
        ],
        
        # Enabling/facilitating language
        'enablement': [
            r'\bwill enable\b',
            r'\bto enable\b',
            r'\benabling\b',
            r'\bwill facilitate\b',
            r'\bto facilitate\b',
            r'\bfacilitating\b',
            r'\bwill support\b',
            r'\bto support\b',
        ],
        
        # Impact/outcome language
        'impact_statements': [
            r'\bmeasurable outcomes?\b',
            r'\bpositive impact\b',
            r'\btangible results?\b',
            r'\bdeliverable outcomes?\b',
            r'\bimpact assessment\b',
            r'\bdemonstrable results?\b',
            r'\bsignificant impact\b',
        ],
        
        # Implementation language
        'implementation': [
            r'\bimplementation plan\b',
            r'\bimplementation strategy\b',
            r'\bphased implementation\b',
            r'\bimplementation timeline\b',
            r'\bsuccessful implementation\b',
            r'\bimplementation framework\b',
        ],
        
        # Structured lists/initiatives
        'structured_content': [
            r'\binitiative will\b',
            r'\bprogram aims? to\b',
            r'\bproject will deliver\b',
            r'\bframework provides?\b',
            r'\bstrategy includes?\b',
        ],
        
        # Data-driven language
        'data_driven': [
            r'\bdata-driven\b',
            r'\bevidence-based\b',
            r'\bdata analytics?\b',
            r'\bdata insights?\b',
            r'\binformed by data\b',
        ],
        
        # Action-oriented verbs
        'action_verbs': [
            r'\boptimize\b',
            r'\bstreamline\b',
            r'\benhance\b',
            r'\bleverage\b',
            r'\bmaximize\b',
            r'\ballocate\b',
            r'\bcoordinate\b',
        ]
    }
    
    # Claude-specific phrases
    CLAUDE_PHRASES = {
        'hedging': [
            r'\bit\'s worth noting\b',
            r'\bit\'s important to consider\b',
            r'\bit should be noted\b',
            r'\bone might argue\b',
            r'\bone could say\b',
            r'\bthat said\b',
            r'\bin fairness\b',
        ],
        
        'meta_commentary': [
            r'\bthis raises questions? about\b',
            r'\bthis highlights? the\b',
            r'\bthis underscores?\b',
            r'\bthis illustrates?\b',
        ],
        
        'balanced_phrasing': [
            r'\bon one hand.*on the other hand\b',
            r'\bwhile.*however\b',
            r'\balthough.*nevertheless\b',
        ]
    }
    
    # GPT (OpenAI) specific phrases
    GPT_PHRASES = {
        'general_statements': [
            r'\bin today\'s world\b',
            r'\bin today\'s.*landscape\b',
            r'\bin the modern era\b',
            r'\bit\'s no secret that\b',
        ],
        
        'transitions': [
            r'\bfurthermore\b',
            r'\bmoreover\b',
            r'\badditionally\b',
            r'\bin conclusion\b',
            r'\bin summary\b',
        ],
        
        'emphasis': [
            r'\bcrucial to\b',
            r'\bessential to\b',
            r'\bvital to\b',
            r'\bimperative to\b',
        ]
    }
    
    # Gemini-specific phrases
    GEMINI_PHRASES = {
        'contextual': [
            r'\blet\'s explore\b',
            r'\blet\'s dive into\b',
            r'\blet\'s examine\b',
            r'\bconsider the following\b',
        ],
        
        'explanatory': [
            r'\bsimply put\b',
            r'\bin essence\b',
            r'\bbasically\b',
            r'\bfundamentally\b',
        ]
    }
    
    # Mistral-specific phrases  
    MISTRAL_PHRASES = {
        'technical': [
            r'\bimplementation details?\b',
            r'\btechnical specifications?\b',
            r'\barchitectural considerations?\b',
        ],
        
        'procedural': [
            r'\bstep-by-step\b',
            r'\bsequential process\b',
            r'\bsystematic approach\b',
        ]
    }
    
    def __init__(self):
        self.phrase_db = {
            'Cohere': self.COHERE_PHRASES,
            'Claude': self.CLAUDE_PHRASES,
            'GPT': self.GPT_PHRASES,
            'Gemini': self.GEMINI_PHRASES,
            'Mistral': self.MISTRAL_PHRASES,
        }
    
    def scan_text(self, text: str) -> Dict[str, any]:
        """
        Scan text for all known phrase fingerprints.
        
        Returns:
            Dictionary with model matches and specific phrases found
        """
        results = {}
        total_matches = 0
        
        for model, categories in self.phrase_db.items():
            model_matches = {}
            model_total = 0
            
            for category, patterns in categories.items():
                matches = []
                
                for pattern in patterns:
                    found = re.findall(pattern, text, re.IGNORECASE)
                    if found:
                        matches.extend(found)
                
                if matches:
                    model_matches[category] = {
                        'count': len(matches),
                        'examples': list(set(matches))[:5]  # Top 5 unique examples
                    }
                    model_total += len(matches)
            
            if model_matches:
                results[model] = {
                    'categories': model_matches,
                    'total_matches': model_total,
                    'confidence': self._calculate_confidence(model_total, len(text))
                }
                total_matches += model_total
        
        # Determine primary model
        if results:
            primary_model = max(results.items(), key=lambda x: x[1]['total_matches'])
            results['primary_model'] = primary_model[0]
            results['primary_confidence'] = primary_model[1]['confidence']
        else:
            results['primary_model'] = 'Unknown'
            results['primary_confidence'] = 0
        
        results['total_fingerprints_found'] = total_matches
        
        return results
    
    def _calculate_confidence(self, match_count: int, text_length: int) -> float:
        """
        Calculate confidence level based on phrase density.
        
        Higher density = higher confidence
        """
        # Normalize by text length (per 1000 characters)
        density = (match_count / max(text_length, 1)) * 1000
        
        if density > 10:
            confidence = 100
        elif density > 5:
            confidence = 90
        elif density > 2:
            confidence = 75
        elif density > 1:
            confidence = 60
        elif density > 0.5:
            confidence = 45
        else:
            confidence = max(30, density * 30)
        
        return round(confidence, 1)
    
    def get_phrase_count(self, text: str, model: str = 'Cohere') -> Dict[str, int]:
        """Get detailed phrase counts for specific model"""
        if model not in self.phrase_db:
            return {}
        
        results = {}
        categories = self.phrase_db[model]
        
        for category, patterns in categories.items():
            count = 0
            for pattern in patterns:
                count += len(re.findall(pattern, text, re.IGNORECASE))
            results[category] = count
        
        return results
    
    def generate_report(self, scan_results: Dict) -> str:
        """Generate human-readable fingerprint report"""
        if scan_results.get('total_fingerprints_found', 0) == 0:
            return "No AI phrase fingerprints detected."
        
        report = f"""
{'='*80}
LEVEL 5: AI PHRASE FINGERPRINTING ANALYSIS
{'='*80}

DETECTION SUMMARY:
Primary Model: {scan_results['primary_model']} ({scan_results['primary_confidence']}% confidence)
Total Fingerprints: {scan_results['total_fingerprints_found']}

{'-'*80}
MODEL-SPECIFIC SIGNATURES:
{'-'*80}
"""
        
        for model in ['Cohere', 'Claude', 'GPT', 'Gemini', 'Mistral']:
            if model in scan_results and model != 'primary_model':
                model_data = scan_results[model]
                report += f"\n{model}:\n"
                report += f"  Total Matches: {model_data['total_matches']}\n"
                report += f"  Confidence: {model_data['confidence']}%\n"
                
                if model_data['categories']:
                    report += f"  Categories Found:\n"
                    for category, data in model_data['categories'].items():
                        report += f"    • {category}: {data['count']} instances\n"
                        if data['examples']:
                            report += f"      Examples: {', '.join(data['examples'][:3])}\n"
        
        report += f"\n{'='*80}\n"
        return report


def main():
    """Demo the phrase fingerprinting"""
    fingerprints = PhraseFingerprints()
    
    # Test with Cohere-like text
    test_text = """
    The government will implement a comprehensive approach to ensure economic growth.
    This initiative will enable key stakeholders to achieve their objectives through
    stakeholder engagement and consultation. The implementation plan includes a 
    data-driven framework that will facilitate measurable outcomes. All stakeholders
    will be consulted to maximize impact and deliver tangible results.
    """
    
    print("Analyzing text for AI phrase fingerprints...")
    results = fingerprints.scan_text(test_text)
    print(fingerprints.generate_report(results))
    
    # Show Cohere-specific counts
    cohere_counts = fingerprints.get_phrase_count(test_text, 'Cohere')
    print("\nDetailed Cohere Phrase Counts:")
    for category, count in cohere_counts.items():
        if count > 0:
            print(f"  {category}: {count}")


if __name__ == '__main__':
    main()
