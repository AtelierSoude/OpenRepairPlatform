import axios from 'axios'

export function getNow () {
  const today = new Date().toLocaleDateString("fr-FR").split("/")
  const day = today[0]
  const month = today[1]
  const year = today[2]
  return year + '-' + month + '-' + day
}

export function getCookie (name) {
  let cookieValue = null
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';')
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim()
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
        break
      }
    }
  }
  return cookieValue
}

const header = {
  headers: {
    'Content-Type': 'application/json; charset=UTF-8',
    'X-CSRFToken': getCookie('csrftoken')
  }
}

export async function get (url) {
  const response = axios.get(url, header)
  return await response
}

export async function post (url, data) {
  return axios.post(url, data, header)
}

export async function put (url, data) {
  return axios.put(url, data, header)
}
