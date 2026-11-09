import { readFileSync } from "node:fs";
import { parse, walk, lexer, generate } from "css-tree";

const css = parse(readFileSync("site/style.css", "utf8"), {
  positions: true,
  onParseError(error) {
    throw error;
  },
});

// css-tree cannot match values containing var(), so every declared value of a
// custom property is substituted in turn and each resulting value is checked.
const custom = new Map();
walk(css, {
  visit: "Declaration",
  enter(node) {
    if (!node.property.startsWith("--")) return;
    const values = custom.get(node.property) ?? [];
    values.push(generate(node.value).trim());
    custom.set(node.property, values);
  },
});

function expand(text) {
  const match = /var\(\s*(--[\w-]+)\s*\)/.exec(text);
  if (!match) return [text];
  const values = custom.get(match[1]);
  if (!values) throw new Error(`Undefined custom property ${match[1]}`);
  return values.flatMap((value) => expand(text.replace(match[0], () => value)));
}

let declarations = 0;
walk(css, {
  visit: "Declaration",
  enter(node) {
    if (node.property.startsWith("--")) return;
    const atrule = this.atrule?.name;
    for (const text of expand(generate(node.value))) {
      const value = parse(text, { context: "value" });
      const result =
        atrule === "font-face"
          ? lexer.matchAtruleDescriptor(atrule, node.property, value)
          : lexer.matchProperty(node.property, value);
      if (result.error) {
        const line = node.loc?.start.line;
        throw new Error(`style.css:${line} ${node.property}: ${text}`, {
          cause: result.error,
        });
      }
    }
    declarations++;
  },
});
console.log(`CSS valid: ${declarations} declarations checked`);
