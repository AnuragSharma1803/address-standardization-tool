import re
import pandas as pd

# -------------------- CLEANING PHASES --------------------

def clean_address_parts(address):
    keywords = ['div', 'unit', 'fac', 'hub', 'branch', 'minist', 'marg', 'rd','vihar']
    keyword_patterns = [re.compile(rf'\b{kw}\b', re.IGNORECASE) for kw in keywords]
    govt_pattern = re.compile(r'\bgovt\b', re.IGNORECASE)
    coll_or_polytech_pattern = re.compile(r'\b(coll|polytech|dept)\b', re.IGNORECASE)
    deemed_univ_pattern = re.compile(r'^deemed(?:\s+\w+){0,3}?\s+univ$', re.IGNORECASE)

    address = [part for part in address if not deemed_univ_pattern.match(part)]

    filtered_parts = []
    for part in address:
        if any(p.search(part) for p in keyword_patterns):
            continue
        if govt_pattern.search(part) and not coll_or_polytech_pattern.search(part):
            continue
        filtered_parts.append(part)

    return filtered_parts

def merge_abbreviation_with_organization(address):
    keywords = ["inst", "univ", "lab", "coll", "ctr", "acad", "org", "consortium", "labs"]
    keyword_patterns = [re.compile(rf'\b{kw}\b', re.IGNORECASE) for kw in keywords]

    if len(address) > 3:
        first, second = address[0], address[1]
        if len(first.strip().split()) == 1:
            if any(pat.search(second) for pat in keyword_patterns):
                merged = f"{first} {second}"
                address = [merged] + address[2:]
    return address

def clean_address_phase2(address):
    phase2_keywords = ["campus", "grp", "sch", "sect", "plant", "cell", "wing"]
    pattern = re.compile(r'\b(' + '|'.join(map(re.escape, phase2_keywords)) + r')\b', re.IGNORECASE)
    if len(address) <= 3:
        return address
    return [address[0]] + [part for part in address[1:-2] if not pattern.search(part)] + address[-2:]

def remove_cent_address(address):
    if len(address) <= 3: return address
    cent_pattern = re.compile(r'\bcent\b', re.IGNORECASE)
    required = re.compile(r'\b(univ|inst|org)\b', re.IGNORECASE)
    return [address[0]] + [part for part in address[1:-2] if not (cent_pattern.search(part) and not required.search(part))] + address[-2:]

def remove_dept_address(address):
    if len(address) <= 3: return address
    dept_pattern = re.compile(r'\bdept\b', re.IGNORECASE)
    keywords = ['Inst', 'Univ', 'Lab', 'Sch', 'Acad', 'Ctr', 'Coll', 'Cent', 'Educ','Campus', 'Council', 'Grp', 'Assoc', 'Consortium', 'Polytech','CSIR','org']
    keyword_patterns = [re.compile(rf'\b{kw}\b', re.IGNORECASE) for kw in keywords]
    first = address[0]
    rest = address[1:]
    keep_first = not dept_pattern.search(first) or any(any(kw.search(part) for kw in keyword_patterns) for part in rest)
    filtered = [first] if keep_first else []
    filtered += [part for part in rest if not dept_pattern.search(part)]
    return filtered

def priority_based_deletion(address):
    if len(address) <= 3: return address
    global_kw = ['org', 'consortium']
    first_kw = ['univ', 'polytech', 'assoc', 'cent', 'inst', 'ltd']
    delete_kw = ['univ', 'inst', 'ctr', 'lab', 'labs', 'acad', 'coll', 'educ', 'ltd', 'polytech', 'council', 'facil', 'studies', 'cell']

    global_pat = [re.compile(rf'\b{kw}\b', re.IGNORECASE) for kw in global_kw]
    first_pat = [re.compile(rf'\b{kw}\b', re.IGNORECASE) for kw in first_kw]
    delete_pat = [re.compile(rf'\b{kw}\b', re.IGNORECASE) for kw in delete_kw]

    body, last = address[:-2], address[-2:]

    for i, part in enumerate(body):
        if any(p.search(part) for p in global_pat):
            new_body = [part] + [p for j, p in enumerate(body) if j != i and not any(dp.search(p) for dp in delete_pat)]
            return new_body + last

    if any(p.search(address[0]) for p in first_pat):
        new_middle = [p for p in address[1:-2] if not any(dp.search(p) for dp in delete_pat)]
        return [address[0]] + new_middle + last

    return address

