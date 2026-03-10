import re
import sys
import json
import os
import uuid
import tika
tika.initVM()
from tika import parser


cispdf, outfile = "",""

if len(sys.argv) < 3:
	print("[!] Please provide input and output filename!")
	print("Usage: python {} <input.pdf> <output>\n".format(sys.argv[0]))
	print("Note: For <output>, no need to provide file extension.")
	exit()
else:
    cispdf = sys.argv[1]
    outfile = sys.argv[2]

# Extract PDF filename (without extension) for folder name
pdf_basename = os.path.splitext(os.path.basename(cispdf))[0]

# Create output directory structure
output_dir = os.path.join("output", pdf_basename)
os.makedirs(output_dir, exist_ok=True)

# cis text output (save in output directory)
cistext = os.path.join(output_dir, 'cis_text.txt')
temptext = os.path.join(output_dir, 'temp.txt')

#---------------------------------------------------
# Helper functions for Directus transformation
#---------------------------------------------------

def extract_rule_id(title):
    """Extract rule ID like '1.1', '3.1.3', '3.2.4' from title"""
    match = re.match(r'^(\d+(?:\.\d+)+)', title.strip())
    return match.group(1) if match else ""

def extract_severity(title, context=""):
    """Extract assessment status (Manual/Automated) from title or context"""
    # Search in title first, then in context
    match = re.search(r'\((Manual|Automated)\)', title)
    if not match and context:
        match = re.search(r'\((Manual|Automated)\)', context)
    return match.group(1) if match else "not_specified"

def extract_profile_level(context):
    """Extract profile level (Level 1/Level 2) indicating security priority"""
    # Match bullet point followed by Level 1 or Level 2
    match = re.search(r'\u2022?\s*Level\s+([12])', context)
    if match:
        level_num = match.group(1)
        return f"level_{level_num}"
    return "not_specified"

def clean_title(title):
    """Remove rule_id and assessment status from title"""
    # Remove rule_id pattern
    cleaned = re.sub(r'^\d+\.\d+\s*', '', title.strip())
    # Remove severity pattern
    cleaned = re.sub(r'\s*\((Manual|Automated)\)\s*', '', cleaned)
    return cleaned.strip()

def parse_framework_info(pdf_filename):
    """Extract framework name and version from PDF filename"""
    # Extract base filename without extension
    basename = os.path.splitext(os.path.basename(pdf_filename))[0]
    
    # Extract version (e.g., v2.0.0)
    version_match = re.search(r'v?(\d+\.\d+\.\d+)', basename)
    version = version_match.group(1) if version_match else "1.0.0"
    
    # Create readable framework name
    # Remove version and normalize
    name = re.sub(r'_v?\d+\.\d+\.\d+', '', basename)
    name = name.replace('_', ' ').strip()
    # Clean up duplicate words (e.g., "CIS CIS" -> "CIS")
    words = name.split()
    cleaned_words = []
    for word in words:
        if not cleaned_words or word != cleaned_words[-1]:
            cleaned_words.append(word)
    name = ' '.join(cleaned_words)
    
    return {"name": name, "version": version}

#---------------------------------------------------
print("[+] Output will be saved to: {}".format(output_dir))
print("[+] Converting '{}' to text...".format(cispdf))
# tika write get text from pdf
raw = parser.from_file(cispdf)
data = raw['content']

print("[+] creating temp text file...")
# write pdf to text
f = open(cistext,'w', encoding='utf-8')
f.write(data)

# Remove blank lines

with open(cistext, 'r', encoding='utf-8') as filer:
	with open(temptext, 'w', encoding='utf-8') as filew:
		for line in filer:
			if not line.strip():
				continue
			if line:
				# start writing
				filew.write(line)

#-------------------------------------------------------
				

flagStart, flagDesc, flagAudit, flagRecom, flagComplete = False, False, False, False, False
flagProfile, flagTitle = False, False
cis_title, cis_desc, cis_audit, cis_recom, cis_profile = "","","","",""
listObj = []


