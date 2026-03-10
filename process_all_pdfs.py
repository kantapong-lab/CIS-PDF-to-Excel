import os
import glob
import subprocess
import sys


def process_all_pdfs():
    """Process all PDF files in the pdf directory"""
    
    # Step 1: Discover all PDF files
    pdf_dir = "pdf"
    pdf_files = glob.glob(os.path.join(pdf_dir, "*.pdf"))
    pdf_files.sort()  # Consistent ordering
    
    if not pdf_files:
        print("[!] No PDF files found in the 'pdf' directory!")
        return
    
    print("[+] Found {} PDF file(s) to process".format(len(pdf_files)))
    print("=" * 70)
    
    # Initialize counters
    successful = 0
    failed = 0
    failed_files = []
    
    # Step 2: Process each PDF file
    for idx, pdf_file in enumerate(pdf_files, 1):
        filename = os.path.basename(pdf_file)
        print("\n[+] Processing {}/{}: {}".format(idx, len(pdf_files), filename))
        print("-" * 70)
        
        try:
            # Run cis_to_excel.py for each PDF
            result = subprocess.run(
                [sys.executable, "cis_to_excel.py", pdf_file, "output"],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout per file
            )
            
            # Print the output
            if result.stdout:
                print(result.stdout)
            
            # Check result
            if result.returncode == 0:
                print("[✓] Successfully processed: {}".format(filename))
                successful += 1
            else:
                print("[✗] Failed to process: {}".format(filename))
                if result.stderr:
                    print("    Error: {}".format(result.stderr))
                failed += 1
                failed_files.append(filename)
                
        except subprocess.TimeoutExpired:
            print("[✗] Timeout processing {}: exceeded 5 minutes".format(filename))
            failed += 1
            failed_files.append(filename)
        except Exception as e:
            print("[✗] Error processing {}: {}".format(filename, str(e)))
            failed += 1
            failed_files.append(filename)
    
    # Step 3: Print summary
    print("\n" + "=" * 70)
    print("[+] Processing Complete!")
    print("    Total files: {}".format(len(pdf_files)))
    print("    Successful: {}".format(successful))
    print("    Failed: {}".format(failed))
    
    if failed_files:
        print("\n[!] Failed files:")
        for failed_file in failed_files:
            print("    - {}".format(failed_file))
    
    print("=" * 70)
    
    # Return exit code based on results
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    exit_code = process_all_pdfs()
    sys.exit(exit_code)
