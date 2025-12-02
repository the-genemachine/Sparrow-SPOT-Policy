"""
Critique Ingestion Module for SPOT-Policy™ v8.0

Integrates external human critiques from verified sources into policy evaluation.
Implements multi-stakeholder perspective balancing and dynamic score adjustment.

Features:
- External source integration (PBO, opposition parties, think tanks)
- Sentiment analysis and relevance scoring
- Dynamic Bayesian score adjustment
- Trust score enhancement through critique diversity
- NIST AI RMF alignment (Manage function)

Author: SPOT-Policy™ v8.0
Date: November 15, 2025
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import re


@dataclass
class CritiqueSource:
    """Represents a single critique source"""
    source_name: str
    critique_type: str  # 'official', 'think_tank', 'political', 'media'
    credibility_score: float  # 0.0-1.0
    sentiment: str  # 'critical', 'neutral', 'supportive'
    key_claims: List[str]
    relevant_criteria: List[str]  # ['SB', 'ER', 'PA', 'PC', 'FT']
    publish_date: str
    source_url: Optional[str] = None


class CritiqueIngestionModule:
    """
    Ingests and integrates external human critiques into SPOT-Policy™ v8.0
    
    Implements mechanisms from: Critique Ingestion Module V7.md spec
    """
    
    # Source credibility weights (higher = more trusted)
    SOURCE_CREDIBILITY_WEIGHTS = {
        'PBO': 0.95,  # Parliamentary Budget Officer (highest credibility)
        'Conservative_Party': 0.75,  # Official opposition
        'NDP': 0.75,
        'Bloc_Québécois': 0.75,
        'Green_Party': 0.70,
        'Think_Tank_Fraser': 0.80,
        'Think_Tank_CDHowe': 0.80,
        'Think_Tank_Brookings': 0.75,
        'Media_Mainstream': 0.70,
        'Media_Alternative': 0.60,
    }
    
    # Score adjustment formulas per criterion
    SCORE_ADJUSTMENT_FORMULAS = {
        'ER': {  # Economic Rigor - highly sensitive to fiscal critiques
            'factor': 0.25,  # Maximum adjustment: -25%
            'trigger_keywords': ['deficit', 'fiscal', 'surplus', 'projections', 'spending'],
            'source_bias': {'PBO': 0.9, 'Conservative_Party': 0.7}
        },
        'SB': {  # Stakeholder Balance - benefits from diverse perspective inclusion
            'factor': 0.15,  # Maximum boost: +15%
            'trigger_keywords': ['equity', 'affordability', 'workers', 'regions', 'indigenous'],
            'source_bias': {'NDP': 0.8, 'Conservative_Party': 0.7, 'Bloc_Québécois': 0.8}
        },
        'PA': {  # Public Accessibility - improved by external explanation
            'factor': 0.10,
            'trigger_keywords': ['clarity', 'language', 'complexity', 'jargon'],
            'source_bias': {'Media_Mainstream': 0.75}
        },
        'PC': {  # Policy Consequentiality - adjusted by real-world reception
            'factor': 0.20,
            'trigger_keywords': ['impact', 'implementation', 'outcome', 'consequence'],
            'source_bias': {'PBO': 0.85, 'Think_Tank': 0.80}
        },
        'FT': {  # Fiscal Transparency - enhanced by critique verification
            'factor': 0.12,
            'trigger_keywords': ['disclosure', 'breakdown', 'methodology', 'validation'],
            'source_bias': {'PBO': 0.9}
        }
    }
    
    def __init__(self):
        """Initialize critique ingestion module"""
        self.ingested_critiques: List[CritiqueSource] = []
        self.adjustment_log: List[Dict] = []
        self.timestamp = datetime.now().isoformat()
        
    def ingest_external_critique(
        self,
        source_name: str,
        critique_type: str,
        sentiment: str,
        key_claims: List[str],
        relevant_criteria: List[str],
        publish_date: str,
        credibility_override: Optional[float] = None,
        source_url: Optional[str] = None
    ) -> CritiqueSource:
        """
        Ingest a single critique from external source.
        
        Args:
            source_name: Name of source (e.g., 'PBO', 'Conservative_Party')
            critique_type: Type of source ('official', 'think_tank', 'political', 'media')
            sentiment: Sentiment direction ('critical', 'neutral', 'supportive')
            key_claims: List of main claims in critique
            relevant_criteria: Which scoring criteria are affected
            publish_date: ISO date of publication
            credibility_override: Optional override for auto-calculated credibility
            source_url: Optional URL to source
            
        Returns:
            CritiqueSource object
        """
        # Calculate or use override credibility score
        if credibility_override is not None:
            credibility = credibility_override
        else:
            credibility = self.SOURCE_CREDIBILITY_WEIGHTS.get(source_name, 0.65)
        
        critique = CritiqueSource(
            source_name=source_name,
            critique_type=critique_type,
            credibility_score=credibility,
            sentiment=sentiment,
            key_claims=key_claims,
            relevant_criteria=relevant_criteria,
            publish_date=publish_date,
            source_url=source_url
        )
        
        self.ingested_critiques.append(critique)
        return critique
    
    def load_budget_2025_critiques(self) -> List[CritiqueSource]:
        """
        Load default critiques for Canada's 2025 Federal Budget.
        Based on documented sources from November 3-14, 2025.
        """
        critiques = []
        
        # PBO Critique (Jason Jacques, November 14, 2025)
        pbo_critique = self.ingest_external_critique(
            source_name='PBO',
            critique_type='official',
            sentiment='critical',
            key_claims=[
                '7.5% chance deficit-to-GDP ratio declines annually (2026-2030)',
                'Deficit averages $64.3B/year (2025-2030), double prior projections',
                'Operating budget in deficit until 2028-29',
                'Broad capital spending definition inflates fiscal anchors'
            ],
            relevant_criteria=['ER', 'FT'],
            publish_date='2025-11-14',
            source_url='https://www.pbo-dpb.ca/en'
        )
        critiques.append(pbo_critique)
        
        # Conservative Party (Pierre Poilievre, November 4, 2025)
        conservative_critique = self.ingest_external_critique(
            source_name='Conservative_Party',
            critique_type='political',
            sentiment='critical',
            key_claims=[
                'Budget labeled "costly" and inflationary',
                'Increases costs for food, housing, essentials',
                'Fails to address Liberal-induced inflation',
                'Rejects $126B spending and $60B savings as unsustainable'
            ],
            relevant_criteria=['SB', 'PC', 'ER'],
            publish_date='2025-11-04'
        )
        critiques.append(conservative_critique)
        
        # NDP Critique (Jagmeet Singh, November 4-5, 2025)
        ndp_critique = self.ingest_external_critique(
            source_name='NDP',
            critique_type='political',
            sentiment='critical',
            key_claims=[
                'Insufficient investment in social programs',
                'Exacerbates cost-of-living crisis',
                'Inadequate worker protections',
                'Housing investment insufficient'
            ],
            relevant_criteria=['SB', 'PC'],
            publish_date='2025-11-05'
        )
        critiques.append(ndp_critique)
        
        # Bloc Québécois (Yves-François Blanchet, November 4, 2025)
        bloc_critique = self.ingest_external_critique(
            source_name='Bloc_Québécois',
            critique_type='political',
            sentiment='critical',
            key_claims=[
                'Misalignment with Quebec priorities',
                'Emissions caps inadequate',
                'Regional investments insufficient',
                'Unlikely to support without concessions'
            ],
            relevant_criteria=['SB', 'PA'],
            publish_date='2025-11-04'
        )
        critiques.append(bloc_critique)
        
        # Conference Board of Canada (Think Tank analysis)
        cbc_critique = self.ingest_external_critique(
            source_name='Think_Tank_CDHowe',
            critique_type='think_tank',
            sentiment='critical',
            key_claims=[
                'Pivot to capital spending at expense of social programs',
                'Strains long-term equity',
                'Lacks comprehensive tax reform'
            ],
            relevant_criteria=['ER', 'SB'],
            publish_date='2025-11-10',
            source_url='https://www.conferenceboard.ca/insights/analysis-of-the-2025-federal-budget/'
        )
        critiques.append(cbc_critique)
        
        # RBC Economics (Think Tank analysis)
        rbc_critique = self.ingest_external_critique(
            source_name='Think_Tank_Fraser',
            critique_type='think_tank',
            sentiment='critical',
            key_claims=[
                'Big new spending leads to larger-than-expected deficits',
                'Weak growth forecasts (1% GDP in 2025-2026)',
                'Trade war vulnerabilities'
            ],
            relevant_criteria=['ER', 'PC'],
            publish_date='2025-11-08',
            source_url='https://www.rbc.com/en/economics/'
        )
        critiques.append(rbc_critique)
        
        return critiques
    
    def calculate_sentiment_score(self, sentiment: str) -> float:
        """Convert sentiment to numerical score for calculations"""
        sentiment_map = {
            'highly_critical': -0.9,
            'critical': -0.7,
            'somewhat_critical': -0.5,
            'neutral': 0.0,
            'somewhat_supportive': 0.5,
            'supportive': 0.7,
            'highly_supportive': 0.9
        }
        return sentiment_map.get(sentiment, 0.0)
    
    def aggregate_critiques_by_criterion(self) -> Dict[str, Dict]:
        """
        Aggregate ingested critiques by criterion.
        
        Returns:
            Dict mapping criteria to aggregated critique data
        """
        aggregated = {}
        
        for criterion in ['FT', 'SB', 'ER', 'PA', 'PC']:
            aggregated[criterion] = {
                'total_critiques': 0,
                'avg_credibility': 0.0,
                'avg_sentiment': 0.0,
                'sources': [],
                'key_themes': []
            }
        
        for critique in self.ingested_critiques:
            for criterion in critique.relevant_criteria:
                if criterion in aggregated:
                    agg = aggregated[criterion]
                    agg['total_critiques'] += 1
                    agg['sources'].append(critique.source_name)
                    
                    # Accumulate for averaging
                    if 'credibility_sum' not in agg:
                        agg['credibility_sum'] = 0.0
                        agg['sentiment_sum'] = 0.0
                    agg['credibility_sum'] += critique.credibility_score
                    agg['sentiment_sum'] += self.calculate_sentiment_score(critique.sentiment)
                    
                    # Extract themes
                    for claim in critique.key_claims:
                        if claim not in agg['key_themes']:
                            agg['key_themes'].append(claim)
        
        # Finalize averages
        for criterion in aggregated:
            agg = aggregated[criterion]
            if agg['total_critiques'] > 0:
                agg['avg_credibility'] = agg['credibility_sum'] / agg['total_critiques']
                agg['avg_sentiment'] = agg['sentiment_sum'] / agg['total_critiques']
                del agg['credibility_sum']
                del agg['sentiment_sum']
        
        return aggregated
    
    def adjust_criterion_scores(self, original_scores: Dict[str, float]) -> Dict[str, Dict]:
        """
        Calculate adjusted scores based on ingested critiques.
        
        Implements Bayesian update: Adjusted = Original × (1 - Critique Impact)
        
        Args:
            original_scores: Dict with original criterion scores (FT, SB, ER, PA, PC)
            
        Returns:
            Dict with adjusted scores and adjustment details
        """
        adjusted = {}
        aggregated = self.aggregate_critiques_by_criterion()
        
        for criterion, score in original_scores.items():
            agg = aggregated.get(criterion, {})
            
            # Calculate adjustment factor
            if agg.get('total_critiques', 0) == 0:
                # No critiques for this criterion
                adjusted[criterion] = {
                    'original_score': score,
                    'adjusted_score': score,
                    'adjustment': 0.0,
                    'rationale': 'No external critiques ingested'
                }
            else:
                formula = self.SCORE_ADJUSTMENT_FORMULAS.get(criterion, {})
                factor = formula.get('factor', 0.1)
                
                # Calculate severity based on sentiment and credibility
                severity = abs(agg['avg_sentiment']) * agg['avg_credibility']
                
                # Apply adjustment
                adjustment_magnitude = severity * factor
                
                # Determine direction based on sentiment
                if agg['avg_sentiment'] < 0:  # Critical
                    adjusted_score = score * (1 - adjustment_magnitude)
                else:  # Supportive/diverse perspectives
                    adjusted_score = min(100, score + (adjustment_magnitude * score / 100))
                
                adjusted[criterion] = {
                    'original_score': score,
                    'adjusted_score': round(adjusted_score, 1),
                    'adjustment': round(adjusted_score - score, 1),
                    'adjustment_percentage': round((adjusted_score - score) / score * 100, 1),
                    'critique_count': agg['total_critiques'],
                    'avg_credibility': round(agg['avg_credibility'], 2),
                    'avg_sentiment': round(agg['avg_sentiment'], 2),
                    'sources': list(set(agg['sources'])),
                    'rationale': f"{agg['total_critiques']} critiques ingested from {len(set(agg['sources']))} sources (avg credibility: {agg['avg_credibility']:.2f})"
                }
                
                self.adjustment_log.append({
                    'criterion': criterion,
                    'original': score,
                    'adjusted': adjusted_score,
                    'sources': agg['sources'],
                    'timestamp': datetime.now().isoformat()
                })
        
        return adjusted
    
    def calculate_trust_score_enhancement(self, base_trust_score: float) -> Tuple[float, Dict]:
        """
        Calculate enhancement to trust score based on critique diversity.
        
        Implementation: +10-15% boost for diverse perspectives
        
        Args:
            base_trust_score: Original trust score (0-100)
            
        Returns:
            Tuple of (enhanced_score, enhancement_details)
        """
        if not self.ingested_critiques:
            return base_trust_score, {'boost': 0.0, 'rationale': 'No critiques ingested'}
        
        # Count unique sources and types
        unique_sources = len(set(c.source_name for c in self.ingested_critiques))
        unique_types = len(set(c.critique_type for c in self.ingested_critiques))
        
        # Criteria for maximum enhancement
        max_sources = 6
        max_types = 3
        
        # Calculate boost (0.10-0.15 range)
        source_factor = min(unique_sources / max_sources, 1.0) * 0.08
        type_factor = min(unique_types / max_types, 1.0) * 0.07
        total_boost_percentage = source_factor + type_factor
        
        # Apply enhancement
        enhancement_amount = base_trust_score * total_boost_percentage
        enhanced_score = min(100, base_trust_score + enhancement_amount)
        
        details = {
            'boost': round(enhancement_amount, 1),
            'boost_percentage': round(total_boost_percentage * 100, 1),
            'unique_sources': unique_sources,
            'unique_types': unique_types,
            'rationale': f'Multi-stakeholder perspective integration: {unique_sources} sources, {unique_types} types'
        }
        
        return round(enhanced_score, 1), details
    
    def generate_critique_integration_summary(self, original_analysis: Dict) -> Dict:
        """
        Generate comprehensive critique integration summary.
        
        Args:
            original_analysis: Original v7 analysis dict
            
        Returns:
            Summary dict suitable for JSON output
        """
        # Aggregate critiques
        aggregated = self.aggregate_critiques_by_criterion()
        
        # Adjust scores
        original_criteria_scores = {
            'FT': original_analysis.get('criteria', {}).get('FT', {}).get('score', 0),
            'SB': original_analysis.get('criteria', {}).get('SB', {}).get('score', 0),
            'ER': original_analysis.get('criteria', {}).get('ER', {}).get('score', 0),
            'PA': original_analysis.get('criteria', {}).get('PA', {}).get('score', 0),
            'PC': original_analysis.get('criteria', {}).get('PC', {}).get('score', 0),
        }
        
        adjusted_scores = self.adjust_criterion_scores(original_criteria_scores)
        
        # Calculate trust score enhancement
        base_trust_score = original_analysis.get('trust_score', {}).get('trust_score', 66.7)
        enhanced_trust_score, trust_details = self.calculate_trust_score_enhancement(base_trust_score)
        
        return {
            'metadata': {
                'module': 'CritiqueIngestionModule',
                'version': 'v8.0',
                'timestamp': self.timestamp,
                'critiques_ingested': len(self.ingested_critiques),
                'unique_sources': len(set(c.source_name for c in self.ingested_critiques))
            },
            'ingested_critiques': [
                {
                    'source': c.source_name,
                    'type': c.critique_type,
                    'sentiment': c.sentiment,
                    'credibility': c.credibility_score,
                    'relevant_criteria': c.relevant_criteria,
                    'key_claims': c.key_claims,
                    'publish_date': c.publish_date,
                    'url': c.source_url
                }
                for c in self.ingested_critiques
            ],
            'criterion_adjustments': adjusted_scores,
            'trust_score_enhancement': {
                'original': base_trust_score,
                'enhanced': enhanced_trust_score,
                'details': trust_details
            },
            'aggregated_critique_analysis': aggregated,
            'adjustment_log': self.adjustment_log,
            'recommendations': self._generate_recommendations(adjusted_scores, aggregated)
        }
    
    def _generate_recommendations(self, adjusted_scores: Dict, aggregated: Dict) -> List[str]:
        """
        Generate actionable recommendations based on critiques.
        
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        # Check for criteria needing attention
        for criterion, data in adjusted_scores.items():
            if data.get('adjustment', 0) < -5:
                recommendations.append(
                    f"{criterion}: Consider incorporating external perspectives on "
                    f"{', '.join(aggregated.get(criterion, {}).get('key_themes', [])[:2])}"
                )
        
        # Credibility-based recommendations
        high_credibility_sources = [
            c.source_name for c in self.ingested_critiques 
            if c.credibility_score > 0.85
        ]
        if high_credibility_sources:
            recommendations.append(
                f"High-credibility sources ({', '.join(set(high_credibility_sources))}) "
                f"warrant prioritized review"
            )
        
        # Sentiment clustering
        critical_count = sum(1 for c in self.ingested_critiques if c.sentiment == 'critical')
        if critical_count >= 3:
            recommendations.append(
                f"Multiple critical perspectives ({critical_count} sources) suggest "
                f"potential policy risks requiring professional review"
            )
        
        return recommendations


def create_critique_ingestion_module() -> CritiqueIngestionModule:
    """Factory function for module creation"""
    return CritiqueIngestionModule()
