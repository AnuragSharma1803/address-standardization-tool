import re
manual_groups = [
    (["ACSIR Inst Mineral & Mat Technol,New Delhi 110001,India","Acad Sci & Innovat Res New Delhi,New Delhi 110001,India","Acad Sci & Innovat Res,Bhubaneswar 751013,Odisha,India","Acad Sci & Innovat Res,Madras 600113,Tamil Nadu,India",
      "AcSIR,CSIR IMMT,Bhubaneswar,India","AcSIR,New Delhi 110025,India","CSIR Acad Sci & Innovat Res AcSIR,IMMT,PO RRL,Bhubaneswar 751013,Odisha,India","CSIR Inst Minerals Mat Technol AcSIR,Res,Bhubaneswar 751013,Orissa,India",
      "CSIR HRDG,Acad Sci & innovat Res AcSIR,Ghaziabad 201002,Uttar Pradesh,India","CSIR,AcSIR,New Delhi 110001,India"], "Acad Sci & Innovat Res,Ghaziabad 201002,India"),
    (["AMITY Inst Nanotechnol,Noida 201303,Uttar Pradesh,India","Amity Univ,Noida,Uttar Pradesh,India"], "Amity Univ,Noida 201313,India"),
    (["Andhra Univ,Waltair 530003,Andhra Pradesh,India"], "Andhra Univ,Vishakhapatnam 530003,India"),
    (["Anna Univ,Arni 632326,India", "Anna Univ,Trichy 620024,Tamilnadu,India" ], "Anna Univ,Chennai,India"),
    (["BIT Mesra,Ranchi 835215,Bihar,India", "BIT,Ranchi,Bihar,India","Birla Inst Technol,Mesra 835215,India"], "BIT,Ranchi,India"),
    (["BJB Autonomous Coll,Bhubaneswar 751014,Odisha,India", "BJB Coll,Bhubaneswar 751013,Orissa,India"], "BJB Coll,Bhubaneswar 751013,India"),
    (["Bijupatnaik Univ,Bhubaneswar,Orissa,India", "Biju Patnaik Univ Technol,Bhubaneswar 751013,Odisha,India", "BPUT Univ,Bhubaneswar,Odisha,India"], "Biju Patnaik Univ Technol,Bhubaneswar 751013,India"),
    (["Banaras Hindu Univ,Banaras,UP,India"], "Banaras Hindu Univ,Varanasi 221005,India"),
    (["BS Abdur Rahman Crescent Inst Sci & Technol,Vandalur,Tamil Nadu,India", "BS AbdurRahman Univ,Madras 600048,Tamil Nadu,India"], "   BS Abdur Rahman Univ,Madras 600048,India"),
    (["Bar Ilan Inst Nanotechnol & Adv Mat,IL-5290002 Ramat Gan,Israel"], "Bar Ilan Univ,IL-5290002 Ramat Gan,Israel"),
    (["BARC,Mumbai 85,Maharashtra,India", "Bhabha Atom Res Ctr,Hyderabad 500016,India", "Bhabha Atom Res Ctr,Bombay,Maharashtra,India"], "Bhabha Atom Res Ctr,Mumbai 400085,India"),
    (["Bose Inst,Darjeeling,W Bengal,India", "Bose Inst,Kolkata 700091,W Bengal,India"], "Bose Inst,Kolkata,India"),
    (["Brandenburg Univ Technol,Chair Mineral Proc,Cottbus,Germany", "Brandenburgische Tech Univ,Lehrstuhl Aufbereitungstech,D-03044 Cottbus,Germany"], "Brandenburg Tech Univ Cottbus,D-03046 Cottbus,Germany"),
    (["CENT INST MED & AROMAT PLANTS,LUCKNOW 226015,India"], "CIMAP,Lucknow 226016,India"),
    (["CSIR CLRI,Chennai 20,Tamil Nadu,India", "CENT LEATHER RES INST,MADRAS 600020,TAMIL NADU,India", "CSIR Cent Leather Res Inst CLRI,Chennai 600020,India", "CSIR,CLRI,Chennai 600020,Tamil Nadu,India"], "CSIR Cent Leather Res Inst,Chennai 600020,India"),
    (["CFRI,DHANBAD 828108,BIHAR,India", "CSIR Cent Inst Min & Fuel Res,Dhanbad 828108,Bihar,India", "Cent Fuel Res Inst,Dhanbad 828108,Jharkhand,India"], "CSIR Cent Inst Min & Fuel Res,Dhanbad 828108,India"),
    (["CV Raman Coll Engn Bhubaneswar,Rourkela 752054,Orissa,India", "CV Raman Coll Engn,Bhubaneswar 752054,India"], "CV Raman Global Univ,Bhubaneswar 752054,India"),
    (["CSIR NEERI,Nagpur 440020,Maharashtra,India", "CSIR Natl Environm Engn Res Inst,Nagpur 440020,Maharashtra,India","CSIR Technol Dev Ctr,NEERI,Nagpur,Maharashtra,India"], "CSIR Natl Environm Engn Res Inst,Nagpur 440020,India"),
    (["Natl Aerosp Labs NAL,Bangalore 560017,India", "CSIR Natl Aerosp Labs,Bangalore 560017,Karnataka,India"], "CSIR Natl Aerosp Labs,Bengaluru,India"),
    (["Natl Met Lab,Madras 600113,Tamil Nadu,India", "CSIR Natl Met Lab Madras Ctr,Chennai,Tamil Nadu,India"], "Natl Met Lab,Madras 600113,India"),
    (["NISER Ctr Interdisciplinary Sci CIS,Bhubaneswar 752050,Odisha,India", "NISER,Bhubaneswar,Odisha,India"], "Natl Inst Sci Educ & Res,Jatni 752050,India"),
    (["N Orissa Univ,Mayurbhanj 757003,Orissa,India"], "N Orissa Univ,Baripada 757003,India"),
    (["Murdoch Univ,AJ Parker CRC Hydromet,Perth,WA,Australia", "Murdoch Univ,Chem & Met Engn & Chem,90 South St,Perth,WA 6150,Australia", "Murdoch Univ,Perth,WA 6150,Australia"], "Murdoch Univ,WA 6150,Australia"),
    (["Leibniz Inst Tropospher Res,Expt Aerosol & Cloud Microphys,Leipzig,Germany"], "Leibniz Inst Tropospher Res,D-04318 Leipzig,Germany"),
    (["Khallikote Univ,Ganjam 761008,Odisha,India", "Khallikote Autonomous Coll,Berhampur 760001,Orissa,India"], "Khallikote Univ,Berhampur,India"),
    (["Khalifa Univ Sci & Technol,Abu Dhabi,U Arab Emirates"], "Khalifa Univ,Abu Dhabi 127788,U Arab Emirates"),
    (["KIIT Deemed Univ,Bhubaneswar 751024,India", "KIIT Polytech,Bhubaneswar 751024,Odisha,India", "KIIT Univ,Bhubaneswar 751024,India", "KIIT Univ,Odisha,India", "KIIT,TBI,Bhubaneswar 751024,India",
      "Kalinga Inst Ind Technol KIIT,KIIT Technol Business Incubator KIIT TBI,Bhubaneswar 751024,India","Kalinga Inst Technol KIIT Deemed Univ,Bhubaneswar 751024,India"], "Kalinga Inst Ind Technol,Bhubaneswar 751024,India"),
    (["ITER SOA Univ,Bhubaneswar,Odisha,India", "S O A,ITER,Bbsr 751030,Odisha,India", "SOA Deemed Univ,Bhubaneswar 751030,India", "SOA Univ,Bhubaneswar 751030,India", "SOA Univ,ITER,Bhubaneswar,Orissa,India", "SOA,Bhubaneswar,India",
      "SOA,ITER,Bhubaneswar 751030,Odisha,India", "Siksha O Anusandhan Deemed Univ,Bhubaneswar 751030,India", "Siksha O Anusandhan,Bhubaneswar 751030,Odisha,India","Inst Tech Educ & Res,Bhubaneswar 751030,Orissa,India"], "Siksha O Anusandhan,Bhubaneswar 751030,India"),
    (["Shiv Nadar Inst Eminence SN IoE,Delhi Ncr 201314,Greater Noida,India", "Shiv Nadar Univ,Gautam Buddha Nagar 201314,Uttar Pradesh,India"], "Shiv Nadar Inst Eminence,Greater Noida 201314,India"),
    (["BMBT,CSIR,Inst Mineral & Mat Technol,Bhubaneswar 751013,Orissa,India", "Bioresource Engn Dept,Bhubaneswar 751013,Orissa,India", "CSIR IMMT,Bhubaneswar 751013,India", "CSIR IMMT,Inst Minerals & Mat Technol,Bhubaneswar 751013,Odisha,India",
      "CSIR Innovat Ctr Plasma Proc,IMMT,Bhubaneswar 751013,India", "CSIR Inst Minerals & Mat Technol,Herbal Drugs & Bioremedies,Bhubaneswar,Orissa,India", "CSIR Inst Minerals & Mat Technol,Odisha 700013,India", "CSIR Reg Res Lab,Orissa,India",
      "CSIR,IMMT,Bhubaneswar 751013,India", "CSIR,IMMT,Inst Minerals & Mat Technol,Bhubaneswar 751013,Odisha,India", "CSIR,IMMT,Odisha,India", "CSIR,RRL,Bhubaneswar,Orissa,India", "Coucil Sci & Ind Res,Bhubaneswar 751013,Orissa,India",
      "IMMT Adv Mat Lab,Bhubaneswar 751013,India", "IMMT Bhubaneswar,Bhubaneswar 751013,Orissa,India", "IMMT CMC,Bhubaneswar,Orissa,India","IMMT CSIR,Bhubaneswar 751013,Orissa,India", "IMMT,CSIR,Bhubaneswar 751013,Orissa,India", "IMMT,Khurja,Odisha,India",
      "Inst Minerals & Mat Technol CSIR IMMT,Bhubaneswar 751013,India", "Inst Minerals & Mat,Bhubaneswar 751013,Orissa,India", "Inst Sci Mat,Bhubaneswar 751013,Orissa,India", "REG RES LAB,BHUBANESWAR 751013,India",
      "RRL BHUBANESWAR,BHUBANESWAR,ORISSA,India", "RRL,Bhubaneswar,Orissa,India", "Reg Res Lab,Coun Sci & Ind Res,Bhubaneswar,Orissa,India", "Technol CSIR,Inst Minerals & Mat,Bhubaneswar 751013,Orissa,India"], "CSIR Inst Mineral & Mat Technol,Bhubaneswar 751013,India")
]


def normalize_address(addr):
    if not isinstance(addr, str):
        return ""
    addr = addr.lower()
    addr = re.sub(r"\s*,\s*", ",", addr)  # normalize comma spacing
    addr = re.sub(r"\s+", " ", addr)      # collapse spaces
    return addr.strip()

def fix_comma_spacing(addr):
    if not isinstance(addr, str):
        return addr
    addr = re.sub(r"\s*,\s*", ", ", addr)
    addr = re.sub(r"\s+", " ", addr)
    return addr.strip()

# ------------------ Manual Mapping Logic ------------------

def apply_manual_mapping(df):
    df = df.copy()
    col = "canonical_address23"

    # Build normalized lookup dict
    normalized_lookup = {}
    for variants, canonical in manual_groups:
        for var in variants:
            norm = normalize_address(var)
            normalized_lookup[norm] = canonical

    # Apply mapping
    df["manual_standardized"] = df[col].apply(
        lambda x: normalized_lookup.get(normalize_address(x), x)
    )

    # Format final addresses cleanly
    df["manual_standardized"] = df["manual_standardized"].apply(fix_comma_spacing)

    # Output final subset
    return df[["Record Index", "Original_Raw_Addresses", "Cleaned Address", "manual_standardized"]]