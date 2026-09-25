/* A small Markdown renderer covering what PyForge content uses:
   headings, paragraphs, lists, tables, block quotes, fenced code and inline
   code / bold / italic / links. Fenced ```python blocks can be handed to a
   callback so lessons can turn them into runnable examples. */
(function () {
  "use strict";

  function escapeHtml(s) {
    return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }

  function inline(text) {
    return text.split(/(`[^`]+`)/g).map(function (part) {
      if (part.length > 1 && part[0] === "`" && part[part.length - 1] === "`") {
        return "<code>" + escapeHtml(part.slice(1, -1)) + "</code>";
      }
      return escapeHtml(part)
        .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
        .replace(/(^|[^\w*])\*(?!\s)([^*]+?)\*(?!\w)/g, "$1<em>$2</em>")
        .replace(/\[([^\]]+)\]\((https?:\/\/[^)\s]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
    }).join("");
  }

  function slug(text) {
    return text.toLowerCase().replace(/<[^>]+>/g, "").replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
  }

  function splitRow(line) {
    return line.trim().replace(/^\||\|$/g, "").split("|").map(function (c) { return c.trim(); });
  }

  /* Syntax-highlight Python using CodeMirror's runMode when available. */
  function highlight(code) {
    if (!window.CodeMirror || !CodeMirror.runMode) return escapeHtml(code);
    var html = "";
    CodeMirror.runMode(code, "python", function (text, style) {
      var t = escapeHtml(text);
      html += style ? '<span class="cm-' + style.replace(/ +/g, " cm-") + '">' + t + "</span>" : t;
    });
    return html;
  }

  var BLOCK_START = /^(```|#{1,4}\s|>|\s*[-*]\s+|\s*\d+\.\s+|\|)/;

  function render(src, opts) {
    opts = opts || {};
    var lines = String(src).split("\n");
    var out = [];
    var i = 0;

    while (i < lines.length) {
      var line = lines[i];
      var m;

      if ((m = line.match(/^```(\w*)\s*$/))) {
        var lang = m[1];
        var buf = [];
        i++;
        while (i < lines.length && !/^```\s*$/.test(lines[i])) { buf.push(lines[i]); i++; }
        i++;
        var code = buf.join("\n");
        if (lang === "python" && opts.onPython) {
          out.push(opts.onPython(code));
        } else {
          var body = lang === "python" ? highlight(code) : escapeHtml(code);
          out.push('<pre class="md-pre' + (lang === "text" ? " md-text" : "") + '"><code>' + body + "</code></pre>");
        }
        continue;
      }

      if (!line.trim()) { i++; continue; }

      if ((m = line.match(/^(#{1,4})\s+(.*)$/))) {
        var level = Math.min(6, m[1].length + (opts.headingOffset || 0));
        var content = inline(m[2]);
        var id = slug(m[2]);
        if (opts.onHeading) opts.onHeading(level, m[2], id);
        out.push("<h" + level + ' id="' + id + '">' + content + "</h" + level + ">");
        i++;
        continue;
      }

      if (/^\|.*\|\s*$/.test(line) && i + 1 < lines.length && /^\|[\s:|-]+\|\s*$/.test(lines[i + 1])) {
        var head = splitRow(line);
        var rows = [];
        i += 2;
        while (i < lines.length && /^\|.*\|\s*$/.test(lines[i])) { rows.push(splitRow(lines[i])); i++; }
        var t = '<div class="table-wrap"><table><thead><tr>' +
          head.map(function (c) { return "<th>" + inline(c) + "</th>"; }).join("") + "</tr></thead><tbody>" +
          rows.map(function (r) { return "<tr>" + r.map(function (c) { return "<td>" + inline(c) + "</td>"; }).join("") + "</tr>"; }).join("") +
          "</tbody></table></div>";
        out.push(t);
        continue;
      }

      if (line.startsWith(">")) {
        var quote = [];
        while (i < lines.length && lines[i].startsWith(">")) { quote.push(lines[i].replace(/^>\s?/, "")); i++; }
        out.push('<aside class="callout"><p>' + inline(quote.join(" ")) + "</p></aside>");
        continue;
      }

      var ordered = /^\s*\d+\.\s+/.test(line);
      if (ordered || /^\s*[-*]\s+/.test(line)) {
        var itemRe = ordered ? /^\s*\d+\.\s+/ : /^\s*[-*]\s+/;
        var items = [];
        while (i < lines.length && lines[i].trim()) {
          if (itemRe.test(lines[i])) items.push(lines[i].replace(itemRe, ""));
          else if (/^\s+/.test(lines[i]) && items.length) items[items.length - 1] += " " + lines[i].trim();
          else break;
          i++;
        }
        var tag = ordered ? "ol" : "ul";
        out.push("<" + tag + ">" + items.map(function (it) { return "<li>" + inline(it) + "</li>"; }).join("") + "</" + tag + ">");
        continue;
      }

      var para = [];
      while (i < lines.length && lines[i].trim() && !(para.length && BLOCK_START.test(lines[i]))) {
        para.push(lines[i].trim());
        i++;
      }
      out.push("<p>" + inline(para.join(" ")) + "</p>");
    }
    return out.join("\n");
  }

  window.MD = { render: render, inline: inline, escapeHtml: escapeHtml, highlight: highlight };
})();
