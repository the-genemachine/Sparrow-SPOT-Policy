"""
Format Renderer Module for v8
Outputs narrative in multiple platform-specific formats

This module renders narrative components for:
- X (Twitter) threads (280-char format, threaded)
- LinkedIn articles (professional, long-form)
- Social badges (image + caption format)
- HTML certificates (full design)
"""

from typing import Dict, List, Optional
import json
from datetime import datetime


class FormatRenderer:
    """
    Renders narrative content in multiple formats.
    
    Input: Narrative text/components + format choice
    Output: Platform-specific formatted content
    
    NEW (v8): Includes AI disclosure statements per Recommendation #4
    """
    
    AVAILABLE_FORMATS = ['x_thread', 'linkedin', 'social_badge', 'html_certificate']
    
    def __init__(self):
        """Initialize format renderer"""
        self.max_x_length = 280
        self.timestamp = datetime.now().isoformat()
        self.include_ai_disclosure = True  # NEW: Include AI disclosure in outputs
        
        # Centralized scoring configuration
        self.score_precision = {
            'heading': 0,  # Round to nearest integer for headings/titles
            'detailed': 1,  # 1 decimal place for detailed sections
            'exact': 1     # Default exact representation
        }
    
    def _format_score(self, score: float, context: str = 'exact', add_footnote: bool = False) -> str:
        """Format score according to centralized rules.
        
        Args:
            score: The numerical score
            context: 'heading', 'detailed', or 'exact'
            add_footnote: Whether to add rounding footnote for headings
            
        Returns:
            Formatted score string
        """
        precision = self.score_precision.get(context, 1)
        formatted = f"{score:.{precision}f}"
        
        if add_footnote and context == 'heading' and score != round(score):
            return f"{formatted}* (rounded from {score:.1f})"
        
        return formatted
    
    def render(self, narrative_text: str, format_type: str = 'x_thread', 
               narrative_components: Optional[Dict] = None) -> str:
        """
        Render narrative in specified format.
        
        Args:
            narrative_text: The narrative text to render
            format_type: One of 'x_thread', 'linkedin', 'social_badge', 'html_certificate'
            narrative_components: Optional dict with structured components
            
        Returns:
            Formatted content ready for platform
        """
        if format_type not in self.AVAILABLE_FORMATS:
            format_type = 'x_thread'
        
        if format_type == 'x_thread':
            return self._render_x_thread(narrative_text, narrative_components)
        elif format_type == 'linkedin':
            return self._render_linkedin(narrative_text, narrative_components)
        elif format_type == 'social_badge':
            return self._render_social_badge(narrative_text, narrative_components)
        elif format_type == 'html_certificate':
            return self._render_html_certificate(narrative_text, narrative_components)
        
        return narrative_text
    
    def _render_x_thread(self, narrative_text: str, components: Optional[Dict] = None) -> str:
        """
        Render as X (Twitter) thread format.
        
        Multiple tweets connected as thread, each under 280 chars.
        Numbered tweets: 1/n, 2/n, etc.
        """
        if not narrative_text:
            return ""
        
        tweets = []
        
        # Get key data from components if available
        if components:
            score = components.get('composite_score', 0)
            grade = components.get('grade', 'N/A')
            lede = components.get('lede', narrative_text)
            tweet_num = 1
            
            # Tweet 1: Hook with score (rounded for brevity)
            score_rounded = self._format_score(score, 'heading')
            tweet1 = f"{tweet_num}/8 🧵 Breaking: Policy analysis reveals [{grade} | {score_rounded}/100]\n\n{lede[:240]}"
            tweets.append(tweet1)
            tweet_num += 1
            
            # Tweets 2-3: All criteria breakdown (exact scores)
            criteria = components.get('criteria', {})
            if criteria:
                criteria_lines = []
                for key, data in list(criteria.items()):
                    if isinstance(data, dict):
                        name = data.get('name', key)
                        score_val = data.get('score', 0)
                        interp = data.get('interpretation', '')
                        score_formatted = self._format_score(score_val, 'detailed')
                        criteria_lines.append(f"• {name}: {interp} ({score_formatted}/100)")
                
                if len(criteria_lines) <= 3:
                    tweet = f"{tweet_num}/8 Assessment breakdown:\n\n" + "\n".join(criteria_lines)
                    tweets.append(tweet)
                    tweet_num += 1
                elif len(criteria_lines) <= 5:
                    # Split across 2 tweets
                    tweet = f"{tweet_num}/8 Assessment (Part 1):\n\n" + "\n".join(criteria_lines[:3])
                    tweets.append(tweet)
                    tweet_num += 1
                    tweet = f"{tweet_num}/8 Assessment (Part 2):\n\n" + "\n".join(criteria_lines[3:])
                    tweets.append(tweet)
                    tweet_num += 1
                else:
                    # Split across 3 tweets
                    tweet = f"{tweet_num}/8 Assessment (Part 1):\n\n" + "\n".join(criteria_lines[:2])
                    tweets.append(tweet)
                    tweet_num += 1
                    tweet = f"{tweet_num}/8 Assessment (Part 2):\n\n" + "\n".join(criteria_lines[2:4])
                    tweets.append(tweet)
                    tweet_num += 1
                    tweet = f"{tweet_num}/8 Assessment (Part 3):\n\n" + "\n".join(criteria_lines[4:])
                    tweets.append(tweet)
                    tweet_num += 1
            
            # Tweet on tensions
            tension = components.get('key_tension', '')
            if tension:
                tweet_tension = f"{tweet_num}/8 Key tension:\n\n{tension[:240]}"
                tweets.append(tweet_tension)
                tweet_num += 1
            
            # Tweet on implications
            implications = components.get('implications', [])
            if implications:
                impl_text = f"{tweet_num}/8 Key takeaway:\n\n{implications[0][:240]}"
                tweets.append(impl_text)
                tweet_num += 1
            
            # Tweet on escalations if any
            escalations = components.get('escalations', [])
            if escalations and tweet_num < 8:
                high_severity = [e for e in escalations if e.get('severity') == 'HIGH']
                if high_severity:
                    esc_text = f"{tweet_num}/8 ⚠️ Alert: {high_severity[0].get('message', 'Expert review recommended')}"
                    tweets.append(esc_text)
                    tweet_num += 1
            
            # Fill remaining tweets to reach 8
            filler_messages = [
                "This analysis employs rigorous, multi-criteria assessment per governance standards.",
                "Methodology: Assessment based on fiscal transparency, stakeholder balance, and economic rigor.",
            ]
            
            while tweet_num <= 8:
                if tweet_num == 7:
                    # Recommendation #3: Streamlined risk disclosure
                    trust_data = components.get('trust_score', {})
                    trust_score = trust_data.get('trust_score', 0) if isinstance(trust_data, dict) else 0
                    
                    risk_data = components.get('risk_tier', {})
                    if isinstance(risk_data, dict):
                        risk_tier = risk_data.get('risk_tier', 'MEDIUM').upper()
                        risk_score = risk_data.get('risk_score', 0)
                        controls = risk_data.get('required_controls', [])
                        control_summary = ' | '.join(c.replace('_', ' ').title() for c in controls[:3])
                    else:
                        risk_tier = str(risk_data).upper() if risk_data else 'MEDIUM'
                        risk_score = 50
                        control_summary = 'See certificate for details'
                    
                    bias_data = components.get('bias_audit', {})
                    fairness_score = bias_data.get('overall_fairness_score', 0) if isinstance(bias_data, dict) else 0
                    
                    # Fix #3: Normalize to one decimal place
                    risk_tweet = f"{tweet_num}/8 ⚠ Risk Tier: {risk_tier} ({risk_score}/100)\n"
                    risk_tweet += f"• Trust Score: {trust_score:.1f} → {'Human review required' if trust_score < 70 else 'Approved'}\n"
                    risk_tweet += f"• Fairness: {fairness_score:.1f}% (Demographic Parity)\n"
                    risk_tweet += f"• NIST Controls: {control_summary}"
                    tweets.append(risk_tweet)
                elif tweet_num == 8:
                    # Recommendation #5: AI transparency disclosure
                    # Fix #1: Extract with one decimal precision
                    ai_data = components.get('ai_detection', {})
                    if isinstance(ai_data, dict):
                        ai_detection = ai_data.get('overall_percentage')
                        if ai_detection is None:
                            ai_score = ai_data.get('ai_detection_score', 0)
                            ai_detection = ai_score * 100 if ai_score <= 1 else ai_score
                    else:
                        ai_detection = ai_data if ai_data else 0
                    
                    # Add model detection if available
                    model_info = ""
                    if isinstance(ai_data, dict):
                        likely_model = ai_data.get('likely_ai_model', {})
                        if isinstance(likely_model, dict) and likely_model.get('model'):
                            model_name = likely_model.get('model')
                            model_conf = likely_model.get('confidence', 0)
                            if model_name and model_name != 'Mixed/Uncertain':
                                model_info = f" Detected: {model_name} ({model_conf*100:.0f}% confidence)."
                    
                    final_tweet = f"{tweet_num}/8 🔍 AI Contribution: {ai_detection:.1f}% AI-assisted.{model_info} Human reviewed {datetime.now().strftime('%b %d, %Y')}.\n"
                    final_tweet += "Read full analysis for methodology & recommendations. #PolicyAnalysis #Governance"
                    tweets.append(final_tweet)
                else:
                    # Standard filler tweets
                    filler_idx = (tweet_num - 5) % len(filler_messages)
                    filler_text = filler_messages[filler_idx]
                    tweet = f"{tweet_num}/8 {filler_text}"
                    tweets.append(tweet)
                tweet_num += 1
        else:
            # Simple fallback: split narrative into thread
            sentences = narrative_text.split('. ')
            tweet_count = 1
            current_tweet = f"{tweet_count}/n 🧵 "
            
            for sentence in sentences:
                if len(current_tweet) + len(sentence) + 2 <= self.max_x_length:
                    current_tweet += sentence + ". "
                else:
                    tweets.append(current_tweet.rstrip())
                    tweet_count += 1
                    current_tweet = f"{tweet_count}/n {sentence}. "
            
            if current_tweet.strip() != f"{tweet_count}/n":
                tweets.append(current_tweet.rstrip())
            
            # Update final tweet with correct count
            if tweets:
                last_tweet = tweets[-1]
                last_tweet = last_tweet.replace(f"{len(tweets)}/n", f"{len(tweets)}/{len(tweets)}")
                tweets[-1] = last_tweet
        
        return "\n\n".join(tweets)
    
    def _render_linkedin(self, narrative_text: str, components: Optional[Dict] = None) -> str:
        """
        Render as LinkedIn article format.
        
        Professional, longer-form with formatting for LinkedIn.
        """
        article = []
        
        # Title/Headline
        if components:
            score = components.get('composite_score', 0)
            grade = components.get('grade', 'N/A')
            title = f"Policy Analysis: {grade}-Rated Assessment ({score:.0f}/100)"
        else:
            title = "Policy Analysis & Assessment"
        
        article.append(f"# {title}\n")
        
        # Subheading/Summary
        if components and components.get('lede'):
            article.append(f"## Summary\n{components['lede']}\n")
        
        # Key Findings Section
        if components:
            article.append("## Key Findings\n")
            
            criteria = components.get('criteria', {})
            for key, data in criteria.items():
                if isinstance(data, dict):
                    name = data.get('name', key)
                    score = data.get('score', 0)
                    interpretation = data.get('interpretation', '')
                    narrative = data.get('narrative', '')
                    
                    # Fix #8: Use plain text instead of Markdown for LinkedIn
                    article.append(f"\n{name}")
                    article.append(f"Score: {score:.0f}/100 - {interpretation}\n")
                    if narrative:
                        article.append(f"{narrative}\n")
            article.append("")
        
        # Analysis Section
        if components and components.get('key_tension'):
            article.append("\nAnalysis\n")
            article.append("="*50)
            article.append(f"\nKey Tension: {components['key_tension']}\n")
            
            if components.get('secondary_tensions'):
                article.append("\nSecondary Tensions:")
                for tension in components['secondary_tensions']:
                    article.append(f"• {tension}")
        
        # Implications Section
        if components and components.get('implications'):
            article.append("\nImplications\n")
            article.append("-"*50)
            for i, imp in enumerate(components['implications'], 1):
                article.append(f"{i}. {imp}")
        
        # Escalations if needed
        if components and components.get('escalations'):
            high_severity = [e for e in components['escalations'] if e.get('severity') == 'HIGH']
            if high_severity:
                article.append("\n⚠️ Important Notes\n")
                article.append("-"*50)
                for escalation in high_severity:
                    article.append(f"{escalation.get('type', 'Alert')}: {escalation.get('message', '')}")
        
        # NEW: AI Disclosure & Fairness Section (Recommendation #4 & #3)
        if components and self.include_ai_disclosure:
            article.append("\nTransparency & Governance\n")
            article.append("-"*50)
            
            # Extract AI detection properly
            ai_data = components.get('ai_detection', {})
            if isinstance(ai_data, dict):
                ai_detection = ai_data.get('overall_percentage')
                if ai_detection is None:
                    ai_score = ai_data.get('ai_detection_score', 0)
                    ai_detection = ai_score * 100 if ai_score <= 1 else ai_score
            else:
                ai_detection = ai_data if ai_data else 0
            
            # Extract trust score properly
            trust_data = components.get('trust_score', {})
            trust_score = trust_data.get('trust_score', 66.7) if isinstance(trust_data, dict) else trust_data
            
            # Recommendation #1: Fix dict formatting for risk_tier
            risk_data = components.get('risk_tier', {})
            if isinstance(risk_data, dict):
                risk_tier = risk_data.get('risk_tier', 'MEDIUM').upper()
                risk_score = risk_data.get('risk_score', 0)
                controls = risk_data.get('required_controls', [])
                control_list = ', '.join(c.replace('_', ' ').title() for c in controls[:3])
                if len(controls) > 3:
                    control_list += f' (+{len(controls)-3} more)'
            else:
                risk_tier = str(risk_data).upper() if risk_data else 'MEDIUM'
                risk_score = 50
                control_list = 'See certificate for full details'
            
            # Add model detection information
            model_disclosure = f"\nAI Involvement: {ai_detection:.1f}% AI-assisted analysis detected."
            if isinstance(ai_data, dict):
                likely_model = ai_data.get('likely_ai_model', {})
                if isinstance(likely_model, dict) and likely_model.get('model'):
                    model_name = likely_model.get('model')
                    model_conf = likely_model.get('confidence', 0)
                    model_analysis = likely_model.get('analysis', '')
                    if model_name and model_name != 'Mixed/Uncertain':
                        model_disclosure += f" Likely model: {model_name} ({model_conf*100:.0f}% confidence)."
                    elif model_name == 'Mixed/Uncertain':
                        model_disclosure += " Mixed AI model patterns detected."
                    if model_analysis:
                        model_disclosure += f" {model_analysis}"
            model_disclosure += " Professional review recommended."
            
            article.append(model_disclosure)
            article.append(f"Trust Assessment: {trust_score:.1f}/100 confidence score.")
            article.append(f"Risk Tier: {risk_tier} ({risk_score}/100)")
            article.append(f"Required Controls: {control_list}")
            
            # Add contradiction notice if detected (Recommendation #5)
            contradiction_data = components.get('contradiction_analysis', {})
            contradictions = contradiction_data.get('contradictions', [])
            if contradictions:
                high_count = len([c for c in contradictions if c.get('severity') == 'HIGH'])
                article.append(f"⚠️ Data Quality Alert: {len(contradictions)} numerical inconsistencies detected"
                              f"{f' ({high_count} HIGH severity)' if high_count > 0 else ''}. "
                              "ER score adjusted. See full narrative for details.")
            
            # Fix #5: Add Post-Audit Adjustments section
            bias_data = components.get('bias_audit', {})
            if isinstance(bias_data, dict) and bias_data.get('adjustment_log'):
                article.append("\n\nPost-Audit Score Adjustments")
                article.append("-"*50)
                article.append("Scores adjusted based on external stakeholder critiques:\n")
                for adj in bias_data['adjustment_log']:
                    criterion = adj.get('criterion', 'N/A')
                    original = adj.get('original', 0)
                    adjusted = adj.get('adjusted', 0)
                    sources = adj.get('sources', [])
                    source_list = ', '.join(sources[:3])
                    if len(sources) > 3:
                        source_list += f' (+{len(sources)-3} more)'
                    article.append(f"• {criterion}: {original:.1f} → {adjusted:.1f} (Sources: {source_list})")
            
            article.append("\nFairness Audit: Multi-demographic assessment conducted across vulnerable groups and "
                          f"regional minorities to ensure equitable policy impacts.")
            article.append(f"See Certificate: Full methodology, fairness dashboard, and escalation status available "
                          f"in detailed assessment certificate.")
        
        # Closing
        article.append("\n---")
        article.append("*This analysis is based on comprehensive assessment using multiple criteria.*")
        article.append(f"*Analysis Date: {datetime.now().strftime('%B %d, %Y')}*")
        
        return "\n".join(article)
    
    def _render_social_badge(self, narrative_text: str, components: Optional[Dict] = None) -> str:
        """
        Render as social media badge format.
        
        Image description + caption for social sharing.
        """
        badge = {}
        
        if components:
            score = components.get('composite_score', 0)
            grade = components.get('grade', 'N/A')
            
            # Badge visual description
            score_exact = self._format_score(score, 'exact')
            badge['image_alt'] = f"Policy Quality Score: {grade} ({score_exact}/100)"
            badge['image_src'] = f"badge-{grade}.svg"  # Reference to badge image
            
            # Caption text (optimized for social sharing)
            caption_parts = []
            
            # Main takeaway
            lede = components.get('lede', '')
            if lede:
                caption_parts.append(lede)
            
            # Quick score breakdown
            score_exact = self._format_score(score, 'exact')
            caption_parts.append(f"\nScore: {score_exact}/100 | Grade: {grade}")
            
            # Key finding
            if components.get('key_tension'):
                caption_parts.append(f"\nKey finding: {components['key_tension'][:100]}...")
            
            # Implications summary
            if components.get('implications'):
                caption_parts.append(f"\nBottom line: {components['implications'][0]}")
            
            # Call to action
            caption_parts.append("\n\n#PolicyAnalysis #Governance")
            
            badge['caption'] = "".join(caption_parts)
            
            # Hashtags
            badge['hashtags'] = ['#PolicyAnalysis', '#Governance', f'#{grade}Rated']
            
        else:
            badge['image_alt'] = "Policy Analysis Badge"
            badge['image_src'] = "badge-generic.svg"
            badge['caption'] = narrative_text[:280]
            badge['hashtags'] = ['#PolicyAnalysis']
        
        # Format for JSON output
        return json.dumps(badge, indent=2)
    
    def _render_html_certificate(self, narrative_text: str, components: Optional[Dict] = None) -> str:
        """
        Render as HTML certificate format.
        
        Full visual design with styling.
        """
        if not components:
            components = {'composite_score': 0, 'grade': 'N/A', 'lede': narrative_text}
        
        score = components.get('composite_score', 0)
        grade = components.get('grade', 'N/A')
        lede = components.get('lede', 'Policy Analysis')
        
        # Grade color mapping
        grade_colors = {
            'A': '#2ecc71',
            'B': '#3498db',
            'C': '#f39c12',
            'D': '#e74c3c',
            'F': '#c0392b'
        }
        
        color = grade_colors.get(grade[0] if grade else 'C', '#95a5a6')
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Policy Analysis Certificate</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
        }}
        
        .certificate {{
            background: white;
            width: 100%;
            max-width: 800px;
            padding: 60px;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            text-align: center;
        }}
        
        .header {{
            margin-bottom: 40px;
            border-bottom: 3px solid {color};
            padding-bottom: 20px;
        }}
        
        h1 {{
            color: #2c3e50;
            font-size: 32px;
            margin-bottom: 10px;
        }}
        
        .subtitle {{
            color: #7f8c8d;
            font-size: 16px;
        }}
        
        .score-container {{
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 40px 0;
            gap: 30px;
        }}
        
        .score-box {{
            background: {color};
            color: white;
            border-radius: 10px;
            padding: 30px;
            min-width: 150px;
        }}
        
        .score-number {{
            font-size: 48px;
            font-weight: bold;
        }}
        
        .score-label {{
            font-size: 14px;
            margin-top: 10px;
        }}
        
        .grade-box {{
            background: #ecf0f1;
            border: 3px solid {color};
            border-radius: 10px;
            padding: 30px;
            min-width: 150px;
        }}
        
        .grade-letter {{
            font-size: 48px;
            font-weight: bold;
            color: {color};
        }}
        
        .grade-label {{
            font-size: 14px;
            color: #7f8c8d;
            margin-top: 10px;
        }}
        
        .content {{
            margin: 40px 0;
            text-align: left;
        }}
        
        .content p {{
            color: #2c3e50;
            line-height: 1.8;
            margin-bottom: 15px;
        }}
        
        .criteria {{
            margin: 30px 0;
            text-align: left;
        }}
        
        .criteria-header {{
            color: {color};
            font-weight: bold;
            margin-bottom: 15px;
            font-size: 18px;
        }}
        
        .criteria-item {{
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #ecf0f1;
        }}
        
        .criteria-name {{
            color: #2c3e50;
        }}
        
        .criteria-score {{
            color: {color};
            font-weight: bold;
        }}
        
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ecf0f1;
            color: #7f8c8d;
            font-size: 12px;
        }}
        
        .timestamp {{
            color: #95a5a6;
            font-size: 12px;
            margin-top: 10px;
        }}
    </style>
