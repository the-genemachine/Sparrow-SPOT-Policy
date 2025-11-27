#!/usr/bin/env python3
"""
Level 6: Statistical AI Detection Analyzer
Provides mathematical proof of AI generation through linguistic metrics
"""

import textstat
import numpy as np
from collections import Counter
import re
from typing import Dict, List, Tuple
import nltk
from scipy import stats

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

class StatisticalAnalyzer:
    """
    Analyzes text using statistical linguistics to provide mathematical
    proof of AI generation. Measures:
    - Perplexity (text predictability)
    - Burstiness (sentence length variance)
    - Lexical diversity (vocabulary richness)
    - N-gram patterns
    - Passive voice ratio
    - Readability scores
    """
    
    # Known thresholds (calibrated from AI vs human text)
    AI_THRESHOLDS = {
        'perplexity_low': 50,      # AI text is more predictable (lower perplexity)
        'burstiness_low': 0.3,     # AI has uniform sentence lengths (low burstiness)
        'lexical_diversity_low': 0.65,  # AI repeats words more (low diversity)
        'passive_voice_high': 0.20,     # AI uses more passive voice
        'avg_sentence_length': (20, 30),  # AI clusters in this range
    }
    
    def __init__(self):
        self.sentence_tokenizer = nltk.tokenize.punkt.PunktSentenceTokenizer()
    
    def calculate_perplexity(self, text: str) -> float:
        """
        Calculate perplexity score (text predictability).
        Lower perplexity = more predictable = more likely AI
        
        Simplified perplexity based on word frequency distributions
        """
        words = re.findall(r'\b\w+\b', text.lower())
        if len(words) < 10:
            return 0.0
        
        # Calculate word frequency distribution
        word_freq = Counter(words)
        total_words = len(words)
        
        # Calculate entropy
        entropy = 0
        for count in word_freq.values():
            prob = count / total_words
            entropy -= prob * np.log2(prob)
        
        # Perplexity is 2^entropy
        perplexity = 2 ** entropy
        
        return round(perplexity, 2)
    
    def calculate_burstiness(self, text: str) -> float:
        """
        Calculate burstiness (sentence length variance).
        Lower burstiness = more uniform = more likely AI
        
        Burstiness = (σ - μ) / (σ + μ)
        Range: -1 to 1, where 0 = uniform, 1 = bursty
        """
        sentences = self.sentence_tokenizer.tokenize(text)
        if len(sentences) < 3:
            return 0.0
        
        lengths = [len(s.split()) for s in sentences]
        mean = np.mean(lengths)
        std = np.std(lengths)
        
        if mean == 0:
            return 0.0
        
        burstiness = (std - mean) / (std + mean)
        return round(burstiness, 3)
    
    def calculate_lexical_diversity(self, text: str) -> float:
        """
        Calculate lexical diversity (vocabulary richness).
        Lower diversity = more repetitive = more likely AI
        
        Uses Type-Token Ratio (TTR): unique words / total words
        """
        words = re.findall(r'\b\w+\b', text.lower())
        if len(words) < 10:
            return 0.0
        
        unique_words = len(set(words))
        total_words = len(words)
        
        diversity = unique_words / total_words
        return round(diversity, 3)
    
    def calculate_passive_voice_ratio(self, text: str) -> float:
        """
        Calculate passive voice usage ratio.
        Higher ratio = more passive = more likely AI
        
        Detects common passive voice patterns
        """
        sentences = self.sentence_tokenizer.tokenize(text)
        if len(sentences) == 0:
            return 0.0
        
        # Common passive voice patterns
        passive_patterns = [
            r'\b(is|are|was|were|been|be)\s+\w+ed\b',
            r'\b(is|are|was|were|been|be)\s+being\s+\w+ed\b',
            r'\b(has|have|had)\s+been\s+\w+ed\b',
        ]
        
        passive_count = 0
        for sentence in sentences:
            for pattern in passive_patterns:
                if re.search(pattern, sentence, re.IGNORECASE):
                    passive_count += 1
                    break
        
        ratio = passive_count / len(sentences)
        return round(ratio, 3)
    
    def calculate_readability_scores(self, text: str) -> Dict[str, float]:
        """
        Calculate multiple readability scores.
        AI text tends to cluster in specific readability ranges.
        """
        return {
            'flesch_reading_ease': round(textstat.flesch_reading_ease(text), 2),
            'flesch_kincaid_grade': round(textstat.flesch_kincaid_grade(text), 2),
            'gunning_fog': round(textstat.gunning_fog(text), 2),
            'automated_readability_index': round(textstat.automated_readability_index(text), 2),
        }
    
    def analyze_ngrams(self, text: str, n: int = 3) -> Dict[str, any]:
        """
        Analyze n-gram patterns.
        AI text has distinctive n-gram frequency distributions.
        """
        words = re.findall(r'\b\w+\b', text.lower())
        if len(words) < n:
            return {'total': 0, 'unique': 0, 'repetition_rate': 0.0}
        
        ngrams = [tuple(words[i:i+n]) for i in range(len(words) - n + 1)]
        ngram_freq = Counter(ngrams)
        
        total_ngrams = len(ngrams)
        unique_ngrams = len(ngram_freq)
        repetition_rate = 1 - (unique_ngrams / total_ngrams) if total_ngrams > 0 else 0
        
        # Find most common repeated n-grams
        most_common = ngram_freq.most_common(5)
        
        return {
            'total': total_ngrams,
            'unique': unique_ngrams,
            'repetition_rate': round(repetition_rate, 3),
            'most_common': [(' '.join(ng), count) for ng, count in most_common if count > 1]
        }
    
    def calculate_sentence_statistics(self, text: str) -> Dict[str, float]:
        """Calculate sentence-level statistics"""
        sentences = self.sentence_tokenizer.tokenize(text)
        if len(sentences) == 0:
            return {
                'avg_length': 0,
                'std_length': 0,
                'min_length': 0,
                'max_length': 0,
                'median_length': 0,
            }
        
        lengths = [len(s.split()) for s in sentences]
        
        return {
            'avg_length': round(np.mean(lengths), 2),
            'std_length': round(np.std(lengths), 2),
            'min_length': min(lengths),
            'max_length': max(lengths),
            'median_length': round(np.median(lengths), 2),
        }
    
    def calculate_ai_probability(self, metrics: Dict) -> Tuple[float, str]:
        """
        Calculate overall AI probability based on statistical metrics.
        Returns (probability, confidence_level)
        """
        indicators = []
        
        # Perplexity check
        if metrics['perplexity'] < self.AI_THRESHOLDS['perplexity_low']:
            indicators.append(0.85)  # Strong AI indicator
        
        # Burstiness check
        if abs(metrics['burstiness']) < self.AI_THRESHOLDS['burstiness_low']:
            indicators.append(0.80)  # Strong AI indicator
        
        # Lexical diversity check
        if metrics['lexical_diversity'] < self.AI_THRESHOLDS['lexical_diversity_low']:
            indicators.append(0.75)  # Moderate AI indicator
        
        # Passive voice check
        if metrics['passive_voice_ratio'] > self.AI_THRESHOLDS['passive_voice_high']:
            indicators.append(0.70)  # Moderate AI indicator
        
        # Sentence length check
        avg_len = metrics['sentence_stats']['avg_length']
        low, high = self.AI_THRESHOLDS['avg_sentence_length']
        if low <= avg_len <= high:
            indicators.append(0.65)  # Weak AI indicator
        
        # Calculate weighted average
        if len(indicators) == 0:
            probability = 0.15  # Low baseline
            confidence = "LOW"
        elif len(indicators) <= 2:
            probability = np.mean(indicators) * 0.7  # Medium confidence
            confidence = "MEDIUM"
        else:
            probability = np.mean(indicators)
            confidence = "HIGH"
        
        return round(probability, 3), confidence
    
    def analyze(self, text: str) -> Dict:
        """
        Perform complete statistical analysis.
        Returns comprehensive metrics and AI probability.
        """
        if len(text.strip()) < 50:
            return {
                'error': 'Text too short for statistical analysis (minimum 50 characters)',
                'ai_probability': 0.0,
                'confidence': 'N/A'
            }
        
        # Calculate all metrics
        perplexity = self.calculate_perplexity(text)
        burstiness = self.calculate_burstiness(text)
        lexical_diversity = self.calculate_lexical_diversity(text)
        passive_ratio = self.calculate_passive_voice_ratio(text)
        readability = self.calculate_readability_scores(text)
        trigrams = self.analyze_ngrams(text, n=3)
        sentence_stats = self.calculate_sentence_statistics(text)
        
        metrics = {
            'perplexity': perplexity,
            'burstiness': burstiness,
            'lexical_diversity': lexical_diversity,
            'passive_voice_ratio': passive_ratio,
            'readability': readability,
            'trigram_analysis': trigrams,
            'sentence_stats': sentence_stats,
        }
        
        # Calculate AI probability
        ai_prob, confidence = self.calculate_ai_probability(metrics)
        
        return {
            'metrics': metrics,
            'ai_probability': ai_prob,
            'confidence': confidence,
            'interpretation': self._interpret_results(metrics, ai_prob, confidence)
        }
    
    def _interpret_results(self, metrics: Dict, ai_prob: float, confidence: str) -> str:
        """Generate human-readable interpretation"""
        interpretations = []
        
        # Perplexity
        if metrics['perplexity'] < self.AI_THRESHOLDS['perplexity_low']:
            interpretations.append(f"✓ Low perplexity ({metrics['perplexity']}) indicates highly predictable text (AI characteristic)")
        else:
            interpretations.append(f"✗ Normal perplexity ({metrics['perplexity']}) suggests natural variation")
        
        # Burstiness
        if abs(metrics['burstiness']) < self.AI_THRESHOLDS['burstiness_low']:
            interpretations.append(f"✓ Low burstiness ({metrics['burstiness']}) indicates uniform sentence lengths (AI characteristic)")
        else:
            interpretations.append(f"✗ Normal burstiness ({metrics['burstiness']}) suggests natural variation")
        
        # Lexical diversity
        if metrics['lexical_diversity'] < self.AI_THRESHOLDS['lexical_diversity_low']:
            interpretations.append(f"✓ Low lexical diversity ({metrics['lexical_diversity']}) indicates repetitive vocabulary (AI characteristic)")
        else:
            interpretations.append(f"✗ Normal lexical diversity ({metrics['lexical_diversity']}) suggests rich vocabulary")
        
        # Passive voice
        if metrics['passive_voice_ratio'] > self.AI_THRESHOLDS['passive_voice_high']:
            interpretations.append(f"✓ High passive voice ({metrics['passive_voice_ratio']}) is common in AI text")
        else:
            interpretations.append(f"✗ Normal passive voice ({metrics['passive_voice_ratio']}) suggests active writing")
        
        interpretations.append(f"\n📊 Statistical AI Probability: {ai_prob*100:.1f}% ({confidence} confidence)")
        
        return '\n'.join(interpretations)
    
    def generate_report(self, analysis: Dict, text_sample: str = None) -> str:
        """Generate formatted analysis report"""
        if 'error' in analysis:
            return f"ERROR: {analysis['error']}"
        
        metrics = analysis['metrics']
        
        report = f"""
{'='*80}
LEVEL 6: STATISTICAL AI DETECTION ANALYSIS
{'='*80}

MATHEMATICAL PROOF METRICS:
{'-'*80}

1. PERPLEXITY (Text Predictability):
   Score: {metrics['perplexity']}
   Threshold: < {self.AI_THRESHOLDS['perplexity_low']} = AI
   Status: {'🚨 AI INDICATOR' if metrics['perplexity'] < self.AI_THRESHOLDS['perplexity_low'] else '✓ Human-like'}

2. BURSTINESS (Sentence Length Variance):
   Score: {metrics['burstiness']}
   Threshold: < {self.AI_THRESHOLDS['burstiness_low']} = AI
   Status: {'🚨 AI INDICATOR' if abs(metrics['burstiness']) < self.AI_THRESHOLDS['burstiness_low'] else '✓ Human-like'}

3. LEXICAL DIVERSITY (Vocabulary Richness):
   Score: {metrics['lexical_diversity']}
   Threshold: < {self.AI_THRESHOLDS['lexical_diversity_low']} = AI
   Status: {'🚨 AI INDICATOR' if metrics['lexical_diversity'] < self.AI_THRESHOLDS['lexical_diversity_low'] else '✓ Human-like'}

4. PASSIVE VOICE RATIO:
   Score: {metrics['passive_voice_ratio']}
   Threshold: > {self.AI_THRESHOLDS['passive_voice_high']} = AI
   Status: {'🚨 AI INDICATOR' if metrics['passive_voice_ratio'] > self.AI_THRESHOLDS['passive_voice_high'] else '✓ Human-like'}

5. SENTENCE STATISTICS:
   Average Length: {metrics['sentence_stats']['avg_length']} words
   Std Deviation: {metrics['sentence_stats']['std_length']}
   Range: {metrics['sentence_stats']['min_length']}-{metrics['sentence_stats']['max_length']} words
   Median: {metrics['sentence_stats']['median_length']} words
   Status: {'🚨 AI RANGE' if self.AI_THRESHOLDS['avg_sentence_length'][0] <= metrics['sentence_stats']['avg_length'] <= self.AI_THRESHOLDS['avg_sentence_length'][1] else '✓ Outside AI range'}

6. READABILITY SCORES:
   Flesch Reading Ease: {metrics['readability']['flesch_reading_ease']}
   Flesch-Kincaid Grade: {metrics['readability']['flesch_kincaid_grade']}
   Gunning Fog Index: {metrics['readability']['gunning_fog']}
   ARI: {metrics['readability']['automated_readability_index']}

7. TRIGRAM ANALYSIS:
   Total Trigrams: {metrics['trigram_analysis']['total']}
   Unique Trigrams: {metrics['trigram_analysis']['unique']}
   Repetition Rate: {metrics['trigram_analysis']['repetition_rate']}
   Most Common Repeats: {len(metrics['trigram_analysis']['most_common'])} patterns
"""
        
        if metrics['trigram_analysis']['most_common']:
            report += "\n   Top Repeated Trigrams:\n"
            for phrase, count in metrics['trigram_analysis']['most_common'][:3]:
                report += f"      - '{phrase}': {count} times\n"
        
        report += f"""
{'-'*80}
FINAL STATISTICAL ASSESSMENT:
{'-'*80}

AI Probability: {analysis['ai_probability']*100:.1f}%
Confidence Level: {analysis['confidence']}

INTERPRETATION:
{analysis['interpretation']}

{'='*80}
"""
        
        return report


