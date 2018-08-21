#!/usr/bin/env python3

import json as pyjson
import os
import os.path
import re
import psycopg2
import psycopg2.extras

from flask import Flask, g, json, request, Response
from typing import Pattern


BASE_DIR = os.path.dirname(__file__)

# Version for Metadata Endpoint
__version__ = json.load(open(os.path.join(BASE_DIR, "web/package.json"), "r"))["version"]


# Database Setup
DATABASE_PATH = os.path.join(BASE_DIR, "db.sqlite")


# Search Operator / Condition Domains
SEARCH_OPERATORS = {
    "equals": ("=", "{}"),
    "<": ("<", "{}"),
    "<=": ("<=", "{}"),
    ">": (">", "{}"),
    ">=": (">=", "{}"),

    # TEXT
    "contains": ("LIKE", "%{}%"),
    "starts_with": ("LIKE", "{}%"),
    "ends_with": ("LIKE", "%{}"),

    # NULLABLE
    "is_null": ("IS NULL", "")
}

# Domain lists for metadata endpoint
CHR_VALUES = ("chr1", "chr2", "chr3", "chr4", "chr5", "chr6", "chr7", "chr8", "chr9", "chr10",
              "chr11", "chr12", "chr13", "chr14", "chr15", "chr16", "chr17", "chr18", "chr19",
              "chr20", "chr21", "chr22", "chrX", "chrY")
LOCATION_VALUES = ("intronic", "exonic", "intergenic")

# Domains
CHR_DOMAIN = re.compile("^(chr(1|2|3|4|5|6|7|8|9|10|11|12|13|14|15|16|17|18|19|20|21|22|X|Y)|any)$")
POS_INT_DOMAIN = re.compile("^[1-9]\d*$")
NON_NEG_INT_DOMAIN = re.compile("^\d+$")
BOOLEAN_DOMAIN = re.compile("^(true|false)$")
POSITION_OPERATOR_DOMAIN = re.compile("^(overlap|not_overlap|within)$")
SORT_ORDER_DOMAIN = re.compile("^(ASC|DESC)$")

app = Flask(__name__)


class DomainError(Exception):
    """
    Error to be thrown if a variable's value falls outside of its domain.
    """
    pass


def verify_domain(value, domain: Pattern):
    if re.match(domain, str(value)):
        return value
    raise DomainError


def search_param(c):
    return "search_cond_{}".format(str(c).strip())


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = psycopg2.connect("dbname=crispr user={} password={}".format(
            os.environ.get("DB_USER"),
            os.environ.get("DB_PASSWORD")
        ))
    return db


def get_variants_columns(c):
    c.execute("SELECT column_name, is_nullable, data_type FROM information_schema.columns "
              "WHERE table_schema = 'public' AND table_name = 'variants' AND column_name != 'full_row'")
    return tuple([dict(i) for i in c.fetchall()])


def build_variants_columns_domain(c):
    return re.compile("^({})$".format("|".join([i["column_name"] for i in get_variants_columns(c)])))


def get_guides_columns(c):
    c.execute("SELECT column_name, is_nullable, data_type FROM information_schema.columns "
              "WHERE table_schema = 'public' AND table_name = 'guides'")
    return tuple([dict(i) for i in c.fetchall()])


def build_search_query(raw_query, c):
    search_query_fragment = ""
    search_query_data = {}

    try:
        column_names = [c["column_name"] for c in get_variants_columns(c)]

        query_obj = json.loads(raw_query)
        for c in query_obj:
            if c["field"] not in column_names:
                continue

            if c["operator"] not in SEARCH_OPERATORS.keys():
                continue

            op_data = SEARCH_OPERATORS[c["operator"]]

            if search_query_fragment != "":
                search_query_fragment += " {} ".format(c["boolean"])

            search_query_fragment += "({}({} {}".format("NOT " if c["negated"] else "", c["field"], op_data[0])

            if op_data[1] != "":
                search_query_fragment += " %({})s".format(search_param(c["id"]))
                search_query_data[search_param(c["id"])] = op_data[1].format(c["value"])

            search_query_fragment += "))"

    except (pyjson.decoder.JSONDecodeError, TypeError, AttributeError):
        if raw_query.strip() == "":
            return "true", search_query_data

        search_query_fragment = "full_row LIKE %(full_row_cond)s "
        search_query_data = {"full_row_cond": "%{}%".format(raw_query.strip().lower())}

    return search_query_fragment, search_query_data