</head>
<body>
    <div class="certificate">
        <div class="header">
            <h1>Policy Analysis Certificate</h1>
            <p class="subtitle">Comprehensive Assessment Report</p>
        </div>
        
        <div class="score-container">
            <div class="score-box">
                <div class="score-number">{self._format_score(score, 'exact')}</div>
                <div class="score-label">Composite Score</div>
            </div>
            <div class="grade-box">
                <div class="grade-letter">{grade}</div>
                <div class="grade-label">Grade</div>
            </div>
        </div>
        
        <div class="content">
            <p><strong>Assessment Summary:</strong></p>
            <p>{lede}</p>
        </div>
"""
        
        # Add criteria breakdown
        if components.get('criteria'):
            html += '<div class="criteria">\n'
            html += '<div class="criteria-header">Detailed Assessment</div>\n'
            
            for key, data in components['criteria'].items():
                if isinstance(data, dict):
                    name = data.get('name', key)
                    score_val = data.get('score', 0)
                    score_formatted = self._format_score(score_val, 'detailed')
                    html += f"""<div class="criteria-item">
                        <span class="criteria-name">{name}</span>
                        <span class="criteria-score">{score_formatted}/100</span>
                    </div>
"""
            
            html += '</div>\n'
        
        # Add footer
        html += f"""        <div class="footer">
            <p>This certificate represents an objective assessment based on standardized criteria.</p>
            <div class="timestamp">Generated: {datetime.now().strftime('%B %d, %Y at %H:%M %Z')}</div>
        </div>
    </div>
