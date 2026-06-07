import axios from 'axios'
import apiEndpoints from '../config/api'

const emailService = {
  // Basic emails (manual pending)
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

  // Priority emails (unreviewed)
  getPriorityUnreviewed: async () => {
    console.log('Calling API:', apiEndpoints.getPriorityUnreviewed)
    const response = await axios.get(apiEndpoints.getPriorityUnreviewed)
    console.log('API Response:', response.data)
    return response.data
  },

  takePriorityAction: async (payload) => {
    console.log('Sending to API:', apiEndpoints.postPriorityAction)
    console.log('Full payload:', JSON.stringify(payload, null, 2))
    const response = await axios.post(apiEndpoints.postPriorityAction, payload)
    return response.data
  },

  // Common delete method (works for both basic and priority)
  deleteEmail: async (gmailId) => {
    console.log('Deleting via API:', apiEndpoints.deleteEmail(gmailId))
    const response = await axios.delete(apiEndpoints.deleteEmail(gmailId))
    return response.data
  }
}

export default emailService