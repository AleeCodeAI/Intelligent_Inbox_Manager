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
    console.log('Payload being sent:', JSON.stringify(payload, null, 2))
    const response = await axios.post(apiEndpoints.postPriorityAction, payload)
    return response.data
  },

  // Non-business emails (unreviewed)
  getNonBusinessUnreviewed: async () => {
    console.log('Calling API:', apiEndpoints.getNonBusinessUnreviewed)
    const response = await axios.get(apiEndpoints.getNonBusinessUnreviewed)
    console.log('API Response:', response.data)
    return response.data
  },

  takeNonBusinessAction: async (payload) => {
    console.log('Sending to API:', apiEndpoints.postNonBusinessAction)
    console.log('Payload being sent:', JSON.stringify(payload, null, 2))
    const response = await axios.post(apiEndpoints.postNonBusinessAction, payload)
    return response.data
  },

  // Common delete method
  deleteEmail: async (gmailId) => {
    console.log('Deleting via API:', apiEndpoints.deleteEmail(gmailId))
    const response = await axios.delete(apiEndpoints.deleteEmail(gmailId))
    return response.data
  }
}

export default emailService