def get_search_params_from_request(c):
    chromosomes = [ch for ch in request.args.get("chr", "").split(",") if re.match(CHR_DOMAIN, ch)]
    if len(chromosomes) == 0:
        chromosomes = list(CHR_VALUES)
    chr_fragment = "(" + ",".join(["'{}'::CHROMOSOME".format(ch) for ch in chromosomes]) + ")"

    start_pos = int(verify_domain(request.args.get("start", "0"), NON_NEG_INT_DOMAIN))
    end_pos = int(verify_domain(request.args.get("end", "1000000000000"), POS_INT_DOMAIN))
    position_filter_fragment = ("pos_start <= %(end_pos)s AND pos_end >= %(start_pos)s"
                                if not (start_pos == 0 and end_pos == 1000000000000) else "true")

    gene_locations = [l.strip() for l in request.args.get("location", "").split(",") if l.strip() in LOCATION_VALUES]
    if len(gene_locations) == 0:
        gene_locations = list(LOCATION_VALUES)
    location_fragment = "(" + ",".join(["'{}'::GENE_LOCATION".format(l) for l in gene_locations]) + ")"

    min_mh_l = int(verify_domain(request.args.get("min_mh_l", "0"), NON_NEG_INT_DOMAIN))

    dbsnp = verify_domain(request.args.get("dbsnp", "false"), BOOLEAN_DOMAIN) == "true"
    clinvar = verify_domain(request.args.get("clinvar", "false"), BOOLEAN_DOMAIN) == "true"

    ngg_pam_avail = verify_domain(request.args.get("ngg_pam_avail", "false"), BOOLEAN_DOMAIN) == "true"
    unique_guide_avail = verify_domain(request.args.get("unique_guide_avail", "false"), BOOLEAN_DOMAIN) == "true"

    search_query_fragment, search_query_data = build_search_query(request.args.get("search_query", ""), c)

    return {
        "chr": chromosomes,
        "chr_fragment": chr_fragment,

        "start_pos": start_pos,
        "end_pos": end_pos,

        "position_filter_fragment": position_filter_fragment,
        "location": gene_locations,
        "location_fragment": location_fragment,

        "min_mh_l": min_mh_l,

        "dbsnp": dbsnp,
        "clinvar": clinvar,

        "ngg_pam_avail": ngg_pam_avail,
        "unique_guide_avail": unique_guide_avail,

        "search_query_fragment": search_query_fragment,
        "search_query_data": search_query_data
    }


def build_variants_query(c, selection, search_params, cartoons=False, sort_by=None, sort_order=None, page=None,
                         items_per_page=None):
    return c.mogrify(
        "SELECT {} FROM variants {} WHERE {}{}{} "
        "NOT ((%(dbsnp)s AND rs IS NULL) OR (%(clinvar)s AND gene_info_clinvar IS NULL)) "
        "AND (pam_mot > 0 OR NOT %(ngg_pam_avail)s) AND (pam_uniq > 0 OR NOT %(unique_guide_avail)s) "
        "AND ({}) AND ({}) {}{}{}".format(
            selection,
            "LEFT JOIN cartoons ON id = variant_id" if cartoons else "",
            "(chr IN {}) AND ".format(search_params["chr_fragment"])
            if len(search_params["chr"]) < len(CHR_VALUES) else "",
            "(location IN {}) AND ".format(search_params["location_fragment"])
            if len(search_params["location"]) < len(LOCATION_VALUES) else "",
            "(mh_l >= %(min_mh_l)s) AND " if search_params["min_mh_l"] > 0 else "",
            search_params["position_filter_fragment"],
            search_params["search_query_fragment"],
            "ORDER BY {} {} ".format(sort_by, sort_order) if sort_by is not None and sort_order is not None else "",
            "LIMIT %(items_per_page)s " if items_per_page is not None else "",
            "OFFSET %(start)s" if page is not None else ""
        ),
        {
            "start": ((page if page is not None else 0) - 1) * (items_per_page if items_per_page is not None else 0),
            "items_per_page": items_per_page,
            "start_pos": search_params["start_pos"],
            "end_pos": search_params["end_pos"],
            "min_mh_l": search_params["min_mh_l"],
            "dbsnp": search_params["dbsnp"],
            "clinvar": search_params["clinvar"],
            "ngg_pam_avail": search_params["ngg_pam_avail"],
            "unique_guide_avail": search_params["unique_guide_avail"],
            **search_params["search_query_data"]
        }
    )


