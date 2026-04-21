<script setup>
import { ref } from 'vue'
import axios from 'axios'

const text = ref('')
const auxiliaryText = ref('')
const position = ref('bottom')
const width = ref(2048)
const height = ref(2048)
const autoFont = ref(true)
const loading = ref(false)
const generatedImage = ref(null)
const error = ref(null)

const positions = [
  { value: 'bottom', label: '底部 (默认)' },
  { value: 'top', label: '顶部' },
  { value: 'center', label: '居中' },
  { value: 'auto', label: '智能选择' },
]

// Doubao official supported sizes
const sizes = [
  { label: '1:1 正方形 2048×2048', width: 2048, height: 2048 },
  { label: '3:4 竖屏 1728×2304', width: 1728, height: 2304 },
  { label: '4:3 横屏 2304×1728', width: 2304, height: 1728 },
  { label: '16:9 宽屏 2560×1440', width: 2560, height: 1440 },
  { label: '9:16 竖屏 1440×2560', width: 1440, height: 2560 },
  { label: '2:3 竖屏 1664×2496', width: 1664, height: 2496 },
  { label: '3:2 横屏 2496×1664', width: 2496, height: 1664 },
]

async function generateImage() {
  if (!text.value.trim()) {
    error.value = '请输入文字'
    return
  }

  loading.value = true
  error.value = null
  generatedImage.value = null

  try {
    const response = await axios.post('/api/generate', {
      text: text.value.trim(),
      auxiliary_text: auxiliaryText.value.trim() || undefined,
      position: position.value,
      width: Number(width.value),
      height: Number(height.value),
      auto_font: autoFont.value,
    }, {
      responseType: 'blob',
    })

    // The response is the image blob
    const imageUrl = URL.createObjectURL(response.data)
    generatedImage.value = imageUrl
  } catch (err) {
    error.value = err.response?.data?.detail || err.message || '生成失败'
    console.error(err)
  } finally {
    loading.value = false
  }
}

function selectSize(size) {
  width.value = size.width
  height.value = size.height
}

function downloadImage() {
  if (!generatedImage.value) return
  const a = document.createElement('a')
  a.href = generatedImage.value
  const filename = text.value.replace(/[^a-zA-Z0-9\u4e00-\u9fa5]/g, '_').slice(0, 30)
  a.download = `${filename}.png`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
}
</script>

<template>
  <div class="container">
    <header class="header">
      <h1 class="title">文字转二次元背景图</h1>
      <p class="subtitle">输入文字，AI 帮你生成精美的二次元背景并自动添加文字</p>
    </header>

    <main class="main">
      <div class="card input-card">
        <div class="form-group">
          <label for="text">输入文案 <span class="label-hint">（会显示在图片上）</span></label>
          <textarea
            id="text"
            v-model="text"
            placeholder="在这里输入你的文案... 例如：樱花飘落的公园小路"
            rows="3"
          />
        </div>

        <div class="form-group">
          <label for="auxiliaryText">辅助描述 <span class="label-hint">（不会显示在图片上，仅帮助 AI 理解画面）</span></label>
          <textarea
            id="auxiliaryText"
            v-model="auxiliaryText"
            placeholder="描述你想要的画面氛围、场景细节、风格等... 例如：春天早晨，阳光透过树叶，粉色樱花，浪漫氛围"
            rows="3"
          />
        </div>

        <div class="form-row">
          <div class="form-group">
            <label>文字位置</label>
            <div class="radio-group">
              <label
                v-for="p in positions"
                :key="p.value"
                class="radio-label"
              >
                <input
                  type="radio"
                  v-model="position"
                  :value="p.value"
                />
                <span>{{ p.label }}</span>
              </label>
            </div>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label>图片尺寸</label>
            <div class="size-buttons">
              <button
                v-for="s in sizes"
                :key="s.label"
                class="size-btn"
                :class="{ active: width === s.width && height === s.height }"
                @click="selectSize(s)"
              >
                {{ s.label }}
              </button>
            </div>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <div class="checkbox-group">
              <label class="checkbox-label">
                <input
                  type="checkbox"
                  v-model="autoFont"
                />
                <span>根据文字意境自动选择字体</span>
              </label>
            </div>
          </div>
        </div>

        <div style="margin-top: 1.5rem;"></div>

        <button
          class="generate-btn"
          :disabled="loading || !text.trim()"
          @click="generateImage"
        >
          <span v-if="loading" class="loading-spinner"></span>
          <span>{{ loading ? '生成中...' : '生成图片' }}</span>
        </button>

        <div v-if="error" class="error-message">
          {{ error }}
        </div>
      </div>

      <div class="card result-card" v-if="generatedImage || loading">
        <h3 class="result-title">生成结果</h3>
        <div class="result-container">
          <div v-if="loading" class="loading-placeholder">
            <div class="loading-spinner large"></div>
            <p>AI 正在创作中，请稍候...</p>
            <p class="hint">第一次调用需要一些时间</p>
          </div>
          <div v-else-if="generatedImage" class="image-container">
            <img :src="generatedImage" alt="Generated image" />
            <div class="image-actions">
              <button class="download-btn" @click="downloadImage">
                下载图片
              </button>
            </div>
          </div>
        </div>
      </div>
    </main>

    <footer class="footer">
      <p>Powered by Doubao-seed-2.0-code + Python + Vue3</p>
    </footer>
  </div>
