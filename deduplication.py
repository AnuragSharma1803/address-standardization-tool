import pandas as pd
from rapidfuzz import fuzz
from collections import Counter
import re

# ===============================================================
#                        NORMALIZATION
# ===============================================================

def normalize(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    text = text.replace("orissa", "odisha")
    text = text.replace("csir immt", "csir inst minerals & mat technol")
    text = text.replace("acsir", "acad sci & innovat res")
    text = re.sub(r"\biiit\b", "indian inst info technol", text)
    text = re.sub(r"\biit\b", "indian inst technol", text)
    return text.strip()

def normalize_text(text):
    text = str(text).lower().strip().replace('&', 'and')
    text = re.sub(r'\s+', ' ', text)
    return text

def extract_institution_part(text):
    return text.split(',')[0].strip()

def split_line(line):
    parts = line.split(',', 1)
    if len(parts) == 2:
        return normalize_text(parts[0]), normalize_text(parts[1])
    return normalize_text(line), ''

# ===============================================================
#                BASIC UTILITIES & SELECT BEST
# ===============================================================

def contains_digit(text):
    return any(char.isdigit() for char in text)

def starts_with_digit_in_first_n_words(text, n=3):
    tokens = text.lower().split()
    return any(any(c.isdigit() for c in token) for token in tokens[:n])

def select_best_line(group):
    candidate_group = [line for line in group if not starts_with_digit_in_first_n_words(line)]
    if not candidate_group:
        candidate_group = group

    counts = Counter(candidate_group)
    most_common_line, freq = counts.most_common(1)[0]
    if freq > 1:
        return most_common_line

    if len(candidate_group) == 2:
        digit_lines = [line for line in candidate_group if contains_digit(line)]
        if len(digit_lines) == 2:
            return min(digit_lines, key=len)
        elif len(digit_lines) == 1:
            return digit_lines[0]
        else:
            return min(candidate_group, key=len)

    digit_lines = [line for line in candidate_group if contains_digit(line)]
    return min(digit_lines, key=len) if digit_lines else min(candidate_group, key=len)

# ===============================================================
#            CLASSIC FUZZY DEDUPLICATION (STAGE 1–17)
# ===============================================================
def deduplicate_addresses_classic(df, input_column, output_column, inst_threshold=90, full_threshold=85):
    unique_addresses = df[input_column].astype(str).drop_duplicates().tolist()
    norm_map = {addr: normalize(addr) for addr in unique_addresses}
    inst_map = {addr: normalize(extract_institution_part(addr)) for addr in unique_addresses}

    groups = []
    used = set()

    for i, line_i in enumerate(unique_addresses):
        if i in used:
            continue
        group = [line_i]
        norm_i = norm_map[line_i]
        inst_i = inst_map[line_i]
        for j in range(i + 1, len(unique_addresses)):
            if j in used:
                continue
            line_j = unique_addresses[j]
            norm_j = norm_map[line_j]
            inst_j = inst_map[line_j]
            inst_score = fuzz.token_sort_ratio(inst_i, inst_j)
            full_score = fuzz.token_sort_ratio(norm_i, norm_j)
            if inst_score >= inst_threshold and full_score >= full_threshold:
                group.append(line_j)
                used.add(j)
        used.add(i)
        groups.append(group)

    canonical_map = {}
    for group in groups:
        best = select_best_line(group)
        for line in group:
            canonical_map[line] = best

    df[output_column] = df[input_column].map(lambda x: canonical_map.get(x, x))

# ===============================================================
#            OPTIMIZED FAST GROUPING DEDUPLICATION (18–23)
# ===============================================================
def group_similar_fast(lines, inst_threshold=90, addr_threshold=85):
    normalized_cache = {}
    buckets = {}

    for line in lines:
        norm_line = normalize_text(line)
        inst, addr = split_line(norm_line)
        normalized_cache[line] = (inst, addr)
        key = inst[0] if inst else '#'
        buckets.setdefault(key, []).append(line)

    used = set()
    groups = []

    for key, bucket in buckets.items():
        for i, line in enumerate(bucket):
            if line in used or not line.strip():
                continue
            group = [line]
            inst1, addr1 = normalized_cache[line]
            for j in range(i + 1, len(bucket)):
                other = bucket[j]
                if other in used or not other.strip():
                    continue
                inst2, addr2 = normalized_cache[other]
                score_inst = fuzz.token_sort_ratio(inst1, inst2)
                score_addr = fuzz.token_sort_ratio(addr1, addr2)
                if score_inst >= inst_threshold and score_addr >= addr_threshold:
                    group.append(other)
                    used.add(other)
            used.add(line)
            groups.append(group)
    return groups

def deduplicate_addresses_fast(df, input_col, output_col, inst_thresh, addr_thresh):
    unique_addresses = df[input_col].astype(str).drop_duplicates().tolist()
    groups = group_similar_fast(unique_addresses, inst_thresh, addr_thresh)
    canonical_map = {}
    for group in groups:
        canonical = select_best_line(group)
        for item in group:
            canonical_map[item] = canonical
    full_series = df[input_col].astype(str)
    df[output_col] = full_series.map(canonical_map).fillna(full_series)

# ===============================================================
#            BATCH EXECUTION WRAPPERS WITH LIMITS
# ===============================================================
def run_chained_classic_dedup(df, limit=None):
    thresholds = [
        ("Cleaned Address", "canonical_address1", 90, 85),
        ("canonical_address1", "canonical_address2", 90, 85),
        ("canonical_address2", "canonical_address3", 90, 85),
        ("canonical_address3", "canonical_address4", 90, 80),
        ("canonical_address4", "canonical_address5", 90, 80),
        ("canonical_address5", "canonical_address6", 88, 85),
        ("canonical_address6", "canonical_address7", 88, 80),
        ("canonical_address7", "canonical_address8", 88, 78),
        ("canonical_address8", "canonical_address9", 85, 85),
        ("canonical_address9", "canonical_address10", 85, 83),
        ("canonical_address10", "canonical_address11", 85, 80),
        ("canonical_address11", "canonical_address12", 85, 78),
        ("canonical_address12", "canonical_address13", 83, 85),
        ("canonical_address13", "canonical_address14", 83, 83),
        ("canonical_address14", "canonical_address15", 83, 80),
        ("canonical_address15", "canonical_address16", 82, 80),
        ("canonical_address16", "canonical_address17", 80, 80),
    ]
    max_steps = limit if limit else len(thresholds)
    for i in range(max_steps):
        in_col, out_col, inst, full = thresholds[i]
        deduplicate_addresses_classic(df, in_col, out_col, inst, full)

def run_chained_fast_dedup(df, limit=None):
    thresholds = [
        ("canonical_address17", "canonical_address18", 90, 75),
        ("canonical_address18", "canonical_address19", 90, 65),
        ("canonical_address19", "canonical_address20", 88, 63),
        ("canonical_address20", "canonical_address21", 86, 63),
        ("canonical_address21", "canonical_address22", 84, 62),
        ("canonical_address22", "canonical_address23", 80, 70),
    ]
    max_steps = limit if limit else len(thresholds)
    for i in range(max_steps):
        in_col, out_col, inst, addr = thresholds[i]
        deduplicate_addresses_fast(df, in_col, out_col, inst, addr)
