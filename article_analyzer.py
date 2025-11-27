#!/usr/bin/env python3
"""
Single Article Analyzer
Command-line tool for analyzing individual articles, blog posts, or any text content
"""

import argparse
import sys
import json
import re
import logging
import warnings
from pathlib import Path

# Configure specific warning filters
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', category=UserWarning, module='textblob')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Optional imports with fallbacks
try:
    from textblob import TextBlob
    import textstat
    READABILITY_AVAILABLE = True
except ImportError as e:
    READABILITY_AVAILABLE = False
    logging.warning(f"Readability analysis unavailable: {str(e)}")

try:
    import spacy
    NER_AVAILABLE = True
except ImportError as e:
    NER_AVAILABLE = False
    logging.warning(f"Entity extraction unavailable: {str(e)}")

try:
    import requests
    from bs4 import BeautifulSoup
    REQUESTS_AVAILABLE = True
except ImportError as e:
    REQUESTS_AVAILABLE = False
    logging.warning(f"URL loading unavailable: {str(e)}")

class ArticleAnalyzer:
    def __init__(self, config_file=None):
        """Initialize analyzer with optional configuration file"""
        try:
            self.journalism_patterns = {
                'news_indicators': ['breaking', 'reported', 'sources', 'investigation', 'exclusive', 'statement'],
                'opinion_indicators': ['believe', 'think', 'opinion', 'argue', 'perspective', 'view', 'i think'],
                'analysis_indicators': ['analysis', 'examination', 'deep dive', 'breakdown', 'explained'],
                'personal_indicators': ['my', 'i', 'me', 'personal', 'experience', 'journey']
            }
            self.bias_patterns = {
                'emotional': ['outrageous', 'shocking', 'devastating', 'brilliant', 'terrible', 'amazing'],
                'certainty': ['definitely', 'obviously', 'clearly', 'undoubtedly', 'certainly'],
                'loaded': ['radical', 'extreme', 'moderate', 'progressive', 'conservative'],
                'speculation': ['might', 'could', 'possibly', 'perhaps', 'maybe', 'allegedly']
            }
            if config_file:
                self._load_config(config_file)
        except Exception as e:
            logging.error(f"Initialization failed: {str(e)}")
            raise RuntimeError(f"Failed to initialize ArticleAnalyzer: {str(e)}") from e

    def _load_config(self, config_file):
        """Load patterns from a configuration file"""
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            self.journalism_patterns.update(config.get('journalism_patterns', {}))
            self.bias_patterns.update(config.get('bias_patterns', {}))
            logging.info(f"Loaded configuration from {config_file}")
        except (IOError, json.JSONDecodeError) as e:
            logging.warning(f"Failed to load config file {config_file}: {str(e)}. Using default patterns.")

    def analyze_single_article(self, text, context=None):
        """Comprehensive analysis of a single article"""
        try:
            if not isinstance(text, str):
                logging.error("Input must be a string")
                return {'error': 'Input must be a string'}
            if not text.strip():
                logging.error("No valid text content provided")
                return {'error': 'No valid text content provided'}
            if len(text) > 1_000_000:
                logging.error("Text exceeds maximum length (1MB)")
                return {'error': 'Text exceeds maximum length (1MB)'}
            if len(text.strip()) < 50:
                logging.error("Text too short for meaningful analysis")
                return {'error': 'Text too short for meaningful analysis (minimum 50 characters)'}
            if not any(char.isalpha() for char in text.lower()):
                logging.error("No valid textual content for analysis")
                return {'error': 'No valid textual content for analysis'}

            logging.info("Starting single article analysis")
            print("📰 SINGLE ARTICLE ANALYSIS")
            print("=" * 50)
            print(f"📝 Text length: {len(text)} characters")
            print(f"📊 Word count: {len(text.split())} words")
            print("-" * 50)

            results = {
                'metadata': {
                    'char_count': len(text),
                    'word_count': len(text.split()),
                    'context': context or 'No context provided'
                },
                'content_type': self.classify_content_type(text),
                'writing_style': self.analyze_writing_style(text),
                'bias_analysis': self.analyze_bias_indicators(text),
                'source_analysis': self.analyze_sources_citations(text),
                'structure_analysis': self.analyze_structure(text),
                'readability': self.analyze_readability(text),
                'entities': self.extract_entities(text),
                'engagement': self.analyze_engagement_indicators(text),
                'key_insights': self.generate_insights(text)
            }

            return results
        except Exception as e:
            logging.error(f"Article analysis failed: {str(e)}")
            return {'error': f'Article analysis failed: {str(e)}'}

    def classify_content_type(self, text):
        """Classify the type of content"""
        try:
            print("🎯 Classifying Content Type...")
            text_lower = text.lower()
            if not any(char.isalpha() for char in text_lower):
                logging.error("No valid textual content for classification")
                return {'error': 'No valid textual content for classification'}

            scores = {}
            for content_type, indicators in self.journalism_patterns.items():
                type_name = content_type.replace('_indicators', '')
                scores[type_name] = sum(1 for indicator in indicators if indicator in text_lower)

            if max(scores.values()) == 0:
                primary_type = 'general'
                confidence = 'low'
            else:
                primary_type = max(scores, key=scores.get)
                total_indicators = sum(scores.values())
                confidence = 'high' if total_indicators > 0 and scores[primary_type] / total_indicators > 0.5 else 'medium'

            print(f"  📋 Primary Type: {primary_type.title()} (confidence: {confidence})")
            print(f"  📊 Type Scores: {scores}")

            return {
                'primary_type': primary_type,
                'confidence': confidence,
                'type_scores': scores
            }
        except Exception as e:
            logging.error(f"Content type classification failed: {str(e)}")
            return {'error': f'Content type classification failed: {str(e)}'}

    def analyze_writing_style(self, text):
        """Analyze writing style characteristics"""
        try:
            print("✍️ Analyzing Writing Style...")
            words = text.split()
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if s.strip()]
            paragraphs = text.split('\n\n')
            paragraphs = [p.strip() for p in paragraphs if p.strip()]

            if not sentences:
                logging.error("No valid sentences detected")
                return {'error': 'No valid sentences detected'}
            if not paragraphs:
                logging.error("No valid paragraphs detected")
                return {'error': 'No valid paragraphs detected'}

            avg_words_per_sentence = len(words) / len(sentences)
            avg_sentences_per_paragraph = len(sentences) / len(paragraphs)
            long_sentences = sum(1 for s in sentences if len(s.split()) > 20)
            complex_words = sum(1 for word in words if len(word) > 6)
            passive_indicators = ['was', 'were', 'been', 'being']
            passive_count = sum(1 for word in words if word.lower() in passive_indicators)

            style_metrics = {
                'word_count': len(words),
                'sentence_count': len(sentences),
                'paragraph_count': len(paragraphs),
                'avg_words_per_sentence': round(avg_words_per_sentence, 1),
                'avg_sentences_per_paragraph': round(avg_sentences_per_paragraph, 1),
                'long_sentences_pct': round((long_sentences / len(sentences)) * 100, 1),
                'complex_words_pct': round((complex_words / len(words)) * 100, 1),
                'passive_voice_indicators': passive_count
            }

            print(f"  📏 Word count: {style_metrics['word_count']}")
            print(f"  📝 Sentences: {style_metrics['sentence_count']}")
            print(f"  📊 Avg words/sentence: {style_metrics['avg_words_per_sentence']}")
            print(f"  🎯 Complex words: {style_metrics['complex_words_pct']}%")

            return style_metrics
        except Exception as e:
            logging.error(f"Writing style analysis failed: {str(e)}")
            return {'error': f'Writing style analysis failed: {str(e)}'}

    def analyze_bias_indicators(self, text):
        """Analyze potential bias indicators"""
        try:
            print("⚖️ Analyzing Bias Indicators...")
            text_lower = text.lower()
            word_count = len(text.split())
            if word_count == 0:
                logging.error("No words detected for bias analysis")
                return {'error': 'No words detected for bias analysis'}

            bias_scores = {}
            for bias_type, indicators in self.bias_patterns.items():
                count = sum(1 for indicator in indicators if indicator in text_lower)
                score_per_1000 = (count / word_count * 1000)
                bias_scores[bias_type] = {
                    'count': count,
                    'per_1000_words': round(score_per_1000, 2),
                    'level': self.interpret_bias_level(score_per_1000, bias_type)
                }
                print(f"  📊 {bias_type.title()}: {score_per_1000:.1f} per 1000 words ({bias_scores[bias_type]['level']})")

            first_person = ['i', 'me', 'my', 'mine', 'myself']
            first_person_count = sum(1 for word in text_lower.split() if word in first_person)
            first_person_score = (first_person_count / word_count * 1000)
            bias_scores['first_person'] = {
                'count': first_person_count,
                'per_1000_words': round(first_person_score, 2),
                'level': self.interpret_bias_level(first_person_score, 'first_person')
            }

            print(f"  👤 First person: {first_person_score:.1f} per 1000 words ({bias_scores['first_person']['level']})")

            return bias_scores
        except Exception as e:
            logging.error(f"Bias indicators analysis failed: {str(e)}")
            return {'error': f'Bias indicators analysis failed: {str(e)}'}

    def interpret_bias_level(self, score, bias_type):
        """Interpret bias score levels"""
        try:
            thresholds = {
                'emotional': {'low': 3, 'medium': 8, 'high': 15},
                'certainty': {'low': 2, 'medium': 5, 'high': 10},
                'loaded': {'low': 1, 'medium': 3, 'high': 6},
                'speculation': {'low': 2, 'medium': 6, 'high': 12},
                'first_person': {'low': 5, 'medium': 15, 'high': 30}
            }
            threshold = thresholds.get(bias_type, {'low': 2, 'medium': 5, 'high': 10})

            if score < threshold['low']:
                return 'Low'
            elif score < threshold['medium']:
                return 'Medium'
            elif score < threshold['high']:
                return 'High'
            else:
                return 'Very High'
        except Exception as e:
            logging.error(f"Bias level interpretation failed: {str(e)}")
            return 'Unknown'

    def analyze_sources_citations(self, text):
        """Analyze source attribution and citations"""
        try:
            print("📚 Analyzing Sources and Citations...")
            quotes = re.findall(r'"[^"]*"', text)
            attribution_patterns = [
                r'according to',
                r'sources say',
                r'reported by',
                r'stated that',
                r'told.*that',
                r'says.*that'
            ]
            attributions = 0
            for pattern in attribution_patterns:
                attributions += len(re.findall(pattern, text, re.IGNORECASE))

            urls = re.findall(r'http[s]?://[^\s]+', text)
            expert_patterns = [r'dr\.?\s+\w+', r'professor\s+\w+', r'expert', r'researcher', r'analyst']
            experts = 0
            for pattern in expert_patterns:
                experts += len(re.findall(pattern, text, re.IGNORECASE))

            word_count = len(text.split())
            if word_count == 0:
                logging.error("No words detected for source analysis")
                return {'error': 'No words detected for source analysis'}

            if not quotes and not attributions and not urls and not experts:
                logging.warning("No source indicators detected")
                return {
                    'direct_quotes': 0,
                    'attribution_phrases': 0,
                    'urls': 0,
                    'expert_references': 0,
                    'source_density': 0.0,
                    'warning': 'No source indicators detected'
                }

            source_analysis = {
                'direct_quotes': len(quotes),
                'attribution_phrases': attributions,
                'urls': len(urls),
                'expert_references': experts,
                'source_density': round((len(quotes) + attributions + experts) / word_count * 100, 2)
            }

            print(f"  💬 Direct quotes: {source_analysis['direct_quotes']}")
            print(f"  📝 Attribution phrases: {source_analysis['attribution_phrases']}")
            print(f"  🔗 URLs: {source_analysis['urls']}")
            print(f"  👨‍🎓 Expert references: {source_analysis['expert_references']}")

            return source_analysis
        except Exception as e:
            logging.error(f"Source analysis failed: {str(e)}")
            return {'error': f'Source analysis failed: {str(e)}'}

    def analyze_structure(self, text):
        """Analyze narrative structure"""
        try:
            print("📖 Analyzing Article Structure...")
            if not text.strip():
                logging.error("No valid text for structure analysis")
                return {'error': 'No valid text for structure analysis'}

            paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
            if not paragraphs:
                logging.warning("No paragraphs detected, treating as single paragraph")
                paragraphs = [text]

            structure = {
                'total_paragraphs': len(paragraphs),
                'avg_paragraph_length': round(sum(len(p.split()) for p in paragraphs) / len(paragraphs), 1),
                'opening_style': self.analyze_opening(paragraphs[0] if paragraphs else ''),
                'conclusion_style': self.analyze_conclusion(paragraphs[-1] if paragraphs else ''),
                'has_subheadings': bool(re.search(r'^#{1,6}\s+', text, re.MULTILINE))
            }

            print(f"  📄 Paragraphs: {structure['total_paragraphs']}")
            print(f"  📏 Avg paragraph length: {structure['avg_paragraph_length']} words")
            print(f"  🎬 Opening style: {structure['opening_style']}")
            print(f"  🎯 Conclusion style: {structure['conclusion_style']}")

            return structure
        except Exception as e:
            logging.error(f"Structure analysis failed: {str(e)}")
            return {'error': f'Structure analysis failed: {str(e)}'}

    def analyze_opening(self, opening_text):
        """Analyze opening paragraph style"""
        try:
            if not opening_text:
                return 'unknown'
            opening_lower = opening_text.lower()
            if opening_text.strip().endswith('?'):
                return 'question'
            elif '"' in opening_text[:100]:
                return 'quote'
            elif re.search(r'\d+', opening_text[:100]):
                return 'statistic'
            elif any(word in opening_lower[:100] for word in ['when', 'once', 'yesterday', 'last week', 'recently']):
                return 'anecdote'
            elif any(word in opening_lower[:50] for word in ['i', 'my', 'me']):
                return 'personal'
            else:
                return 'statement'
        except Exception as e:
            logging.error(f"Opening analysis failed: {str(e)}")
            return 'unknown'

    def analyze_conclusion(self, conclusion_text):
        """Analyze conclusion style"""
        try:
            if not conclusion_text:
                return 'unknown'
            conclusion_lower = conclusion_text.lower()
            if conclusion_text.strip().endswith('?'):
                return 'question'
            elif any(word in conclusion_lower for word in ['should', 'must', 'need to', 'call', 'action']):
                return 'call_to_action'
            elif any(word in conclusion_lower for word in ['conclusion', 'summary', 'in sum']):
                return 'summary'
            elif any(word in conclusion_lower for word in ['will', 'future', 'next', 'ahead']):
                return 'future_outlook'
            else:
                return 'statement'
        except Exception as e:
            logging.error(f"Conclusion analysis failed: {str(e)}")
            return 'unknown'

    def analyze_readability(self, text):
        """Analyze text readability"""
        try:
            print("📚 Analyzing Readability...")
            if not READABILITY_AVAILABLE:
                logging.warning("Readability analysis unavailable (textstat not installed)")
                return {'error': 'textstat not available'}

            try:
                textstat.flesch_reading_ease(text)  # Validate text input
            except ValueError as e:
                logging.error(f"Invalid text for readability analysis: {str(e)}")
                return {'error': f'Invalid text for readability analysis: {str(e)}'}

            readability = {
                'flesch_reading_ease': round(textstat.flesch_reading_ease(text), 1),
                'flesch_kincaid_grade': round(textstat.flesch_kincaid_grade(text), 1),
                'automated_readability_index': round(textstat.automated_readability_index(text), 1),
                'coleman_liau_index': round(textstat.coleman_liau_index(text), 1),
                'reading_time_minutes': round(len(text.split()) / 200, 1)
            }

            flesch_score = readability['flesch_reading_ease']
            if flesch_score >= 90:
                level = "Very Easy"
            elif flesch_score >= 80:
                level = "Easy"
            elif flesch_score >= 70:
                level = "Fairly Easy"
            elif flesch_score >= 60:
                level = "Standard"
            elif flesch_score >= 50:
                level = "Fairly Difficult"
            elif flesch_score >= 30:
                level = "Difficult"
            else:
                level = "Very Difficult"
            readability['readability_level'] = level

            print(f"  📊 Flesch Reading Ease: {readability['flesch_reading_ease']} ({level})")
            print(f"  🎓 Grade Level: {readability['flesch_kincaid_grade']}")
            print(f"  ⏱️ Reading Time: {readability['reading_time_minutes']} minutes")

            return readability
        except Exception as e:
            logging.error(f"Readability analysis failed: {str(e)}")
            return {'error': f'Readability analysis failed: {str(e)}'}

    def extract_entities(self, text):
        """Extract named entities"""
        try:
            print("🏷️ Extracting Named Entities...")
            if not NER_AVAILABLE:
                logging.warning("Entity extraction unavailable (spaCy not installed)")
                return {'error': 'spaCy not available'}

            try:
                nlp = spacy.load('en_core_web_sm')
            except OSError as e:
                logging.error(f"Failed to load spaCy model: {str(e)}")
                return {'error': f'Failed to load spaCy model: {str(e)}'}

            doc = nlp(text)
            entities = {
                'people': [],
                'organizations': [],
                'locations': [],
                'dates': [],
                'money': [],
                'other': []
            }

            for ent in doc.ents:
                if ent.label_ in ['PERSON']:
                    entities['people'].append(ent.text)
                elif ent.label_ in ['ORG']:
                    entities['organizations'].append(ent.text)
                elif ent.label_ in ['GPE', 'LOC']:
                    entities['locations'].append(ent.text)
                elif ent.label_ in ['DATE', 'TIME']:
                    entities['dates'].append(ent.text)
                elif ent.label_ in ['MONEY']:
                    entities['money'].append(ent.text)
                else:
                    entities['other'].append(f"{ent.text} ({ent.label_})")

            for category in entities:
                unique_entities = list(set(entities[category]))
                entities[category] = unique_entities[:10]

            total_entities = sum(len(entities[cat]) for cat in entities)
            print(f"  📊 Total entities found: {total_entities}")
            for category, entity_list in entities.items():
                if entity_list:
                    print(f"  {category.title()}: {', '.join(entity_list[:3])}{'...' if len(entity_list) > 3 else ''}")

            return entities
        except Exception as e:
            logging.error(f"Entity extraction failed: {str(e)}")
            return {'error': f'Entity extraction failed: {str(e)}'}

    def analyze_engagement_indicators(self, text):
        """Analyze audience engagement indicators"""
        try:
            print("📈 Analyzing Engagement Indicators...")
            text_lower = text.lower()
            word_count = len(text.split())
            if word_count == 0:
                logging.error("No words detected for engagement analysis")
                return {'error': 'No words detected for engagement analysis'}

            reader_questions = len(re.findall(r'\?[^.!]*(?:you|your|we|us)', text, re.IGNORECASE))
            personal_pronouns = len(re.findall(r'\b(you|your|yours)\b', text_lower))
            cta_words = ['subscribe', 'share', 'comment', 'follow', 'join', 'sign up', 'click', 'read more']
            cta_count = sum(1 for word in cta_words if word in text_lower)
            inclusive_words = ['we', 'us', 'our', 'together', 'community']
            inclusive_count = sum(1 for word in inclusive_words if word in text_lower)
            emotional_words = ['amazing', 'incredible', 'shocking', 'surprising', 'fascinating', 'important']
            emotional_count = sum(1 for word in emotional_words if word in text_lower)

            engagement = {
                'reader_questions': reader_questions,
                'personal_pronouns': personal_pronouns,
                'call_to_action': cta_count,
                'inclusive_language': inclusive_count,
                'emotional_words': emotional_count,
                'engagement_score': round((reader_questions * 3 + personal_pronouns + cta_count * 2 + inclusive_count + emotional_count) / word_count * 100, 2)
            }

            print(f"  ❓ Reader questions: {engagement['reader_questions']}")
            print(f"  👤 Personal pronouns: {engagement['personal_pronouns']}")
            print(f"  📢 Call to action: {engagement['call_to_action']}")
            print(f"  🤝 Inclusive language: {engagement['inclusive_language']}")
            print(f"  📊 Engagement score: {engagement['engagement_score']}")

            return engagement
        except Exception as e:
            logging.error(f"Engagement indicators analysis failed: {str(e)}")
            return {'error': f'Engagement indicators analysis failed: {str(e)}'}

    def generate_insights(self, text):
        """Generate key insights about the article"""
        try:
            print("💡 Generating Key Insights...")
            if not text.strip():
                logging.error("No valid text for insights")
                return ['No valid text for insights']

            insights = []
            word_count = len(text.split())
            if word_count < 300:
                insights.append("Short form content - good for social media or quick reads")
            elif word_count < 800:
                insights.append("Medium length article - typical blog post or newsletter")
            elif word_count < 2000:
                insights.append("Long form content - in-depth analysis or feature article")
            else:
                insights.append("Very long article - comprehensive analysis or investigative piece")

            first_person_count = len(re.findall(r'\b(i|me|my|mine)\b', text.lower()))
            if first_person_count > 10:
                insights.append("Personal narrative style - author sharing experience or opinion")

            question_count = text.count('?')
            if question_count > 3:
                insights.append("Interactive style - engages reader with questions")

            quote_count = text.count('"')
            if quote_count > 4:
                insights.append("Well-sourced content - includes quotes and attributions")

            technical_words = ['analysis', 'data', 'research', 'study', 'methodology']
            if sum(1 for word in technical_words if word in text.lower()) > 3:
                insights.append("Technical/analytical content - data-driven or research-based")

            print(f"  💡 Generated {len(insights)} insights")
            for insight in insights:
                print(f"    • {insight}")

            return insights
        except Exception as e:
            logging.error(f"Insights generation failed: {str(e)}")
            return ['Insights generation failed']

    def save_results(self, results, output_file):
        """Save analysis results to file"""
        try:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2)
            print(f"\n💾 Results saved to {output_file}")
            logging.info(f"Results saved to {output_file}")
        except (IOError, TypeError) as e:
            logging.error(f"Failed to save results to {output_file}: {str(e)}")
            raise RuntimeError(f"Failed to save results to {output_file}: {str(e)}") from e

    def load_text_from_url(self, url):
        """Load text content from URL"""
        try:
            if not REQUESTS_AVAILABLE:
                logging.error("requests library not available for URL loading")
                raise RuntimeError("requests library not available for URL loading")

            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
            except requests.exceptions.Timeout:
                logging.error(f"Timeout fetching URL {url}")
                raise RuntimeError(f"Timeout fetching URL {url}") from None
            except requests.exceptions.HTTPError as e:
                logging.error(f"HTTP error fetching URL {url}: {str(e)}")
                raise RuntimeError(f"HTTP error fetching URL {url}: {str(e)}") from e
            except requests.exceptions.RequestException as e:
                logging.error(f"Failed to fetch URL {url}: {str(e)}")
                raise RuntimeError(f"Failed to fetch URL {url}: {str(e)}") from e

            try:
                soup = BeautifulSoup(response.content, 'html.parser')
            except Exception as e:
                logging.error(f"Failed to parse HTML from {url}: {str(e)}")
                raise RuntimeError(f"Failed to parse HTML from {url}: {str(e)}") from e

            for script in soup(["script", "style"]):
                script.decompose()

            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)

            if not text.strip():
                logging.error(f"No valid text extracted from URL {url}")
                raise RuntimeError(f"No valid text extracted from URL {url}")

            return text
        except Exception as e:
            logging.error(f"URL loading failed: {str(e)}")
            raise RuntimeError(f"Failed to load URL: {str(e)}") from e