def clean_ctr_related_parts(address):
    if len(address) <= 3: return address
    address_copy = address[:]
    ctr_indices = [i for i, part in enumerate(address_copy) if 'ctr' in part.lower()]
    if len(ctr_indices) > 1:
        first_ctr_index = ctr_indices[0]
        address_copy = [part for i, part in enumerate(address_copy) if 'ctr' not in part.lower() or i == first_ctr_index]

    for i, part in enumerate(address):
        part_lower = part.lower()
        if 'lab' in part_lower and 'ctr' not in part_lower:
            for j in range(i + 1, len(address)):
                if 'ctr' in address[j].lower() and 'lab' not in address[j].lower():
                    address_copy = [p for p in address_copy if 'ctr' not in p.lower()]
                    return address_copy
        elif 'ctr' in part_lower and 'lab' not in part_lower:
            for j in range(i + 1, len(address)):
                if 'lab' in address[j].lower() and 'ctr' not in address[j].lower():
                    address_copy = [p for p in address_copy if 'lab' not in p.lower()]
                    return address_copy

    co_keywords = ['acad', 'labs', 'inst', 'csr', 'complex']
    ctr_parts = [i for i, part in enumerate(address_copy) if 'ctr' in part.lower()]
    co_kw_parts = [i for i, part in enumerate(address_copy) if any(kw in part.lower() for kw in co_keywords)]
    if ctr_parts and co_kw_parts and not any(i == j for i in ctr_parts for j in co_kw_parts):
        address_copy = [part for part in address_copy if 'ctr' not in part.lower()]
        return address_copy

    for i, part in enumerate(address_copy[1:], start=1):
        if 'ctr' in part.lower():
            address_copy = [p for idx, p in enumerate(address_copy) if idx == 0 or 'ctr' not in p.lower()]
            break

    return address_copy

def resolve_acad_conflicts(address):
    if len(address) <= 3: return address
    acad_index = inst_index = None
    for i, part in enumerate(address):
        if acad_index is None and 'acad' in part.lower():
            acad_index = i
        if inst_index is None and 'inst' in part.lower():
            inst_index = i

    if acad_index is not None and inst_index is not None and acad_index != inst_index:
        if 'res' in address[acad_index].lower():
            address = [part for i, part in enumerate(address) if i != inst_index]
        else:
            address = [part for i, part in enumerate(address) if i != acad_index]
    elif acad_index is not None:
        for j in range(acad_index + 1, len(address)):
            if re.search(r'\b(lab|council)\b', address[j], re.IGNORECASE):
                address = [part for i, part in enumerate(address) if i != j]
                break
    return address

