import katex from "katex";

type Props = {
  expr: string;
  display?: boolean;
  className?: string;
  label?: string;
};

/** Server-rendered TeX via KaTeX. Requires katex/dist/katex.min.css (imported in app/layout.tsx). */
export default function Tex({ expr, display = false, className, label }: Props) {
  const html = katex.renderToString(expr, { displayMode: display, throwOnError: false, output: "htmlAndMathml" });
  const Tag = display ? "div" : "span";
  return <Tag className={className} aria-label={label} dangerouslySetInnerHTML={{ __html: html }} />;
}
