"""
Data Lineage Visualization for Sparrow SPOT Scale™ v8.4.0

Generates visual flowcharts showing document analysis pipeline and data flow.

Status values:
- completed: Stage ran successfully
- skipped: Stage was not enabled (optional feature)
- pending: Stage not yet run (only during active processing)
- failed: Stage encountered an error
- not_applicable: Stage does not apply to this document type (v8.4.0)
"""

from typing import Dict, List
from datetime import datetime

VERSION = "8.4.0"


class DataLineageVisualizer:
    """Generate data lineage visualizations for document analysis."""
    
    def __init__(self):
        """Initialize lineage visualizer."""
        self.stages = []
        self.current_stage = None
    
    def add_stage(self, name: str, description: str, status: str = "completed"):
        """
        Add a stage to the lineage pipeline.
        
        Args:
            name: Stage name
            description: What happens in this stage
            status: pending, in-progress, completed, skipped, failed
                    Default is 'completed' since stages are usually added after completion.
        """
        stage = {
            "name": name,
            "description": description,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "details": []
        }
        self.stages.append(stage)
        return len(self.stages) - 1
    
    def update_stage(self, index: int, status: str, details: List[str] = None):
        """Update stage status and add details."""
        if index < len(self.stages):
            self.stages[index]["status"] = status
            if details:
                self.stages[index]["details"].extend(details)
    
    def generate_ascii_flowchart(self) -> str:
        """Generate ASCII art flowchart of analysis pipeline."""
        lines = []
        lines.append("=" * 80)
        lines.append(f"  SPARROW SPOT SCALE™ v{VERSION} - DATA LINEAGE FLOWCHART")
        lines.append("=" * 80)
        lines.append("")
        
        for i, stage in enumerate(self.stages):
            # Status indicator - v8.4.0: Added skipped and not_applicable
            status_icon = {
                "pending": "⏳",
                "in-progress": "🔄",
                "completed": "✅",
                "failed": "❌",
                "skipped": "⏭️",
                "not_applicable": "➖"
            }.get(stage["status"], "❓")
            
            # Stage box
            lines.append(f"┌─ STAGE {i+1}: {stage['name'].upper()}")
            lines.append(f"│  {status_icon} Status: {stage['status'].title()}")
            lines.append(f"│  📝 {stage['description']}")
            
            # Details
            if stage["details"]:
                lines.append("│  Details:")
                for detail in stage["details"]:
                    lines.append(f"│    • {detail}")
            
            lines.append("└" + "─" * 78)
            
            # Arrow to next stage
            if i < len(self.stages) - 1:
                lines.append("   │")
                lines.append("   ▼")
                lines.append("")
        
        lines.append("")
        lines.append("=" * 80)
        lines.append("  END OF PIPELINE")
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    def generate_html_flowchart(self) -> str:
        """Generate interactive HTML flowchart."""
        html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Data Lineage - Sparrow SPOT Scale™</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 40px;
            margin: 0;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        }
        h1 {
            color: #764ba2;
            text-align: center;
            margin-bottom: 30px;
        }
        .stage {
            background: #f8f9fa;
            border-left: 5px solid #667eea;
            padding: 20px;
            margin: 20px 0;
            border-radius: 5px;
            position: relative;
        }
        .stage.completed {
            border-left-color: #27ae60;
            background: #e8f5e9;
        }
        .stage.failed {
            border-left-color: #e74c3c;
            background: #ffebee;
        }
        .stage.in-progress {
            border-left-color: #f39c12;
            background: #fff3e0;
        }
        .stage.skipped {
            border-left-color: #95a5a6;
            background: #f5f5f5;
        }
        .stage.not_applicable {
            border-left-color: #bdc3c7;
            background: #fafafa;
            opacity: 0.7;
        }
        .stage-header {
            font-size: 1.2em;
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
        }
        .stage-status {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 0.85em;
            font-weight: 600;
            margin-left: 10px;
        }
        .status-completed { background: #27ae60; color: white; }
        .status-failed { background: #e74c3c; color: white; }
        .status-in-progress { background: #f39c12; color: white; }
        .status-pending { background: #95a5a6; color: white; }
        .status-skipped { background: #7f8c8d; color: white; }
        .status-not_applicable { background: #bdc3c7; color: #333; }
        .stage-description {
            color: #666;
            margin: 10px 0;
        }
        .stage-details {
            margin-top: 15px;
            padding-left: 20px;
        }
        .stage-details li {
            color: #555;
            margin: 5px 0;
        }
        .arrow {
            text-align: center;
            font-size: 2em;
            color: #667eea;
            margin: 10px 0;
        }
        .metadata {
            background: #e3f2fd;
            padding: 15px;
            border-radius: 5px;
            margin-top: 30px;
        }
        .metadata h3 {
            color: #1976d2;
            margin-top: 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔬 Data Lineage Flowchart</h1>
        <p style="text-align: center; color: #666;">Sparrow SPOT Scale™ v{VERSION} Analysis Pipeline</p>
"""
        
        for i, stage in enumerate(self.stages):
            status_class = f"status-{stage['status']}"
            stage_class = stage['status']
            
            html += f"""
        <div class="stage {stage_class}">
            <div class="stage-header">
                Stage {i+1}: {stage['name']}
                <span class="stage-status {status_class}">{stage['status'].title()}</span>
            </div>
            <div class="stage-description">{stage['description']}</div>
"""
            
            if stage["details"]:
                html += "            <div class='stage-details'><ul>\n"
                for detail in stage["details"]:
                    html += f"                <li>{detail}</li>\n"
                html += "            </ul></div>\n"
            
            html += "        </div>\n"
            
            if i < len(self.stages) - 1:
                html += "        <div class='arrow'>▼</div>\n"
        
        html += f"""
        <div class="metadata">
            <h3>Pipeline Metadata</h3>
            <p><strong>Total Stages:</strong> {len(self.stages)}</p>
            <p><strong>Completed:</strong> {sum(1 for s in self.stages if s['status'] == 'completed')}</p>
            <p><strong>Failed:</strong> {sum(1 for s in self.stages if s['status'] == 'failed')}</p>
            <p><strong>Skipped:</strong> {sum(1 for s in self.stages if s['status'] == 'skipped')}</p>
            <p><strong>Generated:</strong> {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}</p>
        </div>
    </div>
</body>
</html>
"""
        
        # Replace version placeholder with actual version
        html = html.replace('{VERSION}', VERSION)
        
        return html
    
    def generate_json_lineage(self) -> Dict:
        """Generate JSON representation of lineage for programmatic use."""
        return {
            "pipeline": f"Sparrow SPOT Scale v{VERSION}",
            "timestamp": datetime.now().isoformat(),
            "total_stages": len(self.stages),
            "completed_stages": sum(1 for s in self.stages if s["status"] == "completed"),
            "failed_stages": sum(1 for s in self.stages if s["status"] == "failed"),
            "skipped_stages": sum(1 for s in self.stages if s["status"] == "skipped"),
            "stages": self.stages
        }
    
    @staticmethod
    def create_standard_pipeline() -> 'DataLineageVisualizer':
        """Create a standard v8.2 analysis pipeline template."""
        viz = DataLineageVisualizer()
        
        viz.add_stage(
            "Document Ingestion",
            "Load and parse input document (PDF, TXT, DOCX)",
            "pending"
        )
        
        viz.add_stage(
            "Text Extraction",
            "Extract text content and structure from document",
            "pending"
        )
        
        viz.add_stage(
            "Provenance Analysis",
            "Extract metadata, file hash, creation tools, author info",
            "pending"
        )
        
        viz.add_stage(
            "SPOT Grading",
            "Multi-dimensional quality assessment (FT, SB, ER, PA, PC)",
            "pending"
        )
        
        viz.add_stage(
            "AI Detection",
            "Basic AI content detection and model identification",
            "pending"
        )
        
        viz.add_stage(
            "Deep Analysis (Optional)",
            "6-level AI transparency analysis if --deep-analysis flag enabled",
            "pending"
        )
        
        viz.add_stage(
            "Ethical Framework",
            "Trust score, bias audit, risk classification, fairness metrics",
            "pending"
        )
        
        viz.add_stage(
            "Narrative Generation (Optional)",
            "AI-powered narrative summaries if --narrative-style flag enabled",
            "pending"
        )
        
        viz.add_stage(
            "Certificate Generation",
            "Create HTML certificate with all findings and transparency data",
            "pending"
        )
        
        viz.add_stage(
            "Output Compilation",
            "Save JSON report, text summary, and optional narrative outputs",
            "pending"
        )
        
        return viz


def generate_lineage_report(output_file: str = "lineage_flowchart.html", format: str = "html"):
    """
    Generate a data lineage report.
    
    Args:
        output_file: Output file path
        format: 'html', 'ascii', or 'json'
    """
    viz = DataLineageVisualizer.create_standard_pipeline()
    
    # Mark all as completed for demonstration
    for i in range(len(viz.stages)):
        viz.update_stage(i, "completed")
    
    if format == "html":
        content = viz.generate_html_flowchart()
    elif format == "ascii":
        content = viz.generate_ascii_flowchart()
    elif format == "json":
        import json
        content = json.dumps(viz.generate_json_lineage(), indent=2)
    else:
        raise ValueError(f"Unknown format: {format}")
    
    with open(output_file, 'w') as f:
        f.write(content)
    
    print(f"✅ Lineage flowchart generated: {output_file}")
    return output_file


if __name__ == "__main__":
    import sys
    
    # Command-line usage
    if len(sys.argv) > 1:
        format_arg = sys.argv[1]
    else:
        format_arg = "html"
    
    if format_arg == "ascii":
        output = "lineage_flowchart.txt"
    elif format_arg == "json":
        output = "lineage_flowchart.json"
    else:
        output = "lineage_flowchart.html"
    
    generate_lineage_report(output, format_arg)
