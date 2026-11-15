import { notFound } from "next/navigation";
import Dashboard from "../../components/Dashboard";
const routes = [
  "",
  "mission",
  "investigations",
  "compare",
  "insights",
  "habitat",
  "ask",
  "methods",
];
export default async function Page({
  params,
}: {
  params: Promise<{ page?: string[] }>;
}) {
  const route = (await params).page?.join("/") || "";
  if (!routes.includes(route)) notFound();
  return <Dashboard route={route} />;
}