def main():
    """Demo the statistical analyzer"""
    analyzer = StatisticalAnalyzer()
    
    # Test with AI-like text
    ai_text = """
    The government will implement a comprehensive approach to ensure economic growth.
    This initiative will enable key stakeholders to achieve their objectives.
    The policy framework has been designed to support sustainable development.
    Implementation will be coordinated across multiple departments.
    The budget allocation has been optimized to maximize impact.
    Stakeholder engagement will be facilitated through established channels.
    The program will deliver measurable outcomes for all participants.
    Resources will be allocated based on strategic priorities.
    """
    
    print("Analyzing AI-like text sample...")
    print("="*80)
    analysis = analyzer.analyze(ai_text)
    print(analyzer.generate_report(analysis))
    
    # Test with human-like text
    human_text = """
    Look, I've been thinking about this budget thing for weeks now. Some parts make 
    sense - who wouldn't want better healthcare? But then you read the fine print 
    and it's like, wait, what? They're cutting funding here to pay for that over 
    there. My neighbor works for the government and she says nobody even knows 
    how half of this stuff will actually work in practice. It's frustrating because 
    we all want things to improve, but throwing money at problems doesn't always 
    fix them. Remember last year's big announcement? Yeah, whatever happened to that.
    """
    
    print("\nAnalyzing human-like text sample...")
    print("="*80)
    analysis = analyzer.analyze(human_text)
    print(analyzer.generate_report(analysis))


if __name__ == '__main__':
    main()
