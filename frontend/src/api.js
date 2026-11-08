const BASE = (import.meta.env.VITE_API_URL || "http://localhost:8000").replace(/\/+$/, "");

async function request(path, options = {}) {
  let res;
  try {
    res = await fetch(`${BASE}${path}`, options);
  } catch {
    throw new Error("Cannot reach the server. If it was idle, it may take up to a minute to wake up; try again shortly.");
  }
  if (!res.ok) {
    let message = `Request failed (${res.status})`;
    try {
      const body = await res.json();
      if (typeof body.detail === "string") message = body.detail;
      else if (Array.isArray(body.detail)) message = body.detail.map((d) => d.msg).join(", ");
    } catch {
      /* keep default message */
    }
    throw new Error(message);
  }
  return res.json();
}

export const api = {
  analyze: (file, jobDescription, jobTitle) => {
    const form = new FormData();
    form.append("file", file);
    form.append("job_description", jobDescription);
    form.append("job_title", jobTitle || "");
    return request("/api/analyze", { method: "POST", body: form });
  },
  listAnalyses: () => request("/api/analyses"),
  getAnalysis: (id) => request(`/api/analyses/${id}`),
  deleteAnalysis: (id) => request(`/api/analyses/${id}`, { method: "DELETE" }),
  listJobs: () => request("/api/jobs"),
  createJob: (job) =>
    request("/api/jobs", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(job),
    }),
  deleteJob: (id) => request(`/api/jobs/${id}`, { method: "DELETE" }),
  rankJobs: (analysisId) => request(`/api/analyses/${analysisId}/rank-jobs`),
};
