import fitz
import csv
import re
import logging
import io
from collections import namedtuple
BenchmarkConfig = namedtuple("BenchmarkConfig", ["pattern", "identifier", "category"])
BENCHMARK_MAP = {
    "CIS MongoDB 7  Benchmark": BenchmarkConfig(r"(\d+(?:\.\d.\d*)+)(.*?)(\(Automated\)|\(Manual\))", "MONGODB_", "Database"),
    "CIS Docker Benchmark": BenchmarkConfig(r"(v\d+(?:\.\d+)*)(.*?)(\(Automated\)|\(Manual\))", "Docker_", "Contrainerisation"),
    
    "PostgreSQL 9.5 Benchmark": BenchmarkConfig(r"(\d+(?:\.\d.\d*)+)(.*?)(\(Scored\)|\(Not(.*?)Scored\))", "PGSQL_", "Database"),
    "PostgreSQL 9.6 Benchmark": BenchmarkConfig(r"(\d+(?:\.\d.\d*)+)(.*?)(\(Scored\)|\(Not(.*?)Scored\))", "PGSQL_", "Database"),
    "PostgreSQL 10 Benchmark": BenchmarkConfig(r"(\d+(?:\.\d.\d*)+)(.*?)(\(Scored\)|\(Not(.*?)Scored\))", "PGSQL_", "Database"),
    "PostgreSQL 11 Benchmark": BenchmarkConfig(r"(\d+(?:\.\d.\d*)+)(.*?)(\(Scored\)|\(Not(.*?)Scored\))", "PGSQL_", "Database"),
    "Oracle MySQL Community Server 5.6 Benchmark": BenchmarkConfig(r"(\d+(?:\.\d.\d*)+)(.*?)(\(Automated\)|\(Manual\))", "MYSQLCS_", "Database"),
    "CIS Oracle MySQL  Community Server 8.0  Benchmark": BenchmarkConfig(r"(\d+(?:\.\d.\d*)+)(.*?)(\(Automated\)|\(Manual\))", "MYSQLCS_", "Database"),
    "CIS Oracle MySQL  Enterprise Edition 5.6  Benchmark - ARCHIVE": BenchmarkConfig(r"(\d+(?:\.\d.\d*)+)(.*?)(\(Automated\)|\(Manual\))", "MYSQLEE_", "Database"),
    "CIS Oracle MySQL  Enterprise Edition 5.7  Benchmark": BenchmarkConfig(r"(\d+(?:\.\d.\d*)+)(.*?)(\(Automated\)|\(Manual\))", "MYSQLEE_", "Database"),
    "CIS Oracle MySQL  Enterprise Edition 8.0  Benchmark": BenchmarkConfig(r"(\d+(?:\.\d.\d*)+)(.*?)(\(Automated\)|\(Manual\))", "MYSQLEE_", "Database"),
    "CIS MariaDB 10.11  Benchmark": BenchmarkConfig(r"(\d+(?:\.\d.\d*)+)(.*?)(\(Automated\)|\(Manual\))", "MADB_", "Database"),
    "CIS MariaDB 10.11  Benchmark": BenchmarkConfig(r"(\d+(?:\.\d.\d*)+)(.*?)(\(Automated\)|\(Manual\))", "MADB_", "Database"),
    "CIS IBM DB2 9 Benchmark - ARCHIVE": BenchmarkConfig(r"(\d+(?:\.\d.\d*)+)(.*?)(\(Scored\)|\(Not(.*?)Scored\))", "IBMDB2_", "Database"),
    "CIS IBM DB2 10 Benchmark - ARCHIVE": BenchmarkConfig(r"(\d+(?:\.\d.\d*)+)(.*?)(\(Scored\)|\(Not(.*?)Scored\))", "IBMDB2_", "Database"),
    "CIS IBM Db2 11  Benchmark": BenchmarkConfig(r"(\d+(?:\.\d.\d*)+)(.*?)(\(Automated\)|\(Manual\))", "IBMDB2_", "Database"),
    "CIS IBM Db2 13 for z/OS  Benchmark": BenchmarkConfig(r"(\d+(?:\.\d.\d*)+)(.*?)(\(Automated\)|\(Manual\))", "IBMDB2_", "Database"),
    "CIS Kubernetes  Benchmark": BenchmarkConfig(r"(v\d+(?:\.\d+)*)(.*?)(\(Automated\)|\(Manual\))", "CISK8s_", "Containerisation"),
    }