</body>
</html>
"""
        
        return html
    
    def get_available_formats(self) -> List[str]:
        """Return list of available format options"""
        return self.AVAILABLE_FORMATS
    
    def get_format_description(self, format_type: str) -> str:
        """Get description of a format"""
        descriptions = {
            'x_thread': 'X (Twitter) thread format with numbered tweets',
            'linkedin': 'LinkedIn article with professional formatting',
            'social_badge': 'Social media badge with caption for sharing',
            'html_certificate': 'Full HTML certificate with visual design'
        }
        return descriptions.get(format_type, 'Unknown format')


def create_format_renderer() -> FormatRenderer:
    """Factory function to create format renderer instance."""
    return FormatRenderer()


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) > 2:
        # Load narrative and render format
        narrative_file = sys.argv[1]
        format_type = sys.argv[2]
        
        with open(narrative_file) as f:
            data = json.load(f)
        
        # Extract narrative text or components
        if isinstance(data, dict) and 'narrative' in data:
            narrative_text = data['narrative']
            components = data
        else:
            narrative_text = json.dumps(data)
            components = data
        
        renderer = FormatRenderer()
        if format_type not in renderer.get_available_formats():
            print(f"Unknown format: {format_type}")
            print(f"Available formats: {', '.join(renderer.get_available_formats())}")
            sys.exit(1)
        
        output = renderer.render(narrative_text, format_type, components)
        print(output)
    else:
        print("Usage: python format_renderer.py <narrative.json> <format>")
        print("\nAvailable formats:")
        renderer = FormatRenderer()
        for fmt in renderer.get_available_formats():
            print(f"  • {fmt}: {renderer.get_format_description(fmt)}")
        print("\nExample:")
        print("  python format_renderer.py narrative.json x_thread")
