"""Semantic failure-mode tests, not tests of model performance."""
import copy
import csv
import io
import json
import pathlib
import tempfile
import unittest

import build_catalogue as b


def source_row(pid="100", sku=None, size="M", **changes):
    r = dict.fromkeys(b.HEADER, "")
    r.update({"uniq_id": "a" * 32, "product_id": pid,
              "variant_sku": sku or pid + "_" + size, "size": size,
              "title": "Brand Blue Kurta", "brand": "Brand", "ideal_for": "Women",
              "type": "Clothing/Women/Kurtas/Brand", "variant_price": "599",
              "is_in_stock": "In Stock", "inventory": "2",
              "specifications": "Neck : Round Neck | Sleeve Length : Long Sleeves | Fabric : Cotton | Wash Care : Machine Wash | Pattern : Printed | Number of Components : 1",
              "product_details": "Blue kurta, has a round neck and long sleeves",
              "care_instructions": "Cotton | Machine-wash", "dominant_material": "Cotton"})
    r.update(changes)
    return r


def parse_rows(rows):
    text = io.StringIO()
    writer = csv.writer(text)
    writer.writerow(b.HEADER)
    writer.writerows([r[x] for x in b.HEADER] for r in rows)
    return b.parse_source(text.getvalue().encode())


def products_from(rows):
    variants, claims, blanks, invalid = parse_rows(rows)
    config = json.loads((b.BASE / "config.json").read_text())
    return b.build_products(variants, claims, config), variants, claims