</template>

<style scoped>
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

.container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem 1rem;
}

.header {
  text-align: center;
  color: white;
  margin-bottom: 2rem;
}

.title {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  letter-spacing: -0.5px;
}

.subtitle {
  font-size: 1.125rem;
  opacity: 0.9;
  font-weight: 300;
}

.main {
  flex: 1;
  max-width: 900px;
  width: 100%;
  margin: 0 auto;
}

.card {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
  margin-bottom: 2rem;
}

.input-card {
  margin-bottom: 2rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  font-weight: 600;
  color: #333;
  margin-bottom: 0.5rem;
  font-size: 0.95rem;
}

.label-hint {
  font-weight: 400;
  color: #6b7280;
  font-size: 0.85rem;
}

textarea {
  width: 100%;
  padding: 0.875rem 1rem;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.2s;
  resize: vertical;
  font-family: inherit;
}

textarea:focus {
  outline: none;
  border-color: #667eea;
}

.form-row {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

.form-row .form-group {
  flex: 1;
  min-width: 250px;
  margin-bottom: 0;
}

.radio-group {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.radio-label {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 500;
}

.radio-label:has(input:checked) {
  border-color: #667eea;
  background: #667eea;
  color: white;
}

.radio-label input {
  margin: 0;
}

.checkbox-group {
  display: flex;
  gap: 0.75rem;
}

.checkbox-label {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 500;
}

.checkbox-label:has(input:checked) {
  border-color: #667eea;
  background: #667eea;
  color: white;
}

.checkbox-label input {
  margin: 0;
}

.size-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.size-btn {
  padding: 0.5rem 1rem;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  background: white;
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 500;
  font-size: 0.9rem;
}

.size-btn:hover {
  border-color: #667eea;
}

.size-btn.active {
  border-color: #667eea;
  background: #667eea;
  color: white;
}

.generate-btn {
  width: 100%;
  padding: 1rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1.125rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.generate-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
}

.generate-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.loading-spinner {
  width: 18px;
  height: 18px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.loading-spinner.large {
  width: 48px;
  height: 48px;
  border-width: 4px;
  margin-bottom: 1rem;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.error-message {
  margin-top: 1rem;
  padding: 1rem;
  background: #fef2f2;
  color: #dc2626;
  border-radius: 8px;
  font-size: 0.95rem;
}

.result-card {
  text-align: center;
}

.result-title {
  font-size: 1.25rem;
  color: #333;
  margin-bottom: 1rem;
}

.result-container {
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.loading-placeholder {
  padding: 3rem;
  color: #6b7280;
}

.loading-placeholder p {
  margin: 0.5rem 0;
}

.loading-placeholder .hint {
  font-size: 0.875rem;
  opacity: 0.7;
}

.image-container {
  width: 100%;
}

.image-container img {
  max-width: 100%;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.image-actions {
  margin-top: 1rem;
}

.download-btn {
  padding: 0.75rem 2rem;
  background: #10b981;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.download-btn:hover {
  background: #059669;
  transform: translateY(-1px);
}

.footer {
  text-align: center;
  color: rgba(255, 255, 255, 0.8);
  margin-top: 2rem;
  font-size: 0.9rem;
}

@media (max-width: 768px) {
  .title {
    font-size: 2rem;
  }

  .card {
    padding: 1.5rem;
  }

  .radio-group {
    flex-direction: column;
  }
}
</style>
