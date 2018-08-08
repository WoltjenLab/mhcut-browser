DROP TABLE IF EXISTS variants;
DROP TABLE IF EXISTS guides;

CREATE TABLE variants (
  id INTEGER PRIMARY KEY,
  chr TEXT NOT NULL CHECK (chr IN ('chr1', 'chr2', 'chr3', 'chr4', 'chr5', 'chr6', 'chr7', 'chr8', 'chr9', 'chr10',
                                   'chr11', 'chr12', 'chr13', 'chr14', 'chr15', 'chr16', 'chr17', 'chr18', 'chr19',
                                   'chr20', 'chr21', 'chr22', 'chrX', 'chrY')),
  start INTEGER NOT NULL CHECK (start >= 0),
  end INTEGER NOT NULL CHECK (end >= 0),
  rs INTEGER CHECK (rs >= 0), -- Reference SNP
  caf TEXT, -- TODO: WHAT IS THIS?
  topmed TEXT, -- TODO: WHAT IS THIS?
  gene_info TEXT, -- TODO: WHAT IS THIS?
  pm TEXT, -- TODO: WHAT IS THIS? - NA VS. "-"
  mc TEXT, -- TODO: NA VS. "-"?
  af_exac TEXT,
  af_tgp TEXT,
  allele_id INTEGER CHECK (allele_id >= 0),
  clndn TEXT,
  clnsig TEXT,
  dbvarid TEXT,
  gene_info_clinvar TEXT, -- NA is represented as NULL, '-' is left as-is
  mc_clinvar TEXT,
  citation TEXT,
  geneloc TEXT NOT NULL CHECK (geneloc IN ('intronic', 'exonic', 'intergenic')),
  var_l INTEGER NOT NULL CHECK (var_l >= 0), -- Variant Size
  mh_l INTEGER NOT NULL CHECK (mh_l >= 0), -- Micro-Homology Length
  mh_1l INTEGER NOT NULL CHECK (mh_1l >= 0), -- Number of First Consecutive Matches
  hom TEXT, -- Decimal field with precision 1 or 2
  nbmm INTEGER NOT NULL CHECK (nbmm >= 0),
  mh_dist INTEGER,
  mh_seq_1 TEXT,
  mh_seq_2 TEXT,
  pam_mot INTEGER CHECK (pam_mot >= 0), -- NULL means NA
  pam_uniq INTEGER CHECK (pam_uniq >= 0), -- NULL means NA
  guides_no_ot INTEGER CHECK (guides_min_ot >= 0), -- NULL means NA
  guides_min_ot INTEGER CHECK (guides_min_ot >= 0) -- NULL means NA
);

CREATE TABLE guides (
  id INTEGER PRIMARY KEY,
  variant_id INTEGER NOT NULL REFERENCES variants,
  protospacer TEXT,
  mm0 INTEGER, -- NULL means NA
  mm1 INTEGER, -- NULL means NA
  mm2 INTEGER, -- NULL means NA
  m1_dist_1 INTEGER NOT NULL,
  m1_dist_2 INTEGER NOT NULL,
  mh_dist_1 INTEGER NOT NULL,
  mh_dist_2 INTEGER NOT NULL,
  nb_off_tgt INTEGER, -- NULL means NA
  largest_off_tgt INTEGER, -- NULL means NA
  bot_score TEXT NOT NULL,
  bot_size TEXT,
  bot_var_l INTEGER, -- NULL means NA
  bot_gc INTEGER, -- NULL means NA
  bot_seq TEXT -- NULL means NA
);