print("[+] Converting to Json...")
with open(temptext, 'r', encoding='utf-8') as filer:
	for line in filer:
		if not line.strip():
			continue
		if line.strip():

			x = {} #json object
			# Match rule IDs like 2.1, 3.1.3, 4.2, etc.
			if re.match(r"^[0-9]+(\.[0-9]+)+\s", line):
				# flagStart = True		# identified CIS title			
				cis_title, cis_desc, cis_audit, cis_recom, cis_profile = line,"","","",""
				flagStart, flagDesc, flagAudit, flagRecom, flagComplete = True, False, False, False, False
				flagProfile, flagTitle = False, True
				# cis_title, cis_desc, cis_audit, cis_recom = "","","",""

			if flagStart:
				# Continue capturing title lines until we hit a section marker
				if flagTitle:
					# Check if this is a section marker that ends the title
					if "Profile Applicability:" in line or "Description:" in line or "Audit:" in line:
						flagTitle = False
					else:
						# If not the initial title line, append this line to title
						if not re.match(r"^[0-9]+(\.[0-9]+)+\s", line):
							cis_title = cis_title + " " + line
				
				# Get profile - capture Profile Applicability section
				if "Profile Applicability:" in line:
					flagProfile = True
					flagTitle = False
				
				if flagProfile:
					if "Profile Applicability:" in line:
						continue
					cis_profile = cis_profile + line
					
				if "Description:" in line:
					flagProfile = False
				
				# Get description - capture everything between 'Description:' and 'Rationale:'
				if "Description:" in line:	
					flagDesc = True
					
				if flagDesc:
					if "Description:" in line:
						continue
					cis_desc = cis_desc + line

				if "Rationale:" in line:
					flagDesc = False

																
				# # Get Audit - capture everything between 'Audit:' and 'Remediation:'
				if "Audit:" in line:
					flagAudit = True

				if flagAudit:
					if ("Audit:" in line):
						continue
					cis_audit = cis_audit + line



				# # Get Remediation - capture everything between 'Remediation:'
				# and 'References:'
				# or sometimes 'Additional Information:'
				# or sometimes 'CIS Controls:'
				if "Remediation:" in line:
					flagAudit = False
					flagRecom = True

				if flagRecom:
					if "Remediation:" in line:
						continue
					cis_recom = cis_recom + line

				if ("References:" in line) or ("Additional Information:" in line) or ("CIS Controls:" in line):
					flagRecom = False
					flagComplete = True


				if flagComplete:
					cis_title = cis_title.replace('\n','')
					cis_profile = cis_profile.replace('\n','')
					cis_profile = cis_profile.replace('| P a g e','')
					cis_desc = cis_desc.replace('\n','')
					cis_desc = cis_desc.replace('Rationale:','')
					cis_desc = cis_desc.replace('| P a g e','')
					cis_audit = cis_audit.replace('\n','')
					cis_audit = cis_audit.replace('Remediation:','')
					cis_audit = cis_audit.replace('| P a g e','')
					cis_recom = cis_recom.replace('\n','')
					cis_recom = cis_recom.replace('CIS Controls:','')
					cis_recom = cis_recom.replace('Additional Information:','')
					cis_recom = cis_recom.replace('References:','')
					cis_recom = cis_recom.replace('| P a g e','')

					x['title'] = cis_title
					x['profile'] = cis_profile
					x['description'] = cis_desc
					x['audit'] = cis_audit
					x['recommendations'] = cis_recom
					# print(x)
					cis_title, cis_desc, cis_audit, cis_recom, cis_profile = "","","","",""
					flagStart = False
					# parsed = json.loads(x)
					# print(json.dumps(x, indent=4))
					listObj.append(x)

# Transform to Directus structure
print("[+] Creating Directus import structure...")
framework_info = parse_framework_info(cispdf)

# Generate UUID for framework
framework_id = str(uuid.uuid4())
framework_info['id'] = framework_id

directus_rules = []
for item in listObj:
    rule_id = extract_rule_id(item.get('title', ''))
    assessment_status = extract_severity(
        item.get('title', ''), 
        item.get('description', '')
    ).lower()
    profile_level = extract_profile_level(item.get('profile', '')).lower()
    clean_title_text = clean_title(item.get('title', ''))
    
    directus_rule = {
        "id": str(uuid.uuid4()),
        "framework": framework_id,
        "rule_id": rule_id,
        "title": clean_title_text,
        "assessment_status": assessment_status,
        "profile_level": profile_level,
        "details": {
            "description": item.get('description', ''),
            "audit": item.get('audit', ''),
            "remediation": item.get('recommendations', '')
        }
    }
    directus_rules.append(directus_rule)

print("[+] Framework: {} v{} (ID: {})".format(framework_info['name'], framework_info['version'], framework_id))
print("[+] Total rules: {}".format(len(directus_rules)))

# Save separate files for framework and rules
framework_json = os.path.join(output_dir, "framework.json")
rules_json = os.path.join(output_dir, "rules.json")

print("[+] Writing to '{}' ...".format(framework_json))
with open(framework_json, 'w') as json_file:
    json.dump(framework_info, json_file, 
                        indent=4,  
                        separators=(',',': '))

print("[+] Writing to '{}' ...".format(rules_json))
with open(rules_json, 'w') as json_file:
    json.dump(directus_rules, json_file, 
                        indent=4,  
                        separators=(',',': '))

print("[+] Done!")

# print(d)			

#print(record[0])

# with open('test.csv', 'w') as ofile:
# 	for i in record:
# 		ofile.write("%s\n" % i)
# 	print("Done")