def resolve_lab_conflicts(address):
    if len(address) <= 3: return address
    lab_pattern = re.compile(r'\blab\b', re.IGNORECASE)
    natl_pattern = re.compile(r'\bnatl\b', re.IGNORECASE)
    council_pattern = re.compile(r'\bcouncil\b', re.IGNORECASE)
    inst_pattern = re.compile(r'\binst\b', re.IGNORECASE)
    coll_pattern = re.compile(r'\bcoll\b', re.IGNORECASE)

    lab_indices = [i for i, part in enumerate(address) if lab_pattern.search(part)]
    if len(lab_indices) > 1:
        natl_lab_index = next((i for i in lab_indices if natl_pattern.search(address[i])), None)
        keep = natl_lab_index if natl_lab_index is not None else lab_indices[0]
        address = [part for i, part in enumerate(address) if i == keep or not lab_pattern.search(part)]

    lab_index = next((i for i, part in enumerate(address) if lab_pattern.search(part)), None)
    inst_index = next((i for i, part in enumerate(address) if inst_pattern.search(part)), None)

    if lab_index is not None:
        address = [part for part in address if not council_pattern.search(part)]
    if lab_index is not None and inst_index is not None and lab_index != inst_index:
        address = [part for i, part in enumerate(address) if i != lab_index]
    coll_index = next((i for i, part in enumerate(address) if coll_pattern.search(part)), None)
    if coll_index is not None and lab_index is not None and coll_index < lab_index:
        address = [part for i, part in enumerate(address) if i != lab_index]
    if any(lab_pattern.search(part) for part in address[1:]):
        address = [part for i, part in enumerate(address) if i == 0 or not lab_pattern.search(part)]
    return address

def resolve_sch_and_council_conflicts(address):
    if len(address) <= 3: return address
    sch_index = council_index = inst_index = polytech_index = None
    for i, part in enumerate(address):
        part_l = part.lower()
        if sch_index is None and 'sch' in part_l: sch_index = i
        if council_index is None and 'council' in part_l: council_index = i
        if inst_index is None and 'inst' in part_l: inst_index = i
        if polytech_index is None and 'polytech' in part_l: polytech_index = i

    if sch_index is not None and inst_index is not None and sch_index != inst_index:
        address = [part for i, part in enumerate(address) if i != sch_index]
    elif council_index is not None and inst_index is not None and council_index != inst_index:
        if 'res' in address[inst_index].lower():
            address = [part for i, part in enumerate(address) if i != inst_index]
        else:
            address = [part for i, part in enumerate(address) if i != council_index]
    elif council_index is not None and polytech_index is not None and council_index != polytech_index:
        address = [part for i, part in enumerate(address) if i != polytech_index]
    return address

# -------------------- MASTER PHASE WRAPPER --------------------

def apply_all_phases(address):
    address = clean_address_parts(address)
    address = merge_abbreviation_with_organization(address)
    address = clean_address_phase2(address)
    address = remove_cent_address(address)
    address = remove_dept_address(address)
    address = merge_abbreviation_with_organization(address)
    address = priority_based_deletion(address)
    address = clean_ctr_related_parts(address)
    address = resolve_acad_conflicts(address)
    address = resolve_lab_conflicts(address)
    address = resolve_sch_and_council_conflicts(address)
    return address

# -------------------- CLEANING PIPELINE ENTRY --------------------

def run_cleaning_pipeline(df, column):
    addr_ser = df[column]
    addr_list = [re.sub(r'\[.*?\]', '', cell).strip() if isinstance(cell, str) else '' for cell in addr_ser]
    addr_list = [cell.split("; ") for cell in addr_list]
    addr_list = [[re.split(r'\s*,\s*', addr) for addr in sublist] for sublist in addr_list]
    addr_list = [[[part.strip() for part in addr] for addr in rec] for rec in addr_list]

    def standardize_country(name):
        if any(char.isdigit() for char in name) or "usa" in name.lower():
            return "USA"
        elif name.lower() in ["fed rep ger", "germany"]:
            return "Germany"
        return name.title()

    for rec in addr_list:
        for addr in rec:
            if addr:
                addr[-1] = standardize_country(addr[-1].strip())

    for record in addr_list:
        for i in range(len(record)):
            record[i] = apply_all_phases(record[i])

    # Convert to dataframe
    rows = []
    for idx, record in enumerate(addr_list):
        for address in record:
            cleaned = ", ".join(address)
            rows.append({"Record Index": idx, "Original_Raw_Addresses": ", ".join(address), "Cleaned Address": cleaned})
    return pd.DataFrame(rows)
