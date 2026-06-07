const API_BASE_URL = 'http://localhost:8000'

const apiEndpoints = {
  getBasicManualPending: `${API_BASE_URL}/retrieval/basic/manual-pending`,
  postBasicAction: `${API_BASE_URL}/actions/basic-action`,
  getPriorityUnreviewed: `${API_BASE_URL}/retrieval/priority/unreviewed`,
  postPriorityAction: `${API_BASE_URL}/actions/priority-action`,  // Make sure this matches your backend route
  deleteEmail: (gmailId) => `${API_BASE_URL}/delete/email/${gmailId}`,
}

export default apiEndpoints