@app.route("/", methods=["GET"])
def index():
    c = get_db().cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    c.execute(build_variants_query(
        c,
        "variants.*, cartoon_text AS cartoon",
        get_search_params_from_request(c),
        cartoons=True,
        sort_by=verify_domain(request.args.get("sort_by", "id"), build_variants_columns_domain(c)),
        sort_order=verify_domain(request.args.get("sort_order", "ASC").upper(), SORT_ORDER_DOMAIN),
        page=int(verify_domain(request.args.get("page", "1"), POS_INT_DOMAIN)),
        items_per_page=int(verify_domain(request.args.get("items_per_page", "100"), POS_INT_DOMAIN))
    ))

    results = c.fetchall()
    for r in results:
        del r["full_row"]
    return json.jsonify(results)


@app.route("/tsv", methods=["GET"])
def variants_tsv():
    c = get_db().cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    search_params = get_search_params_from_request(c)

    sort_by = verify_domain(request.args.get("sort_by", "id"), build_variants_columns_domain(c))
    sort_order = verify_domain(request.args.get("sort_order", "ASC").upper(), SORT_ORDER_DOMAIN)

    column_names = [i["column_name"] for i in get_variants_columns(c)]

    def generate():
        with app.app_context():
            c2 = get_db().cursor("variants-tsv-cursor")
            c2.execute(build_variants_query(c2, "*", search_params, sort_by=sort_by, sort_order=sort_order))

            yield "\t".join(column_names) + "\n"
            row = c2.fetchone()
            while row is not None:
                yield "\t".join([str(col) if col is not None else "NA" for col in row[:-1]]) + "\n"
                row = c2.fetchone()

    return Response(generate(), mimetype="text/tab-separated-values",
                    headers={"Content-Disposition": "Content-Disposition: attachment; filename=\"variants.tsv\""})


@app.route("/variants/<int:variant_id>/guides", methods=["GET"])
def variant_guides(variant_id):
    c = get_db().cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    c.execute("SELECT * FROM guides WHERE variant_id = %s", (variant_id,))
    return json.jsonify(c.fetchall())


@app.route("/variants/<int:variant_id>/guides/tsv", methods=["GET"])
def variant_guides_tsv(variant_id):
    c = get_db().cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    column_names = [i["column_name"] for i in get_guides_columns(c)]

    def generate():
        with app.app_context():
            c2 = get_db().cursor("variant-guides-tsv-cursor")
            c2.execute("SELECT * FROM guides WHERE variant_id = %s", (variant_id,))

            yield "\t".join(column_names) + "\n"
            row = c2.fetchone()
            while row is not None:
                yield "\t".join([str(col) if col is not None else "NA" for col in row]) + "\n"
                row = c2.fetchone()

    return Response(generate(), mimetype="text/tab-separated-values",
                    headers={"Content-Disposition": "Content-Disposition: attachment; "
                                                    "filename=\"variant_{}_guides.tsv\"".format(variant_id)})


@app.route("/guides", methods=["GET"])
def guides():
    page = int(verify_domain(request.args.get("page", "1"), POS_INT_DOMAIN))
    items_per_page = int(verify_domain(request.args.get("items_per_page", "100"), POS_INT_DOMAIN))

    c = get_db().cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    search_params = get_search_params_from_request(c)

    sort_by = verify_domain(request.args.get("sort_by", "id"), build_variants_columns_domain(c))
    sort_order = verify_domain(request.args.get("sort_order", "ASC").upper(), SORT_ORDER_DOMAIN)

    # TODO: ALLOW SORTING GUIDES AS WELL?

    c.execute("SELECT * FROM guides WHERE variant_id IN ({}) ORDER BY id".format(build_variants_query(
        c,
        "id",
        search_params,

        sort_by=sort_by,
        sort_order=sort_order,

        page=page,
        items_per_page=items_per_page
    ).decode("utf-8")))

    return json.jsonify(c.fetchall())


@app.route("/guides/tsv", methods=["GET"])
def guides_tsv():
    c = get_db().cursor(cursor_factory=psycopg2.extras.DictCursor)
    search_params = get_search_params_from_request(c)
    column_names = [i["column_name"] for i in get_guides_columns(c)]

    def generate():
        with app.app_context():
            c2 = get_db().cursor("guides-tsv-cursor")
            c2.execute("SELECT * FROM guides WHERE variant_id IN "
                       "({})".format(build_variants_query(c, "id", search_params).decode("utf-8")))

            yield "\t".join(column_names) + "\n"
            row = c2.fetchone()
            while row is not None:
                yield "\t".join([str(col) if col is not None else "NA" for col in row]) + "\n"
                row = c2.fetchone()

    return Response(generate(), mimetype="text/tab-separated-values",
                    headers={"Content-Disposition": "Content-Disposition: attachment; filename=\"guides.tsv\""})


