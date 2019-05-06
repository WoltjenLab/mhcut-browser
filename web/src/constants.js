export const CONDITION_OPERATORS = {
    both: ["equals", "<", "<=", ">", ">="],
    text: ["contains", "starts_with", "ends_with"],
    nullable: ["is_null"]
};

export const DEFAULT_CONDITION_BOOLEAN = "AND";

export const COLUMN_HELP_TEXT = {
    id: "Database ID.",
    chr: "Chromosome.",
    pos_start: "Starting position.",
    pos_end: "Ending position.",
    rs: "dbSNP ID.",
    caf: "Allele frequency from 1000GP, extracted from dbSNP.",
    topmed: "Allele frequency from TOPMED, extracted from dbSNP.",
    gene_info: "Genes overlapping the variants extracted from dbSNP.",
    pm: "Variant is precious (clinical, PubMed-cited). Extracted from dbSNP.",
    mc: "Molecular consequences, from dbSNP. Acronym Key: NSF=frameshift, NSN=nonsense, NSM=missense, " +
        "SYN=synonymous, INT=intronic, ASS/DSS=in acceptor/donor splice site, U3/U5=in UTR 3/5, " +
        "R3/R5=in upstream/downstream gene region.",
    af_exac: "Allele frequency from ExAC, extracted from ClinVar.",
    af_tgp: "Allele frequency from 1000GP, extracted from ClinVar.",
    allele_id: "ClinVar ID.",
    clndn: "ClinVar's preferred disease name for the concept specified by disease identifiers in CLNDISDB.",
    clnsig: "Clinical significance. E.g. \"Pathogenic\".",
    dbvarid: "Some variants in ClinVar are not in dbSNP but in dbVar. In that case this column contains the dbVar ID.",
    gene_info_clinvar: "Same as gene_info, but extracted from ClinVar.",
    mc_clinvar: "Molecular consequences, extracted from ClinVar.",

    citation: "The citation(s) associated with the variant (from PubMed, PubMedCentral, or the NCBI Bookshelf).", // TODO
    location: "The location of the variant relative to genes (Gencode v28).", // TODO
    var_l: "The variant size (bp).", // TODO

    mh_l: "MH length.",
    mh_1l: "Number of first consecutive matches.",
    hom: "Proportion of matches.",
    nbmm: "Number of mismatches.",
    mh_max_cons: "Longest stretch of consecutive matches in the MH.",
    mh_dist: "Distance between the end of MH and the variant boundary.",
    mh_1dist: "Distance between the end of the first consecutive matches and the variant boundary.",
    mh_seq_1: "Sequence 1 of the MH.",
    mh_seq_2: "Sequence 2 of the MH.",
    gc: "GC content of the MH sequence.",
    pam_mot: "The number of PAMs in a valid location.",
    pam_uniq: "The number of PAMs in a valid location and whose protospacer sequence is unique in the genome.",
    guides_no_nmh: "The number of guides that have no nested MH.",
    guides_min_nmh: "The number of nested MHs for the guide which has the least amount of nested MH.",
    max_2_cuts_dist: "The distance between the two cuts that are the furthest from each other. Only PAMs whose protospacer sequence is unique in the genome are considered", // TODO

    cartoon: "Cartoon showing the variant region, annotated with the microhomology (top) and the positions of valid cuts (bottom).", // TODO

    variant_id: "Corresponding variant database ID.",

    protospacer: "The sequence of the protospacer.",
    mm0: "The number of positions in the genome where the sequence aligns with no mismatches.",
    mm1: "The number of positions in the genome where the sequence aligns with 1 mismatch.",
    mm2: "The number of positions in the genome where the sequence aligns with 2 mismatches.",
    m1_dist_1: "Considering perfect homology only, the distance between the cut position and the upstream microhomology.", // TODO: grammar???
    m1_dist_2: "Considering perfect homology only, the distance between the cut position and the downstream microhomology.", // TODO: grammar???
    mh_dist_1: "The distance between the cut position and the upstream microhomology.", // TODO: grammar???
    mh_dist_2: "The distance between the cut position and the downstream microhomology.", // TODO: grammar???
    nb_nmh: "The number of nested MHs.",
    largest_nmh: "The size of the largest nested MH.",
    nmh_score: "The MMEJ score of the best nested MH (\"best\" defined as the highest MMEJ score).",
    nmh_size: "The MH length of the best nested MH (\"best\" defined as the highest MMEJ score).",
    nmh_var_l: "The length of the variant created by the best nested MH (\"best\" defined as the highest MMEJ score).",
    nmh_gc: "The GC content of the best nested MH (\"best\" defined as the highest MMEJ score).",
    nmh_seq: "The sequence of the best nested MH (\"best\" defined as the highest MMEJ score).",
};

export const VARIANTS_LAYOUT = [
    {
        group_name: "IDs",
        default_columns: ["id", "rs"],
        optional_columns: ["allele_id", "dbvarid"]
    },
    {
        group_name: "Variant Features",
        default_columns: ["gene_info", "chr", "pos_start", "pos_end", "location", "var_l"],
        optional_columns: ["gene_info_clinvar"]
    },
    {
        group_name: "Clinical Significance",
        default_columns: ["clndn", "clnsig", "mc"],
        optional_columns: ["mc_clinvar", "pm", "citation"]
    },
    {
        group_name: "Microhomology Features",
        default_columns: ["mh_l", "mh_1l", "hom", "mh_dist", "mh_1dist", "mh_seq_1", "mh_seq_2"],
        optional_columns: ["nbmm", "mh_max_cons", "gc"]
    },
    {
        group_name: "Guide RNA Features",
        default_columns: ["pam_mot", "pam_uniq", "guides_no_nmh"],
        optional_columns: ["guides_min_nmh", "max_2_cuts_dist"]
    },
    {
        group_name: "Cartoon",
        default_columns: ["cartoon"],
        optional_columns: []
    },
    {
        // TODO: OPTIONAL GROUP
        group_name: "Allele Frequency",
        default_columns: ["caf", "topmed", "af_exac", "af_tgp"],
        optional_columns: []
    }
];

export const GUIDES_LAYOUT = [
    {
        group_name: "IDs",
        default_columns: ["id", "variant_id"],
        optional_columns: []
    },
    {
        group_name: "Guide RNA Features",
        default_columns: ["protospacer", "mm0", "mm1", "mm2", "m1_dist_1", "m1_dist_2", "mh_dist_1", "mh_dist_2"],
        optional_columns: []
    },
    {
        group_name: "Nested Microhomologies",
        default_columns: ["nb_nmh", "largest_nmh", "nmh_size", "nmh_var_l", "nmh_seq"],
        optional_columns: ["nmh_gc"]
    },
    {
        group_name: "Scores",
        default_columns: [],
        optional_columns: []
    }
];
