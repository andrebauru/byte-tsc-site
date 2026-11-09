#!/usr/bin/env node
/* Unit tests for the language detection helper in assets/js/lang.js.
 * Run: node scripts/test_lang.js  (exits non-zero on failure)
 */

var assert = require("assert");
var mod = require("../assets/js/lang.js");
var pickLanguage = mod.pickLanguage;

var cases = [
  // exact matches
  [["ja"], "ja"],
  [["ja-JP"], "ja"],
  [["en"], "en"],
  [["en-US"], "en"],
  [["pt"], "pt"],
  [["pt-BR"], "pt"],
  [["pt-PT"], "pt"],
  // first supported wins, regional variants ignored
  [["fr-FR", "en-US", "ja-JP"], "en"],
  [["zh-CN", "pt-BR"], "pt"],
  [["ja-JP", "en-US"], "ja"],
  // fallback to Japanese: nothing supported
  [["fr-FR"], "ja"],
  [["zh-CN", "ko-KR"], "ja"],
  [["es-ES", "it-IT", "de-DE"], "ja"],
  // unusable input
  [null, "ja"],
  [[], "ja"],
  [[undefined], "ja"],
  [[""], "ja"],
  // odd shapes
  ["en-US", "en"],            // single string
  [["EN-us", "PT-br"], "en"], // case-insensitive
];

var failures = 0;
cases.forEach(function (c) {
  var input = c[0];
  var expected = c[1];
  var actual = pickLanguage(input);
  try {
    assert.strictEqual(actual, expected);
    console.log("ok   ", JSON.stringify(input), "->", actual);
  } catch (e) {
    failures++;
    console.error("FAIL ", JSON.stringify(input), "expected", expected, "got", actual);
  }
});

if (failures > 0) {
  console.error("\n" + failures + " test(s) failed.");
  process.exit(1);
}
console.log("\nAll " + cases.length + " language detection tests passed.");