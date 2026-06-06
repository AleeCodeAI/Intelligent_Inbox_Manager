const API_BASE_URL = 'http://localhost:8000'

const apiEndpoints = {
  getBasicManualPending: `${API_BASE_URL}/retrieval/basic/manual-pending`,
  postBasicAction: `${API_BASE_URL}/actions/basic-action`,
  deleteEmail: (gmailId) => `${API_BASE_URL}/delete/email/${gmailId}`,
}

export default apiEndpoints