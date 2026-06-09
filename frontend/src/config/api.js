const API_BASE_URL = 'http://localhost:8000'

const apiEndpoints = {
  getBasicManualPending: `${API_BASE_URL}/retrieval/basic/manual-pending`,
  postBasicAction: `${API_BASE_URL}/actions/basic-action`,
  getPriorityUnreviewed: `${API_BASE_URL}/retrieval/priority/unreviewed`,
  postPriorityAction: `${API_BASE_URL}/actions/priority-action`,
  getNonBusinessUnreviewed: `${API_BASE_URL}/retrieval/nonbusiness/unreviewed`,
  postNonBusinessAction: `${API_BASE_URL}/actions/nonbusiness-action`,
  deleteEmail: (gmailId) => `${API_BASE_URL}/delete/email/${gmailId}`,
  getDashboardAnalysis: `${API_BASE_URL}/analysis/get-analysis`,
  getAppointments: `${API_BASE_URL}/retrieval/appointments`,
  deleteAppointment: `${API_BASE_URL}/delete/appointment`,
  getAllEmails: `${API_BASE_URL}/retrieval/emails`,
  getProcessedEmails: `${API_BASE_URL}/retrieval/email-processing`,
}

export default apiEndpoints