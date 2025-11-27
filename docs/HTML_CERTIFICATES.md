# HTML Certificates for Sparrow SPOT Scale™ v4.0

**Status:** ✅ NEW FEATURE IN v4.0  
**Date Added:** November 12, 2025  

---

## 🎓 What Are HTML Certificates?

Professional grading certificates are automatically generated alongside JSON and text reports. Each certificate is a beautiful, print-ready HTML document that displays:

- ✅ Official Sparrow SPOT Scale™ branding
- ✅ Document evaluation details
- ✅ All category scores (color-coded by grade)
- ✅ Composite score with letter grade
- ✅ Policy classification or credibility assessment
- ✅ Evaluation date
- ✅ Verification seal

---

## 📋 Certificate Types

### Policy Certificate (SPOT-Policy™)

**When Generated:** `--variant policy`

**Shows:**
- Fiscal Transparency (FT)
- Stakeholder Balance (SB)
- Economic Rigor (ER)
- Public Accessibility (PA)
- Policy Consequentiality (PC)

**Classification Examples:**
- Exemplary Policy
- Excellent Policy
- Good Policy
- Acceptable Policy
- Questionable Policy
- Problematic Policy
- Flawed Policy
- Unacceptable Policy

**Color Scheme:** Blue & cyan

### Journalism Certificate (SPARROW Scale™)

**When Generated:** `--variant journalism`

**Shows:**
- Source Integrity (SI)
- Objectivity Index (OI)
- Technical Precision (TP)
- Accessibility Rating (AR)
- Impact Utility (IU)

**Classification Examples:**
- Exemplary Journalism
- Excellent Journalism
- Good Journalism
- Acceptable Journalism
- Questionable Journalism
- Problematic Journalism
- Flawed Journalism
- Poor Journalism

**Color Scheme:** Purple & gold

---

## 🚀 How to Use

### Automatic Generation

Certificates are generated automatically when you run the grader:

```bash
# Policy grading - creates 3 files
python sparrow_grader_v4.py budget.pdf --variant policy -o report
# Output:
#   report.json                    (structured data)
#   report.txt                     (text summary)
#   report_certificate.html        (certificate) ✨ NEW

# Journalism grading - creates 3 files  
python sparrow_grader_v4.py article.txt --variant journalism -o article
# Output:
#   article.json                   (structured data)
#   article.txt                    (text summary)
#   article_certificate.html       (certificate) ✨ NEW
```

### Viewing Certificates

#### In a Web Browser
```bash
# Open in default browser
open report_certificate.html           # macOS
xdg-open report_certificate.html       # Linux
start report_certificate.html          # Windows
```

#### Printing to PDF
1. Open certificate in browser
2. Press `Ctrl+P` (or `Cmd+P` on Mac)
3. Select "Save as PDF"
4. Choose location and filename

#### Sharing
- Email the `.html` file
- Upload to website (self-contained, no images needed)
- Include in reports and documentation

---

## 🎨 Certificate Features

### Responsive Design
- Displays perfectly on all screen sizes
- Landscape orientation optimized
- Print-friendly format

### Color-Coded Grades
```
A+ / A (Green)      ✓ Excellent
B+ / B (Blue)       ✓ Good
C (Orange)          ⚠️  Fair
D (Red)             ❌ Poor
F (Dark Red)        ❌ Failing
```

### Professional Styling
- Elegant serif fonts
- Gradient backgrounds
- Border decorations
- Verification seal
- Signature lines
- Official branding

### Self-Contained
- No external images needed
- All CSS inline
- Works offline
- No internet connection required
- Print from any device

---

## 📊 Certificate Example

### Policy Certificate for "2025 Budget"
```
┌─────────────────────────────────────────────────────────────────┐
│                   🎯 Sparrow SPOT Scale™                         │
│          Policy Document Grading Certificate                     │
│                                                                   │
│            Certificate of Evaluation                             │
│                                                                   │
│                   2025 Budget                                    │
│                                                                   │
│              ┌─────────────────────────────┐                     │
│              │ FT    84.2/100               │                     │
│              │ SB    82.3/100               │                     │
│              │ ER    75.2/100               │                     │
│              │ PA    85.0/100               │                     │
│              │ PC    97.1/100               │                     │
│              ├─────────────────────────────┤                     │
│              │ Overall: 84.4/100 (B+)      │                     │
│              └─────────────────────────────┘                     │
│                                                                   │
│              Good Policy                                          │
│                                                                   │
│   Certified By:          Evaluation Date:      VERIFIED ✓        │
│   Sparrow SPOT Scale™    November 12, 2025                       │
│   v4.0                                                            │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔧 Advanced Usage

### Programmatic Certificate Generation

```python
from certificate_generator import CertificateGenerator
import json

