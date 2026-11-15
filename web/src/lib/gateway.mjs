export function allowedPath(path) {
  return /^(status|investigations(?:\/[A-Za-z0-9_-]+)?|variables\/[A-Za-z0-9_-]+|sources\/[A-Za-z0-9_-]+|evidence\/[A-Za-z0-9_-]+|chat|data\/query)$/.test(
    path,
  );
}
export function allowedMethod(path, method) {
  return ["chat", "data/query"].includes(path)
    ? method === "POST"
    : method === "GET";
}
