const pptxgen = require("pptxgenjs");
const D = require("./data.json");
const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.title = "B12 - What the Model Is Looking At";
const NAVY = "14213D", ACC = "E07A1F", INK = "222B3A", MUTE = "6B7686", PALE = "F4F1EA";
const F = "Calibri";
const SYN = "Source: SRL scorecards, " + D.n_matches + " matches, 10 seeds";
let n = 0;
function base(title, opts = {}) {
  const s = pres.addSlide(); n++;
  s.background = { color: opts.dark ? NAVY : "FFFFFF" };
  s.addText(title, { x: 0.5, y: 0.3, w: 9, h: 0.8, fontFace: F, fontSize: 28, bold: true, color: opts.dark ? "FFFFFF" : NAVY, isTextBox: true, margin: 0 });
  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 1.08, w: 0.9, h: 0.06, fill: { color: ACC }, line: { color: ACC, width: 0 } });
  s.addText(SYN + "   |   B12   |   " + n, { x: 0.5, y: 5.2, w: 9, h: 0.3, fontFace: F, fontSize: 10, color: opts.dark ? "AAB4C3" : MUTE, isTextBox: true, margin: 0 });
  return s;
}
function bullets(s, items, y = 1.4, h = 3.6, w = 9) {
  s.addText(items.map((t, i) => ({ text: t, options: { bullet: true, breakLine: i < items.length - 1, paraSpaceAfter: 8 } })),
    { x: 0.5, y, w, h, fontFace: F, fontSize: 20, color: INK, valign: "top", isTextBox: true, margin: 0 });
}
// 1 title
let s = pres.addSlide(); n++;
s.background = { color: NAVY };
s.addText("What the model is looking at", { x: 0.6, y: 1.5, w: 8.8, h: 1, fontFace: F, fontSize: 42, bold: true, color: "FFFFFF", isTextBox: true, margin: 0 });
s.addText("SHAP explanations of T20 score prediction at overs 6, 10, 12 and 15", { x: 0.6, y: 2.6, w: 8.8, h: 0.6, fontFace: F, fontSize: 20, color: "D6DCE6", isTextBox: true, margin: 0 });
s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: 3.35, w: 1.2, h: 0.07, fill: { color: ACC }, line: { color: ACC, width: 0 } });
s.addText("Module B12, Track B  |  Muskan, Pooja, Kunal, Samarth", { x: 0.6, y: 3.6, w: 8.8, h: 0.4, fontFace: F, fontSize: 16, color: "D6DCE6", isTextBox: true, margin: 0 });
s.addText(SYN, { x: 0.6, y: 5.0, w: 8.8, h: 0.3, fontFace: F, fontSize: 11, color: ACC, isTextBox: true, margin: 0 });
// 2 problem
s = base("The 165 problem");
bullets(s, ["A projected score is shown with total confidence and no reason", "\"The model said so\" is not an answer a commentator can give", "B12 supplies the reason, and shows how it changes through the innings"]);
// 3 handover
s = base("What B12 hands over");
s.addText("results/feature_importance.csv", { x: 0.5, y: 1.4, w: 9, h: 0.5, fontFace: "Consolas", fontSize: 20, bold: true, color: ACC, isTextBox: true, margin: 0 });
s.addTable([["over_mark", "feature", "importance", "direction"], ["6", "wickets_down", "mean |SHAP|, runs", "negative"], ["15", "runs_so_far", "mean |SHAP|, runs", "positive"]],
  { x: 0.5, y: 2.1, w: 9, colW: [1.6, 2.6, 3, 1.8], fontFace: F, fontSize: 16, color: INK, border: { type: "solid", color: "CCCCCC", pt: 1 }, fill: { color: PALE } });
s.addText("Consumes B1 (score at six) and B2 (checkpoint models). Extra column importance_std at the end.", { x: 0.5, y: 4.2, w: 9, h: 0.6, fontFace: F, fontSize: 16, color: MUTE, isTextBox: true, margin: 0 });
// 4 data
s = base("Data and checkpoints");
bullets(s, ["Shared contract: matches, deliveries, checkpoints", "One row = one innings at over 6, 10, 12 or 15", "Features: runs, wickets, balls since boundary, innings, plus last-2-over momentum from deliveries", "Dropped current_run_rate: it is runs / over, so it splits SHAP credit"]);
// 5 baseline + method
s = base("Baseline and method");
bullets(s, ["Baseline: current run rate held flat to over 20", "Model: gradient boosting, one per checkpoint", "Split by match, 10 seeds, report mean and spread", "SHAP TreeExplainer: importance = mean |SHAP|, direction = sign of correlation"]);
// 6 results chart
s = base("Beats the baseline at every checkpoint");
s.addChart(pres.charts.BAR, [{ name: "Baseline (flat run rate)", labels: D.overs.map(o => "Over " + o), values: D.base }, { name: "Gradient boosting", labels: D.overs.map(o => "Over " + o), values: D.gbm }],
  { x: 0.5, y: 1.3, w: 6.2, h: 3.8, barDir: "col", chartColors: ["B8C0CC", ACC], showLegend: true, legendPos: "b", legendFontSize: 12, showValue: true, dataLabelFontSize: 11, dataLabelColor: INK, dataLabelFormatCode: "0.0",
    valAxisTitle: "RMSE (runs)", showValAxisTitle: true, valAxisLabelColor: MUTE, catAxisLabelColor: MUTE, valGridLine: { color: "E5E5E5", size: 0.5 }, catGridLine: { style: "none" } });