def main():
    parser = argparse.ArgumentParser(description="Analyze individual articles for journalistic content")
    parser.add_argument('filename', nargs='?', help='Path to article file to analyze')
    parser.add_argument('-t', '--text', help='Article text to analyze directly')
    parser.add_argument('-u', '--url', help='Load article from URL')
    parser.add_argument('--stdin', action='store_true', help='Read from stdin')
    parser.add_argument('-o', '--output', help='Save results to JSON file')
    parser.add_argument('--format', choices=['json', 'text'], default='text', help='Output format')
    parser.add_argument('-c', '--context', help='Provide context about the article')
    parser.add_argument('--quick', action='store_true', help='Quick analysis (skip slow operations)')
    parser.add_argument('--config', help='Path to configuration file for patterns')

    try:
        args = parser.parse_args()
    except SystemExit as e:
        logging.error(f"Error parsing arguments: {str(e)}")
        print(f"❌ Error parsing arguments: {str(e)}")
        sys.exit(1)

    try:
        analyzer = ArticleAnalyzer(config_file=args.config)
    except RuntimeError as e:
        logging.error(f"Failed to initialize analyzer: {str(e)}")
        print(f"❌ Failed to initialize analyzer: {str(e)}")
        sys.exit(1)

    text = None
    source = None
    try:
        if args.filename:
            try:
                with open(args.filename, 'r', encoding='utf-8') as f:
                    text = f.read()
                source = f"file: {args.filename}"
            except IOError as e:
                logging.error(f"Error reading file {args.filename}: {str(e)}")
                print(f"❌ Error reading file: {str(e)}")
                sys.exit(1)
        elif args.text:
            text = args.text
            source = "command line argument"
        elif args.url:
            text = analyzer.load_text_from_url(args.url)
            source = f"URL: {args.url}"
        elif args.stdin:
            text = sys.stdin.read()
            source = "stdin"
        else:
            parser.print_help()
            sys.exit(1)

        if not text or not text.strip():
            logging.error("No valid text content found")
            print("❌ No valid text content found")
            sys.exit(1)
    except RuntimeError as e:
        logging.error(f"Failed to load text: {str(e)}")
        print(f"❌ Failed to load text: {str(e)}")
        sys.exit(1)

    context = f"Source: {source}"
    if args.context:
        context += f" | Context: {args.context}"

    try:
        if args.quick:
            logging.info("Running quick analysis (skipping readability and entity extraction)")
            results = {
                'metadata': {'char_count': len(text), 'word_count': len(text.split()), 'context': context},
                'content_type': analyzer.classify_content_type(text),
                'writing_style': analyzer.analyze_writing_style(text),
                'bias_analysis': analyzer.analyze_bias_indicators(text),
                'source_analysis': analyzer.analyze_sources_citations(text),
                'structure_analysis': analyzer.analyze_structure(text),
                'engagement': analyzer.analyze_engagement_indicators(text),
                'key_insights': analyzer.generate_insights(text)
            }
        else:
            results = analyzer.analyze_single_article(text, context)

        if args.format == 'json' or args.output:
            if args.output:
                analyzer.save_results(results, args.output)
            else:
                print(json.dumps(results, indent=2))

        print(f"\n🎉 Analysis complete!")
        print(f"📊 Summary: {results['content_type'].get('primary_type', 'Unknown').title()} content")
        print(f"📚 Readability: {results.get('readability', {}).get('readability_level', 'Unknown')}")
        print(f"⚖️ Bias level: {results['bias_analysis'].get('emotional', {}).get('level', 'Unknown')}")
    except Exception as e:
        logging.error(f"Analysis failed: {str(e)}")
        print(f"❌ Analysis failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()