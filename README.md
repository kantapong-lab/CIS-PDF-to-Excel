# CIS PDF to Excel
Convert CIS PDF benchmarks to Directus-compatible JSON format. Useful for importing CIS Benchmark rules into Directus CMS for compliance tracking and management.


## Description

Reads CIS pdf benchmark and extracts comprehensive rule information for Directus import:
1. **Rule ID** - CIS benchmark rule identifier (e.g., 1.1, 3.2.4)
2. **Title** - Rule title/description
3. **Description** - Detailed rationale and context
4. **Audit** - Commands/procedures to check compliance
5. **Remediation** - Steps to achieve compliance
6. **Assessment Status** - Classification of assessment method:
   - `manual` - Requires human validation
   - `automated` - Fully automated check
   - `not_specified` - Unable to determine
7. **Profile Level** - CIS security priority level:
   - `level_1` - Practical, prudent, baseline security
   - `level_2` - Defense in depth, additional security
   - `not_specified` - Unable to determine

Exports data into Directus-compatible JSON structure with framework metadata and rules array


## Installation

1. **Install Java** (required for Apache Tika PDF parsing)
   ```bash
   # Verify Java installation
   java -version
   ```

2. **Install Python dependencies**
   ```bash
   pip install tika
   ```

3. **Get the scripts**
   - `cis_to_excel.py` - Main PDF parser
   - `process_all_pdfs.py` - Batch processing script (optional)

## Usage

### Method 1: Single File Processing

Process a specific CIS Benchmark PDF:

```bash
python cis_to_excel.py <pdf_file> output
```

**Example:**
```bash
python cis_to_excel.py pdf/CIS_Amazon_Web_Services_Foundations_Benchmark_v6.0.0.pdf output
```

**Output:** Creates `output/<pdf_name>/` directory containing:
- `framework.json` - Framework metadata with UUID
- `rules.json` - Array of rules with all extracted fields


### Method 2: Batch Processing (Recommended)

Process all PDF files in the `pdf/` folder automatically:

```bash
python process_all_pdfs.py
```

**Features:**
- Auto-discovers all `*.pdf` files in `pdf/` directory
- Processes each file sequentially with progress tracking
- Shows processing status (e.g., "Processing 1/2: filename.pdf")
- Generates summary report (total/successful/failed counts)
- Creates separate output directory for each PDF

**Note:** Place all CIS Benchmark PDFs in the `pdf/` subfolder before running.


## Output Structure

Each processed PDF generates a folder in `output/` with the following structure:

```
output/
└── CIS_Amazon_Web_Services_Foundations_Benchmark_v6.0.0/
    ├── framework.json    # Framework metadata
    ├── rules.json        # Array of rules
    ├── cis_text.txt      # Extracted text (intermediate)
    └── temp.txt          # Parsed text (intermediate)
```

### framework.json
Contains framework metadata for Directus import:

```json
{
  "id": "0cbf5bf5-73fa-4ddc-b502-66bce1f6115c",
  "name": "CIS Amazon Web Services Foundations Benchmark v6.0.0",
  "version": "6.0.0"
}
```

### rules.json
Array of rules with comprehensive fields:

```json
[
  {
    "id": "uuid-generated",
    "framework": "0cbf5bf5-73fa-4ddc-b502-66bce1f6115c",
    "rule_id": "1.1",
    "title": "Maintain current contact details",
    "assessment_status": "manual",
    "profile_level": "level_1",
    "details": {
      "description": "AWS account contact information...",
      "audit": "From Console: 1. Sign in to AWS Console...",
      "remediation": "Perform the following to update contact details..."
    }
  }
]
```

**Field Values:**
- `assessment_status`: `manual` | `automated` | `not_specified`
- `profile_level`: `level_1` | `level_2` | `not_specified`

## Screenshots (Legacy)

> **Note:** The screenshots below show the legacy Excel output format. The current version generates Directus-compatible JSON format instead.

![Alt text](screen1.png)

![Alt text](screen2.png)

![Alt text](screen3.png)