class CatalogueTest(unittest.TestCase):
    def test_specification_in_inventory_is_not_stock(self):
        r = source_row()
        r["inventory"], r["specifications"] = r["specifications"], ""
        products, variants, _ = products_from([r])
        self.assertTrue(products[0]["quality"]["strict_eligible"])
        self.assertIsNone(variants[0]["inventory"])
        self.assertEqual(variants[0]["recovered_specification_columns"], ["inventory"])

    def test_evidence_spans_are_exact_with_html_and_unicode(self):
        blob = "  Neck : V–Neck | Pattern : Black &amp; White  "
        claims, bad = b.parse_specification(blob, 2, "specifications", 22)
        self.assertFalse(bad)
        for c in claims:
            a, z = c["span"]
            self.assertEqual(blob[a:z], c["fragment"])
        self.assertEqual(claims[0]["normalized_value"], "v-neck")
        self.assertEqual(claims[1]["normalized_value"], "black & white")

    def test_unknown_is_not_negative(self):
        r = source_row(specifications="Fabric : Cotton")
        p = products_from([r])[0][0]
        self.assertEqual(p["attributes"]["neckline"]["status"], "unknown")
        self.assertIsNone(p["attributes"]["neckline"]["value"])
        self.assertFalse(p["quality"]["strict_eligible"])

    def test_component_fabric_does_not_become_whole_garment_fabric(self):
        r = source_row()
        r["specifications"] = r["specifications"].replace("Fabric : Cotton", "Top Fabric : Cotton")
        p = products_from([r])[0][0]
        self.assertEqual(p["attributes"]["fabric"]["status"], "unknown")
        self.assertEqual(p["attributes"]["top_fabric"]["value"], "cotton")
        self.assertFalse(p["quality"]["strict_eligible"])

    def test_variants_merge_without_losing_size_or_price(self):
        ps, variants, _ = products_from([source_row(), source_row(size="L", variant_price="699")])
        self.assertEqual(len(ps), 1)
        self.assertEqual(len(variants), 2)
        self.assertEqual(ps[0]["size_labels"], ["L", "M"])
        self.assertEqual(ps[0]["source_price"]["values"], ["599", "699"])
        self.assertIn("one_source_price", ps[0]["quality"]["exclusion_reasons"])

    def test_disagreeing_variants_are_ambiguous(self):
        r = source_row(size="L")
        r["specifications"] = r["specifications"].replace("Round Neck", "V-Neck")
        p = products_from([source_row(), r])[0][0]
        self.assertEqual(p["attributes"]["neckline"]["status"], "ambiguous")
        self.assertIsNone(p["attributes"]["neckline"]["value"])
        self.assertFalse(p["quality"]["strict_eligible"])

    def test_multiple_values_are_retained(self):
        r = source_row()
        r["specifications"] += " | Neck : V-Neck"
        p = products_from([r])[0][0]
        self.assertEqual(p["attributes"]["neckline"]["reported_values"], ["round neck", "v-neck"])

    def test_care_does_not_define_exclusive_permissions(self):
        positive, negative = b.care_mentions("Cotton | Hand-wash")
        self.assertEqual(positive, {"hand wash"})
        self.assertFalse(negative)

    def test_negated_care_is_not_a_positive_instruction(self):
        positive, negative = b.care_mentions("Do not machine wash. Dry-clean only")
        self.assertEqual(positive, {"dry clean"})
        self.assertEqual(negative, {"machine wash"})

    def test_concatenated_care_text_is_recognized(self):
        positive, _ = b.care_mentions("100% cottonMachine-wash")
        self.assertEqual(positive, {"machine wash"})

    def test_care_contradiction_excluded(self):
        p = products_from([source_row(care_instructions="Cotton | Dry-clean")])[0][0]
        self.assertIn("no_detected_core_discordance", p["quality"]["exclusion_reasons"])

    def test_neck_and_sleeve_conflicts_detected(self):
        p = products_from([source_row(product_details="Blue kurta, has a V-neck and short sleeves")])[0][0]
        kinds = {x["kind"] for x in p["quality"]["discordances"]}
        self.assertIn("neckline_description_discordance", kinds)
        self.assertIn("sleeve_length_description_discordance", kinds)

    def test_decorative_neck_detail_is_not_an_exclusive_shape(self):
        r = source_row()
        r["specifications"] = r["specifications"].replace("Round Neck", "Keyhole Neck")
        p = products_from([r])[0][0]
        self.assertFalse(p["quality"]["discordances"])

    def test_collar_with_split_v_neckline_is_not_forced_exclusive(self):
        r = source_row(product_details="A mandarin collar with a split V-neckline and long sleeves")
        r["specifications"] = r["specifications"].replace("Round Neck", "V-Neck")
        p = products_from([r])[0][0]
        self.assertFalse(p["quality"]["discordances"])

    def test_printed_and_floral_are_separate_axes(self):
        r = source_row()
        r["specifications"] += " | Print or Pattern Type : Floral"
        p = products_from([r])[0][0]
        self.assertEqual(p["attributes"]["pattern"]["value"], "printed")
        self.assertEqual(p["attributes"]["print_pattern_type"]["value"], "floral")
        self.assertFalse(p["quality"]["discordances"])

    def test_cotton_is_not_normalized_into_pure_cotton(self):
        r = source_row()
        r["specifications"] = r["specifications"].replace("Fabric : Cotton", "Fabric : Pure Cotton")
        p = products_from([r])[0][0]
        self.assertEqual(p["attributes"]["fabric"]["value"], "pure cotton")
        self.assertFalse(p["quality"]["discordances"])

    def test_disjoint_known_material_labels_excluded(self):
        p = products_from([source_row(dominant_material="Polyester")])[0][0]
        self.assertTrue(any(x["kind"] == "fabric_label_discordance" for x in p["quality"]["discordances"]))

    def test_sets_not_flattened_or_given_single_garment_conflicts(self):
        r = source_row(type="Clothing/Women/Kurta Sets/Brand", product_details="Round neck top; V-neck outer layer")
        r["specifications"] = r["specifications"].replace("Components : 1", "Components : 2")
        p = products_from([r])[0][0]
        self.assertFalse(p["quality"]["strict_eligible"])
        self.assertFalse(p["quality"]["discordances"])

    def test_all_blank_records_accounted_for(self):
        _, _, blank, invalid = parse_rows([source_row(), dict.fromkeys(b.HEADER, "")])
        self.assertEqual(blank, [3])
        self.assertEqual(invalid, [])

    def test_invalid_product_record_retained_in_accounting(self):
        variants, _, _, invalid = parse_rows([source_row(pid="bad")])
        self.assertFalse(variants)
        self.assertEqual(invalid[0]["reason"], "invalid_product_id")

    def test_urls_are_not_specifications(self):
        claims, _ = b.parse_specification("https://www.myntra.com/brand", 2, "", 23)
        self.assertFalse(claims)

    def test_malformed_fragment_retained(self):
        claims, failed = b.parse_specification("Neck : Round Neck | broken fragment", 2, "specifications", 22)
        self.assertEqual(len(claims), 1)
        self.assertEqual(failed[0]["fragment"], "broken fragment")

    def test_header_drift_fails_closed(self):
        with self.assertRaises(ValueError):
            b.parse_source(b"product_id,title\n100,kurta\n")

    def test_prices_do_not_admit_nan_infinity_or_negative(self):
        for value in ["NaN", "Infinity", "-1", "0", "", "unknown"]:
            self.assertIsNone(b.decimal_value(value))
        self.assertEqual(b.decimal_value("1,299.00"), "1299")

    def test_exact_text_duplicates_share_split_without_identity_merge(self):
        products, _, _ = products_from([source_row(), source_row(pid="101")])
        config = json.loads((b.BASE / "config.json").read_text())
        mapping, groups = b.assign_splits(products, config)
        self.assertEqual(len(products), 2)
        self.assertEqual(mapping["100"], mapping["101"])
        self.assertEqual(groups, [["100", "101"]])

    def test_split_assignment_is_order_independent(self):
        products, _, _ = products_from([source_row(), source_row(pid="101", title="Another item")])
        config = json.loads((b.BASE / "config.json").read_text())
        a, _ = b.assign_splits(products, config)
        z, _ = b.assign_splits(list(reversed(copy.deepcopy(products))), config)
        self.assertEqual(a, z)

    def test_cards_do_not_include_advertising_or_invent_currency(self):
        p = products_from([source_row(complete_the_look="You must buy this amazing piece now")])[0][0]
        p.update(split="development", leakage_group_id="test")
        card = b.make_card(p)
        self.assertNotIn("amazing", card["card_text_zh"])
        self.assertIsNone(card["currency"])
        self.assertNotIn("purchase_label", card)

    def test_frozen_source_hash_enforced(self):
        with tempfile.TemporaryDirectory() as directory:
            source = pathlib.Path(directory) / "wrong.csv"
            source.write_bytes(b"not the source")
            with self.assertRaisesRegex(ValueError, "SHA256"):
                b.build(source, pathlib.Path(directory) / "out", b.BASE / "config.json")

    def test_alternative_config_cannot_bypass_freeze(self):
        with tempfile.TemporaryDirectory() as directory:
            config_path = pathlib.Path(directory) / "config.json"
            config_path.write_text('{"source_sha256": "changed"}')
            with self.assertRaisesRegex(ValueError, "configuration"):
                b.build(pathlib.Path(directory) / "missing", pathlib.Path(directory) / "out", config_path)


if __name__ == "__main__":
    unittest.main()