s.addText([{ text: "10 seeds, split by match", options: { breakLine: true, bold: true } }, { text: "Over 6: " + D.base[0] + " to " + D.gbm[0] + " runs, std about 1, far smaller than the gain.", options: { breakLine: true } }, { text: "Gain narrows by over 15: less of the innings is unseen.", options: {} }],
  { x: 7, y: 1.5, w: 2.6, h: 3.2, fontFace: F, fontSize: 15, color: INK, valign: "top", isTextBox: true, margin: 0, paraSpaceAfter: 10 });
// 7 importance
s = base("What changes between over 6 and over 15");
const keys = ["runs_so_far", "wickets_down", "balls_since_boundary", "runs_last2"];
s.addChart(pres.charts.LINE, keys.map(k => ({ name: k, labels: D.overs.map(o => "Over " + o), values: D.imp[k] })),
  { x: 0.5, y: 1.3, w: 6.4, h: 3.8, chartColors: [ACC, NAVY, "7FA7C9", "9AA5B1"], lineSize: 3, lineDataSymbolSize: 8, showLegend: true, legendPos: "b", legendFontSize: 11, valAxisTitle: "mean |SHAP| (runs)", showValAxisTitle: true, valAxisLabelColor: MUTE, catAxisLabelColor: MUTE, valGridLine: { color: "E5E5E5", size: 0.5 }, catGridLine: { style: "none" } });
s.addText([{ text: "Runs on the board take over as the innings advances.", options: { breakLine: true } }, { text: "Wickets lost matter less and less as the innings advances.", options: { breakLine: true } }, { text: "Momentum features stay small. (innings is a data effect, see limits.)", options: {} }],
  { x: 7.1, y: 1.5, w: 2.5, h: 3.2, fontFace: F, fontSize: 15, color: INK, valign: "top", isTextBox: true, margin: 0, paraSpaceAfter: 10 });
// 8 interaction
s = base("An interaction, in cricket terms");
s.addImage({ path: "../results/plots/dependence_over15.png", x: 0.5, y: 1.3, w: 5.2, h: 3.7 });
s.addText([{ text: D.pair[0] + " x " + D.pair[1], options: { bold: true, breakLine: true } }, { text: "Strongest pair at over 15: " + D.pair[2] + " runs.", options: { breakLine: true } }, { text: "Strongest pair excluding innings: the same score is worth more with wickets in hand, because batters still to come can accelerate.", options: {} }],
  { x: 6, y: 1.5, w: 3.6, h: 3.2, fontFace: F, fontSize: 15, color: INK, valign: "top", isTextBox: true, margin: 0, paraSpaceAfter: 10 });
// 9 trust
s = base("Can we trust the explanation?");
bullets(s, ["Seed-to-seed rank agreement of importances: " + D.stab.join(", ") + " (overs 6, 10, 12, 15)", "Cross-check with permutation importance: rank agreement " + D.perm.join(", ") + " (rho)", "SHAP explains the model, not cricket: no causal claims"]);
// 10 failures
s = base("Where it fails");
s.addImage({ path: "../results/plots/error_by_wickets.png", x: 0.5, y: 1.3, w: 5.4, h: 3.7 });
s.addText([{ text: D.inn2_share + "% of the 100 worst misses are chases that ended early.", options: { breakLine: true } }, { text: "The explanation points to what it can see, never to the overs not yet bowled.", options: { breakLine: true } }, { text: "Cases listed in results/failure_cases.csv", options: {} }],
  { x: 6.2, y: 1.5, w: 3.4, h: 3.2, fontFace: F, fontSize: 15, color: INK, valign: "top", isTextBox: true, margin: 0, paraSpaceAfter: 10 });
// 11 limits
s = base("Limits and stress tests");
bullets(s, ["10% of training data: RMSE rises by about " + D.data_drop10 + " runs at over 6", "3% corrupted inputs add " + D.out_lo + " to " + D.out_hi + " runs of RMSE", "Chase scores are censored, so innings is a top feature for data reasons", "Explains our own model; B1/B2 model files still needed"]);
// 11b B1
s = base("Tested against B1 at over 6");
s.addChart(pres.charts.BAR, [{ name: "RMSE (runs)", labels: ["Flat run rate", "B1", "B12 GBM"], values: [D.b1.flat, D.b1.b1, D.b1.ours] }],
  { x: 0.5, y: 1.3, w: 5.2, h: 3.8, barDir: "col", chartColors: [ACC], showLegend: false, showValue: true, dataLabelFontSize: 12, dataLabelFormatCode: "0.0", valAxisLabelColor: MUTE, catAxisLabelColor: MUTE, valGridLine: { color: "E5E5E5", size: 0.5 }, catGridLine: { style: "none" } });
s.addText([{ text: "Same 766 over-6 rows, out-of-fold.", options: { breakLine: true } }, { text: "Gap B1 minus ours, 95% bootstrap: " + D.b1.ci + " runs.", options: { breakLine: true } }, { text: "B1 range covers truth " + (D.b1.cover * 100).toFixed(1) + "% of the time.", options: { breakLine: true } }, { text: "Caveat: B1 features and validation unknown.", options: {} }],
  { x: 6, y: 1.5, w: 3.6, h: 3.2, fontFace: F, fontSize: 15, color: INK, valign: "top", isTextBox: true, margin: 0, paraSpaceAfter: 10 });
// 12 integration
s = base("Integration and next steps", { dark: false });
bullets(s, ["Message B1 and B2 for model files and an agreed match ID", "Get B1/B2 model files so SHAP explains their models", "Add the chase target as a feature to remove the censoring effect", "Handover: feature_importance.csv + results/README.md"]);
pres.writeFile({ fileName: "../slides/B12_presentation.pptx" }).then(() => console.log("ok"));
