import axios from 'axios'

const dropZone   = document.getElementById('drop-zone')
const fileInput  = document.getElementById('file-input')
const fileNameEl = document.getElementById('file-name')
const uploadBtn  = document.getElementById('upload-btn')
const statusEl   = document.getElementById('status')

let selectedFile = null

// Click on drop zone → open file picker
dropZone.addEventListener('click', () => fileInput.click())

// File selected via picker
fileInput.addEventListener('change', () => {
  selectFile(fileInput.files[0])
})

// Drag & drop
dropZone.addEventListener('dragover', (e) => {
  e.preventDefault()
  dropZone.classList.add('dragover')
})

dropZone.addEventListener('dragleave', () => {
  dropZone.classList.remove('dragover')
})

dropZone.addEventListener('drop', (e) => {
  e.preventDefault()
  dropZone.classList.remove('dragover')
  selectFile(e.dataTransfer.files[0])
})

function selectFile(file) {
  if (!file) return
  selectedFile = file
  fileNameEl.textContent = `📎 ${file.name}`
  uploadBtn.disabled = false
  statusEl.textContent = ''
  statusEl.className = ''
}

// Upload
uploadBtn.addEventListener('click', async () => {
  if (!selectedFile) return

  const formData = new FormData()
  formData.append('file', selectedFile)

  uploadBtn.disabled = true
  statusEl.textContent = 'Uploading...'
  statusEl.className = ''

  try {
    const res = await axios.post('/api/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    statusEl.textContent = `✅ ${res.data.message}`
    statusEl.className = 'success'
  } catch (err) {
    statusEl.textContent = `❌ Upload failed: ${err.response?.data?.detail || err.message}`
    statusEl.className = 'error'
  } finally {
    uploadBtn.disabled = false
  }
})