def parse_cis_pdf(pdf_file_stream, output_stream):

    def normalize_spaces(text):
        return re.sub(r'\s+', ' ', text.strip())

   # Initialize variables
    rule_count = 0
    description_count = 0
    audit_count = 0
    rationale_count = 0
    impact_count = 0
    remediation_count = 0
    defaultvalue_count = 0
    references_count = 0
    additionalinformation_count = 0
    ciscontrols_count = 0
    nextrule_count = 0  # Initialize nextrule_count
    firstPage = None
    seenList = []
    # Setup console logging
    logger = logging.getLogger("cis_parser")
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(fmt="%(asctime)s %(levelname)-8s %(message)s"))
        logger.addHandler(handler)
    # Open PDF File
    doc = fitz.open(stream=pdf_file_stream.read(), filetype="pdf")

    # Get CIS Type from the name of the document in the cover page as it doesn't appear in the metadata
    coverPageText = doc.load_page(0).get_text("text")
    coverPageTextReplaced = coverPageText.strip().replace('\n', '')
    logger.debug("*** Cover Page Text ***".format(coverPageTextReplaced))

    # Regular expression to extract the first word after 'CIS' (the editor's name)
    editor_name_match = re.search(r"CIS\s+(\w+)", coverPageTextReplaced)
    if editor_name_match:
        editor_name = editor_name_match.group(1).strip()
        logger.info("*** Editor Name Extracted: {} ***".format(editor_name))
    else:
        logger.error("No editor name found after 'CIS'. Using 'Unknown'.")
        editor_name = "Unknown"

    # Regular expression to extract the version number before 'Benchmark'
    version_match = re.search(r"(\d{1,4}[a-zA-Z]?\d*(?:\.\d+)?)(?=\s*Benchmark)", coverPageTextReplaced)

    # Regular expression to extract version like 'v2.0.0'
    benchmark_version_match = re.search(r"(v\d+(?:\.\d+)+)", coverPageTextReplaced)

    if benchmark_version_match:
        benchmark_version = benchmark_version_match.group(1).strip()
        logger.info("*** Benchmark Version Extracted: {} ***".format(benchmark_version))
    else:
        logger.error("No benchmark version (vX.X.X) found. Defaulting to 'Unknown'.")
        benchmark_version = "Unknown"

    # Check if we found a version match
    if version_match:
        version = version_match.group(1).strip()
        logger.info("*** Version Extracted: {} ***".format(version))
    else:
        logger.warning("No version found before 'Benchmark'. Defaulting to 'Unknown'.")
        version = "Unknown"

    # Extract config based on the document name
    # Normalize document title to match against BENCHMARK_MAP
    CISName = None

    # Try to extract a more complete CIS Benchmark title
    title_match = re.search(r"(CIS\s+[A-Za-z0-9\s\/\.\-]+Benchmark(?:\s*-\s*ARCHIVE)?)", coverPageText, re.IGNORECASE)

    if title_match:
        CISName = title_match.group(1).strip().replace('\n', ' ')
        logger.info("*** CIS Title Extracted from PDF: {} ***".format(CISName))
    else:
        # fallback: build it manually from known parts
        CISName = f"CIS {editor_name} {version} {benchmark_version} Benchmark"
        logger.warning("*** Falling back to generated title: {} ***".format(CISName))

    # Now match against benchmark config map using the simplified name
    # Normalize and match against BENCHMARK_MAP
    normalized_CISName = normalize_spaces(CISName)

    logger.debug(f"Normalized extracted CISName: '{normalized_CISName}'")
    logger.debug(f"Normalized keys: {[normalize_spaces(k) for k in BENCHMARK_MAP.keys()]}")

    matched_config = None
    for key in BENCHMARK_MAP:
        if normalize_spaces(key) in normalized_CISName:
            matched_config = BENCHMARK_MAP[key]
            break


    if matched_config:
        pattern = matched_config.pattern
        identifier_initial = matched_config.identifier
        category = matched_config.category
    else:
        raise ValueError(f"No matching CIS benchmark configuration found for: {CISName}")

   # Locate starting page of recommendations
    for currentPage in range(len(doc) - 1):  # Check to avoid out of range
        findPage = doc.load_page(currentPage)
        findNextPage = doc.load_page(currentPage + 1)
        if findPage.search_for("Recommendations 1 "):
            firstPage = currentPage
            break
        elif findPage.search_for("Recommendations ") and findNextPage.search_for("1 Initial Setup "):
            firstPage = currentPage
            break

    if firstPage is None:
        raise ValueError("Unable to locate the 'Recommendations' section in the PDF.")


    logger.info("*** Total Number of Pages: %i ***", doc.page_count)

    string_buffer = io.StringIO()
    rule_writer = csv.writer(string_buffer, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)
    rule_writer.writerow(
        [
           "Identifier",
            "Category",  # <- Added Category column here
            "Editor Name",
            "Version",      # Added Version column
            "Benchmark Version",  # <- New column
            "Rule",
            "Compliance",
            "Description",
            "Rationale",
            "Impact",
            "Risque",
            "Audit",
            "Proof",
            "Remediation",
            "Default Value",
            "References",
            "Additional Information",
            ]
        )

        # Loop through all PDF pages
    for page in range(firstPage, len(doc)):
            logger.debug("*****************************************************************************************************************************************************************")
            if page < len(doc):
                data = doc.load_page(page).get_text("text")
                if page+1 < len(doc):
                    datanextpage = doc.load_page(page+1).get_text("text")
                logger.debug("*** Parsing Page Number: %i ***", page)

                row_initiale_count = [
                    rule_count,
                    description_count,
                    rationale_count,
                    impact_count,
                    audit_count,
                    remediation_count,
                    defaultvalue_count,
                    references_count,
                    additionalinformation_count,
                    ciscontrols_count,
                ]
                logging.debug(row_initiale_count)
                # Get rule by matching regex pattern for x.x.* (Automated) or (Manual), there are no "x.*" we care about
                try:
                    rerule = re.search(pattern, data, re.DOTALL)
                    logger.debug("*** Page : Before Rule Name {} ***".format(rerule))
                    logger.debug("*** Page : Pattern {} ***".format(pattern))
                    if rerule is not None:
                        ruleintermediate = rerule.group()
                        rule = ruleintermediate.strip().replace('\n','')
                        rule_count += 1                        
                        logger.debug("*** Page : Rule Name {} ***".format(rule))
                        logger.debug("*** Page : Rule Count %i ***",rule_count)
                        audit = None
                        rationale = None
                        impact = None
                        remediation = None
                        defaultvalue = None
                        references = None
                        additionalinformation = None
                        ciscontrols = None
                    renextrule = re.search(pattern, datanextpage, re.DOTALL)
                    nextrule = False
                    if renextrule is not None:
                        nextruleintermediate = renextrule.group()
                        nextrule = nextruleintermediate.strip().replace('\n','')
                        nextrule_count += 1
                        nextrule = True
                        logger.debug("*** Next Page : Rule Name {} ***".format(nextrule))
                        logger.debug("*** Next Page : Rule Count %i ***",rule_count)
                except IndexError:
                    logger.debug("*** Page does not contain a Rule Name (Index) ***")
                except AttributeError:
                    logger.debug("*** Page does not contain a Rule Name (Attribute) ***")
                row_initiale_count = [
                    rule_count,
                    description_count,
                    rationale_count,
                    impact_count,
                    audit_count,
                    remediation_count,
                    defaultvalue_count,
                    references_count,
                    additionalinformation_count,
                    ciscontrols_count,
                ]
                logging.debug(row_initiale_count)

                # Get Description by regex as it is always between Description and ( Rationale or Audit )
                try:
                    description_post = data.split("\nDescription:", 1)[1]
                    logger.info("*** Description Post {} ***".format(description_post))
                    complete_description = description_post
                    description_stop_position = re.search(r"(\nAudit: \n|\nRationale: \n)", complete_description)
                    logger.info("*** Description Stop Position {} ***".format(description_stop_position))   
                    while not description_stop_position:
                        # Assuming data is split into pages by some delimiter (e.g., "Page Break")
                        try:
                            additional_page = data.split("P a g e")[page]
                            complete_description += additional_page
                            description_stop_position = re.search(r"(\nAudit: \n|\nRationale: \n)", complete_description)
                            page += 1
                        except IndexError:
                            # No more pages available
                            break                  
                    logger.info("*** Complete Description {} ***".format(complete_description))  
                    if description_stop_position:
                        description = complete_description[:description_stop_position.start()].strip()
                    else:
                        description = complete_description.strip()
                    description_count += 1
                    logger.debug("*** Page does contain Description ***")
                    logger.debug("*** Description {} ***".format(description))
                    logger.debug("*** Description Count %i ***",description_count)
                except IndexError:
                    logger.debug("*** Page does not contain Description ***")

                # Get Rationale by regex as it is always between Rationale and ( Audit or Impact )               
                try:
                    rationale_post = data.split("\nRationale: \n", 1)[1]
                    logger.info("*** Rationale Post {} ***".format(rationale_post))
                    complete_rationale = rationale_post
                    rationale_stop_position = re.search(r"(\nAudit: \n|\nImpact: \n)", complete_rationale)
                    logger.info("*** Rationale Stop Position {} ***".format(rationale_stop_position))   
                    while not rationale_stop_position:
                        # Assuming data is split into pages by some delimiter (e.g., "Page Break")
                        try:
                            additional_page = data.split("P a g e")[page]
                            complete_rationale += additional_page
                            rationale_stop_position = re.search(r"(\nAudit: \n|\nImpact: \n)", complete_rationale)
                            page += 1
                        except IndexError:
                            # No more pages available
                            break
                    logger.info("*** Complete Rationale {} ***".format(complete_rationale))  
                    if rationale_stop_position:
                        rationale = complete_rationale[:rationale_stop_position.start()].strip()
                    else:
                        rationale = complete_rationale.strip()
                    rationale_count += 1  
                    logger.debug("*** Page does contain Rationale ***")
                    logger.debug("*** Rationale {} ***".format(rationale))
                    logger.debug("*** Rationale Count %i ***",rationale_count)
                except IndexError:
                    logger.debug("*** Page does not contain Rationale ***")

                # Get Impact by splits as it is always between Impact and Audit, faster than regex              
                try:
                    impact_post = data.split("\nImpact: \n", 1)[1]
                    impact_stop_position = re.search(r"(\nAudit: \n)", impact_post)
                    if impact_stop_position:
                        impact = impact_post[:impact_stop_position.start()].strip()
                    else:
                        impact = impact_post.strip()
                    # impact = impact_post.partition("Audit:")[0].strip()
                    impact_count += 1
                    logger.debug("*** Page does contain Impact ***")
                    logger.debug("*** Impact {} ***".format(impact))
                    logger.debug("*** Impact Count %i ***",impact_count)
                except IndexError:
                    logger.debug("*** Page does not contain Impact ***")

                # Get Audit by splits as it is always between Audit and Remediation, faster than regex              
                try:
                    #audit_post_bold = re.split(r"(\nAudit: \n)", data, 1)
                    #audit_post = audit_post_bold[1]
                    audit_post = data.split("\nAudit: \n", 1)[1]
                    audit_stop_position = re.search(r"(\nRemediation: \n)", audit_post)
                    if audit_stop_position:
                        audit = audit_post[:audit_stop_position.start()].strip()
                    else:
                        audit = audit_post.strip()
                    # audit = audit_post.partition("Remediation:")[0].strip()
                    audit_count += 1
                    logger.debug("*** Page does contain Audit ***")
                    logger.debug("*** Audit {} ***".format(audit))
                    logger.debug("*** Audit Count %i ***",audit_count)
                except IndexError:
                    logger.debug("*** Page does not contain Audit ***")

                # Get Remediation by splits as it is always between Remediation and ( Default value or References or Additional Information or CIS Controls ), faster than regex                
                try:
                    remediation_post = data.split("\nRemediation: \n", 1)[1]
                    remediation_stop_position = re.search(r"(\nAdditional Information: \n|\nDefault Value: \n|\nReferences: \n|\nCIS Controls: \n)", remediation_post)
                    if remediation_stop_position:
                        remediation = remediation_post[:remediation_stop_position.start()].strip()
                    else:
                        remediation = remediation_post.strip()
                    remediation_count += 1
                    logger.debug("*** Page does contain Remediation ***")
                    logger.debug("*** Remediation {} ***".format(remediation))
                    logger.debug("*** Remediation Count %i ***",remediation_count)
                except IndexError:
                    logger.debug("*** Page does not contain Remediation ***")

                # Get Default Value by splits as WHEN PRESENT it is always between Default Value and ( CIS Controls or References ), faster than regex                
                try:
                    defaultvalue_post = data.split("\nDefault Value: \n", 1)[1]
                    defaultvalue_stop_position = re.search(r"(\nReferences: \n|\nCIS Controls: \n)", defaultvalue_post)
                    if defaultvalue_stop_position:
                        defaultvalue = defaultvalue_post[:defaultvalue_stop_position.start()].strip()
                    else:
                        defaultvalue = defaultvalue_post.strip()
                    defaultvalue_count += 1
                    logger.debug("*** Page does contain Default Value ***")
                    logger.debug("*** Default Value {} ***".format(defaultvalue))
                    logger.debug("*** Default Value Count %i ***",defaultvalue_count)
                except IndexError:
                    logger.debug("*** Page does not contain Default Value ***")

                # Get References by splits as it is always between References and ( Default value or Additional Information or CIS Controls or P a g e ), faster than regex
                
                try:
                    references_post = data.split("\nReferences: \n", 1)[1]
                    references_stop_position = re.search(r"(\nAdditional Information: \n|\nDefault Value: \n|\nCIS Controls: \n|P a g e)", references_post)
                    if references_stop_position:
                        references = references_post[:references_stop_position.start()].strip()
                    else:
                        references = references_post.strip()
                    references_count += 1
                    logger.debug("*** Page does contain References ***")
                    logger.debug("*** References {} ***".format(references))
                    logger.debug("*** References Count %i ***",references_count)
                except IndexError:
                    logger.debug("*** Page does not contain References ***")

                # Get Additional Information by splits as WHEN PRESENT it is always between Additional Information and ( CIS Controls or Default Value ), faster than regex
                
                try:
                    additionalinformation_post = data.split("\nAdditional Information: \n", 1)[1]
                    additionalinformation_stop_position = re.search(r"(\nDefault Value: \n|\nCIS Controls: \n|P a g e)", additionalinformation_post)
                    if additionalinformation_stop_position:
                        additionalinformation = additionalinformation_post[:additionalinformation_stop_position.start()].strip()
                    else:
                        additionalinformation = additionalinformation_post.strip()
                    additionalinformation_count += 1
                    logger.debug("*** Page does contain Additional Information ***")
                    logger.debug("*** Additional Information {} ***".format(additionalinformation))
                    logger.debug("*** Additional Information Count %i ***",additionalinformation_count)
                except IndexError:
                    logger.debug("*** Page does not contain Additional Information ***")

                # Get CIS Controls by splits as they are always between CIS Controls and P a g e, regex the result
                try:
                    ciscontrols_post = data.split("\nCIS Controls: \n", 1)[1]
                    ciscontrols = ciscontrols_post.partition("P a g e")[0].strip()
                    ciscontrols = re.sub("[^a-zA-Z0-9\\n.-]+", " ", ciscontrols)
                    ciscontrols_count += 1
                    logger.debug("*** Page does contain CIS Controls ***")
                    logger.debug("*** CIS Controls {} ***".format(ciscontrols))
                    logger.debug("*** Rule Count %i ***",ciscontrols_count)
                except IndexError:
                    logger.debug("*** Page does not contain CIS Controls ***")
                
                # Incrementting the count and emptying the parameters that are not always present
                try:
                    appendix = re.search("Appendix:", datanextpage, re.DOTALL)
                    if nextrule == True or appendix is not None :
                        # Incrementing audit_count if rule_count is found as Rationale is not always present
                        if audit_count == (rule_count-1):
                            audit = ""
                            audit_count += 1
                        # Incrementing audit_count if remediation_count is found as Rationale is not always present
                        if remediation_count == (rule_count-1):
                            remediation = ""
                            remediation_count += 1
                        # Incrementing rationale_count if rule_count is found as Rationale is not always present
                        if rationale_count == (rule_count-1):
                            rationale = ""
                            rationale_count += 1
                        # Incrementing impact_count if rule_count is found as Impact is not always present
                        if impact_count == (rule_count-1):
                            impact = ""
                            impact_count += 1
                        # Incrementing defaultvalue_count if rule_count is found as Default Value is not always present
                        if defaultvalue_count == (rule_count-1):
                            defaultvalue = ""
                            defaultvalue_count += 1  
                        # Incrementing references_count if rule_count is found as References is not always present
                        if references_count == (rule_count-1):
                            references = ""
                            references_count += 1
                        # Incrementing additionalinformation_count if rule_count is found as Additional Information is not always present
                        if additionalinformation_count == (rule_count-1):
                            additionalinformation = ""
                            additionalinformation_count += 1
                        # Incrementing additionalinformation_count if rule_count is found as Additional Information is not always present
                        if ciscontrols_count == (rule_count-1):
                            ciscontrols = ""
                            ciscontrols_count += 1
                except IndexError:
                    logger.debug("*** Doesn't increment counts because an error ***")

                # We only write to csv if a parsed rule is fully assembled
                if rule_count:
                    row_count = [
                        rule_count,
                        #level_count,
                        description_count,
                        rationale_count,
                        impact_count,
                        audit_count,
                        remediation_count,
                        defaultvalue_count,
                        references_count,
                        additionalinformation_count,
                        ciscontrols_count,
                    ]
                    logging.debug(row_count)
                    if row_count.count(row_count[0]) == len(row_count):
                        # Have we seen this rule before? If not, write it to file
                        if row_count not in seenList:
                            seenList = [row_count]
                            logger.info("*** Writing the following rule to csv: ***")
                            identifier = identifier_initial + str(rule_count)
                            row = [identifier,category,editor_name,version, benchmark_version, rule, "", description, rationale, impact, "Risque", audit, "Proof", remediation, defaultvalue, references, additionalinformation]
                            logger.info(row)
                            rule_writer.writerow(row)
                page += 1
            else:
                logger.info("*** All pages parsed, exiting. ***")
                exit()
                

    output_stream.write(string_buffer.getvalue().encode('utf-8'))
    output_stream.seek(0)