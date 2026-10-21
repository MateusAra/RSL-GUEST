import { request } from "../../../api";

/** Fetch an authenticated file (GET by default, or POST with a JSON body) and hand it to the browser as a download. */
export async function downloadFile(path: string, fileName: string, json?: unknown) {
  const blob = await request<Blob>(path, json === undefined ? {} : { method: "POST", json });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = fileName;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}