@app.route("/combined/tsv", methods=["GET"])
def combined_tsv():
    c = get_db().cursor(cursor_factory=psycopg2.extras.DictCursor)

    search_params = get_search_params_from_request(c)

    sort_by = verify_domain(request.args.get("sort_by", "id"), build_variants_columns_domain(c))
    sort_order = verify_domain(request.args.get("sort_order", "ASC").upper(), SORT_ORDER_DOMAIN)

    variants_column_names = [i["column_name"] for i in get_variants_columns(c)]
    guides_column_names = [i["column_name"] for i in get_guides_columns(c)]

    def generate():
        with app.app_context():
            c2 = get_db().cursor("combined-tsv-cursor")
            c2.execute(build_variants_query(c, "*", search_params, sort_by, sort_order))

            yield "\t".join(variants_column_names + [col if col != "id" else "guide_id"
                                                     for col in guides_column_names]) + "\n"
            c3 = get_db().cursor()
            row = c2.fetchone()
            while row is not None:
                row_to_return = [str(col) if col is not None else "NA" for col in row[:-1]]

                yield "\t".join(row_to_return) + "\n"

                c3.execute("SELECT * FROM guides WHERE variant_id = %s", (row_to_return[0],))
                guide_row = c3.fetchone()
                while guide_row is not None:
                    yield "\t".join(([""] * len(variants_column_names))
                                    + [str(col) if col is not None else "NA" for col in guide_row]) + "\n"
                    guide_row = c3.fetchone()

                row = c2.fetchone()

    return Response(generate(), mimetype="text/tab-separated-values",
                    headers={"Content-Disposition": "Content-Disposition: attachment; "
                                                    "filename=\"variants_with_guides.tsv\""})


@app.route("/variants/entries", methods=["GET"])
def variants_entries():
    c = get_db().cursor(cursor_factory=psycopg2.extras.DictCursor)

    entries_query = build_variants_query(c, "COUNT(*)", get_search_params_from_request(c))

    c.execute("SELECT * FROM entries_query_cache WHERE e_query = %s::bytea", (entries_query,))
    cache_value = c.fetchone()

    if cache_value is None:
        c.execute(entries_query)
        num_entries = c.fetchone()[0]
        c.execute("INSERT INTO entries_query_cache VALUES(%s::bytea, %s)", (entries_query, num_entries))
        get_db().commit()
    else:
        num_entries = cache_value[1]

    return json.jsonify(num_entries)


@app.route("/guides/entries", methods=["GET"])
def guides_entries():
    c = get_db().cursor(cursor_factory=psycopg2.extras.DictCursor)
    search_params = get_search_params_from_request(c)

    entries_query = c.mogrify("SELECT COUNT(*) FROM guides WHERE variant_id IN "
                              "({})".format(build_variants_query(c, "id", search_params).decode("utf-8")))

    c.execute("SELECT * FROM entries_query_cache WHERE e_query = %s::bytea", (entries_query,))
    cache_value = c.fetchone()

    if cache_value is None:
        c.execute(entries_query)
        num_entries = c.fetchone()[0]
        c.execute("INSERT INTO entries_query_cache VALUES(%s::bytea, %s)", (entries_query, num_entries))
        get_db().commit()
    else:
        num_entries = cache_value[1]

    return json.jsonify(num_entries)


@app.route("/fields", methods=["GET"])
def fields():
    c = get_db().cursor(cursor_factory=psycopg2.extras.DictCursor)
    return json.jsonify({
        "variants": get_variants_columns(c),
        "guides": get_guides_columns(c)
    })


@app.route("/metadata", methods=["GET"])
def metadata():
    """
    Returns various metadata and summary statistics about the entries in the database. Does not respect filtering
    parameters.
    :return: A JSON response with metadata and summary statistics.
    """
    c = get_db().cursor(cursor_factory=psycopg2.extras.DictCursor)
    c.execute("SELECT (SELECT CAST(s_value AS INTEGER) FROM summary_statistics WHERE s_key = 'min_pos') AS min_pos, "
              "  (SELECT CAST(s_value AS INTEGER) FROM summary_statistics WHERE s_key = 'max_pos') AS max_pos, "
              "  MAX(mh_l) AS max_mh_l FROM variants")
    return json.jsonify({
        **dict(c.fetchone()),
        "chr": CHR_VALUES,
        "location": LOCATION_VALUES,
        "version": __version__
    })


@app.teardown_appcontext
def close_connection(_exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


if __name__ == "__main__":
    app.run()
