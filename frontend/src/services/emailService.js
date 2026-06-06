import axios from 'axios'
import apiEndpoints from '../config/api'

const emailService = {
  getPendingEmails: async () => {
    console.log('Calling API:', apiEndpoints.getBasicManualPending)
    const response = await axios.get(apiEndpoints.getBasicManualPending)
    console.log('API Response:', response.data)
    return response.data
  },

  sendManualResponse: async (gmailId, senderName, manualResponse) => {
    console.log('Sending to API:', apiEndpoints.postBasicAction)
    const response = await axios.post(apiEndpoints.postBasicAction, {
      gmail_id: gmailId,
      sender_name: senderName,
      manual_response: manualResponse
    })
    return response.data
  },

  deleteEmail: async (gmailId) => {
    console.log('Deleting via API:', apiEndpoints.deleteEmail(gmailId))
    const response = await axios.delete(apiEndpoints.deleteEmail(gmailId))
    return response.data
  }
}

export default emailService