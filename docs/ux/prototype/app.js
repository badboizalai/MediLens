/* MediLens low-fi prototype. Vanilla JS, no network, no storage. Synthetic data only. */
(function () {
  "use strict";

  // ---- copy (VI/EN). Keys follow docs/ux/wireframes/*.md ----
  var T = {
    vi: {
      skip: "Bỏ qua đến nội dung", proto: "Bản mẫu - dữ liệu giả",
      foot: "Bản mẫu thử nghiệm. Dữ liệu hoàn toàn giả. Không có kết nối mạng.",
      "nav.consent": "Đồng ý", "nav.upload": "Tải lên", "nav.review": "Kiểm tra", "nav.viewer": "Hình cơ thể",
      "nav.explain": "Giải thích", "nav.timeline": "Dòng thời gian", "nav.share": "Chia sẻ", "nav.settings": "Cài đặt",
      "common.yes": "Chia sẻ", "common.cancel": "Hủy",
      "consent.title": "Trước khi bắt đầu",
      "consent.b1": "Chúng tôi hiển thị hồ sơ của bạn lên hình cơ thể.",
      "consent.b2": "Chúng tôi giải thích hồ sơ của bạn ghi gì.",
      "consent.b3": "Không dùng dữ liệu của bạn để huấn luyện trừ khi bạn đồng ý.",
      "consent.notice": "Đọc thông báo quyền riêng tư đầy đủ (bản mẫu)",
      "consent.health": "Tôi đồng ý cho MediLens xử lý dữ liệu sức khỏe của tôi để hiển thị và giải thích hồ sơ.",
      "consent.research": "(Tùy chọn) Tôi đồng ý cho dùng dữ liệu đã ẩn danh để cải thiện MediLens.",
      "consent.hint": "Hãy đánh dấu ô bắt buộc (ô đầu tiên) để tiếp tục.",
      "consent.cta": "Đồng ý và tiếp tục", "consent.no": "Để sau",
      "consent.declined": "Bạn cần đồng ý để tải hồ sơ lên. Bạn có thể quay lại bất cứ lúc nào.",
      "ai.label": "Do AI trích xuất — vui lòng kiểm tra lại",
      "upload.title": "Tải hồ sơ lên",
      "upload.hint": "Chụp hoặc chọn hồ sơ của bạn (JPG, PNG, HEIC, PDF, tối đa 20 MB, 30 trang).",
      "upload.sample": "Hồ sơ mẫu (giả)", "upload.pick": "Chọn hồ sơ mẫu",
      "upload.processing": "Đang đọc hồ sơ… thường mất dưới 2 phút.",
      "upload.leave": "Bạn có thể rời trang này, chúng tôi sẽ báo khi xong.",
      "upload.next": "Xem kết quả đọc được",
      "rec.name": "Nguyễn Văn Mẫu (người giả, không có thật)", "rec.desc": "Phiếu khám răng mẫu - dữ liệu tổng hợp",
      "review.title": "Kiểm tra thông tin",
      "review.lowConfidence": "Chúng tôi chưa chắc chắn về thông tin này. Bạn kiểm tra giúp nhé.",
      "review.confirmAll": "Xác nhận và hiển thị lên cơ thể",
      "review.remaining": "Còn {n} mục cần kiểm tra",
      "review.done": "Đã xác nhận. Đang mở hình cơ thể.",
      "r.checked": "Tôi đã kiểm tra mục này",
      "viewer.title": "Hình cơ thể",
      "viewer.illustration": "Đây là hình minh họa giúp bạn hiểu hồ sơ của mình.",
      "viewer.empty": "Chưa có thông tin nào được xác nhận. Hãy tải hồ sơ lên để bắt đầu.",
      "viewer.list": "Danh sách (theo hồ sơ)", "viewer.legend": "Chú giải",
      "viewer.chart": "Sơ đồ răng minh họa (kiểu FDI)", "viewer.tooth": "Răng",
      "viewer.selected": "Đã chọn răng {n}", "viewer.upper": "Hàm trên", "viewer.lower": "Hàm dưới",
      "disclaimer.short": "Hình minh họa giúp bạn hiểu hồ sơ của mình; hãy dùng cùng lời khuyên của bác sĩ.",
      "finding.recordSays": "Hồ sơ của bạn ghi:", "finding.usuallyMeans": "Điều này thường có nghĩa là:",
      "finding.askDoctor": "Câu hỏi bạn có thể hỏi bác sĩ:",
      "f.36": "sâu răng", "f.46": "trám cũ, ghi chú theo dõi", "f.24": "mòn cổ răng nhẹ",
      "f.36.mean": "Một vùng men răng ở răng này được ghi là bị sâu.",
      "f.46.mean": "Răng này có miếng trám cũ và hồ sơ ghi là cần theo dõi.",
      "f.24.mean": "Hồ sơ ghi phần cổ răng bị mòn nhẹ.",
      "f.q": "Răng này đang ở tình trạng nào theo hồ sơ của tôi? / Tôi nên hỏi gì ở lần hẹn tới?",
      "sev.monitor": "Theo dõi", "sev.mild": "Nhẹ", "sev.moderate": "Trung bình", "sev.severe": "Nặng",
      "sev.spread": "Di căn / lan rộng", "sev.reference": "Tham khảo",
      "explain.title": "Giải thích hồ sơ",
      "explain.emergency": "Nếu bạn đang đau ngực, khó thở hoặc có nguy hiểm tức thời, hãy gọi 115 ngay.",
      "explain.suggest": "Gợi ý: \"Hồ sơ này ghi gì?\", \"Mình nên hỏi bác sĩ điều gì?\"",
      "explain.noSource": "Hiện chưa có thông tin đã được kiểm duyệt cho câu hỏi này. Bạn nên hỏi bác sĩ.",
      "explain.noDose": "Mình không thể tư vấn về liều hay ngừng thuốc. Hãy trao đổi với bác sĩ kê đơn.",
      "explain.noFuture": "Mình không thể dự đoán diễn tiến. Bác sĩ điều trị của bạn là người phù hợp để trao đổi.",
      "x.q.says": "Hồ sơ này ghi gì?", "x.q.ask": "Mình nên hỏi bác sĩ điều gì?",
      "x.q.dose": "Mình dùng thuốc thế nào?", "x.q.future": "Rồi sẽ ra sao?",
      "x.src": "Nguồn: hồ sơ mẫu (giả) ngày 2026-09-15",
      "timeline.title": "Dòng thời gian",
      "timeline.changes": "Theo hồ sơ: {new} mục mới, {resolved} mục đã ghi nhận hết, {changed} mục thay đổi.",
      "t.region": "Vị trí", "t.none": "không ghi", "t.new": "mới", "t.gone": "không còn ghi", "t.same": "không đổi",
      "share.title": "Chia sẻ", "share.email": "Email người nhận", "share.scope": "Nội dung chia sẻ",
      "share.dental": "Nha khoa", "share.cardio": "Tim mạch", "share.days": "Thời hạn (ngày, tối đa 90)",
      "share.cta": "Tiếp tục", "share.list": "Đang chia sẻ",
      "share.needAccount": "Người nhận cần đăng nhập MediLens để xem.",
      "share.invalid": "Hãy nhập email hợp lệ, chọn ít nhất một mục và thời hạn tối đa 90 ngày.",
      "share.confirm": "Chia sẻ {scope} với {email} trong {days} ngày?",
      "share.expiry": "Quyền xem sẽ tự hết hạn sau {days} ngày. Bạn có thể thu hồi bất cứ lúc nào.",
      "share.revoke": "Thu hồi", "share.revokeConfirm": "Thu hồi quyền xem của {email} ngay bây giờ?",
      "share.created": "Đã tạo chia sẻ.", "share.empty": "Bạn chưa chia sẻ hồ sơ nào.",
      "settings.title": "Cài đặt",
      "settings.optIn": "Cho phép dùng dữ liệu đã ẩn danh để cải thiện MediLens (tùy chọn).",
      "settings.onlyThis": "Bạn chỉ đang đăng nhập trên thiết bị này.",
      "settings.exportH": "Tải dữ liệu của bạn", "settings.export": "Yêu cầu bản xuất dữ liệu",
      "settings.exportPending": "Đang chuẩn bị dữ liệu của bạn. Bạn có thể rời trang này.",
      "settings.exportReady": "Dữ liệu đã sẵn sàng để tải xuống.",
      "settings.deleteH": "Xóa tài khoản", "settings.delete": "Xóa tài khoản", "settings.deleteYes": "Xóa",
      "settings.deleteConfirm": "Tài khoản sẽ bị khóa ngay và dữ liệu bị xóa vĩnh viễn sau 30 ngày. Bạn chắc chắn chứ?",
      "settings.deleted": "Đã gửi yêu cầu xóa. Bạn có 30 ngày trước khi dữ liệu bị xóa vĩnh viễn.",
      "settings.reset": "Đặt lại bản mẫu về đầu"
    },
    en: {
      skip: "Skip to content", proto: "Prototype - fake data",
      foot: "Test prototype. All data is fake. No network connection.",
      "nav.consent": "Consent", "nav.upload": "Upload", "nav.review": "Review", "nav.viewer": "Body view",
      "nav.explain": "Explain", "nav.timeline": "Timeline", "nav.share": "Share", "nav.settings": "Settings",
      "common.yes": "Share", "common.cancel": "Cancel",
      "consent.title": "Before you start",
      "consent.b1": "We show your record on a body view.",
      "consent.b2": "We explain what your record says.",
      "consent.b3": "No training on your data unless you opt in.",
      "consent.notice": "Read the full privacy notice (prototype)",
      "consent.health": "I agree that MediLens may process my health data to display and explain my records.",
      "consent.research": "(Optional) I agree to use de-identified data to improve MediLens.",
      "consent.hint": "Tick the required box (the first one) to continue.",
      "consent.cta": "Agree and continue", "consent.no": "Not now",
      "consent.declined": "You need to agree to upload records. You can come back anytime.",
      "ai.label": "Extracted by AI — please check",
      "upload.title": "Upload a record",
      "upload.hint": "Take or choose your record (JPG, PNG, HEIC, PDF, up to 20 MB, 30 pages).",
      "upload.sample": "Sample record (fake)", "upload.pick": "Choose the sample record",
      "upload.processing": "Reading your record… usually under 2 minutes.",
      "upload.leave": "You can leave this page; we'll tell you when it's done.",
      "upload.next": "See what was read",
      "rec.name": "Demo Patient Nguyen Van Mau (fictional, not a real person)", "rec.desc": "Sample dental visit sheet - synthetic data",
      "review.title": "Check the information",
      "review.lowConfidence": "We're not sure about this one. Please check it.",
      "review.confirmAll": "Confirm and show on the body",
      "review.remaining": "{n} items left to check",
      "review.done": "Confirmed. Opening the body view.",
      "r.checked": "I checked this item",
      "viewer.title": "Body view",
      "viewer.illustration": "This is an illustration that helps you understand your records.",
      "viewer.empty": "Nothing confirmed yet. Upload a record to begin.",
      "viewer.list": "List (per your record)", "viewer.legend": "Legend",
      "viewer.chart": "Illustrative tooth chart (FDI style)", "viewer.tooth": "Tooth",
      "viewer.selected": "Selected tooth {n}", "viewer.upper": "Upper jaw", "viewer.lower": "Lower jaw",
      "disclaimer.short": "This illustration helps you understand your records; use alongside your doctor's advice.",
      "finding.recordSays": "Your record says:", "finding.usuallyMeans": "This usually means:",
      "finding.askDoctor": "Questions you could ask your doctor:",
      "f.36": "dental caries", "f.46": "old filling, noted for follow-up", "f.24": "mild wear at the neck of the tooth",
      "f.36.mean": "An area of enamel on this tooth is recorded as decayed.",
      "f.46.mean": "This tooth has an old filling and the record notes it for monitoring.",
      "f.24.mean": "The record notes mild wear near the gum line.",
      "f.q": "What state is this tooth in, according to my record? / What should I ask at my next visit?",
      "sev.monitor": "Monitor", "sev.mild": "Mild", "sev.moderate": "Moderate", "sev.severe": "Severe",
      "sev.spread": "Metastasis / spread", "sev.reference": "Reference",
      "explain.title": "Explain my record",
      "explain.emergency": "If you have chest pain, trouble breathing or are in immediate danger, call 115 now.",
      "explain.suggest": "Try: \"What does this record say?\", \"What should I ask my doctor?\"",
      "explain.noSource": "We don't have reviewed information for this yet. Please ask your doctor.",
      "explain.noDose": "I can't advise on doses or stopping medicine. Please talk to the prescribing doctor.",
      "explain.noFuture": "I can't predict how things will go. Your treating doctor is the right person to ask.",
      "x.q.says": "What does this record say?", "x.q.ask": "What should I ask my doctor?",
      "x.q.dose": "How should I take my medicine?", "x.q.future": "What will happen next?",
      "x.src": "Source: sample record (fake) dated 2026-09-15",
      "timeline.title": "Timeline",
      "timeline.changes": "Per your records: {new} new, {resolved} no longer listed, {changed} changed.",
      "t.region": "Location", "t.none": "not listed", "t.new": "new", "t.gone": "no longer listed", "t.same": "unchanged",
      "share.title": "Share", "share.email": "Recipient email", "share.scope": "What to share",
      "share.dental": "Dental", "share.cardio": "Heart", "share.days": "Period (days, up to 90)",
      "share.cta": "Continue", "share.list": "Currently shared",
      "share.needAccount": "The recipient must sign in to MediLens to view.",
      "share.invalid": "Enter a valid email, pick at least one item, and a period of up to 90 days.",
      "share.confirm": "Share {scope} with {email} for {days} days?",
      "share.expiry": "Access expires after {days} days. You can revoke it anytime.",
      "share.revoke": "Revoke", "share.revokeConfirm": "Revoke access for {email} now?",
      "share.created": "Share created.", "share.empty": "You haven't shared anything yet.",
      "settings.title": "Settings",
      "settings.optIn": "Allow de-identified data to improve MediLens (optional).",
      "settings.onlyThis": "You are signed in on this device only.",
      "settings.exportH": "Download your data", "settings.export": "Request a data export",
      "settings.exportPending": "Preparing your data. You can leave this page.",
      "settings.exportReady": "Your data is ready to download.",
      "settings.deleteH": "Delete account", "settings.delete": "Delete account", "settings.deleteYes": "Delete",
      "settings.deleteConfirm": "Your account is locked now and data is permanently deleted after 30 days. Are you sure?",
      "settings.deleted": "Deletion requested. You have 30 days before data is permanently removed.",
      "settings.reset": "Reset the prototype to the start"
    }
  };

  // ---- synthetic data. region_code style ids; severity = design-system token names ----
  var GLYPH = { monitor: "◉", mild: "◔", moderate: "◑", severe: "●", spread: "✳", reference: "ⓘ" };
  var FINDINGS = [
    { code: "tooth-36", n: "36", sev: "moderate", low: true },
    { code: "tooth-46", n: "46", sev: "monitor", low: false },
    { code: "tooth-24", n: "24", sev: "mild", low: true }
  ];
  var VISITS = { // region -> severity per visit; null = not listed
    "tooth-24": [ "mild", null ], "tooth-36": [ null, "moderate" ], "tooth-46": [ "monitor", "monitor" ]
  };

  var lang = "vi", state, selected = null;
  function fresh() {
    return { consent: false, uploaded: false, checked: {}, confirmed: false, shares: [], pendingShare: null };
  }
  state = fresh();

  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  function t(k, v) {
    var s = (T[lang][k] != null ? T[lang][k] : k);
    if (v) Object.keys(v).forEach(function (x) { s = s.replace("{" + x + "}", v[x]); });
    return s;
  }
  function el(tag, attrs, text) {
    var e = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (a) { e.setAttribute(a, attrs[a]); });
    if (text != null) e.textContent = text;
    return e;
  }
  function svgEl(tag, attrs) {
    var e = document.createElementNS("http://www.w3.org/2000/svg", tag);
    Object.keys(attrs || {}).forEach(function (a) { e.setAttribute(a, attrs[a]); });
    return e;
  }
  function sevChip(sev) {
    var c = el("span", { "class": "sevchip sev-" + sev, "data-g": GLYPH[sev] }, t("sev." + sev));
    return c;
  }
  function byCode(code) { return FINDINGS.filter(function (f) { return f.code === code; })[0]; }

  // ---- routing (hash) ----
  var ROUTES = ["consent", "upload", "review", "viewer", "explain", "timeline", "share", "settings"];
  function route() {
    var r = location.hash.replace("#", "");
    if (ROUTES.indexOf(r) < 0) r = "consent";
    if (!state.consent && r !== "consent" && r !== "settings") { location.hash = "#consent"; return; }
    $$(".screen").forEach(function (s) { s.hidden = s.id !== r; });
    $$(".steps a").forEach(function (a) {
      if (a.getAttribute("href") === "#" + r) a.setAttribute("aria-current", "page"); else a.removeAttribute("aria-current");
    });
    render(r);
    var h = $("#" + r + " h1");
    document.title = h.textContent + " - MediLens (prototype)";
    $("#main").focus({ preventScroll: true });
    window.scrollTo(0, 0);
  }

  var RENDER = { review: renderReview, viewer: renderViewer, timeline: renderTimeline, share: renderShares, upload: renderUpload };
  function render(r) { if (RENDER[r]) RENDER[r](); }

  // ---- i18n ----
  function applyLang() {
    document.documentElement.lang = lang;
    $$("[data-i18n]").forEach(function (n) { n.textContent = t(n.getAttribute("data-i18n")); });
    $$("[data-lang]").forEach(function (b) { b.setAttribute("aria-pressed", String(b.getAttribute("data-lang") === lang)); });
    $("#s-email").setAttribute("aria-label", t("share.email"));
    route();
    renderLog();
  }

  // ---- consent ----
  function updateConsent() { $("#c-go").disabled = !$("#c-health").checked; }
  // ---- upload ----
  function renderUpload() { $("#u-next").hidden = !state.uploaded; }
  function startUpload() {
    var bar = $("#u-bar"), v = 0;
    $("#u-prog").hidden = false; $("#u-pick").disabled = true;
    var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduce) v = 100;
    var iv = setInterval(function () {
      v += 20; bar.value = v;
      if (v >= 100) { clearInterval(iv); state.uploaded = true; renderUpload(); $("#u-next").focus(); }
    }, 300);
    if (reduce) { clearInterval(iv); bar.value = 100; state.uploaded = true; renderUpload(); }
  }
  // ---- review ----
  function renderReview() {
    var ul = $("#r-fields"); ul.textContent = "";
    var rows = [
      { id: "date", label: "2026-09-15", name: lang === "vi" ? "Ngày khám" : "Visit date", low: false },
      { id: "name", label: t("rec.name").split(" (")[0], name: lang === "vi" ? "Tên (giả)" : "Name (fake)", low: false }
    ];
    FINDINGS.forEach(function (f) {
      rows.push({ id: f.code, label: t("viewer.tooth") + " " + f.n + ": " + t("f." + f.n), name: f.code, low: f.low });
    });
    rows.forEach(function (r) {
      var li = el("li", r.low ? { "class": "low" } : {});
      var lab = el("label", { "for": "rf-" + r.id }, r.name);
      var inp = el("input", { id: "rf-" + r.id, type: "text", value: r.label });
      li.appendChild(lab); li.appendChild(inp);
      if (r.low) {
        li.appendChild(el("p", { "class": "lowtxt" }, "⚠ " + t("review.lowConfidence")));
        var cl = el("label", { "class": "check" });
        var cb = el("input", { type: "checkbox", "data-code": r.id });
        cb.checked = !!state.checked[r.id];
        cl.appendChild(cb); cl.appendChild(el("span", {}, t("r.checked")));
        li.appendChild(cl);
      }
      ul.appendChild(li);
    });
    updateReview();
  }
  function updateReview() {
    var left = FINDINGS.filter(function (f) { return f.low && !state.checked[f.code]; }).length;
    $("#r-remaining").textContent = left ? t("review.remaining", { n: left }) : "";
    $("#r-confirm").disabled = left > 0 || state.confirmed;
    $("#r-done").hidden = !state.confirmed;
  }
  // ---- viewer: inline SVG odontogram, ids = region_code ----
  var UPPER = [18,17,16,15,14,13,12,11,21,22,23,24,25,26,27,28];
  var LOWER = [48,47,46,45,44,43,42,41,31,32,33,34,35,36,37,38];
  function renderViewer() {
    var wrap = $("#odonto-wrap"); wrap.textContent = "";
    var list = $("#v-list"); list.textContent = "";
    var leg = $("#v-legend"); leg.textContent = "";
    $("#v-detail").hidden = true;
    var shown = state.confirmed ? FINDINGS : [];
    if (!state.confirmed) { wrap.appendChild(el("p", { "class": "banner" }, t("viewer.empty"))); return; }
    var svg = svgEl("svg", { "class": "odonto", viewBox: "0 0 480 230", role: "group", "aria-label": t("viewer.chart") });
    svg.appendChild(svgEl("title")).textContent = t("viewer.chart");
    drawRow(svg, UPPER, 60, "tooth-up", t("viewer.upper"), 26);
    drawRow(svg, LOWER, 150, "tooth-lo", t("viewer.lower"), 194);
    wrap.appendChild(svg);
    shown.forEach(function (f) {
      var li = el("li");
      var b = el("button", { type: "button", "data-code": f.code });
      b.appendChild(el("span", {}, t("viewer.tooth") + " " + f.n + ": " + t("f." + f.n) + " "));
      b.appendChild(sevChip(f.sev));
      li.appendChild(b); list.appendChild(li);
    });
    Object.keys(GLYPH).forEach(function (s) { var li = el("li"); li.appendChild(sevChip(s)); leg.appendChild(li); });
    if (selected) select(selected, false);
  }
  function drawRow(svg, nums, y, cls, label, ly) {
    svg.appendChild(svgEl("text", { x: 240, y: ly - 8, "class": "lbl" })).textContent = label;
    nums.forEach(function (n, i) {
      var code = "tooth-" + n, f = byCode(code), x = 16 + i * 28 + (i >= 8 ? 8 : 0);
      var g = svgEl("rect", {
        id: code, x: x, y: y, width: 22, height: 30, rx: 6,
        "class": "tooth" + (f ? " sev sev-" + f.sev : ""), tabindex: 0, role: "button",
        "aria-label": t("viewer.tooth") + " " + n + (f ? ": " + t("f." + n) + ", " + t("sev." + f.sev) : "")
      });
      g.appendChild(svgEl("title")).textContent = t("viewer.tooth") + " " + n + (f ? " - " + t("sev." + f.sev) : "");
      svg.appendChild(g);
      svg.appendChild(svgEl("text", { x: x + 11, y: y + 19 })).textContent = n;
      if (f) {
        var ty = cls === "tooth-up" ? y + 44 : y - 6;
        svg.appendChild(svgEl("text", { x: x + 11, y: ty })).textContent = GLYPH[f.sev] + " " + t("sev." + f.sev);
      }
    });
  }
  function select(code, announce) {
    selected = code;
    $$("svg .tooth").forEach(function (n) { n.classList.toggle("sel", n.id === code); });
    var n = code.replace("tooth-", ""), f = byCode(code), d = $("#v-detail");
    d.textContent = ""; d.hidden = false;
    d.appendChild(el("h2", {}, t("viewer.tooth") + " " + n));
    if (f) {
      d.appendChild(el("p", {}, t("finding.recordSays") + " " + t("f." + n) + " "));
      d.lastChild.appendChild(sevChip(f.sev));
      d.appendChild(el("p", {}, t("finding.usuallyMeans") + " " + t("f." + n + ".mean")));
      d.appendChild(el("p", {}, t("finding.askDoctor") + " " + t("f.q")));
      d.appendChild(el("p", { "class": "muted" }, t("x.src")));
    } else {
      d.appendChild(el("p", {}, t("sev.reference") + ": " + t("t.none")));
    }
    if (announce !== false) $("#v-sel").textContent = t("viewer.selected", { n: n });
  }
  // ---- explain (canned answers only; no model) ----
  var log = [];
  function ask(q) {
    log.push({ u: t("x.q." + q), q: q });
    renderLog();
  }
  function answer(q) {
    if (q === "dose") return [t("explain.noDose")];
    if (q === "future") return [t("explain.noFuture")];
    if (!state.confirmed) return [t("explain.noSource")];
    if (q === "says") {
      return [t("finding.recordSays")].concat(FINDINGS.map(function (f) {
        return t("viewer.tooth") + " " + f.n + ": " + t("f." + f.n) + " (" + t("sev." + f.sev) + ")";
      }), [t("x.src")]);
    }
    return [t("finding.askDoctor"), t("f.q")];
  }
  function renderLog() {
    var box = $("#x-log"); box.textContent = "";
    log.forEach(function (m) {
      box.appendChild(el("p", { "class": "u" }, t("x.q." + m.q)));
      var p = el("p", { "class": "b" });
      answer(m.q).forEach(function (line, i) { if (i) p.appendChild(el("br")); p.appendChild(document.createTextNode(line)); });
      box.appendChild(p);
    });
  }
  // ---- timeline ----
  function renderTimeline() {
    var tb = $("#t-body"); tb.textContent = ""; var nw = 0, gone = 0, ch = 0;
    Object.keys(VISITS).forEach(function (code) {
      var v = VISITS[code], tr = el("tr"), n = code.replace("tooth-", "");
      tr.appendChild(el("th", { scope: "row" }, t("viewer.tooth") + " " + n));
      v.forEach(function (s) {
        var td = el("td"); if (s) td.appendChild(sevChip(s)); else td.textContent = t("t.none"); tr.appendChild(td);
      });
      var st = !v[0] && v[1] ? "new" : v[0] && !v[1] ? "gone" : v[0] !== v[1] ? "chg" : "same";
      if (st === "new") nw++; else if (st === "gone") gone++; else if (st === "chg") ch++;
      tb.appendChild(tr);
    });
    $("#t-summary").textContent = t("timeline.changes", { "new": nw, resolved: gone, changed: ch });
  }
  // ---- share ----
  function scopeNames(vals) { return vals.map(function (v) { return t("share." + v); }).join(", "); }
  function renderShares() {
    var ul = $("#s-items"); ul.textContent = "";
    $("#s-empty").hidden = state.shares.length > 0;
    state.shares.forEach(function (s, i) {
      var li = el("li");
      li.appendChild(el("p", {}, s.email + " - " + scopeNames(s.scope)));
      li.appendChild(el("p", { "class": "muted" }, t("share.expiry", { days: s.days })));
      var b = el("button", { type: "button", "data-revoke": i }, t("share.revoke"));
      li.appendChild(b); ul.appendChild(li);
    });
  }
  function submitShare(e) {
    e.preventDefault();
    var email = $("#s-email").value.trim(), days = parseInt($("#s-days").value, 10);
    var scope = $$("input[name=scope]:checked").map(function (c) { return c.value; });
    var ok = /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email) && scope.length > 0 && days >= 1 && days <= 90;
    $("#s-err").hidden = ok; $("#s-created").hidden = true;
    if (!ok) { $("#s-err").focus(); return; }
    state.pendingShare = { email: email, days: days, scope: scope };
    $("#s-ctext").textContent = t("share.confirm", { scope: scopeNames(scope), email: email, days: days });
    $("#s-confirm").hidden = false; $("#s-yes").focus();
  }

  // ---- wiring ----
  function init() {
    $$("[data-lang]").forEach(function (b) { b.addEventListener("click", function () { lang = b.getAttribute("data-lang"); applyLang(); }); });
    window.addEventListener("hashchange", route);

    $("#c-health").addEventListener("change", updateConsent);
    $("#c-go").addEventListener("click", function () { state.consent = true; location.hash = "#upload"; });
    $("#c-no").addEventListener("click", function () { $("#c-declined").hidden = false; });

    $("#u-pick").addEventListener("click", startUpload);
    $("#r-fields").addEventListener("change", function (e) {
      var c = e.target.getAttribute("data-code"); if (c) { state.checked[c] = e.target.checked; updateReview(); }
    });
    $("#r-confirm").addEventListener("click", function () {
      state.confirmed = true; updateReview();
      setTimeout(function () { location.hash = "#viewer"; }, window.matchMedia("(prefers-reduced-motion: reduce)").matches ? 0 : 600);
    });

    $("#odonto-wrap").addEventListener("click", function (e) { if (e.target.id && e.target.id.indexOf("tooth-") === 0) select(e.target.id); });
    $("#odonto-wrap").addEventListener("keydown", function (e) {
      if ((e.key === "Enter" || e.key === " ") && e.target.id && e.target.id.indexOf("tooth-") === 0) { e.preventDefault(); select(e.target.id); }
    });
    $("#v-list").addEventListener("click", function (e) {
      var b = e.target.closest("button"); if (b) select(b.getAttribute("data-code"));
    });

    $$("[data-q]").forEach(function (b) { b.addEventListener("click", function () { ask(b.getAttribute("data-q")); }); });

    $("#s-form").addEventListener("submit", submitShare);
    $("#s-cancel").addEventListener("click", function () { $("#s-confirm").hidden = true; state.pendingShare = null; });
    $("#s-yes").addEventListener("click", function () {
      state.shares.push(state.pendingShare); state.pendingShare = null;
      $("#s-confirm").hidden = true; $("#s-created").hidden = false; renderShares();
    });
    $("#s-items").addEventListener("click", function (e) {
      var i = e.target.getAttribute("data-revoke");
      if (i != null && window.confirm(t("share.revokeConfirm", { email: state.shares[i].email }))) { state.shares.splice(i, 1); renderShares(); }
    });

    $("#st-export").addEventListener("click", function () {
      var m = $("#st-exp-msg"); m.textContent = t("settings.exportPending");
      setTimeout(function () { m.textContent = t("settings.exportReady"); }, 1200);
    });
    $("#st-del").addEventListener("click", function () { $("#st-conf").hidden = false; $("#st-yes").focus(); });
    $("#st-no").addEventListener("click", function () { $("#st-conf").hidden = true; });
    $("#st-yes").addEventListener("click", function () { $("#st-conf").hidden = true; $("#st-done").hidden = false; });
    $("#st-reset").addEventListener("click", function () { location.hash = ""; location.reload(); });

    $("#st-conf").hidden = true;
    applyLang();
  }
  init();
})();
