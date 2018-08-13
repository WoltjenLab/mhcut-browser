CREATE INDEX variants_chr_idx ON variants(chr);
CREATE INDEX variants_start_idx ON variants(pos_start);
CREATE INDEX variants_end_idx ON variants(pos_end);
CREATE INDEX variants_chr_start_end_idx ON variants(chr, pos_start, pos_end);
CREATE INDEX variants_mh_l_start_end_idx ON variants(mh_l, pos_start, pos_end);
CREATE INDEX variants_rs_idx ON variants(rs);
CREATE INDEX variants_caf_idx ON variants(caf);
CREATE INDEX variants_topmed_idx ON variants(caf);
CREATE INDEX variants_gene_info_idx ON variants(gene_info);
CREATE INDEX variants_pm_idx ON variants(pm);
CREATE INDEX variants_mc_idx ON variants(mc);
CREATE INDEX variants_af_exac_idx ON variants(af_exac);
CREATE INDEX variants_af_tgp_idx ON variants(af_tgp);
CREATE INDEX variants_allele_id_idx ON variants(allele_id);
CREATE INDEX variants_clndn_idx ON variants(clndn);
CREATE INDEX variants_clnsig_idx ON variants(clnsig);
-- CREATE INDEX variants_gene_info_clinvar_idx ON variants(gene_info_clinvar);
CREATE INDEX variants_geneloc_idx ON variants(geneloc);
CREATE INDEX variants_mh_l_idx ON variants(mh_l);
CREATE INDEX variants_pam_uniq_idx ON variants(pam_uniq);
CREATE INDEX variants_guides_no_ot_idx ON variants(guides_no_ot) WHERE guides_no_ot IS NOT NULL;
CREATE INDEX variants_guides_min_ot_idx ON variants(guides_min_ot) WHERE guides_min_ot IS NOT NULL;
