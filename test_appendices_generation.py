"""
Test Script: Automated Appendices Generation System
Tests the complete pipeline with a sample policy analysis

Run with: python test_appendices_generation.py
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from appendices_generator import AppendicesGenerator


def create_sample_analysis():
    """Create a comprehensive sample analysis for testing."""
    return {
        'title': 'Test Policy Document Analysis',
        'document_title': 'Test Bill 2025',
        'variant': 'Policy Analysis Test',
        'document_info': {
            'type': 'Policy Bill',
            'jurisdiction': 'Canada',
            'date_passed': '2025-01-15'
        },
        
        # Criteria scores
        'criteria': {
            'FT': {
                'name': 'Fiscal Transparency',
                'score': 62.4,
                'evidence': {
                    'Budget Allocations': {
                        'strength': 'MODERATE',
                        'description': 'Clear allocation of funds across 5 departments',
                        'instances': 12
                    },
                    'Cost Analysis': {
                        'strength': 'STRONG',
                        'description': 'Detailed cost-benefit analysis provided in Appendix A',
                        'instances': 1
                    },
                    'Implementation Costs': {
                        'strength': 'MODERATE',
                        'description': 'Estimated costs provided but range varies by scenario',
                        'instances': 3
                    }
                },
                'key_findings': [
                    'Overall fiscal transparency is above average',
                    'Cost estimates could be more precise',
                    'Budget distribution aligns with stated priorities'
                ]
            },
            'SB': {
                'name': 'Stakeholder Balance',
                'score': 48.9,
                'evidence': {
                    'Industry Consultation': {
                        'strength': 'MODERATE',
                        'description': 'Consultation with 3 major industry bodies documented',
                        'instances': 3
                    },
                    'Civil Society Input': {
                        'strength': 'WEAK',
                        'description': 'Limited NGO input in development process',
                        'instances': 1
                    },
                    'Indigenous Perspectives': {
                        'strength': 'WEAK',
                        'description': 'No documented consultation with Indigenous communities',
                        'instances': 0
                    }
                },
                'key_findings': [
                    'Stakeholder engagement is uneven',
                    'Business perspectives well-represented',
                    'Civil society and Indigenous voices underrepresented'
                ]
            },
            'ER': {
                'name': 'Economic Rigor',
                'score': 71.2,
                'evidence': {
                    'Data Quality': {
                        'strength': 'STRONG',
                        'description': 'Uses Statistics Canada and OECD data',
                        'instances': 8
                    },
                    'Analysis Depth': {
                        'strength': 'MODERATE',
                        'description': 'Reasonable economic modeling, some simplifications',
                        'instances': 5
                    },
                    'Assumptions Transparency': {
                        'strength': 'STRONG',
                        'description': 'All modeling assumptions explicitly stated',
                        'instances': 12
                    }
                },
                'key_findings': [
                    'Economic analysis is generally rigorous',
                    'Relies on high-quality statistical sources',
                    'Assumptions are clearly documented'
                ]
            },
            'PA': {
                'name': 'Public Accessibility',
                'score': 55.7,
                'evidence': {
                    'Language Clarity': {
                        'strength': 'MODERATE',
                        'description': 'Generally clear but some technical jargon remains',
                        'instances': 4
                    },
                    'Summary Availability': {
                        'strength': 'MODERATE',
                        'description': 'Executive summary provided, could be more comprehensive',
                        'instances': 1
                    },
                    'Visual Aids': {
                        'strength': 'WEAK',
                        'description': 'Limited charts and diagrams for non-expert readers',
                        'instances': 3
                    }
                },
                'key_findings': [
                    'Document requires some policy background',
                    'Key information is present but not always easily findable',
                    'More visual aids would improve accessibility'
                ]
            },
            'PC': {
                'name': 'Policy Consequentiality',
                'score': 66.3,
                'evidence': {
                    'Impact Analysis': {
                        'strength': 'STRONG',
                        'description': 'Comprehensive analysis of policy impacts on 6 stakeholder groups',
                        'instances': 6
                    },
                    'Unintended Consequences': {
                        'strength': 'MODERATE',
                        'description': 'Some consideration of secondary effects',
                        'instances': 3
                    },
                    'Long-term Effects': {
                        'strength': 'MODERATE',
                        'description': '5-year projections provided, 10-year effects unclear',
                        'instances': 2
                    }
                },
                'key_findings': [
                    'Policy impacts are well-documented',
                    'Short-term effects clear, long-term effects less certain',
                    'Stakeholder impact analysis is comprehensive'
                ]
            },
            'CA': {
                'name': 'Constitutional Alignment',
                'score': 73.5,
                'evidence': {
                    'Charter Compliance': {
                        'strength': 'STRONG',
                        'description': 'Policy reviewed against Charter of Rights and Freedoms',
                        'instances': 4
                    },
                    'Federal Jurisdiction': {
                        'strength': 'STRONG',
                        'description': 'Powers clearly within federal jurisdiction',
                        'instances': 3
                    },
                    'Division of Powers': {
                        'strength': 'MODERATE',
                        'description': 'Some provincial coordination required',
                        'instances': 2
                    }
                },
                'key_findings': [
                    'Policy is constitutionally sound',
                    'Charter compliance confirmed',
                    'Within clear federal jurisdiction'
                ]
            }
        },
        
        # Trust and risk scores
        'trust_score': {
            'trust_score': 63.5,
            'component_scores': {
                'Credibility': 68.0,
                'Evidence': 61.0,
                'Objectivity': 62.0,
                'Completeness': 63.0
            }
        },
        
        'risk_tier': {
            'risk_tier': 'MEDIUM',
            'reasoning': 'Average scores across criteria with some gaps in stakeholder balance and accessibility'
        },
        
        'ai_detection': {
            'overall_percentage': 22.5,
            'confidence': 'HIGH',
            'by_component': {
                'Criteria Scoring': 25.0,
                'Evidence Collection': 20.0,
                'Risk Assessment': 15.0,
                'Narrative Generation': 28.0
            }
        },
        
        # Additional findings
        'major_findings': [
            'Policy demonstrates strong fiscal transparency with clear budget allocations',
            'Stakeholder engagement is uneven with underrepresentation of civil society',
            'Economic analysis is rigorous but relies heavily on baseline assumptions',
            'Accessibility could be improved through visual aids and simplified language',
            'Policy impacts are comprehensively analyzed with focus on short-term effects',
            'Constitutional compliance is strong with clear jurisdictional basis'
        ],
        
        'implementation_concerns': [
            'Stakeholder coordination will be critical for successful implementation',
            'Accessibility of plain-language guidance materials should be improved',
            'Long-term financial sustainability requires monitoring and adjustment',
            'Indigenous consultation process should be strengthened for future iterations'
        ],
        
        'recommendations': [
            'Expand stakeholder consultation to include more diverse civil society voices',
            'Develop visual aids and infographics for public-facing materials',
            'Establish monitoring framework for unintended consequences',
            'Create plain-language summary for broader public understanding',
            'Strengthen consultation with Indigenous communities before implementation',
            'Document lessons learned for future policy development'
        ]
    }


def main():
    """Run the appendices generation test."""
    print("\n" + "="*80)
    print("APPENDICES GENERATION SYSTEM - TEST RUN")
    print("="*80 + "\n")
    
    # Create sample analysis
    print("📋 Creating sample analysis...")
    analysis = create_sample_analysis()
    print(f"   ✓ Sample analysis created with {len(analysis.get('criteria', {}))} criteria\n")
    
    # Initialize generator
    print("🔧 Initializing AppendicesGenerator...")
    generator = AppendicesGenerator()
    print("   ✓ Generator initialized\n")
    
    # Generate appendices
    print("🚀 Generating appendices...")
    try:
        appendices = generator.generate_all_appendices(
            analysis,
            document_title=analysis['document_title'],
            include_index=True
        )
        print(f"   ✓ Generated {len(appendices)} items\n")
        
    except Exception as e:
        print(f"   ❌ Error generating appendices: {e}\n")
        import traceback
        traceback.print_exc()
        return False
    
    # Display metadata
    print("📊 Generation Metadata:")
    metadata = appendices.get('metadata', {})
    for key, value in metadata.items():
        print(f"   • {key}: {value}")
    print()
    
    # Show appendices summary
    print("📚 Generated Appendices:")
    appendix_keys = ['appendix_a', 'appendix_b', 'appendix_c', 'appendix_d', 'appendix_e', 'navigation_index']
    for key in appendix_keys:
        if key in appendices:
            content = appendices[key]
            word_count = len(content.split()) if isinstance(content, str) else 0
            line_count = len(content.split('\n')) if isinstance(content, str) else 0
            
            if key == 'appendix_a':
                title = "Appendix A: Evidence Citations"
            elif key == 'appendix_b':
                title = "Appendix B: Methodology"
            elif key == 'appendix_c':
                title = "Appendix C: Component Disclosure"
            elif key == 'appendix_d':
                title = "Appendix D: Bill Findings"
            elif key == 'appendix_e':
                title = "Appendix E: Verification Guide"
            else:
                title = "Navigation Index"
            
            print(f"   ✓ {title}")
            print(f"     - Words: {word_count:,}")
            print(f"     - Lines: {line_count}")
    
    print()
    
    # Save appendices to test directory
    output_dir = Path('/home/gene/Sparrow-SPOT-Policy/test_appendices_output')
    print(f"💾 Saving appendices to {output_dir}...")
    
    try:
        saved_files = generator.save_appendices(appendices, str(output_dir))
        for key, filepath in saved_files.items():
            print(f"   ✓ Saved {key} to {Path(filepath).name}")
        print()
        
    except Exception as e:
        print(f"   ❌ Error saving appendices: {e}\n")
        import traceback
        traceback.print_exc()
        return False
    
    # Display sample content
    print("📖 Sample Content - First 500 characters from each appendix:\n")
    
    for key in appendix_keys:
        if key in appendices:
            content = appendices[key]
            if isinstance(content, str):
                sample = content[:500] + "..." if len(content) > 500 else content
                
                # Format title
                if key == 'appendix_a':
                    print("─" * 80)
                    print("APPENDIX A: EVIDENCE CITATIONS")
                    print("─" * 80)
                elif key == 'appendix_b':
                    print("─" * 80)
                    print("APPENDIX B: METHODOLOGY")
                    print("─" * 80)
                elif key == 'appendix_c':
                    print("─" * 80)
                    print("APPENDIX C: COMPONENT DISCLOSURE")
                    print("─" * 80)
                elif key == 'appendix_d':
                    print("─" * 80)
                    print("APPENDIX D: BILL-SPECIFIC FINDINGS")
                    print("─" * 80)
                elif key == 'appendix_e':
                    print("─" * 80)
                    print("APPENDIX E: VERIFICATION GUIDE")
                    print("─" * 80)
                else:
                    print("─" * 80)
                    print("NAVIGATION INDEX")
                    print("─" * 80)
                
                print(sample)
                print()
    
    # Final summary
    print("="*80)
    print("✅ APPENDICES GENERATION TEST COMPLETED SUCCESSFULLY")
    print("="*80)
    print(f"\n📁 All outputs saved to: {output_dir}")
    print("\n📋 Generated Files:")
    for filepath in sorted(output_dir.glob('*.md')):
        print(f"   • {filepath.name}")
    
    if (output_dir / 'METADATA.json').exists():
        print(f"   • METADATA.json")
    
    print("\n✨ Next Steps:")
    print("   1. Review appendices in test_appendices_output/")
    print("   2. Run GUI with: python gui/sparrow_gui.py")
    print("   3. Upload a real policy document and test pipeline")
    print("   4. Check 'Appendices' tab for auto-generated outputs")
    
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
