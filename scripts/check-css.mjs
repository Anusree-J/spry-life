import { readFileSync } from "node:fs";
import { parse, walk, lexer } from "css-tree";

const css = parse(readFileSync("site/style.css", "utf8"), {
  positions: true,
  onParseError(error) {
    throw error;
  },
});
let declarations = 0;
walk(css, {
  visit: "Declaration",
  enter(node) {
    const result = lexer.matchProperty(node.property, node.value);
    if (result.error) throw result.error;
    declarations++;
  },
});
console.log(`CSS valid: ${declarations} declarations checked`);
