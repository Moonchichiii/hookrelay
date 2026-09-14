import { mkdir } from "node:fs/promises";

const copies: Array<[string, string]> = [
  ["node_modules/htmx.org/dist/htmx.min.js", "static/dist/htmx.min.js"],
  ["node_modules/@alpinejs/csp/dist/cdn.min.js", "static/dist/alpine-csp.min.js"],
  ["static/src/app.js", "static/dist/app.js"],
];

await mkdir("static/dist", { recursive: true });
for (const [from, to] of copies) {
  await Bun.write(to, Bun.file(from));
}
