-- noinspection SqlResolveForFile

CREATE INDEX variants_start_idx ON variants(pos_start);
CREATE INDEX variants_end_idx ON variants(pos_end);
CREATE UNIQUE INDEX variants_chr_start_end_rs_idx ON variants(chr, pos_start, pos_end, rs);
CREATE INDEX variants_rs_idx ON variants(rs);
CREATE INDEX variants_caf_idx ON variants(caf);
CREATE INDEX variants_topmed_idx ON variants(topmed);
CREATE INDEX variants_gene_info_idx ON variants(gene_info);
CREATE INDEX variants_gene_info_trgm_idx ON variants USING gin(gene_info gin_trgm_ops) WHERE gene_info IS NOT NULL;
CREATE INDEX variants_pm_idx ON variants(pm);
CREATE INDEX variants_mc_idx ON variants(mc);
CREATE INDEX variants_af_exac_idx ON variants(af_exac);
CREATE INDEX variants_af_tgp_idx ON variants(af_tgp);
CREATE INDEX variants_allele_id_idx ON variants(allele_id);
CREATE INDEX variants_clndn_idx ON variants(clndn);
CREATE INDEX variants_clnsig_idx ON variants(clnsig);
CREATE INDEX variants_dbvarid_idx ON variants(dbvarid);
CREATE INDEX variants_gene_info_clinvar_idx ON variants(gene_info_clinvar);
CREATE INDEX variants_gene_info_clinvar_trgm_idx ON variants
  USING gin(gene_info_clinvar gin_trgm_ops) WHERE gene_info_clinvar IS NOT NULL;
CREATE INDEX variants_mc_clinvar_idx ON variants(mc_clinvar);
CREATE INDEX variants_citation_idx ON variants(citation);
CREATE INDEX variants_location_idx ON variants(location);
CREATE INDEX variants_var_l_idx ON variants(var_l);
CREATE INDEX variants_mh_l_start_end_idx ON variants(mh_l, pos_start, pos_end);
CREATE INDEX variants_mh_1l_idx ON variants(mh_1l);
CREATE INDEX variants_hom_idx ON variants(hom);
CREATE INDEX variants_nbmm_idx ON variants(nbmm);
CREATE INDEX variants_mh_dist_idx ON variants(mh_dist);
CREATE INDEX variants_mh_seq_1_idx ON variants(mh_seq_1);
CREATE INDEX variants_mh_seq_2_idx ON variants(mh_seq_2);
CREATE INDEX variants_pam_mot_idx ON variants(pam_mot);
CREATE INDEX variants_pam_uniq_idx ON variants(pam_uniq);
CREATE INDEX variants_guides_no_ot_idx ON variants(guides_no_ot) WHERE guides_no_ot IS NOT NULL;
CREATE INDEX variants_guides_min_ot_idx ON variants(guides_min_ot) WHERE guides_min_ot IS NOT NULL;
CREATE INDEX variants_max_2_cuts_dist_idx ON variants(max_2_cuts_dist);
CREATE INDEX variants_full_row_trgm_idx ON variants USING gin(full_row gin_trgm_ops);