# Load existing report
with open('report.json') as f:
    report = json.load(f)

# Create certificate
gen = CertificateGenerator()
gen.generate_policy_certificate(
    report, 
    document_title="My Budget 2025",
    output_file="my_certificate.html"
)
```

### Generate from Existing JSON

```python
from certificate_generator import CertificateGenerator

gen = CertificateGenerator()

# From saved JSON file
gen.generate_certificate_from_json(
    'report.json',
    variant='policy',
    output_file='new_certificate.html'
)
```

---

## 📝 File Structure

### Generated Files

```
my_grading/
├── report.json                 # Structured data (1-2 KB)
├── report.txt                  # Text summary (200-300 bytes)
└── report_certificate.html     # Certificate (10-12 KB)
```

### Certificate File Size
- Typical: 10-12 KB per certificate
- Single file (no external assets)
- Compresses well for email/sharing

---

## ✨ Certificate Contents

### Header Section
- Sparrow SPOT Scale™ logo
- Certificate type (Policy/Journalism)
- Official title
- Subtitle with framework name

### Document Information
- Document title/name
- Clear identification

### Scores Section
- All category scores
- Full category names
- Individual score displays
- Composite score box
- Grade letter with color

### Classification
- Policy: 8 classification types (Exemplary → Unacceptable)
- Journalism: 8 classification types (Exemplary → Poor)

### Footer
- Certified by: Sparrow SPOT Scale™ v4.0
- Evaluation date (automatic)
- Verification seal with checkmark

---

## 🖨️ Printing & PDF Export

### Print Settings Recommended
```
Page size:      Landscape
Margins:        Minimal (0.25")
Scaling:        Fit to page
Background:     Include
```

### PDF Export
1. Open in browser
2. Print (Ctrl+P / Cmd+P)
3. Select "Save as PDF"
4. Recommended filename: `{document}_sparrow_certificate.pdf`

### Email Format
- Send as `.html` attachment (can be opened in any browser)
- Or: Print to PDF and send `.pdf` version

---

## 🔍 Customization

### Current Customization Points
- Document title (automatic from filename, customizable)
- Output filename (your choice)
- Colors (fixed per variant)
- Evaluation date (automatic)

### Future Customization (v4.1)
- [ ] Custom logo upload
- [ ] Organization name/branding
- [ ] Custom classifications
- [ ] Theme/color selection
- [ ] Signature image

---

## ⚠️ Notes

### Browser Compatibility
- ✅ Chrome/Chromium
- ✅ Firefox
- ✅ Safari
- ✅ Edge
- ✅ Mobile browsers

### Print Quality
- Best printed at: 300 DPI
- Landscape orientation recommended
- Color printer recommended (but B&W acceptable)

### Digital Sharing
- Self-contained (no links to external resources)
- Works offline (no internet needed)
- Compatible with all email clients
- Can be uploaded to websites

---

## 📚 Quick Reference

### Generate Certificate
```bash
python sparrow_grader_v4.py document.pdf --variant policy -o report
# Creates: report_certificate.html
```

### View Certificate
```bash
open report_certificate.html
```

### Print to PDF
```bash
# Browser: Ctrl+P → Save as PDF
```

### Share
```bash
email report_certificate.html to stakeholders
```

---

## 📞 Support

### Issues with Certificate Generation
- Check if `certificate_generator.py` exists in root directory
- Verify JSON report was created successfully
- Check console for error messages

### Certificate Not Displaying Correctly
- Try different browser
- Check that report JSON is valid
- Ensure HTML file wasn't corrupted

### Customization Requests
- Planned for v4.1 release
- File an issue with specific requirements

---

## 🎉 Examples

### Policy Certificate Generated
```bash
$ python sparrow_grader_v4.py 2025-Budget.pdf --variant policy -o budget
✓ Certificate: budget_certificate.html
```

### Journalism Certificate Generated
```bash
$ python sparrow_grader_v4.py article.txt --variant journalism -o article
✓ Certificate: article_certificate.html
```

---

**Certificate Feature Added:** November 12, 2025  
**Status:** ✅ Production Ready  
**Next:** Customize in v4.1
